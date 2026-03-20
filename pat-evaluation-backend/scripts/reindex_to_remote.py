from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Index, Mapping, Document

index_name = 'patent_new2'
doc_type = 'content'

s_client = Elasticsearch('http://10.0.9.80:9200')
d_client = Elasticsearch('http://10.0.9.80:9200')
s = Index(index_name, using=s_client)
d = Index(index_name, using=d_client)
if d.exists():
    print(d.get_mapping())
    d.delete()
print(s.get_mapping())
d.mapping(Mapping.from_es(index_name, doc_type, using=s_client))
d.create()
res = s.search().query('match_all').scan()
for i in res:
    d_client.index(index_name, doc_type, i.to_dict())