# -*- coding=utf-8 -*-
from flask import Blueprint, jsonify, request, current_app as app
from elasticsearch_dsl import Search, Q
from .utils import get_patent, parse_args, run_es_query, create_es_search, json_abort
from .evaluation import get_evaluation

basic_info = Blueprint('basic_info', __name__, url_prefix='/api/basicinfo')


def get_trade_records(patid):
    """从 patent_trade 索引查询该专利的交易记录"""
    try:
        s = create_es_search('trade').query(
            Q('bool', should=[
                Q('match_phrase', **{'专利号': patid}),
            ], minimum_should_match=1)
        ).sort('交易日期')
        res = run_es_query(s)
        if res is None:
            return []
        records = []
        result_dict = res.to_dict()
        for hit in result_dict.get('hits', {}).get('hits', []):
            src = hit.get('_source', {})
            records.append({
                '交易类型': src.get('交易类型', ''),
                '交易日期': src.get('交易日期', ''),
                '交易金额': src.get('交易金额'),
                '原权利人': src.get('原权利人', ''),
                '新权利人': src.get('新权利人', ''),
                '许可类型': src.get('许可类型', ''),
                '法律事件标题': src.get('法律事件标题', ''),
            })
        return records
    except Exception as e:
        app.logger.warning("get_trade_records error for %s: %s", patid, e)
        return []


@basic_info.route('/get_patent_info')
def get_patent_info():
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    if patent is None:
        return jsonify({"error": "patent not found"}), 404

    source = patent.get('_source', {})
    result = dict(source)

    # 查询真实交易记录
    trade_records = get_trade_records(args['patid'])
    result['trade_records'] = trade_records

    # 判断是否有实际交易
    trade_value = source.get('转化收益（万元）', 0)
    try:
        trade_value = float(trade_value) if trade_value else 0.0
    except (ValueError, TypeError):
        trade_value = 0.0

    current_owner = str(source.get('当前权利人', ''))
    applicant = str(source.get('申请人', ''))
    has_transferred = (current_owner and applicant and current_owner != applicant)
    # 有交易记录、有转化收益、或权利人变更，都算有交易
    has_trade_record = any(t['交易类型'] == '转让' for t in trade_records)
    result['has_traded'] = trade_value > 0 or has_transferred or has_trade_record

    # 查询已有评估结果
    try:
        eval_result = get_evaluation(args['patid'])
        if eval_result and 'price' in eval_result:
            result['estimated_price'] = eval_result['price']
    except Exception as e:
        app.logger.warning("Failed to get evaluation for %s: %s", args['patid'], e)

    return jsonify(result)


@basic_info.route('/trade_records')
def trade_records():
    """独立的交易记录查询接口"""
    args, _ = parse_args(['patid'])
    records = get_trade_records(args['patid'])
    return jsonify(records=records, total=len(records), error_code='success')


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
