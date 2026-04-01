# -*- coding=utf-8 -*-

import difflib
from .txt_similarity import caculate_similarity
from flask import current_app as app


def compute_similarity(target, patent) -> float:
    # TODO: use real Deep Learning algorithm
    return caculate_similarity(target, patent)


def compute_price(target, patents) -> (float, float):
    """
    计算基础价格。
    当转化收益数据不可用（为0）时，基于相似度和专利数量给出估算。
    """
    price = 0.0
    average = 0.0
    n = 0
    has_trade_data = False

    for p in patents:
        p = p.to_dict()
        p_abs = p['摘要'] if p.get('摘要') else target.get('摘要', '')
        if not p_abs:
            continue
        similarity = compute_similarity(target.get('摘要', ''), p_abs)
        trade_value = 0.0
        try:
            trade_value = float(p.get('转化收益（万元）', 0))
        except (ValueError, TypeError):
            pass

        if trade_value > 0:
            has_trade_data = True
            price += similarity * trade_value
            average += trade_value
        n += 1

    if has_trade_data and n > 0:
        return price / n, average / n

    # 无真实交易数据时，基于同领域专利数量给出基础估价
    # 同领域专利越多说明该领域越活跃，基础价值越高
    if n > 0:
        base = 5.0  # 基础价格 5 万元
        activity_factor = min(n / 100.0, 2.0)  # 领域活跃度系数，上限 2x
        estimated = base * (1 + activity_factor)
        return estimated, base

    return 5.0, 1.0
