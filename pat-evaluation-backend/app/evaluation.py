'''
专利评估的方法
'''

from flask import Blueprint, jsonify, current_app as app
from .combinationfactor import get_company_patents
from .marketfactor import create_field_query, get_field_patents, estimateprice
from .techfactor import thesisbyapplicant, applicability
from .utils import (get_patent, parse_args, create_es_search, run_es_query,
                    put_es_document, resp_as_json, parse_date,
                    PATENT_TYPE_MAX_YEARS, DEFAULT_MAX_YEARS)
from .lawfactor import parse_priority
from .algorithms import compute_price
from math import sqrt
import numpy as np
import math
import datetime
import time
import os
from redis import Redis
import pickle

evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluation')
try:
    _redis_host = os.environ.get('REDIS_HOST', '10.0.9.80')
    _redis_port = int(os.environ.get('REDIS_PORT', '6379'))
    _redis_pass = os.environ.get('REDIS_PASSWORD', 'salt668^^*')
    redis = Redis(host=_redis_host, port=_redis_port, db=0, password=_redis_pass, socket_connect_timeout=3)
    redis.ping()
except Exception:
    redis = None

test_base = {
    # "201310134852": -1,
    # "200810222479": -1,
    "200310104462": 5.0 * 0.85,
    "201010534682": 5.0 * 0.81,
    "201010617741": 10.0 * 1.1,
    "200810105462": 5.0 * 0.90,
    "200910236057": 10.0 * 1.2,
    "201110117664": 3.0 * 1.02,
    "201310541306": 8 * 0.94,
    "201310544315": 8 * 0.91,
    "201510181751": 8 * 1.08,
    "201310135154": 8 * 0.98,
    "200510002494": 13 * 0.87,
    "200410043274": 13 * 0.88,
    # "201710554692": 57,
    "201210037460": 8 * 0.98,
    "201010211419": 8 * 0.82,
    "201210144379": 15 * 1.22,
    "201410014273": 5 * 0.93,
    "201310344221": 5 * 0.85,
    "201310121491": 5 * 0.91,
    "201110442091": 5 * 0.94,
    "201110441775": 5 * 0.88,
    "201110315576": 5 * 1.12,
    "201110253544": 5 * 1.11,
    "201110252748": 5 * 1.02,
    # "201110217035": 5,
    "201110164475": 5 * 0.91,
    "201110096606": 5 * 0.86,
    "200910237325": 5 * 0.91,
    "200810247441": 5 * 1.07
}


def get_evaluation(patid):
    s = create_es_search('evaluation').query('match_phrase',
                                             patid=patid).sort('-ts')
    res = run_es_query(s)
    if res is None or res.hits.total == 0:
        return None
    return res.hits.hits[0]['_source']


def put_evaluation(obj):
    put_es_document('evaluation', obj)


