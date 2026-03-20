# -*- coding=utf-8 -*-
from flask import Blueprint, request, jsonify, current_app as app
from .utils import get_patent, parse_args, create_es_search, run_es_query

law_bp = Blueprint('lawfactor', __name__, url_prefix='/api/lawfactor')


@law_bp.route('/validityperiod')
def validityperiod():
    return jsonify(error_code='success', validity={
        "from": "1999-01-01",
        "to": "1999-01-01",
        "status": "valid"
    })


@law_bp.route('/multipleapplications')
def multipleapplications():
    apps = [
        {
            "country": "US",
            "status": "approved"
        },
        {
            "country": "CN",
            "status": "applied"
        }
    ]
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
    
    # company = '华为技术有限公司' # TODO: use real data.
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
