# ============================================================
#  生物医药领域专利价值评价系统 — All-in-One Docker 镜像
#  包含: Elasticsearch 6.3 + IK分词, Redis, Flask后端, Nginx前端
# ============================================================

# ---- Stage 1: 构建前端 ----
FROM node:16-alpine AS frontend-build

WORKDIR /build
COPY pat-evaluation-frontend/package.json pat-evaluation-frontend/yarn.lock ./
RUN yarn install --frozen-lockfile --network-timeout 120000

COPY pat-evaluation-frontend/ .
ENV NODE_OPTIONS=--openssl-legacy-provider
RUN yarn build


# ---- Stage 2: All-in-One 运行镜像 ----
FROM docker.elastic.co/elasticsearch/elasticsearch:6.3.2

USER root

# ---- 系统依赖 ----
RUN yum install -y epel-release && \
    yum install -y python3 python3-pip nginx redis supervisor curl && \
    yum clean all

# ---- ES IK 中文分词插件 ----
USER elasticsearch
RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install \
    https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v6.3.2/elasticsearch-analysis-ik-6.3.2.zip
USER root

# ---- Python 后端 ----
WORKDIR /app/backend
COPY pat-evaluation-backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY pat-evaluation-backend/ .

# ---- 前端静态文件 ----
COPY --from=frontend-build /build/dist /usr/share/nginx/html

# ---- Nginx 配置 ----
COPY docker/nginx-aio.conf /etc/nginx/conf.d/default.conf
# 清除默认 nginx 配置避免冲突
RUN rm -f /etc/nginx/nginx.conf
COPY docker/nginx-main.conf /etc/nginx/nginx.conf

# ---- ES 索引初始化脚本 ----
COPY docker/init-es.sh /app/init-es.sh
RUN chmod +x /app/init-es.sh

# ---- Supervisord 配置 ----
COPY docker/supervisord.conf /etc/supervisord.conf

# ---- ES 配置 ----
RUN echo "discovery.type: single-node" >> /usr/share/elasticsearch/config/elasticsearch.yml && \
    echo "xpack.security.enabled: false" >> /usr/share/elasticsearch/config/elasticsearch.yml && \
    echo "network.host: 127.0.0.1" >> /usr/share/elasticsearch/config/elasticsearch.yml && \
    echo "http.port: 9200" >> /usr/share/elasticsearch/config/elasticsearch.yml

# ---- 环境变量 ----
ENV ESURL=http://127.0.0.1:9200
ENV REDIS_HOST=127.0.0.1
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=salt668
ENV ES_JAVA_OPTS="-Xms512m -Xmx512m"

# ---- 数据卷 ----
VOLUME ["/usr/share/elasticsearch/data", "/data/redis"]

# ---- 端口 ----
EXPOSE 80

# ---- 启动 ----
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
