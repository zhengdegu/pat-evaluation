# -*- coding=utf-8 -*-

import difflib
from .txt_similarity import caculate_similarity
from flask import current_app as app


def compute_similarity(target, patent) -> float:
    # TODO: use real Deep Learning algorithm
    return caculate_similarity(target, patent)


def compute_price(target, patents) -> (float, float):
    price = 0.0
    average = 0.0
    n = 0
    for p in patents:
        # app.logger.info(p.to_dict())
        p = p.to_dict()
        p_abs = p['摘要'] if p.get('摘要') else target['摘要']
        similarity = compute_similarity(target['摘要'], p_abs)
        price += similarity * float(p['转化收益（万元）'])
        average += float(p['转化收益（万元）'])
        n += 1
    return 0 if n == 0 else price / n, 0 if n == 0 else average / n
