# -*- coding=utf-8 -*-
from flask import Blueprint, jsonify, current_app as app
from .utils import get_patent, parse_args, create_es_search, run_es_query

combination_bp = Blueprint('combinationfactor', __name__, url_prefix='/api/combinationfactor')


def get_company_patents(company):
    s = create_es_search('patent').query('match_phrase', 申请人=company)
    '''
    Most fields can use index-time, on-disk doc_values for this data access pattern, but text fields do not support doc_values.
    https://www.elastic.co/guide/en/elasticsearch/reference/current/fielddata.html
    '''
    # IPC分类号在ES中是keyword类型的数组，直接使用字段名即可
    s.aggs.bucket('apply_per_class', 'terms', field='IPC分类号', size=100)
    res = run_es_query(s)
    
    if res is None:
        app.logger.warning(f"ES query returned None for get_company_patents with company {company}")
        return {'hits': {'total': 0, 'hits': []}, 'aggregations': {}}
    
    try:
        return res.to_dict()
    except Exception as e:
        app.logger.error(f"Error converting ES result to dict in get_company_patents: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return {'hits': {'total': 0, 'hits': []}, 'aggregations': {}}


@combination_bp.route('/distribution')
def distribution():
    args, _ = parse_args(['patid'])
    patents = get_patent(args['patid'])
    
    if patents is None:
        app.logger.warning(f"Patent {args['patid']} not found in distribution")
        return jsonify(aggregations={}, error_code='patent_not_found')
    
    company = patents.get('_source', {}).get('申请人', '')
    if not company:
        app.logger.warning(f"Patent {args['patid']} has no applicant in distribution")
        return jsonify(aggregations={}, error_code='no_applicant')
    
    res = get_company_patents(company)
    aggregations = res.get('aggregations', {})
    return jsonify(**aggregations, error_code='success')


@combination_bp.route('/combinationanalysis')
def combinationanalysis():
    args, _ = parse_args(['patid'])
    patents = get_patent(args['patid'])
    
    if patents is None:
        app.logger.warning(f"Patent {args['patid']} not found in combinationanalysis")
        return jsonify(hits={'total': 0, 'hits': []}, error_code='patent_not_found')
    
    company = patents.get('_source', {}).get('申请人', '')
    if not company:
        app.logger.warning(f"Patent {args['patid']} has no applicant in combinationanalysis")
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_applicant')
    
    res = get_company_patents(company)
    hits = res.get('hits', {'total': 0, 'hits': []})
    return jsonify(**hits, error_code='success')


@combination_bp.route('/dependencies')
def dependencies():
    patents = [
        {
            'name':'pat1',
            'id': 'CN123456'
        },
        {
            'name': 'pat2',
            'id': 'CN234567'
        }
    ]
    return jsonify(dependencies=patents, error_code='success')
