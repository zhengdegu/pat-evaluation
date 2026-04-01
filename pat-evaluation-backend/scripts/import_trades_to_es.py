#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将专利交易数据导入 Elasticsearch patent_trade 索引

用法：
    python scripts/import_trades_to_es.py [--es-url http://10.0.9.80:9200]
    python scripts/import_trades_to_es.py --clear
"""

import os
import sys
import json
import argparse
import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADES_FILE = os.path.join(BASE_DIR, "scripts", "output", "patent_trades.json")
EVENTS_FILE = os.path.join(BASE_DIR, "scripts", "output", "legal_events.json")

INDEX_NAME = "patent_trade"
DOC_TYPE = "content"


def ensure_index(es):
    """确保 patent_trade 索引存在"""
    if es.indices.exists(index=INDEX_NAME):
        logger.info("索引 %s 已存在", INDEX_NAME)
        count = es.count(index=INDEX_NAME)["count"]
        logger.info("当前文档数: %d", count)
        return

    mapping = {
        "mappings": {
            DOC_TYPE: {
                "properties": {
                    "专利号": {"type": "keyword"},
                    "公开号": {"type": "keyword"},
                    "交易类型": {"type": "keyword"},
                    "交易日期": {"type": "date", "format": "yyyy-MM-dd||yyyy-MM-dd HH:mm:ss||epoch_millis", "ignore_malformed": True},
                    "交易金额": {"type": "float"},
                    "原权利人": {"type": "text", "analyzer": "standard", "fields": {"keyword": {"type": "keyword"}}},
                    "新权利人": {"type": "text", "analyzer": "standard", "fields": {"keyword": {"type": "keyword"}}},
                    "许可类型": {"type": "keyword"},
                    "数据来源": {"type": "keyword"},
                    "法律事件代码": {"type": "keyword"},
                    "法律事件标题": {"type": "text"},
                    "原始描述": {"type": "text"},
                }
            }
        }
    }

    try:
        es.indices.create(index=INDEX_NAME, body=mapping)
        logger.info("创建索引 %s", INDEX_NAME)
    except Exception as e:
        logger.error("创建索引失败: %s", e)
        raise


def load_trades(path):
    """从 JSON 文件加载交易数据"""
    if not os.path.exists(path):
        logger.error("文件不存在: %s", path)
        return []
    with open(path, "r", encoding="utf-8") as f:
        trades = json.load(f)
    logger.info("从 %s 加载 %d 条交易记录", os.path.basename(path), len(trades))
    return trades


def import_to_es(es, trades):
    """批量导入交易数据到 ES"""
    if not trades:
        return 0

    batch = []
    success_total = 0

    for trade in trades:
        doc = dict(trade)
        # 清理日期字段
        date_val = doc.get("交易日期", "")
        if date_val and len(date_val) >= 10:
            doc["交易日期"] = date_val[:10]
        else:
            doc.pop("交易日期", None)

        # 清理金额字段
        if doc.get("交易金额") is None:
            doc.pop("交易金额", None)

        batch.append({
            "_index": INDEX_NAME,
            "_type": DOC_TYPE,
            "_source": doc,
        })

        if len(batch) >= 500:
            ok, failed = bulk(es, batch, raise_on_error=False)
            success_total += ok
            if failed:
                logger.warning("%d 条导入失败", len(failed))
            batch = []

    if batch:
        ok, failed = bulk(es, batch, raise_on_error=False)
        success_total += ok
        if failed:
            logger.warning("%d 条导入失败", len(failed))

    return success_total


def update_patent_legal_status(es, events_path):
    """用完整法律事件更新专利文档的法律状态字段"""
    if not os.path.exists(events_path):
        logger.warning("法律事件文件不存在: %s", events_path)
        return 0

    with open(events_path, "r", encoding="utf-8") as f:
        all_events = json.load(f)

    logger.info("准备更新 %d 条专利的法律状态", len(all_events))

    patent_index = "patent_new2"
    updated = 0

    for pat_no, info in all_events.items():
        events = info.get("events", [])
        if not events:
            continue

        # 构建法律状态摘要
        status_list = []
        for ev in events:
            status_list.append("{} {} {}".format(
                ev.get("date", ""),
                ev.get("code", ""),
                ev.get("title", ""),
            ))
        status_text = "; ".join(status_list)
        # 判断最终状态
        last_code = events[-1].get("code", "")
        if last_code in ("CX01", "CF01"):
            final_status = "失效"
        elif last_code in ("GR01", "C14"):
            final_status = "有效"
        else:
            final_status = "有效"

        # 用 update_by_query 更新
        body = {
            "script": {
                "source": "ctx._source['法律状态'] = params.status; ctx._source['法律状态详情'] = params.detail",
                "params": {
                    "status": final_status,
                    "detail": status_text,
                },
            },
            "query": {
                "bool": {
                    "should": [
                        {"match_phrase": {"专利号": pat_no}},
                        {"match_phrase": {"申请号": pat_no}},
                    ],
                    "minimum_should_match": 1,
                }
            },
        }

        try:
            resp = es.update_by_query(index=patent_index, doc_type=DOC_TYPE, body=body)
            if resp.get("updated", 0) > 0:
                updated += 1
        except Exception as e:
            logger.debug("更新 %s 失败: %s", pat_no, e)

    logger.info("更新了 %d 条专利的法律状态", updated)
    return updated


def main():
    parser = argparse.ArgumentParser(description="导入专利交易数据到 Elasticsearch")
    parser.add_argument("--es-url", default=os.environ.get("ESURL", "http://10.0.9.80:9200"))
    parser.add_argument("--clear", action="store_true", help="导入前清空索引")
    parser.add_argument("--skip-legal-update", action="store_true", help="跳过更新专利法律状态")
    args = parser.parse_args()

    logger.info("=== 专利交易数据导入 ES ===")
    logger.info("ES: %s", args.es_url)
    logger.info("索引: %s", INDEX_NAME)

    es = Elasticsearch(args.es_url)

    try:
        info = es.info()
        logger.info("ES 版本: %s", info["version"]["number"])
    except Exception as e:
        logger.error("无法连接 ES: %s", e)
        sys.exit(1)

    if args.clear and es.indices.exists(index=INDEX_NAME):
        es.indices.delete(index=INDEX_NAME)
        logger.info("已删除索引 %s", INDEX_NAME)

    ensure_index(es)

    # 导入交易数据
    trades = load_trades(TRADES_FILE)
    if trades:
        count = import_to_es(es, trades)
        logger.info("导入 %d 条交易记录", count)

    # 刷新索引
    es.indices.refresh(index=INDEX_NAME)
    final_count = es.count(index=INDEX_NAME)["count"]
    logger.info("索引总量: %d 条", final_count)

    # 更新专利法律状态
    if not args.skip_legal_update:
        update_patent_legal_status(es, EVENTS_FILE)

    logger.info("=== 完成 ===")


if __name__ == "__main__":
    main()