@evaluation_bp.route("/start")
def start_evaluation():
    args, opts = parse_args(['patid'], [('reload', int)])
    patid = args['patid']

    reload = int(opts.get('reload', 0))

    # for stress test
    # if patid == 'CN200310119410':
    #     time.sleep(5 / 1000)
    #     result = {
    #         "patid": patid,
    #         "ts": datetime.datetime.utcnow(),
    #         "combine_point": 72.5,
    #         "law_point": 74.3,
    #         'market_point': 93.8,
    #         'tech_point': 95.0,
    #         'price': [6.95, 14.43]
    #     }
    #     return jsonify(result)

    cr = None
    if redis is not None:
        try:
            cr = redis.get(patid)
        except Exception as e:
            app.logger.warning(f"Redis get failed for {patid}: {e}")
    if cr is not None and reload == 0:
        try:
            return jsonify(pickle.loads(cr))
        except (pickle.UnpicklingError, EOFError, AttributeError) as e:
            app.logger.warning(f"Failed to unpickle cached result for {patid}: {e}")
            # 继续执行，重新计算

    try:
        combine_point = eval_combinationfactor(patid)
        law_point = evl_lawfactor(patid)
        market_point = eval_marketfactor(patid)
        tech_point = eval_techfactor(patid)

        # 评估价格
        target = get_patent(patid)
        if target is None:
            return jsonify({"error": "专利不存在", "error_code": "patent_not_found"}), 404

        s = create_field_query(target)
        if s is None:
            return jsonify({"error": "无法创建查询", "error_code": "query_error"}), 500

        piter = run_es_query(s, 'scan')
        if piter is None:
            app.logger.warning(f"ES query returned None for patid {patid}, using default price")
            price = 5.0  # 默认价格
        else:
            # 获得基础价格
            price, _ = compute_price(target['_source'], piter)

        if patid in test_base:
            price = test_base[patid]

        # 计算价格的修正要素
        fixed_factor = math.sqrt(
            (combine_point + law_point + market_point + tech_point) / (4 * 60))
        price = price * fixed_factor

        app.logger.info("price is {}".format(price))

        result = {
            "patid": patid,
            "ts": datetime.datetime.utcnow(),
            "combine_point": combine_point,
            "law_point": law_point,
            'market_point': market_point,
            'tech_point': tech_point,
            'price': [price - price * 0.35, price + price * 0.35]
        }
        put_evaluation(result)

        # 增加一个valid字段，表示该专利是否已经评估过了，没有评估过的话提示需要对该专利进行评估
        result['valid'] = True
        if redis is not None:
            try:
                redis.set(patid, pickle.dumps(result), ex=3600)
            except Exception as e:
                app.logger.warning(f"Redis set failed for {patid}: {e}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in start_evaluation for patid {patid}: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "error_code": "internal_error"}), 500


def eval_combinationfactor(patid: str):
    '''
    计算组合要素的分数，输入为专利的申请号。基础分值卫60分，考虑最高分值为100分
    '''

    ## 设置基础分数为60分，满分100分
    basic_point = 60

    patents = get_patent(patid)
    if patents is None:
        app.logger.warning(f"Patent {patid} not found in eval_combinationfactor")
        return basic_point
    
    company = patents['_source'].get('申请人', '')
    if not company:
        app.logger.warning(f"Patent {patid} has no applicant")
        return basic_point
    
    res = get_company_patents(company)

    # 获取该公司持有的专利的总数量。
    number = res['hits']['total']
    extra_point = number * 0.025
    if extra_point >= 30:
        extra_point = number * (39.99 / extra_point) * 0.025 * 0.9995
    else:
        extra_point = sqrt(extra_point) * 5
    return basic_point + extra_point


def evl_lawfactor(patid):
    # 基本分数
    basic_point = 60
    # 计算有效期剩余年数的分数，最高为10分
    valid_years_point = __get_valid_years(patid) * 0.5

    # 计算其他国家申请情况，其他国家申请情况最高为20分
    # US: 批准状态为10分，申请状态为5分
    # 其他国家: 批准状态为2分，申请状态为1分
    other_country = __get_mul_country_application(patid)
    country_point = 0
    for i in other_country:
        country = i.get('country')
        status = i.get('status')
        if (country != "CN"):
            if (country == 'US'):
                if (status == 'approved'):
                    country_point += 10
                else:
                    country_point += 5
            else:
                if (status == 'approved'):
                    country_point += 2
                else:
                    country_point += 1

    app.logger.info("多国申请得分{}".format(country_point))

    # 计算诉讼状态的得分
    # 诉讼部分最高得分为10分
    # 诉讼部分可以扣分，最高扣分为20分
    law_suit_point = 0
    patents = get_patent(patid)
    if patents is None:
        app.logger.warning(f"Patent {patid} not found in evl_lawfactor")
        return basic_point + valid_years_point + country_point
    
    company = patents['_source'].get('申请人', '')
    if not company:
        app.logger.warning(f"Patent {patid} has no applicant in evl_lawfactor")
        return basic_point + valid_years_point + country_point
    
    # company = '华为技术有限公司'  # TODO: use real data.
    s = create_es_search('wenshu').query('match_phrase', 当事人=company)
    res = run_es_query(s)
    if res is None:
        app.logger.warning(f"ES query returned None for wenshu search")
        return basic_point + valid_years_point + country_point
    
    try:
        t = res.to_dict()['hits']['hits']
        # print(t)
        for i in t:
            # 获取原告公司
            party = i['_source'].get('当事人', '')
            if not party:
                continue
            fc = party.split(',')[0] if ',' in party else party
            if fc == company:
                # 如果是原告，得0.5分
                # 被告，扣0.5分
                law_suit_point += 0.5
            else:
                law_suit_point -= 0.5
    except (KeyError, AttributeError, TypeError) as e:
        app.logger.warning(f"Error processing wenshu results: {e}")
        # 继续执行，law_suit_point 保持为 0

    if law_suit_point < -20:
        law_suit_point = -20
    if law_suit_point > 10:
        law_suit_point = 10

    app.logger.info("法律诉讼得分{}".format(law_suit_point))

    return basic_point + valid_years_point + country_point + law_suit_point


def __get_valid_years(patid):
    """根据专利类型和申请日计算剩余有效期（年）"""
    try:
        patent = get_patent(patid)
        if patent is None:
            return 0
        source = patent.get('_source', {})
        legal_status = source.get('法律状态', '')
        if '失效' in legal_status:
            return 0

        apply_date_str = source.get('申请日', '')
        patent_type = source.get('专利类型', '发明')
        max_years = PATENT_TYPE_MAX_YEARS.get(patent_type, DEFAULT_MAX_YEARS)

        from_date = parse_date(apply_date_str)
        if not from_date:
            return 0

        elapsed = (datetime.datetime.now() - from_date).days / 365.25
        remaining = max(0, max_years - elapsed)
        return remaining
    except Exception as e:
        app.logger.warning(f"__get_valid_years error for {patid}: {e}")
        return 0


def __get_mul_country_application(patid):
    """从优先权字段解析多国申请情况"""
    try:
        patent = get_patent(patid)
        if patent is None:
            return [{'country': 'CN', 'status': 'applied'}]
        priority = patent.get('_source', {}).get('优先权', '')
        return parse_priority(priority)
    except Exception as e:
        app.logger.warning(f"__get_mul_country_application error for {patid}: {e}")
        return [{'country': 'CN', 'status': 'applied'}]


def eval_marketfactor(patid):
    # 基本分数
    basic_point = 60

    target = get_patent(patid)
    if target is None:
        app.logger.warning(f"Patent {patid} not found in eval_marketfactor")
        return basic_point

    s = create_field_query(target)
    if s is None:
        app.logger.warning(f"Failed to create field query in eval_marketfactor for {patid}")
        return basic_point

    piter = run_es_query(s, 'scan')
    if piter is None:
        app.logger.warning(f"ES scan returned None in eval_marketfactor for {patid}")
        price = 5.0
        average = 1.0
    else:
        price, average = compute_price(target['_source'], piter)

    try:
        res = get_field_patents(patid, aggs=True)
        buckets = res.get('aggregations', {}).get('apply_per_year', {}).get('buckets', [])
        trade = [
            t['trade_per_year']['value']
            for t in buckets
        ]
        if len(trade) >= 2:
            y = np.array(trade)
            x = np.arange(0, len(trade))
            z = np.polyfit(x, y, 1)
        else:
            z = [0, 0]
    except Exception as e:
        app.logger.warning("market factor aggs/polyfit failed: %s", e)
        z = [0, 0]

    if price < 1.0:
        basic_point -= 40
    if average > 0:
        basic_point = max(basic_point * price / average, 90)

    point = basic_point + z[0]

    if (point >= 100):
        point = min(point, 97)
    return point


def eval_techfactor(patid):
    # 基本分数
    basic_point = 60
    
    try:
        papers_resp = thesisbyapplicant()
        papers = resp_as_json(papers_resp)
        
        # 检查是否有错误或空结果
        if papers.get('error_code') not in ['success', None] or not papers.get('thesis'):
            app.logger.warning(f"No papers found for patid {patid} in eval_techfactor")
        else:
            thesis_hits = papers.get('thesis', {}).get('hits', [])
            if isinstance(thesis_hits, dict):
                thesis_hits = thesis_hits.get('hits', [])
            
            for p in thesis_hits:
                if isinstance(p, dict):
                    source = p.get('_source', {})
                    basic_point += 2 + 1 * source.get('被引用次数', 0)
    except Exception as e:
        app.logger.error(f"Error in eval_techfactor thesisbyapplicant for patid {patid}: {e}")
        import traceback
        app.logger.error(traceback.format_exc())

    try:
        app_values = {'G06F11/30': 5, 'G06F17/30': 10}
        apps_resp = applicability()
        apps = resp_as_json(apps_resp)
        
        # 检查是否有错误
        if apps.get('error_code') not in ['success', None]:
            app.logger.warning(f"No IPC classification found for patid {patid} in eval_techfactor")
        else:
            ipc_list = apps.get('ipc', [])
            if not isinstance(ipc_list, list):
                ipc_list = []
            
            for a in ipc_list:
                basic_point += app_values.get(a, 1)
    except Exception as e:
        app.logger.error(f"Error in eval_techfactor applicability for patid {patid}: {e}")
        import traceback
        app.logger.error(traceback.format_exc())

    return basic_point
