# -*- coding=utf-8 -*-
import re
from flask import Blueprint, jsonify, current_app as app
from .utils import get_patent, parse_args, create_es_search, run_es_query
from elasticsearch_dsl import Q
from .txt_similarity import caculate_similarity

tech_bp = Blueprint('techfactor', __name__, url_prefix='/api/techfactor')

MAX_RESULTS = 10


def _get_hit_count(res):
    """安全获取查询结果数量"""
    if res is None:
        return 0
    try:
        return res.to_dict()['hits']['total']
    except Exception:
        return 0


def _compute_similarities(res_hits, patent_abstract, patent_name=''):
    """计算相似度并排序，没有摘要时用标题"""
    for hit in res_hits['hits']:
        src = hit.get('_source', {})
        hit_abstract = src.get('摘要', '')
        hit_title = src.get('论文名称', '')

        if hit_abstract and patent_abstract:
            src['相似度'] = caculate_similarity(patent_abstract, hit_abstract) * 100
        elif hit_title and patent_name:
            src['相似度'] = caculate_similarity(patent_name, hit_title) * 100
        else:
            src['相似度'] = 0.0

    res_hits['hits'] = sorted(
        res_hits['hits'],
        key=lambda x: x.get('_source', {}).get('相似度', 0),
        reverse=True
    )[:MAX_RESULTS]

    for hit in res_hits['hits']:
        sim = hit.get('_source', {}).get('相似度', 0)
        hit['_source']['相似度'] = "{0:.2f}%".format(sim)

    return res_hits


@tech_bp.route('/applicability')
def applicability():
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    if patent is None:
        return jsonify(ipc=[], error_code='patent_not_found')
    ipc = patent.get('_source', {}).get('IPC分类号', [])
    return jsonify(ipc=ipc if ipc else [], error_code='success')


@tech_bp.route('/thesisbyapplicant')
def thesisbyapplicant():
    """专利申请人论文 — 多层降级查询"""
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    if patent is None:
        return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='patent_not_found')

    source = patent.get('_source', {})
    patent_abstract = source.get('摘要', '')
    patent_name = source.get('专利名', '')
    patid = args['patid']
    inventors = source.get('发明人', '')
    applicant = source.get('申请人', '')

    res = None

    # 第1层：关联专利号精确匹配
    s = create_es_search('paper').query(Q('term', **{'关联专利号': patid}))
    res = run_es_query(s)

    # 第2层：发明人姓名匹配（作者 + 关联发明人）
    if _get_hit_count(res) == 0 and inventors:
        author_list = [a.strip() for a in re.split(r'[;；,，]+', inventors) if len(a.strip()) >= 2]
        if author_list:
            q = Q('bool', should=[
                Q('match_phrase', **{'作者': a}) for a in author_list
            ] + [
                Q('match_phrase', **{'关联发明人': a}) for a in author_list
            ], minimum_should_match=1)
            s = create_es_search('paper').query(q)
            res = run_es_query(s)

    # 第3层：申请人单位匹配
    if _get_hit_count(res) == 0 and applicant:
        q = Q('bool', should=[
            Q('match_phrase', **{'关联申请人': applicant}),
            Q('match', **{'作者': applicant}),
        ], minimum_should_match=1)
        s = create_es_search('paper').query(q)
        res = run_es_query(s)

    # 第4层：用专利摘要关键词搜论文
    if _get_hit_count(res) == 0 and patent_abstract:
        s = create_es_search('paper').query(
            Q('multi_match', query=patent_abstract[:200], fields=['论文名称', '摘要'], type='most_fields')
        )
        res = run_es_query(s)

    if res is None:
        return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='no_results')

    try:
        res_hits = res.to_dict()['hits']
    except Exception as e:
        app.logger.error("thesisbyapplicant error: %s", e)
        return jsonify(thesis={'hits': {'total': 0, 'hits': []}}, error_code='conversion_error')

    res_hits = _compute_similarities(res_hits, patent_abstract, patent_name)
    return jsonify(thesis=res_hits, error_code='success')


@tech_bp.route('/similarthesis')
def similarthesis():
    """其他相关论文 — 基于专利内容语义搜索"""
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    if patent is None:
        return jsonify(hits={'total': 0, 'hits': []}, error_code='patent_not_found')

    source = patent.get('_source', {})
    patent_abstract = source.get('摘要', '')
    patent_name = source.get('专利名', '')
    patid = args['patid']

    queries = []

    # 用专利摘要做语义搜索（权重高）
    if patent_abstract:
        queries.append(Q('multi_match', query=patent_abstract[:300],
                         fields=['论文名称^2', '摘要^3'], type='most_fields'))

    # 用专利名匹配（补充）
    if patent_name:
        queries.append(Q('match', **{'论文名称': {'query': patent_name, 'boost': 2}}))

    if not queries:
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_data')

    # 排除已关联到该专利的论文
    s = create_es_search('paper').query(
        Q('bool', should=queries, minimum_should_match=1,
          must_not=[Q('term', **{'关联专利号': patid})])
    )
    res = run_es_query(s)

    if res is None:
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_results')

    try:
        res_hits = res.to_dict()['hits']
    except Exception as e:
        app.logger.error("similarthesis error: %s", e)
        return jsonify(hits={'total': 0, 'hits': []}, error_code='conversion_error')

    res_hits = _compute_similarities(res_hits, patent_abstract, patent_name)
    return jsonify(**res_hits, error_code='success')
