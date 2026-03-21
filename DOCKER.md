# 生物医药领域专利价值评价系统 — Docker 部署指南

## 镜像说明

All-in-One 单镜像，内含以下服务：

| 服务 | 说明 |
|------|------|
| Elasticsearch 6.3.2 | 专利数据存储，含 IK 中文分词插件 |
| Redis 5 | 缓存 |
| Flask + Gunicorn | Python 后端 API（端口 5001） |
| Nginx | 前端静态文件 + 反向代理（端口 80） |
| Supervisord | 进程管理 |

镜像启动时会自动：
1. 创建 ES 索引（patent_new2、wenshu、paper_data、evaluation）
2. 导入内置的 `生物医药.xlsx` 数据（约 730 条专利，仅首次启动时导入）

---

## 快速开始

### 1. 拉取镜像

```bash
docker pull ghcr.io/zhengdegu/pat-evaluation:latest
```

> 如果拉取失败，可能需要先登录 GitHub Container Registry：
> ```bash
> echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u YOUR_USERNAME --password-stdin
> ```

### 2. 运行容器

```bash
docker run -d \
  --name pat-evaluation \
  -p 80:80 \
  ghcr.io/zhengdegu/pat-evaluation:latest
```

启动后访问 http://localhost 即可使用。

### 3. 持久化数据（推荐）

```bash
docker run -d \
  --name pat-evaluation \
  -p 80:80 \
  -v pat-es-data:/usr/share/elasticsearch/data \
  -v pat-redis-data:/data/redis \
  ghcr.io/zhengdegu/pat-evaluation:latest
```

这样 ES 和 Redis 数据在容器重启后不会丢失。

---

## 自定义端口

如果 80 端口被占用：

```bash
docker run -d \
  --name pat-evaluation \
  -p 8080:80 \
  ghcr.io/zhengdegu/pat-evaluation:latest
```

访问 http://localhost:8080

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ESURL` | `http://127.0.0.1:9200` | Elasticsearch 地址 |
| `REDIS_HOST` | `127.0.0.1` | Redis 地址 |
| `REDIS_PORT` | `6379` | Redis 端口 |
| `REDIS_PASSWORD` | `salt668` | Redis 密码 |

> 默认值适用于容器内置服务，一般无需修改。

---

## 常用操作

### 查看日志

```bash
# 所有服务日志
docker exec pat-evaluation tail -f /var/log/supervisord.log

# 后端日志
docker exec pat-evaluation tail -f /var/log/backend.log

# ES 日志
docker exec pat-evaluation tail -f /var/log/elasticsearch.log

# 数据导入日志
docker exec pat-evaluation cat /var/log/data-import.log
```

### 查看服务状态

```bash
docker exec pat-evaluation supervisorctl status
```

### 检查 ES 数据量

```bash
docker exec pat-evaluation curl -s http://127.0.0.1:9200/patent_new2/_count
```

### 停止 / 启动 / 删除

```bash
docker stop pat-evaluation
docker start pat-evaluation
docker rm -f pat-evaluation
```

---

## 本地构建镜像

```bash
git clone https://github.com/zhengdegu/pat-evaluation.git
cd pat-evaluation
docker build -t pat-evaluation .
docker run -d --name pat-evaluation -p 80:80 pat-evaluation
```

---

## 系统要求

- Docker 20.10+
- 至少 2GB 内存（ES 默认分配 512MB 堆内存）
- 约 1.5GB 磁盘空间（镜像大小）
