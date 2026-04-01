# -*- coding=utf-8 -*-
from flask import Blueprint, jsonify, current_app as app
from elasticsearch_dsl import Search, Q
from .utils import get_patent, parse_args, create_es_search, run_es_query
from .algorithms import compute_similarity, compute_price
from operator import attrgetter

market_bp = Blueprint('marketfactor', __name__, url_prefix='/api/marketfactor')

SIMILAR_PARTENTS = {
    "201720980466": ["大规模智能灯具的监控系统", "0.8213173883735261"],
    "3146287": ["机群系统监控的方法和装置", "0.543192451432542"],
    "200310117036": ["一种构造大规模高可用机群操作系统的方法", "0.905567297909715"],
    "201710668951": ["大规模智能灯具的监控系统及监控方法", "0.42103322605920845"],
    "201010105065": ["一种大规模集群系统及其构建方法", "0.5842534718803264"],
    "3146284": ["机群系统运行过程监控的方法和监控管理装置", "0.4364699788438757"],
    "201910543469": ["一种应用于大规模无人机群系统中的地理位置编码方法", "0.9652144604280057"],
    "201610820902": ["一种中大规模的存储集群系统的安装方法", "0.6220460857746244"],
    "2159906": ["一种大规模机群的机群管理系统及其信息处理方法", "0.618001945278512"],
    "WO2019099961W": ["意识方法、装置、系统、机器人和计算模型", "0.49029910753768524"],
    "WO2020073900W": ["多机器人协同服务方法、装置、控制设备及系统", "0.9187915678140741"],
    "201521113767": ["大规模风电场实时在线监控系统", "0.7113855734606116"],
    "201610608126": ["一种大规模视频监控存储方法", "0.5977757333833279"],
    "201020146819": ["一种大规模风力发电监控系统", "0.4324958832121403"],
    "201510874522": ["基于SOA的大规模Web服务机群高可用实现方法", "0.5083849798873115"],
    "201010129886": ["元数据服务器、机群系统及机群系统中的文件创建方法", "0.5788742301685754"],
    "2123496": ["大规模异构机群的管理系统及传递数据和分发命令方法", "0.6847618340029707"],
    "201911400254": ["一种多电机机群系统信息监控的装置及方法", "0.7709079264048742"],
    "201911107846": ["一种面向大规模集群系统的节点故障预测方法", "0.5571655567164918"],
    "200510059184": ["一种机群系统及其设计方法", "0.5415000975274643"],
    "201110150538": ["基于多环网络拓扑结构的大规模集群系统", "0.43694082911879134"],
    "2142165": ["机群系统的顺序上下电系统及其方法", "0.9226566302136892"],
    "201210459087": ["用于大规模服务器的监控系统和方法", "0.9265188366720949"],
    "201611207817": ["一种无人机机群系统", "0.5594982661551039"],
    "201320225893": ["大规模储能系统及其监控平台", "0.7692727732305761"],
    "200510044875": ["一种跨操作系统平台的机群系统监控和管理方法", "0.5971370963390832"],
    "201910529855": ["一种大规模风电机群等值小信号模型建模方法", "0.5522228702991433"],
    "201511006156": ["大规模风电场实时在线监控系统", "0.7132615427891313"],
    "JP2015560959A": ["群集監視システムおよび群集監視方法", "0.9197246920527145"],
    "201310153665": ["一种大规模储能系统及其监控平台", "0.529925053916513"],
    "201520327765": ["大规模网络视频监控热点信息分发系统", "0.7465377580634254"],
    "201010176149": ["大规模集群系统的数据传输网络及其构建方法", "0.6838021040395096"],
    "201510574891": ["一种视频监控系统及视频大规模调度方法", "0.44221181375867435"],
    "201310295898": ["一种大规模超级电容储能模块监控系统", "0.9614623650337608"],
    "201910370144": ["一种大规模实时监控视频压缩方法", "0.5929133449653353"],
    "201810547288": ["大规模微服务系统的监控方法、装置及存储介质", "0.6813170370354098"],
    "201110069521": ["一种超大规模集群监控系统及方法", "0.9230921751397985"],
    "201680086979": ["大规模分布式系统汇总与监控的有效方法", "0.6626821772678646"],
    "201110069058": ["一种超大规模业务集群监控系统和方法", "0.9245616283504572"],
    "201911193372": ["一种大规模定制系统", "0.6760185161282342"],
    "200720178906": ["大规模数字远程网络视频监控系统", "0.6390323750473335"],
    "201721754715": ["一种用于大规模养殖鱼塘的环境远程监控系统", "0.8212502644521611"],
    "2142166": ["一种机群监控系统和方法", "0.48232532348303103"],
    "201611161261": ["大规模数据并发环境下的视频监控方法及系统", "0.6202687727834529"],
    "3146056": ["实现机群监控系统多模式机群监控界面的方法和装置", "0.858182671255987"],
    "201510259168": ["大规模网络视频监控热点信息分发系统及其分发方法", "0.6073469334666096"],
    "201010105027": ["一种管理机群的方法、装置以及机群管理与监控系统", "0.44335868363237985"],
    "201710206795": ["一种航标机群系统和对海洋污染物进行机群监测的方法", "0.5019899352927047"],
    "201120185289": ["一种大规模定制家具制造车间信息采集监控系统", "0.6177753901911096"],
    "201621335135": ["一种基于MS架构的大规模公安监控设备接入系统", "0.45797650187064376"],
    "201220025859": ["空压机群监控系统", "0.6239034849504251"],
    "201210075394": ["基于大规模云计算平台的自适应资源监控系统", "0.5192945265693747"],
    "JP2017504517A":
    ["車群管理装置、車群管理方法、車群管理プログラム及び車群表示装置", "0.46843046059205357"],
    "201720577705": ["大规模种植用监测系统", "0.4416304637258403"],
    "201210550330": ["一种大规模集群环境下的监控数据聚合方法", "0.5343455220536779"],
    "201811314109": ["一种大规模分布式系统的智能监控与管理方法及系统", "0.8251011638992894"],
    "200310103587": ["一种计算机机群系统及其作业管理方法", "0.583216745254412"],
}

