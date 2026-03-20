import json
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch_dsl import Search, Document
from flask import g, current_app as app, abort, jsonify, request
import requests


def get_index_name(i) -> str:
    index_map = {
        "patent": "patent_new2",
        "wenshu": "wenshu",
        "paper": "paper_data",
        "evaluation": "evaluation"
    }

    return index_map[i]


def get_esclient() -> Elasticsearch:
    if 'esclient' not in g:
        app.logger.info('connecting to es server: %s', app.config['ESURL'])
        g.esclient = Elasticsearch(app.config['ESURL'])
    return g.esclient


def json_abort(code, *args, **kwargs) -> None:
    resp = jsonify(*args, **kwargs)
    resp.status_code = code
    abort(resp)


def resp_as_json(r):
    j = getattr(r, 'json', None)
    return j if j else json.loads(r.data)


def create_es_search(index_name) -> Search:
    s = Search(using=get_esclient(), index=get_index_name(index_name))
    return s


def put_es_document(index_name, doc, doc_type='default') -> bool:
    es = get_esclient()
    res = es.index(index=get_index_name(index_name),
                   doc_type=doc_type, body=doc)
    app.logger.info(res['result'])


def run_es_query(s: Search, action='execute'):
    app.logger.debug('%s : %s', action.ljust(8, ' '), s.to_dict())
    try:
        ret = getattr(s, action, 'execute')()
    except NotFoundError as e:
        app.logger.debug('index %s not found, available indices: \n%s', str(
            s._index), get_esclient().cat.indices())
        ret = None
    except Exception as e:
        app.logger.error('ES query error: %s', str(e))
        import traceback
        app.logger.error(traceback.format_exc())
        ret = None
    return ret


def gongsibao2patpev(resp) -> dict:
    p = resp['data']['list'][0]
    ret = {
        "_source": {
            "专利名": p['filing_name'],
            "申请号": p['filing_no'],
            "申请日": p['filing_date'],
            "摘要": p['abstr_text'],
            "申请人": p['applicant_name'][0],
            "申请人地址": p['appl_address'],
            "发明人": ';'.join(p['inventor_name']),
            "IPC分类号": p['ipc_no'],
            "公开号": p['gr_no'],
            "公开日": p['gr_date'],
            "主分类号": "G06F11/30",
            "转化收益（万元）": "0.0",
        }
    }
    # print(ret)
    return ret
#import logging
# logging.basicConfig(level=logging.DEBUG)


def get_patent_gongsibao(name) -> dict:
    """外部专利API查询 — 当前该服务已下线，直接返回None"""
    app.logger.debug("skipping gongsibao API (service offline) for: %s", name)
    return None


def get_patent(name) -> dict:
    from elasticsearch_dsl import Q
    # 同时匹配专利号和申请号，兼容两种输入
    s = create_es_search('patent').query(
        Q('bool', should=[
            Q('match_phrase', 专利号=name),
            Q('match_phrase', 申请号=name),
        ], minimum_should_match=1)
    )
    res = run_es_query(s)
    if res is None or res.hits.total == 0:
        ret = get_patent_gongsibao(name)
        if ret is None:
            json_abort(404, error_code='patent not found')
            return None
        put_es_document('patent', ret['_source'], 'content')
        return ret
    for p in res.hits.hits:
        app.logger.debug('%f %s %s %s', p['_score'], p['_source']
                         .get('专利号', ''), p['_source']['专利名'], str(p['_source']['IPC分类号']))
        break
    return res.hits.hits[0]


def parse_args(args=(), optargs=()):
    retargs = {}
    retargs2 = {}
    inp = request.args if request.method == 'GET' else request.form
    for i in args:
        n, t = i if isinstance(i, (list, tuple)) else (i, lambda x: x)
        if inp.get(n):
            retargs[n] = t(inp.get(n))
        else:
            json_abort(400, error_code='required argument %s missing' % i)
    for i in optargs:
        n, t = i if isinstance(i, (list, tuple)) else (i, lambda x: x)
        if inp.get(n):
            retargs2[n] = t(inp.get(n))

    return retargs, retargs2
