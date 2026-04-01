#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Docker 启动时自动导入专利交易数据到 Elasticsearch"""

import os
import sys
import time
import json


def wait_for_es(es_url, timeout=120):
    """等待 ES 就绪"""
    import urllib.request
    print("等待 Elasticsearch 启动...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.urlopen(es_url + '/_cluster/health', timeout=5)
            if req.status == 200:
                print("Elasticsearch 已就绪")
                return True
        except Exception:
            pass
        time.sleep(2)
    print("等待 Elasticsearch 超时")
    return False


def main():
    es_url = os.environ.get('ESURL', 'http://127.0.0.1:9200')
    trades_path = os.environ.get('TRADES_JSON', '/app/backend/scripts/output/patent_trades.json')
    events_path = os.environ.get('EVENTS_JSON', '/app/backend/scripts/output/legal_events.json')
    trade_index = 'patent_trade'
    patent_index = 'patent_new2'
    doc_type = 'content'

    if not os.path.exists(trades_path):
        print("交易数据文件不存在: %s，跳过导入" % trades_path)
        return

    if not wait_for_es(es_url):
        sys.exit(1)

    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk

    es = Elasticsearch(es_url)

    # 检查是否已有数据，避免重复导入
    try:
        count = es.count(index=trade_index)['count']
        if count > 0:
            print("索引 %s 已有 %d 条数据，跳过导入" % (trade_index, count))
            return
    except Exception:
        pass

    # 等待索引创建
    for _ in range(30):
        if es.indices.exists(index=trade_index):
            break
        time.sleep(2)

    # === 1. 导入交易数据 ===
    print("开始导入交易数据...")
    with open(trades_path, 'r', encoding='utf-8') as f:
        trades = json.load(f)

    print("共 %d 条交易记录" % len(trades))

    batch = []
    success_total = 0

    for trade in trades:
        doc = dict(trade)
        # 清理日期
        date_val = doc.get('交易日期', '')
        if date_val and len(date_val) >= 10:
            doc['交易日期'] = date_val[:10]
        else:
            doc.pop('交易日期', None)
        # 清理空金额
        if doc.get('交易金额') is None:
            doc.pop('交易金额', None)

        batch.append({'_index': trade_index, '_type': doc_type, '_source': doc})

        if len(batch) >= 500:
            ok, failed = bulk(es, batch, raise_on_error=False)
            success_total += ok
            if failed:
                print("  %d 条导入失败" % len(failed))
            batch = []

    if batch:
        ok, failed = bulk(es, batch, rerror=False)
        success_total += ok
        if failed:
            print("  %d 条导入失败" % len(failed))

    try:
        es.indices.refresh(index=trade_index)
    except Exception:
        pass

    print("交易数据导入完成: %d 条" % success_total)

    # === 2. 更新专利法律状态 ===
    if not os.path.exists(events_path):
        print("法律事件文件不存在，跳过法律状态更新")
        return

    print("开始更新专利法律状态...")
    with open(events_path, 'r', encoding='utf-8') as f:
        all_events = json.load(f)

    updated = 0
    for pat_no, info in all_events.items():
        events = info.get('events', [])
        if not events:
            continue

        # 构建法律状态摘要
        status_parts = []
        for ev in events:
            status_parts.append("%s %s %s" % (
                ev.get('date', ''), ev.get('code', ''), ev.get('title', '')))
        status_text = "; ".join(status_parts)

        # 判断最终状态
        last_code = events[-1].get('code', '')
        if last_code in ('CX01', 'CF01'):
            final_status = '失效'
        else:
            final_status = '有效'

        body = {
            'script': {
                'source': "ctx._source['法律状态'] = params.status; ctx._source['法律状态详情'] = params.detail",
                'params': {'status': final_status, 'detail': status_text},
            },
            'query': {
                'bool': {
                    'should': [
                        {'match_phrase': {'专利号': pat_no}},
                        {'match_phrase': {'申请号': pat_no}},
                    ],
                    'minimum_should_match': 1,
                }
            },
        }

        try:
            resp = es.update_by_query(index=patent_index, doc_type=doc_type, body=body)
            if resp.get('updated', 0) > 0:
                updated += 1
        except Exception:
            pass

    print("法律状态更新完成: %d 条专利" % updated)
    print("=== 交易数据导入全部完成 ===")


if __name__ == '__main__':
    main()
