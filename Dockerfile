# ============================================================
#  生物医药领域专利价值评价系统 — All-in-One Docker 镜像
#  包含: Elasticsearch 6.3 + IK分词, Redis, Flask后端, Nginx前端
# ============================================================

# ---- Stage 1: 构建前端 ----
FROM node:16-alpine AS frontend-build

WORKDIR /build
COPY pat-evaluation-frontend/package.json pat-evaluation-frontend/yarn.lock ./
RUN yarn install --network-timeout 120000

COPY pat-evaluation-frontend/ .
ENV CI=true
RUN yarn build --mode production


# ---- Stage 2: All-in-One 运行镜像 ----
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# ---- 系统依赖 ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-11-jre-headless \
    python3 python3-pip python3-venv \
    nginx redis-server supervisor curl wget ca-certificates unzip \
    && rm -rf /var/lib/apt/lists/*

# ---- 安装 Elasticsearch 6.3.2 ----
RUN wget -q https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.3.2.tar.gz \
    && tar -xzf elasticsearch-6.3.2.tar.gz -C /usr/share/ \
    && mv /usr/share/elasticsearch-6.3.2 /usr/share/elasticsearch \
    && rm elasticsearch-6.3.2.tar.gz \
    && useradd -r -s /bin/false elasticsearch \
    && mkdir -p /usr/share/elasticsearch/data /usr/share/elasticsearch/logs \
    && chown -R elasticsearch:elasticsearch /usr/share/elasticsearch

# ---- ES IK 中文分词插件 ----
RUN curl -fSL -o /tmp/ik.zip \
    "https://release.infinilabs.com/analysis-ik/stable/elasticsearch-analysis-ik-6.3.2.zip" \
    && mkdir -p /usr/share/elasticsearch/plugins/analysis-ik \
    && unzip -q /tmp/ik.zip -d /usr/share/elasticsearch/plugins/analysis-ik \
    && rm /tmp/ik.zip \
    && chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/plugins

# ---- ES 配置 ----
RUN echo "discovery.type: single-node" >> /usr/share/elasticsearch/config/elasticsearch.yml && \
    echo "xpack.security.enabled: false" >> /usr/share/elasticsearch/config/elasticsearch.yml && \
    echo "network.host: 127.0.0.1" >> /usr/share/elasticsearch/config/elasticsearch.yml && \
    echo "http.port: 9200" >> /usr/share/elasticsearch/config/elasticsearch.yml

# ---- Python 后端 ----
WORKDIR /app/backend
COPY pat-evaluation-backend/requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY pat-evaluation-backend/ .

# ---- 前端静态文件 ----
COPY --from=frontend-build /build/dist /usr/share/nginx/html

# ---- Nginx 配置 ----
RUN rm -f /etc/nginx/sites-enabled/default
COPY docker/nginx-aio.conf /etc/nginx/conf.d/default.conf
COPY docker/nginx-main.conf /etc/nginx/nginx.conf

# ---- 初始化脚本 & 启动脚本 ----
COPY docker/init-es.sh /app/init-es.sh
COPY docker/start.sh /app/start.sh
RUN chmod +x /app/init-es.sh /app/start.sh

# ---- Supervisord 配置 ----
COPY docker/supervisord.conf /etc/supervisord.conf

# ---- 环境变量 ----
ENV ESURL=http://127.0.0.1:9200
ENV REDIS_HOST=127.0.0.1
ENV REDIS_PORT=6379
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# ---- 数据卷 ----
VOLUME ["/usr/share/elasticsearch/data", "/data/redis"]

# ---- 端口 ----
EXPOSE 80

# ---- 启动 ----
CMD ["/app/start.sh"]
