# -*- coding=utf-8 -*-
from flask import Blueprint, jsonify, current_app as app
from .utils import get_patent, parse_args, create_es_search, run_es_query
from elasticsearch_dsl import Q
from .txt_similarity import caculate_similarity
from operator import attrgetter

tech_bp = Blueprint('techfactor', __name__, url_prefix='/api/techfactor')


@tech_bp.route('/applicability')
def applicability():
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    
    if patent is None:
        return jsonify(ipc=[], error_code='patent_not_found')
    
    ipc = patent.get('_source', {}).get('IPC分类号', [])
    if not ipc:
        ipc = []
    
    return jsonify(ipc=ipc, error_code='success')


@tech_bp.route('/thesisbyapplicant')
def thesisbyapplicant():
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    
    if patent is None:
        return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='patent_not_found')

    # 获取patent的摘要信息
    patent_abstract = patent.get('_source', {}).get('摘要', '')
    
    # 检查发明人字段是否存在
    inventors = patent.get('_source', {}).get('发明人', '')
    if not inventors:
        return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='no_inventors')

    authors = filter(lambda x: len(x) > 0, inventors.split(';'))
    q = Q('bool', should=[Q('match_phrase', **{'作者':a}) for a in authors], minimum_should_match=1)
    s = create_es_search('paper').query(q)
    res = run_es_query(s)

    # 检查ES查询结果
    if res is None:
        app.logger.warning(f"ES query returned None for thesisbyapplicant with patid {args['patid']}")
        return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='no_results')

    # 计算相似性
    try:
        res_hits = res.to_dict()['hits']
    except Exception as e:
        app.logger.error(f"Error converting ES result to dict: {e}")
        return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='conversion_error')

    for hit in res_hits['hits']:
        # app.logger.info(hit)
        hit_abstract = hit.get('_source', {}).get('摘要', '')
        if hit_abstract and patent_abstract:
            app.logger.info(hit_abstract)
            hit['_source']['相似度'] = caculate_similarity(patent_abstract, hit_abstract) * 100
        else:
            hit['_source']['相似度'] = 0.0
    
    # sorted(res_hits['hits'], key=attrgetter("_source.相似度"))
    res_hits['hits'] = sorted(res_hits['hits'], key=lambda x: x.get("_source", {}).get('相似度', 0), reverse=True)

    for hit in res_hits['hits']:
        similarity = hit.get('_source', {}).get('相似度', 0)
        hit['_source']['相似度'] = "{0:.2f}%".format(similarity)

    return jsonify(thesis=res_hits, error_code='success')


@tech_bp.route('/similarthesis')
def similarthesis():
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    
    if patent is None:
        return jsonify(hits={'total': 0, 'hits': []}, error_code='patent_not_found')

    patent_abstract = patent.get('_source', {}).get('摘要', '')
    
    name = patent.get('_source', {}).get('专利名', '')
    if not name:
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_patent_name')
    
    s = create_es_search('paper').query('match', **{'论文名称':name})
    res = run_es_query(s)

    # 检查ES查询结果
    if res is None:
        app.logger.warning(f"ES query returned None for similarthesis with patid {args['patid']}")
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_results')

    try:
        res_hits = res.to_dict()['hits']
    except Exception as e:
        app.logger.error(f"Error converting ES result to dict: {e}")
        return jsonify(hits={'total': 0, 'hits': []}, error_code='conversion_error')
    
    for hit in res_hits['hits']:
        # app.logger.info(hit)
        hit_abstract = hit.get('_source', {}).get('摘要', '')
        if hit_abstract and patent_abstract:
            app.logger.info(hit_abstract)
            hit['_source']['相似度'] = caculate_similarity(patent_abstract, hit_abstract) * 100
        else:
            hit['_source']['相似度'] = 0.0
    
    res_hits['hits'] = sorted(res_hits['hits'], key=lambda x: x.get("_source", {}).get('相似度', 0), reverse=True)
    for hit in res_hits['hits']:
        similarity = hit.get('_source', {}).get('相似度', 0)
        hit['_source']['相似度'] = "{0:.2f}%".format(similarity)
    return jsonify(**res_hits, error_code='success')
