#!/bin/bash
# 等待 ES 启动
echo "等待 Elasticsearch 启动..."
until curl -s http://127.0.0.1:9200/_cluster/health > /dev/null 2>&1; do
  sleep 2
done
echo "Elasticsearch 已就绪"

# 创建 patent_new2 索引
echo "创建 patent_new2 索引..."
curl -s -X PUT "http://127.0.0.1:9200/patent_new2" -H 'Content-Type: application/json' -d '
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "ik_smart_analyzer": {
          "type": "custom",
          "tokenizer": "ik_smart"
        },
        "ik_max_analyzer": {
          "type": "custom",
          "tokenizer": "ik_max_word"
        }
      }
    }
  },
  "mappings": {
    "content": {
      "properties": {
        "专利号":       { "type": "keyword" },
        "申请号":       { "type": "keyword" },
        "专利名":       { "type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart" },
        "主分类号":     { "type": "keyword" },
        "IPC分类号":    { "type": "keyword" },
        "申请人":       { "type": "text", "analyzer": "ik_smart", "fields": { "keyword": { "type": "keyword" } } },
        "当前权利人":   { "type": "text", "analyzer": "ik_smart" },
        "发明人":       { "type": "text" },
        "公开日":       { "type": "keyword" },
        "公开号":       { "type": "keyword" },
        "代理机构":     { "type": "text" },
        "代理人":       { "type": "text" },
        "申请日":       { "type": "date", "format": "yyyyMMdd||yyyy-MM-dd||epoch_millis", "ignore_malformed": true },
        "申请人地址":   { "type": "text" },
        "优先权":       { "type": "text" },
        "国省代码":     { "type": "keyword" },
        "摘要":         { "type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart" },
        "主权项":       { "type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart" },
        "引用专利":     { "type": "text" },
        "引用文献":     { "type": "text" },
        "法律状态":     { "type": "keyword" },
        "专利类型":     { "type": "keyword" },
        "转化收益（万元）": { "type": "float" }
      }
    }
  }
}'
echo ""

# 创建 wenshu 索引
echo "创建 wenshu 索引..."
curl -s -X PUT "http://127.0.0.1:9200/wenshu" -H 'Content-Type: application/json' -d '
{
  "settings": { "number_of_shards": 1, "number_of_replicas": 0 },
  "mappings": {
    "default": {
      "properties": {
        "当事人": { "type": "text", "analyzer": "ik_smart" },
        "案由":   { "type": "text", "analyzer": "ik_smart" },
        "法院":   { "type": "text" },
        "日期":   { "type": "date", "format": "yyyy-MM-dd||yyyyMMdd||epoch_millis", "ignore_malformed": true }
      }
    }
  }
}'
echo ""

# 创建 paper_data 索引
echo "创建 paper_data 索引..."
curl -s -X PUT "http://127.0.0.1:9200/paper_data" -H 'Content-Type: application/json' -d '
{
  "settings": { "number_of_shards": 1, "number_of_replicas": 0 },
  "mappings": {
    "content": {
      "properties": {
        "论文名称":   { "type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart" },
        "作者":       { "type": "text", "analyzer": "ik_smart" },
        "摘要":       { "type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart" },
        "发表年份":   { "type": "keyword" },
        "被引用次数": { "type": "integer" },
        "期刊":       { "type": "text", "analyzer": "ik_smart" },
        "DOI":        { "type": "keyword" },
        "PMID":       { "type": "keyword" },
        "数据来源":   { "type": "keyword" },
        "关联专利号": { "type": "keyword" },
        "关联发明人": { "type": "text", "analyzer": "ik_smart" },
        "关联申请人": { "type": "text", "analyzer": "ik_smart" }
      }
    }
  }
}'
echo ""

# 创建 evaluation 索引
echo "创建 evaluation 索引..."
curl -s -X PUT "http://127.0.0.1:9200/evaluation" -H 'Content-Type: application/json' -d '
{
  "settings": { "number_of_shards": 1, "number_of_replicas": 0 },
  "mappings": {
    "default": {
      "properties": {
        "patid":          { "type": "keyword" },
        "ts":             { "type": "date" },
        "combine_point":  { "type": "float" },
        "law_point":      { "type": "float" },
        "market_point":   { "type": "float" },
        "tech_point":     { "type": "float" },
        "price":          { "type": "float" },
        "valid":          { "type": "boolean" }
      }
    }
  }
}'
echo ""

# 创建 patent_trade 索引
echo "创建 patent_trade 索引..."
curl -s -X PUT "http://127.0.0.1:9200/patent_trade" -H 'Content-Type: application/json' -d '
{
  "settings": { "number_of_shards": 1, "number_of_replicas": 0 },
  "mappings": {
    "content": {
      "properties": {
        "专利号":       { "type": "keyword" },
        "公开号":       { "type": "keyword" },
        "交易类型":     { "type": "keyword" },
        "交易日期":     { "type": "date", "format": "yyyy-MM-dd||yyyyMMdd||epoch_millis", "ignore_malformed": true },
        "交易金额":     { "type": "float" },
        "原权利人":     { "type": "text", "analyzer": "ik_smart", "fields": { "keyword": { "type": "keyword" } } },
        "新权利人":     { "type": "text", "analyzer": "ik_smart", "fields": { "keyword": { "type": "keyword" } } },
        "许可类型":     { "type": "keyword" },
        "数据来源":     { "type": "keyword" },
        "法律事件代码": { "type": "keyword" },
        "法律事件标题": { "type": "text" },
        "原始描述":     { "type": "text" }
      }
    }
  }
}'
echo ""

echo "所有索引创建完成"
