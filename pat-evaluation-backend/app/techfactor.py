# -*- coding=utf-8 -*-
import re
from flask import Blueprint, jsonify, current_app as app
from .utils import get_patent, parse_args, create_es_search, run_es_query
from elasticsearch_dsl import Q
from .txt_similarity import caculate_similarity, _extract_keywords

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
    """其他相关论文 — 发明人 + 摘要关键词组合搜索"""
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    if patent is None:
        return jsonify(hits={'total': 0, 'hits': []}, error_code='patent_not_found')

    source = patent.get('_source', {})
    patent_abstract = source.get('摘要', '')
    patent_name = source.get('专利名', '')
    patid = args['patid']
    inventors = source.get('发明人', '')

    # 提取摘要关键词
    keywords = {}
    if patent_abstract:
        keywords = _extract_keywords(patent_abstract, topK=10)
    if not keywords and patent_name:
        keywords = _extract_keywords(patent_name, topK=10)

    # 构建关键词查询
    keyword_queries = []
    for word, weight in sorted(keywords.items(), key=lambda x: x[1], reverse=True):
        boost = max(1.0, weight * 5)
        keyword_queries.append(Q('multi_match', query=word,
                                  fields=['论文名称', '摘要'],
                                  boost=boost))

    # 构建发明人查询
    author_queries = []
    if inventors:
        author_list = [a.strip() for a in re.split(r'[;；,，]+', inventors) if len(a.strip()) >= 2]
        for a in author_list:
            author_queries.append(Q('match_phrase', **{'作者': a}))

    if not keyword_queries and not author_queries:
        return jsonify(hits={'total': 0, 'hits': []}, error_code='no_data')

    # 组合查询：发明人 + 关键词都作为 should，要求至少匹配2个条件
    all_queries = author_queries + keyword_queries
    s = create_es_search('paper').query(
        Q('bool', should=all_queries, minimum_should_match=2,
          must_not=[Q('term', **{'关联专利号': patid})])
    )
    res = run_es_query(s)

    # 降级：放宽到1个条件
    if _get_hit_count(res) == 0:
        s = create_es_search('paper').query(
            Q('bool', should=all_queries, minimum_should_match=1,
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
