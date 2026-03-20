# -*- coding=utf-8 -*-
from flask import Blueprint, jsonify, request, current_app as app
from elasticsearch_dsl import Search
from .utils import get_patent, parse_args, run_es_query, create_es_search, json_abort

basic_info = Blueprint('basic_info', __name__, url_prefix='/api/basicinfo')

@basic_info.route('/get_patent_info')
def get_patent_info():
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    if patent is None:
        return jsonify({"error": "patent not found"}), 404
    return jsonify(patent.get('_source'))


@basic_info.route('/fuzz_searh')
def fuzz_search():
    args, _ = parse_args(['keywords'])
    keywords = args['keywords'].strip()
    # 使用简单的match查询，在多个字段中搜索
    from elasticsearch_dsl import Q
    s = create_es_search('patent').query(
        Q('bool', should=[
            Q('match', 申请号=keywords),
            Q('match', 专利号=keywords),
            Q('match', 摘要=keywords),
            Q('wildcard', 专利号=f'*{keywords}*')
        ], minimum_should_match=1)
    )
    try:
        ret = run_es_query(s)
        if ret is None:
            return jsonify({"hits": {"total": 0, "hits": []}, "error_code": "no_results"})
        # 使用to_dict()方法，如果失败则手动构建响应
        try:
            result_dict = ret.to_dict()
            return jsonify(result_dict)
        except Exception as e:
            app.logger.error(f"Error converting result to dict: {e}")
            # 手动构建响应
            hits = []
            for hit in ret.hits:
                hit_dict = {
                    "_index": hit.meta.index,
                    "_type": hit.meta.doc_type,
                    "_id": hit.meta.id,
                    "_score": hit.meta.score,
                    "_source": dict(hit)
                }
                hits.append(hit_dict)
            return jsonify({
                "hits": {
                    "total": ret.hits.total,
                    "max_score": ret.hits.max_score if hasattr(ret.hits, 'max_score') else None,
                    "hits": hits
                }
            })
    except Exception as e:
        app.logger.error(f"Error in fuzz_search: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "error_code": "internal_error"}), 500
