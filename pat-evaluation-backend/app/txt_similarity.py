''' -------------------------------------------------------
    基本步骤：
        1.分别统计两条字符串的关键词
        2.两条字符串的关键词合并成一个集合,相同的合并,不同的添加
        3.生成两篇文章各自的词频向量
        4.计算两个向量的余弦相似度,值越大表示越相似
    -------------------------------------------------------
'''

from __future__ import unicode_literals

import sys
sys.path.append("../")
import jieba
import jieba.posseg
import jieba.analyse
import time
import re
import os
import string
import sys
import math

# 创建停用词list
def stopwordslist(fileName):
    stopwords = [line.strip() for line in open(fileName, 'r').readlines()]
    return stopwords

# 统计关键词及个数 并计算相似度
def merge_keys(dic1,dic2):
    # 合并关键词 采用三个数组实现
    arrayKey = []
    for i in range(len(dic1)):
        arrayKey.append(dic1[i][0])  # 向数组中添加元素
    for i in range(len(dic2)):
        if dic2[i][0] not in arrayKey:
            arrayKey.append(dic2[i][0])
    else:
        print(' ')
        

    # 计算词频 infobox可忽略TF-IDF
    arrayNum1 = [0] * len(arrayKey)
    arrayNum2 = [0] * len(arrayKey)


    # 赋值arrayNum1
    for i in range(len(dic1)):
        key = dic1[i][0]
        value = dic1[i][1]
        j = 0
        while j < len(arrayKey):
            if key == arrayKey[j]:
                arrayNum1[j] = value
                break
            else:
                j = j + 1

    # 赋值arrayNum2
    for i in range(len(dic2)):
        key = dic2[i][0]
        value = dic2[i][1]
        j = 0
        while j < len(arrayKey):
            if key == arrayKey[j]:
                arrayNum2[j] = value
                break
            else:
                j = j + 1

    # print(arrayNum1)
    # print(arrayNum2)
    # print(len(arrayNum1), len(arrayNum2), len(arrayKey))

    # 计算两个向量的点积
    x = 0
    i = 0
    while i < len(arrayKey):
        x = x + arrayNum1[i] * arrayNum2[i]
        i = i + 1
    # print(x)

    # 计算两个向量的模
    i = 0
    sq1 = 0
    while i < len(arrayKey):
        sq1 = sq1 + arrayNum1[i] * arrayNum1[i]  # pow(a,2)
        i = i + 1
    # print(sq1)

    i = 0
    sq2 = 0
    while i < len(arrayKey):
        sq2 = sq2 + arrayNum2[i] * arrayNum2[i]
        i = i + 1
    # print(sq2)
    result = float(x) / (math.sqrt(sq1) * math.sqrt(sq2))
    return result


# 统计词频
def count_key(info):

    # print(info)
    # 统计格式 格式<key:value> <属性:出现个数>
    table = {}
    #stopwords = stopwordslist('stopwords.txt')  # 这里加载停用词的路径

    # 字典插入与赋值
    words = jieba.cut(info)
    for word in words:
        #if word not in stopwords:
            if word != " " and table.get(word):  # 如果存在次数加1
                num = table[word]
                table[word] = num + 1
            elif word != " ":  # 否则初值为1
                table[word] = 1

    # 键值从大到小排序 函数原型：sorted(dic,value,reverse)
    dic = sorted(table.items(), key=lambda asd: asd[1], reverse=True)
    # print(dic)
    return dic


def caculate_similarity(src, target):
    '''
    计算两段文字的相似性
    '''
    try:
        return merge_keys(count_key(src), count_key(target))
    except Exception as e:
        return 0


# 主函数
def main():
    # 计算字符串1的关键词及个数
    info1 = '若视汉语为单一语言，汉语则为当今世界上作为母语使用人数最多的语言。世界上大约有五分之一人口以汉语为母语，主要集中在中国。海外华人亦使用汉语。在中华人民共和国、香港、澳门、中华民国及新加坡，汉语被列为官方语言，更是联合国的正式语文和工作语言。随着大中华地区在世界的影响力增加，在一些国家逐渐兴起学习汉语的风潮。而在部分国家为吸引华裔观光客，会在主要车站、机场等公共场所及观光地区增加中文的标示及说明，部分服务业亦会安排通晓汉语的服务人员。ljink;i[[[][p'

    info2 = '若视汉语为单一语言，汉语则为当今世界上作为母语使用人数最多的语言。世界上大约有五分之一人口以汉语为母语，主要集中在中国。海外华人亦使用汉语。在中华人民共和国、香港、澳门、中华民国及新加坡，汉语被列为官方语言，更是联合国的正式语文和工作语言。随着大中华地区在世界的影响力增加，在一些国家逐渐兴起学习汉语的风潮。而在部分国家为吸引华裔观光客，会在主要车站、机场等公共场所及观光地区增加中文的标示及说明，部分服务业亦会安排通晓汉语的服务人员。lkjljkkjlkjljkljii  kjkj '

    print(caculate_similarity(info1, info2))

if __name__ == '__main__':
    main()
