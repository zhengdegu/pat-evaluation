#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清除Elasticsearch数据的脚本
支持清除指定索引的数据或删除整个索引
"""

import sys
import os
from typing import Optional, List

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


def list_indices(es: Elasticsearch) -> List[str]:
    """列出所有索引"""
    try:
        indices = es.indices.get_alias("*")
        return list(indices.keys())
    except Exception as e:
        print(f"获取索引列表失败: {e}")
        return []


def get_index_info(es: Elasticsearch, index_name: str) -> dict:
    """获取索引信息"""
    try:
        stats = es.indices.stats(index=index_name)
        return {
            'exists': es.indices.exists(index=index_name),
            'doc_count': stats['indices'][index_name]['total']['docs']['count'] if index_name in stats['indices'] else 0,
            'size': stats['indices'][index_name]['total']['store']['size_in_bytes'] if index_name in stats['indices'] else 0
        }
    except Exception as e:
        return {'exists': False, 'doc_count': 0, 'size': 0, 'error': str(e)}


def clear_index_data(es: Elasticsearch, index_name: str, doc_type: Optional[str] = None) -> bool:
    """
    清除索引中的所有数据（保留索引结构）
    
    Args:
        es: ES客户端
        index_name: 索引名称
        doc_type: 文档类型（可选，ES 6.x需要）
    
    Returns:
        是否成功
    """
    try:
        if not es.indices.exists(index=index_name):
            print(f"索引 {index_name} 不存在")
            return False
        
        # 使用delete_by_query删除所有文档
        query = {"query": {"match_all": {}}}
        
        if doc_type:
            # ES 6.x 需要指定doc_type
            result = es.delete_by_query(
                index=index_name,
                doc_type=doc_type,
                body=query,
                refresh=True
            )
        else:
            # ES 7.x+ 不需要doc_type
            result = es.delete_by_query(
                index=index_name,
                body=query,
                refresh=True
            )
        
        deleted = result.get('deleted', 0)
        print(f"✓ 成功清除 {deleted} 条文档")
        return True
        
    except Exception as e:
        print(f"✗ 清除数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def delete_index(es: Elasticsearch, index_name: str) -> bool:
    """
    删除整个索引（包括索引结构）
    
    Args:
        es: ES客户端
        index_name: 索引名称
    
    Returns:
        是否成功
    """
    try:
        if not es.indices.exists(index=index_name):
            print(f"索引 {index_name} 不存在")
            return False
        
        es.indices.delete(index=index_name)
        print(f"✓ 成功删除索引 {index_name}")
        return True
        
    except Exception as e:
        print(f"✗ 删除索引失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def clear_all_data(es: Elasticsearch, doc_type: Optional[str] = None) -> int:
    """
    清除所有索引的数据
    
    Args:
        es: ES客户端
        doc_type: 文档类型（可选）
    
    Returns:
        成功清除的索引数量
    """
    indices = list_indices(es)
    if not indices:
        print("没有找到任何索引")
        return 0
    
    print(f"找到 {len(indices)} 个索引:")
    for idx in indices:
        info = get_index_info(es, idx)
        if info['exists']:
            print(f"  - {idx}: {info['doc_count']} 条文档")
    
    count = 0
    for index_name in indices:
        if clear_index_data(es, index_name, doc_type):
            count += 1
    
    return count


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='清除Elasticsearch数据')
    parser.add_argument('--index', '-i', type=str, help='要清除的索引名称（如: patent_new2）')
    parser.add_argument('--type', '-t', type=str, default='content', help='文档类型（默认: content）')
    parser.add_argument('--delete-index', '-d', action='store_true', help='删除整个索引（而不只是数据）')
    parser.add_argument('--all', '-a', action='store_true', help='清除所有索引的数据')
    parser.add_argument('--force', '-f', action='store_true', help='跳过确认提示')
    parser.add_argument('--es-url', type=str, help='Elasticsearch服务器地址（覆盖配置）')
    
    args = parser.parse_args()
    
    # 设置ES URL
    if args.es_url:
        app.config['ESURL'] = args.es_url
    
    print("=" * 60)
    print("Elasticsearch 数据清除工具")
    print("=" * 60)
    print(f"ES服务器: {app.config['ESURL']}")
    print("-" * 60)
    
    es = get_es_client()
    
    # 检查ES连接
    if not es.ping():
        print(f"✗ 错误: 无法连接到Elasticsearch服务器 {app.config['ESURL']}")
        sys.exit(1)
    
    print("✓ ES连接成功\n")
    
    # 清除所有索引
    if args.all:
        indices = list_indices(es)
        if not indices:
            print("没有找到任何索引")
            sys.exit(0)
        
        print(f"将清除以下 {len(indices)} 个索引的数据:")
        for idx in indices:
            info = get_index_info(es, idx)
            if info['exists']:
                print(f"  - {idx}: {info['doc_count']} 条文档")
        
        if not args.force:
            confirm = input("\n确认清除所有索引的数据? (yes/no): ")
            if confirm.lower() != 'yes':
                print("已取消")
                sys.exit(0)
        
        count = clear_all_data(es, args.type)
        print(f"\n✓ 完成! 成功清除 {count} 个索引的数据")
        sys.exit(0)
    
    # 清除指定索引
    if args.index:
        index_name = args.index
        
        # 检查索引是否存在
        if not es.indices.exists(index=index_name):
            print(f"✗ 索引 {index_name} 不存在")
            sys.exit(1)
        
        # 获取索引信息
        info = get_index_info(es, index_name)
        print(f"索引: {index_name}")
        print(f"文档数: {info['doc_count']}")
        print(f"大小: {info['size'] / 1024 / 1024:.2f} MB")
        
        if not args.force:
            if args.delete_index:
                confirm = input(f"\n确认删除索引 {index_name}? (yes/no): ")
            else:
                confirm = input(f"\n确认清除索引 {index_name} 的所有数据? (yes/no): ")
            
            if confirm.lower() != 'yes':
                print("已取消")
                sys.exit(0)
        
        if args.delete_index:
            success = delete_index(es, index_name)
        else:
            success = clear_index_data(es, index_name, args.type)
        
        if success:
            print(f"\n✓ 操作成功完成")
            sys.exit(0)
        else:
            print(f"\n✗ 操作失败")
            sys.exit(1)
    
    # 如果没有指定参数，显示帮助
    parser.print_help()
    print("\n示例:")
    print("  # 清除patent_new2索引的所有数据")
    print("  python scripts/clear_es_data.py --index patent_new2")
    print("  # 删除patent_new2索引（包括结构）")
    print("  python scripts/clear_es_data.py --index patent_new2 --delete-index")
    print("  # 清除所有索引的数据")
    print("  python scripts/clear_es_data.py --all")
    print("  # 使用自定义ES地址")
    print("  python scripts/clear_es_data.py --index patent_new2 --es-url http://127.0.0.1:9201")


if __name__ == "__main__":
    main()

