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

    patent_abstract = patent.get('_source', {}).get('摘要', '')
    patid = args['patid']
    
    # 优先用关联专利号查询（论文数据中有关联专利号字段）
    s = create_es_search('paper').query(
        Q('bool', should=[
            Q('match_phrase', **{'关联专利号': patid}),
        ], minimum_should_match=1)
    )
    res = run_es_query(s)

    # 如果关联专利号没查到，再用发明人姓名查
    if res is None or res.to_dict()['hits']['total'] == 0:
        inventors = patent.get('_source', {}).get('发明人', '')
        if not inventors:
            return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='no_inventors')
        # 支持多种分隔符
        import re
        author_list = [a.strip() for a in re.split(r'[;；,，\s]+', inventors) if len(a.strip()) >= 2]
        if not author_list:
            return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='no_inventors')
        q = Q('bool', should=[
            Q('match_phrase', **{'作者': a}) for a in author_list
        ] + [
            Q('match_phrase', **{'关联发明人': a}) for a in author_list
        ], minimum_should_match=1)
        s = create_es_search('paper').query(q)
        res = run_es_query(s)

    if res is None:
        return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='no_results')

    try:
        res_hits = res.to_dict()['hits']
    except Exception as e:
        app.logger.error("Error converting ES result to dict: %s", e)
        return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='conversion_error')

    for hit in res_hits['hits']:
        hit_abstract = hit.get('_source', {}).get('摘要', '')
        if hit_abstract and patent_abstract:
            hit['_source']['相似度'] = caculate_similarity(patent_abstract, hit_abstract) * 100
        else:
            hit['_source']['相似度'] = 0.0
    
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
    patid = args['patid']
    name = patent.get('_source', {}).get('专利名', '')

    # 用专利摘要关键词 + 专利名模糊匹配论文，排除已通过关联专利号查到的
    queries = []
    if name:
        queries.append(Q('match', **{'论文名称': name}))
    if patent_abstract:
        queries.append(Q('match', **{'摘要': patent_abstract}))
    
    if not queries:
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_patent_name')

    # 排除已关联到该专利的论文（避免和 thesisbyapplicant 重复）
    s = create_es_search('paper').query(
        Q('bool', should=queries, minimum_should_match=1,
          must_not=[Q('match_phrase', **{'关联专利号': patid})])
    )
    res = run_es_query(s)

    if res is None:
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_results')

    try:
        res_hits = res.to_dict()['hits']
    except Exception as e:
        app.logger.error("Error converting ES result to dict: %s", e)
        return jsonify(hits={'total': 0, 'hits': []}, error_code='conversion_error')
    
    for hit in res_hits['hits']:
        hit_abstract = hit.get('_source', {}).get('摘要', '')
        if hit_abstract and patent_abstract:
            hit['_source']['相似度'] = caculate_similarity(patent_abstract, hit_abstract) * 100
        else:
            hit['_source']['相似度'] = 0.0
    
    res_hits['hits'] = sorted(res_hits['hits'], key=lambda x: x.get("_source", {}).get('相似度', 0), reverse=True)
    for hit in res_hits['hits']:
        similarity = hit.get('_source', {}).get('相似度', 0)
        hit['_source']['相似度'] = "{0:.2f}%".format(similarity)
    return jsonify(**res_hits, error_code='success')
