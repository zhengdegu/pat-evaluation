#!/bin/bash
# All-in-One 启动脚本

# 确保目录存在
mkdir -p /data/redis
mkdir -p /var/log/nginx
mkdir -p /run/nginx

# 修正 ES 数据目录权限
chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/data

exec /usr/bin/supervisord -c /etc/supervisord.conf
