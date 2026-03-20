#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从计算所交易数据表.xlsx读取数据，填充到patent9_output.csv
不存在的字段自动生成合理的内容
摘要根据专利名自动生成
"""

import pandas as pd
import csv
import sys
import os
import random
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def format_date(date_value: Any) -> str:
    """
    格式化日期字段
    如果无法解析，返回空字符串以便后续生成
    """
    if pd.isna(date_value) or date_value is None:
        return ""
    
    # 如果是字符串，尝试解析
    if isinstance(date_value, str):
        date_value = date_value.strip()
        if not date_value or date_value == "":
            return ""
        # 尝试解析日期字符串
        try:
            # 尝试多种日期格式
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
                try:
                    dt = datetime.strptime(date_value, fmt)
                    return dt.strftime('%Y-%m-%d')
                except:
                    continue
            return date_value  # 如果无法解析，返回原字符串
        except:
            return date_value
    
    # 如果是datetime对象
    if isinstance(date_value, datetime):
        return date_value.strftime('%Y-%m-%d')
    
    # 如果是pandas Timestamp
    if hasattr(date_value, 'strftime'):
        try:
            return date_value.strftime('%Y-%m-%d')
        except:
            pass
    
    return str(date_value) if date_value else ""


def clean_value(value: Any, default: str = "") -> str:
    """
    清理值，处理NaN和None
    """
    if pd.isna(value) or value is None:
        return default
    value_str = str(value).strip()
    return value_str if value_str else default


def generate_abstract_from_title(patent_name: str) -> str:
    """
    根据专利名生成摘要
    """
    if not patent_name or patent_name == "xxx" or pd.isna(patent_name):
        return "本发明涉及一种技术方案，通过创新的方法解决了现有技术中的问题，具有重要的实用价值和应用前景。"
    
    patent_name = str(patent_name).strip()
    
    # 提取关键词
    keywords = []
    
    # 移除常见后缀
    name_clean = patent_name.replace("的方法", "").replace("的装置", "").replace("的系统", "").replace("及系统", "")
    
    # 提取技术领域关键词
    tech_keywords = ["监控", "管理", "控制", "处理", "计算", "存储", "网络", "数据", "信息", 
                     "算法", "优化", "检测", "分析", "识别", "传输", "通信", "安全", "加密"]
    
    for keyword in tech_keywords:
        if keyword in name_clean:
            keywords.append(keyword)
    
    # 生成摘要模板
    templates = [
        f"本发明提供了一种{name_clean}的技术方案。该方案通过创新的设计和方法，有效解决了现有技术中存在的问题，提高了系统的性能和可靠性，具有重要的实用价值。",
        f"本发明涉及{name_clean}领域，提供了一种新的技术实现方法。该方法通过优化算法和系统架构，显著提升了处理效率和用户体验，适用于大规模应用场景。",
        f"本发明公开了一种{name_clean}的实现方案。该方案采用先进的技术手段，实现了高效、稳定、安全的技术目标，为相关领域的发展提供了重要支撑。",
        f"本发明提供了一种{name_clean}的解决方案。通过创新的技术路径和系统设计，该方案能够有效应对复杂场景下的技术挑战，具有良好的应用前景。"
    ]
    
    # 根据专利名长度选择模板
    if len(patent_name) > 30:
        abstract = templates[0]
    elif len(patent_name) > 20:
        abstract = templates[1]
    else:
        abstract = templates[2]
    
    # 如果提取到关键词，在摘要中加入
    if keywords:
        keyword_str = "、".join(keywords[:3])
        abstract = abstract.replace("技术方案", f"{keyword_str}技术方案", 1)
    
    return abstract


def generate_applicant() -> str:
    """
    生成申请人名称（统一为中国科学院计算技术研究所）
    """
    return "中国科学院计算技术研究所"


def generate_applicant_address() -> str:
    """
    生成申请人地址（统一为中国科学院计算技术研究所地址）
    """
    return "北京市海淀区中关村科学院南路6号"


def generate_ipc_classification() -> str:
    """
    生成随机的IPC分类号
    """
    ipc_codes = [
        "G06F11/30",
        "G06F17/30",
        "G06F9/50",
        "H04L29/08",
        "G06F21/60",
        "G06F3/06",
        "G06N3/04",
        "H04L12/24",
        "G06F16/27",
        "G06F8/65"
    ]
    return random.choice(ipc_codes)


def generate_publication_number(application_number: str) -> str:
    """
    根据申请号生成公开号
    """
    if not application_number:
        year = random.randint(2000, 2023)
        num = random.randint(100000, 999999)
        return f"CN{year}{num}A"
    
    # 如果申请号格式类似，生成对应的公开号
    app_num = str(application_number).strip()
    if app_num.startswith("CN"):
        return app_num.replace("CN", "CN") + "A"
    elif len(app_num) >= 4 and app_num[:4].isdigit():
        year = app_num[:4]
        return f"CN{year}{app_num[4:]}A"
    else:
        year = random.randint(2000, 2023)
        num = random.randint(100000, 999999)
        return f"CN{year}{num}A"


def generate_main_classification(ipc: str) -> str:
    """
    根据IPC分类号生成主分类号
    """
    if ipc and ipc.strip():
        # 提取主分类号（IPC的前部分）
        parts = str(ipc).split("/")
        if len(parts) > 0:
            return parts[0]
    return generate_ipc_classification().split("/")[0]


def process_patent_number(patent_num: Any) -> str:
    """
    处理专利号，提取申请号
    """
    if pd.isna(patent_num) or patent_num is None:
        return ""
    
    patent_str = str(patent_num).strip()
    if not patent_str:
        return ""
    
    # 移除常见的专利号前缀和后缀
    patent_str = patent_str.replace('ZL', '').replace('zl', '').strip()
    # 移除末尾的 .X 或其他后缀
    if patent_str.endswith('.X') or patent_str.endswith('.x'):
        patent_str = patent_str[:-2]
    
    return patent_str


def read_excel_data(excel_file: str) -> pd.DataFrame:
    """
    读取Excel文件，正确处理表头
    Excel文件结构：第0行是标题，第1行是表头，第2行开始是数据
    """
    # 先读取所有数据，不使用表头
    df = pd.read_excel(excel_file, header=None)
    
    # 检查第一行是否是"成果转化情况"（标题行）
    if df.iloc[0, 0] == '成果转化情况':
        # 使用第二行（索引1）作为列名
        new_columns = df.iloc[1].values
        # 从第三行（索引2）开始读取数据
        df = df.iloc[2:].copy()
        df.columns = new_columns
        df = df.reset_index(drop=True)
    else:
        # 如果没有标题行，使用第一行作为表头
        new_columns = df.iloc[0].values
        df = df.iloc[1:].copy()
        df.columns = new_columns
        df = df.reset_index(drop=True)
    
    return df


def map_excel_to_csv(row: pd.Series) -> Dict[str, str]:
    """
    将Excel行数据映射到CSV格式
    缺失字段自动生成合理的内容
    """
    # CSV需要的字段列表
    csv_columns = [
        "专利名",
        "申请号",
        "申请日",
        "摘要",
        "申请人",
        "申请人地址",
        "发明人",
        "IPC分类号",
        "公开号",
        "公开日",
        "主分类号",
        "转化收益（万元）",
    ]
    
    result = {}
    
    # 映射Excel字段到CSV字段
    # 专利名称 -> 专利名
    patent_name = clean_value(row.get("专利名称", row.get("专利名", None)), "")
    if not patent_name:
        # 如果专利名也不存在，生成一个
        tech_terms = ["智能", "自动化", "高效", "优化", "创新", "先进"]
        domains = ["系统", "方法", "装置", "平台", "技术"]
        patent_name = f"{random.choice(tech_terms)}{random.choice(domains)}专利"
    result["专利名"] = patent_name
    
    # 专利号 -> 申请号
    patent_num = row.get("专利号", None)
    application_number = process_patent_number(patent_num)
    if not application_number:
        # 生成一个申请号
        year = random.randint(2000, 2023)
        num = random.randint(100000, 999999)
        application_number = f"{year}{num}"
    result["申请号"] = application_number
    
    # 申请日
    apply_date = row.get("申请日", None)
    apply_date_str = format_date(apply_date)
    if not apply_date_str or apply_date_str == "":
        # 根据申请号生成日期，或生成随机日期
        if application_number and len(application_number) >= 4 and application_number[:4].isdigit():
            year = int(application_number[:4])
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            apply_date_str = f"{year}-{month:02d}-{day:02d}"
        else:
            year = random.randint(2000, 2023)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            apply_date_str = f"{year}-{month:02d}-{day:02d}"
    result["申请日"] = apply_date_str
    
    # 摘要 - 根据专利名生成
    result["摘要"] = generate_abstract_from_title(patent_name)
    
    # 申请人 - 生成随机申请人
    applicant = clean_value(row.get("申请人", None), "")
    if not applicant:
        applicant = generate_applicant()
    result["申请人"] = applicant
    
    # 申请人地址 - 生成随机地址
    address = clean_value(row.get("申请人地址", None), "")
    if not address:
        address = generate_applicant_address()
    result["申请人地址"] = address
    
    # 发明人
    inventor = clean_value(row.get("发明人", None), "")
    if not inventor:
        # 生成随机发明人
        surnames = ["张", "王", "李", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        names = ["明", "强", "伟", "敏", "静", "丽", "军", "勇", "磊", "涛"]
        inventor = f"{random.choice(surnames)}{random.choice(names)}"
    result["发明人"] = inventor
    
    # IPC分类号 - 生成随机IPC
    ipc = clean_value(row.get("IPC分类号", None), "")
    if not ipc:
        ipc = generate_ipc_classification()
    result["IPC分类号"] = ipc
    
    # 公开号 - 根据申请号生成
    pub_number = clean_value(row.get("公开号", None), "")
    if not pub_number:
        pub_number = generate_publication_number(application_number)
    result["公开号"] = pub_number
    
    # 公开日 - Excel中有授权日，可以尝试使用，否则生成
    publish_date = row.get("公开日", row.get("授权日", None))
    publish_date_str = format_date(publish_date)
    if not publish_date_str or publish_date_str == "":
        # 根据申请日生成公开日（通常晚于申请日1-3年）
        try:
            apply_dt = datetime.strptime(apply_date_str, '%Y-%m-%d')
            days_later = random.randint(180, 1095)  # 6个月到3年
            publish_dt = apply_dt + timedelta(days=days_later)
            publish_date_str = publish_dt.strftime('%Y-%m-%d')
        except:
            year = random.randint(2000, 2023)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            publish_date_str = f"{year}-{month:02d}-{day:02d}"
    result["公开日"] = publish_date_str
    
    # 主分类号 - 根据IPC生成
    main_class = clean_value(row.get("主分类号", None), "")
    if not main_class:
        main_class = generate_main_classification(ipc)
    result["主分类号"] = main_class
    
    # 转化收益（万元）
    income = row.get("转化收益（万元）", None)
    income_str = clean_value(income, "0.0")
    if not income_str:
        income_str = "0.0"
    result["转化收益（万元）"] = income_str
    
    return result


def fill_csv_from_excel(excel_file: str, csv_file: str) -> int:
    """
    从Excel读取数据并填充到CSV文件
    """
    print(f"正在读取Excel文件: {excel_file}")
    
    try:
        df = read_excel_data(excel_file)
        print(f"成功读取 {len(df)} 行数据")
        print(f"Excel列名: {df.columns.tolist()}")
        
        # 过滤掉空行（所有字段都为空的行）
        df = df.dropna(how='all')
        print(f"过滤空行后剩余 {len(df)} 行数据")
        
        # CSV需要的字段
        csv_columns = [
            "专利名",
            "申请号",
            "申请日",
            "摘要",
            "申请人",
            "申请人地址",
            "发明人",
            "IPC分类号",
            "公开号",
            "公开日",
            "主分类号",
            "转化收益（万元）",
        ]
        
        # 写入CSV文件
        print(f"正在写入CSV文件: {csv_file}")
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            
            count = 0
            for idx, row in df.iterrows():
                # 跳过空行或表头行
                patent_name = row.get("专利名称", None)
                if pd.isna(patent_name) or str(patent_name).strip() == "" or str(patent_name).strip() == "专利名称":
                    continue
                
                # 跳过年份行（如果第一列是年份）
                if str(row.iloc[0] if len(row) > 0 else "").strip() in ["年份", "成果转化情况"]:
                    continue
                
                csv_row = map_excel_to_csv(row)
                writer.writerow(csv_row)
                count += 1
                
                if count % 10 == 0:
                    print(f"已处理 {count} 条记录...")
        
        print(f"\n✓ 成功填充 {count} 条记录到 {csv_file}")
        return count
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """主函数"""
    excel_file = "test/计算所交易数据表.xlsx"
    csv_file = "patent9_output.csv"
    
    if len(sys.argv) >= 2:
        excel_file = sys.argv[1]
    if len(sys.argv) >= 3:
        csv_file = sys.argv[2]
    
    if not os.path.exists(excel_file):
        print(f"错误: Excel文件不存在: {excel_file}")
        sys.exit(1)
    
    print("=" * 60)
    print("从Excel填充CSV文件")
    print("=" * 60)
    print(f"Excel文件: {excel_file}")
    print(f"CSV文件: {csv_file}")
    print("-" * 60)
    
    count = fill_csv_from_excel(excel_file, csv_file)
    
    if count > 0:
        print(f"\n✓ 完成! 共填充 {count} 条记录")
        sys.exit(0)
    else:
        print("\n✗ 填充失败或没有数据")
        sys.exit(1)


if __name__ == "__main__":
    main()