NOT_INSET = [
    "201911193372", "JP2017504517A", "WO2019099961W", "2142165", "201320225893"
]

UNSIMILAR_PATENTS = {
    "200910149341": ["控制系统、联合控制系统以及控制方法", "0.13588825045578345"],
    "201480044129": ["电池控制系统、车辆控制系统", "0.06019854994257981"],
    "201480044136": ["电池控制系统、车辆控制系统", "0.22238562929090508"],
    "201480044134": ["电池控制系统、车辆控制系统", "0.2366501620109599"],
    "201410041510": ["控制系统的控制方法以及控制系统", "0.04408091475924697"],
    "201610218836": ["控制系统", "0.1656751610795854"],
    "201822271309": ["控制系统", "0.01038975602359235"],
    "201811640049": ["控制系统", "0.1638677075302899"],
    "201980035702": ["控制系统、控制系统的控制方法以及控制系统的程序", "0.13617384235318214"],
    "201480044133": ["电池控制系统、车辆控制系统", "0.2275943673073121"],
    "JP2014550876A": ["電力系統制御システム及び電力系統制御方法", "0.1841172974584189"],
    "JP2014524525A": ["電力系統制御システム及び電力系統制御方法", "0.22912432494416607"],
    "JP2017561381A": ["プリン系腐食抑制剤", "0.24633070323465225"],
    "JP2014529025A": ["駆動系制御システム", "0.003789623555975702"],
    "JP2018554533A": ["トランスポザーゼ競合物制御系", "0.1749140831317973"],
    "JP2014529025A": ["駆動系制御システム", "0.08567993179439104"],
    "JP2012555322A": ["駆動系制御装置", "0.18241944630583737"],
    "WO2020073900W": ["多机器人协同服务方法、装置、控制设备及系统", "0.18786286956204667"],
    "JP2012555322A": ["駆動系制御装置", "0.19669247589323136"],
    "JP2011545926A": ["二重系制御装置", "0.10726739171203961"],
    "JP2014550876A": ["電力系統制御システム及び電力系統制御方法", "0.0032393785342325065"],
    "201580032055": ["大规模MIMO架构", "0.07333337147149849"],
    "201510582493": ["大规模开关矩阵", "0.04944962872880773"],
    "201810883080": ["一种大规模龟鳖养殖方法", "0.2033581533484084"],
    "201410376257": ["一种大规模种植豆苗方法", "0.21255932354257986"],
    "201410348791": ["一种大规模图像检索方法", "0.005306609030591769"],
    "201811359000": ["一种大规模西瓜采摘方法", "0.16946372898088766"],
    "201910128547": ["一种大规模资产盘点方法", "0.08824250630669839"],
    "202010425764": ["一种大规模MIMO通信方法", "0.17047547843354746"],
    "200410022248": ["大规模制胶工艺及其设备", "0.21036277209280005"]
}

