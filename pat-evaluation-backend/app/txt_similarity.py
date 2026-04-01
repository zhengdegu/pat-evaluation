"""
文本相似度计算模块
基于 jieba TF-IDF 关键词提取 + 余弦相似度
加载生物医药专业词典提升分词准确性
"""

import os
import math
import jieba
import jieba.analyse

# 加载生物医药专业词典
_DICT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
_BIO_DICT = os.path.join(_DICT_DIR, 'biomedical_dict.txt')
if os.path.exists(_BIO_DICT):
    jieba.load_userdict(_BIO_DICT)


def _extract_keywords(text, topK=50):
    """用 TF-IDF 提取关键词及权重，返回 {word: weight}"""
    if not text or not text.strip():
        return {}
    tags = jieba.analyse.extract_tags(text, topK=topK, withWeight=True)
    return dict(tags)


def caculate_similarity(src, target):
    """计算两段文字的余弦相似度（0~1）"""
    try:
        kw1 = _extract_keywords(src)
        kw2 = _extract_keywords(target)

        if not kw1 or not kw2:
            return 0.0

        # 合并关键词集合
        all_keys = set(kw1.keys()) | set(kw2.keys())

        # 构建向量
        vec1 = [kw1.get(k, 0.0) for k in all_keys]
        vec2 = [kw2.get(k, 0.0) for k in all_keys]

        # 余弦相似度
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)
    except Exception:
        return 0.0


if __name__ == '__main__':
    # 测试
    s1 = '一种新型冠状病毒灭活疫苗的制备方法，包括Vero细胞培养和病毒接种步骤'
    s2 = '新型冠状病毒SARS-CoV-2的Vero细胞适应株培养及灭活疫苗生产工艺'
    print(f'相似度: {caculate_similarity(s1, s2):.4f}')
