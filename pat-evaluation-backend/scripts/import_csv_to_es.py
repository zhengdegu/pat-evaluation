#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将 patent9_output.csv 文件中的数据导入到 Elasticsearch
"""

import csv
import sys
import os
from typing import Dict, List, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elasticsearch import Elasticsearch
from flask import Flask

# 创建临时Flask应用以使用项目配置
app = Flask(__name__)
app.config['ESURL'] = os.environ.get('ESURL', 'http://10.0.9.80:9200')

# ES索引映射
INDEX_MAP = {
    "patent": "patent_new2",
    "wenshu": "wenshu",
    "paper": "paper_data",
    "evaluation": "evaluation"
}


def get_es_client() -> Elasticsearch:
    """获取ES客户端"""
    return Elasticsearch(app.config['ESURL'])


def process_ipc_classification(ipc_str: Optional[str]) -> List[str]:
    """
    处理IPC分类号，转换为列表格式
    如果为空或None，返回空列表
    """
    if not ipc_str or not ipc_str.strip():
        return []
    
    # 尝试按常见分隔符分割（分号、逗号、空格等）
    ipc_list = []
    for separator in [';', '，', ',', '\n', ' ']:
        if separator in ipc_str:
            ipc_list = [item.strip() for item in ipc_str.split(separator) if item.strip()]
            break
    
    # 如果没有找到分隔符，整个字符串作为一个分类号
    if not ipc_list:
        ipc_list = [ipc_str.strip()]
    
    return ipc_list


def convert_row_to_doc(row: Dict[str, str]) -> Dict:
    """
    将CSV行转换为ES文档格式
    """
    doc = {
        "专利名": row.get("专利名", "").strip(),
        "申请号": row.get("申请号", "").strip(),
        "申请日": row.get("申请日", "").strip(),
        "摘要": row.get("摘要", "").strip(),
        "申请人": row.get("申请人", "").strip(),
        "申请人地址": row.get("申请人地址", "").strip(),
        "发明人": row.get("发明人", "").strip(),
        "IPC分类号": process_ipc_classification(row.get("IPC分类号", "")),
        "专利号": row.get("专利号", "").strip(),
        "公开日": row.get("公开日", "").strip(),
        "主分类号": row.get("主分类号", "").strip(),
        "转化收益（万元）": row.get("转化收益（万元）", "0.0").strip(),
    }
    
    return doc


def import_csv_to_es(csv_file: str, index_name: str = "patent_new2", doc_type: str = "content", 
                     batch_size: int = 100) -> int:
    """
    将CSV文件导入到Elasticsearch
    
    Args:
        csv_file: CSV文件路径
        index_name: ES索引名称
        doc_type: 文档类型
        batch_size: 批量导入大小
    
    Returns:
        成功导入的记录数
    """
    es = get_es_client()
    
    # 检查ES连接
    if not es.ping():
        print(f"错误: 无法连接到Elasticsearch服务器 {app.config['ESURL']}")
        return 0
    
    # 检查索引是否存在，如果不存在则创建
    if not es.indices.exists(index=index_name):
        print(f"索引 {index_name} 不存在，将自动创建...")
        # 创建索引（使用基本映射）
        es.indices.create(index=index_name, body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                doc_type: {
                    "properties": {
                        "专利名": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                        "申请号": {"type": "keyword"},
                        "申请日": {"type": "date", "format": "yyyy-MM-dd||yyyy/MM/dd||yyyyMMdd"},
                        "摘要": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                        "申请人": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                        "申请人地址": {"type": "text"},
                        "发明人": {"type": "text"},
                        "IPC分类号": {"type": "keyword"},
                        "专利号": {"type": "keyword"},
                        "公开日": {"type": "date", "format": "yyyy-MM-dd||yyyy/MM/dd||yyyyMMdd"},
                        "主分类号": {"type": "keyword"},
                        "转化收益（万元）": {"type": "float"}
                    }
                }
            }
        })
        print(f"索引 {index_name} 创建成功")
    
    imported_count = 0
    batch = []
    
    print(f"开始读取CSV文件: {csv_file}")
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是表头）
                # 跳过空行
                if not any(row.values()):
                    continue
                
                # 检查必需字段
                if not row.get("申请号", "").strip():
                    print(f"警告: 第 {row_num} 行缺少申请号，跳过")
                    continue
                
                # 转换为ES文档格式
                doc = convert_row_to_doc(row)
                
                batch.append({
                    "_index": index_name,
                    "_type": doc_type,
                    "_source": doc
                })
                
                # 批量导入
                if len(batch) >= batch_size:
                    from elasticsearch.helpers import bulk
                    success, failed = bulk(es, batch, raise_on_error=False)
                    imported_count += success
                    if failed:
                        print(f"警告: {len(failed)} 条记录导入失败")
                    batch = []
                    print(f"已导入 {imported_count} 条记录...")
            
            # 导入剩余记录
            if batch:
                from elasticsearch.helpers import bulk
                success, failed = bulk(es, batch, raise_on_error=False)
                imported_count += success
                if failed:
                    print(f"警告: {len(failed)} 条记录导入失败")
        
        print(f"\n导入完成! 共成功导入 {imported_count} 条记录到索引 {index_name}")
        return imported_count
        
    except FileNotFoundError:
        print(f"错误: 文件 {csv_file} 不存在")
        return 0
    except Exception as e:
        print(f"错误: 导入过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return imported_count


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python scripts/import_csv_to_es.py <csv_file> [index_name] [doc_type]")
        print("示例: python scripts/import_csv_to_es.py patent9_output.csv")
        print("      python scripts/import_csv_to_es.py patent9_output.csv patent_new2 content")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    index_name = sys.argv[2] if len(sys.argv) >= 3 else "patent_new2"
    doc_type = sys.argv[3] if len(sys.argv) >= 4 else "content"
    
    # 支持环境变量设置ES URL
    if 'ESURL' in os.environ:
        app.config['ESURL'] = os.environ['ESURL']
    
    print(f"ES服务器: {app.config['ESURL']}")
    print(f"目标索引: {index_name}")
    print(f"文档类型: {doc_type}")
    print("-" * 50)
    
    count = import_csv_to_es(csv_file, index_name, doc_type)
    
    if count > 0:
        print(f"\n✓ 成功导入 {count} 条记录")
        sys.exit(0)
    else:
        print("\n✗ 导入失败或没有数据")
        sys.exit(1)


if __name__ == "__main__":
    main()



# 基本用法（使用默认索引和文档类型）
# python3 scripts/import_csv_to_es.py patent9_output.csv

# 指定索引和文档类型
# python3 scripts/import_csv_to_es.py patent9_output.csv patent_new2 content

# 使用自定义ES服务器地址
# ESURL=http://10.0.9.80:9200 python3 scripts/import_csv_to_es.py patent9_output.csv