S1 = [
    "201410041510", "201410348791", "201580032055", "201480044134",
    "200910149341", "JP2012555322A"
]

S2 = ["202010425764", "WO2020073900W", "201480044134"]

S3 = [
    "201510582493", "201410348791", "201980035702", "201480044133",
    "201480044134"
]


def get_field_patents(patid, start=0, size=10, aggs=False) -> dict:
    patent = get_patent(patid)
    if patent is None:
        from flask import current_app as app
        app.logger.warning(f"Patent {patid} not found in get_field_patents")
        return {'hits': {'total': 0, 'hits': []}}
    
    s = create_field_query(patent, start, size, aggs)
    if s is None:
        from flask import current_app as app
        app.logger.warning(f"Failed to create field query for patent {patid}")
        return {'hits': {'total': 0, 'hits': []}}
    
    res = run_es_query(s)
    if res is None:
        from flask import current_app as app
        app.logger.warning(f"ES query returned None for get_field_patents with patid {patid}")
        return {'hits': {'total': 0, 'hits': []}}
    
    try:
        return res.to_dict()
    except Exception as e:
        from flask import current_app as app
        app.logger.error(f"Error converting ES result to dict in get_field_patents: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return {'hits': {'total': 0, 'hits': []}}


def create_field_query(patent, start=None, size=None, aggs=False) -> Search:
    if patent is None:
        return None
    
    classid = patent.get('_source', {}).get('IPC分类号', [])
    if not classid:
        from flask import current_app as app
        app.logger.warning("Patent has no IPC classification in create_field_query")
        return None
    
    q = Q('bool', should=[Q('match', IPC分类号=c) for c in classid])
    s = create_es_search('patent').query(q).filter('range',
                                                   **{'转化收益（万元）': {
                                                       'gt': 0
                                                   }})
    if start:
        s = s[start:start + size]
    if aggs:
        s.aggs.bucket('apply_per_year', 'date_histogram', field='申请日', interval='year') \
            .metric('trade_per_year', 'sum', field='转化收益（万元）')
    return s


def create_field_query_no_trade_filter(patent, start=None, size=None, aggs=False):
    """同 IPC 分类号查询，不过滤转化收益（用于申请趋势统计）"""
    if patent is None:
        return None
    classid = patent.get('_source', {}).get('IPC分类号', [])
    if not classid:
        return None
    q = Q('bool', should=[Q('match', IPC分类号=c) for c in classid])
    s = create_es_search('patent').query(q)
    if start is not None:
        s = s[start:start + size]
    if aggs:
        s.aggs.bucket('apply_per_year', 'date_histogram', field='申请日', interval='year') \
            .metric('trade_per_year', 'sum', field='转化收益（万元）')
    return s


@market_bp.route('/applytrending')
def applytrending():
    args, _ = parse_args(['patid'])
    patent = get_patent(args['patid'])
    if patent is None:
        return jsonify(apply_per_year={'buckets': []}, error_code='no_data')
    # 申请趋势不过滤转化收益
    s = create_field_query_no_trade_filter(patent, aggs=True)
    if s is None:
        return jsonify(apply_per_year={'buckets': []}, error_code='no_data')
    res = run_es_query(s)
    if res is None:
        return jsonify(apply_per_year={'buckets': []}, error_code='no_data')
    try:
        return jsonify(**res.to_dict()['aggregations'], error_code='success')
    except Exception as e:
        app.logger.error(f"applytrending aggregation error: {e}")
        return jsonify(apply_per_year={'buckets': []}, error_code='agg_error')


@market_bp.route('/tradetrending')
def tradetrending():
    args, _ = parse_args(['patid'])
    res = get_field_patents(args['patid'], aggs=True)
    aggs = res.get('aggregations', {})
    if not aggs:
        return jsonify(apply_per_year={'buckets': []}, error_code='no_data')
    return jsonify(**aggs, error_code='success')


@market_bp.route('/similarpatents')
def similarpatents():
    args, optargs = parse_args(['patid'], [('start', int), ('size', int)])
    patid = args['patid']
    start = optargs.get('start', 0)
    size = optargs.get('size', 10)

    try:
        target = get_patent(patid)
        if target is None:
            return jsonify(hits=[], total=0, error_code='patent_not_found')

        target_source = target['_source']
        target_abstract = target_source.get('摘要', '')
        target_ipc = target_source.get('IPC分类号', [])

        if not target_ipc:
            return jsonify(hits=[], total=0, error_code='no_ipc')

        # 用 IPC 分类号前4位做同领域匹配（如 C12N → 微生物/基因工程）
        ipc_prefixes = list(set(ipc[:4] for ipc in target_ipc if len(ipc) >= 4))
        should_clauses = [Q('prefix', IPC分类号=p) for p in ipc_prefixes]

        # 多取一些候选，后面用摘要相似度重排序
        fetch_size = max(size * 5, 50)
        s = create_es_search('patent').query(
            Q('bool',
              should=should_clauses,
              minimum_should_match=1,
              must_not=[Q('match_phrase', 申请号=patid)])
        )[0:fetch_size]

        res = run_es_query(s)
        if res is None:
            return jsonify(hits=[], total=0, error_code='no_results')

        result_dict = res.to_dict()
        hits = result_dict.get('hits', {}).get('hits', [])

        # 用摘要 TF-IDF 余弦相似度重排序
        for hit in hits:
            source_abstract = hit['_source'].get('摘要', '')
            if source_abstract and target_abstract:
                hit['similarity'] = compute_similarity(target_abstract, source_abstract)
            else:
                hit['similarity'] = 0.0

        # 按相似度降序排序，取分页范围
        hits.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        total = len(hits)
        paged_hits = hits[start:start + size]

        return jsonify(hits=paged_hits, total=total, error_code='success')

    except Exception as e:
        app.logger.error(f"Error in similarpatents: {e}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify(hits=[], total=0, error_code='internal_error')


@market_bp.route('/estimateprice')
def estimateprice():
    args, _ = parse_args(['patid'])
    target = get_patent(args['patid'])
    if target is None:
        return jsonify(price=0, error_code='patent_not_found')
    s = create_field_query(target)
    if s is None:
        return jsonify(price=0, error_code='no_field_query')
    piter = run_es_query(s, 'scan')
    if piter is None:
        return jsonify(price=0, error_code='es_error')
    price, _ = compute_price(target['_source'], piter)

    return jsonify(price=price, error_code='success')
