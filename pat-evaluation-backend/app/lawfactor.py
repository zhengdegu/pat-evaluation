# -*- coding=utf-8 -*-
import re
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app as app
from .utils import (get_patent, parse_args, create_es_search, run_es_query,
                    parse_date, PATENT_TYPE_MAX_YEARS, DEFAULT_MAX_YEARS)

law_bp = Blueprint('lawfactor', __name__, url_prefix='/api/lawfactor')

# 国家代码集合（用于优先权解析）
KNOWN_COUNTRY_CODES = {
    'US', 'EP', 'JP', 'KR', 'GB', 'FR', 'DE', 'CU',
    'WO', 'CN', 'AU', 'CA', 'IN', 'BR', 'RU', 'IL',
    'SG', 'TW', 'HK', 'NZ', 'ZA', 'MX', 'SE', 'CH',
    'NL', 'IT', 'ES', 'DK', 'FI', 'NO', 'AT', 'BE',
    'PT', 'IE', 'PL', 'CZ', 'HU', 'TH', 'PH', 'MY',
}


def parse_priority(priority_str):
    """从优先权字段解析多国申请情况"""
    if not priority_str:
        return [{'country': 'CN', 'status': 'applied'}]

    countries = set()
    for part in re.split(r'[;；,，\s]+', str(priority_str)):
        part = part.strip()
        if len(part) >= 2:
            code = part[:2].upper()
            if code in KNOWN_COUNTRY_CODES:
                countries.add(code)

    if not countries:
        return [{'country': 'CN', 'status': 'applied'}]

    # 优先权记录标记为 applied（无法从该字段确定是否已授权）
    return [{'country': c, 'status': 'applied'} for c in sorted(countries)]


@law_bp.route('/validityperiod')
def validityperiod():
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    if patent is None:
        return jsonify(error_code='patent_not_found', validity={
            'from': '', 'to': '', 'status': 'unknown', 'max_years': 0, 'patent_type': ''
        })

    source = patent.get('_source', {})
    apply_date_str = source.get('申请日', '')
    patent_type = source.get('专利类型', '发明')
    legal_status = source.get('法律状态', '')

    max_years = PATENT_TYPE_MAX_YEARS.get(patent_type, DEFAULT_MAX_YEARS)
    from_date = parse_date(apply_date_str)

    if from_date:
        to_year = from_date.year + max_years
        to_date = from_date.replace(year=to_year)
    else:
        to_date = None

    # 失效专利
    status = 'invalid' if '失效' in legal_status else 'valid'

    return jsonify(error_code='success', validity={
        'from': from_date.strftime('%Y-%m-%d') if from_date else '',
        'to': to_date.strftime('%Y-%m-%d') if to_date else '',
        'status': status,
        'max_years': max_years,
        'patent_type': patent_type
    })


@law_bp.route('/multipleapplications')
def multipleapplications():
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    if patent is None:
        return jsonify(error_code='patent_not_found', applications=[])

    priority = patent.get('_source', {}).get('优先权', '')
    apps = parse_priority(priority)
    return jsonify(error_code='success', applications=apps)


@law_bp.route('/lawsuits')
def lawsuits():
    args, _ = parse_args(['patid'])

    patents = get_patent(args['patid'])
    if patents is None:
        app.logger.warning(f"Patent {args['patid']} not found in lawsuits")
        return jsonify(hits={'total': 0, 'hits': []}, error_code='patent_not_found')

    company = patents.get('_source', {}).get('申请人', '')
    if not company:
        app.logger.warning(f"Patent {args['patid']} has no applicant in lawsuits")
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_applicant')

    s = create_es_search('wenshu').query('match_phrase', 当事人=company)
    res = run_es_query(s)

    if res is None:
        app.logger.warning(f"ES query returned None for wenshu search with company {company}")
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_results')

    try:
        result_dict = res.to_dict()['hits']
        return jsonify(**result_dict, error_code='success')
    except Exception as e:
        app.logger.error(f"Error converting ES result to dict in lawsuits: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify(hits={'total': 0, 'hits': []}, error_code='conversion_error')
