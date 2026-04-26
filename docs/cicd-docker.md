# CI/CD 与 Docker 部署

本文档覆盖两部分：

1. Docker 部署到服务器
2. GitHub Actions CI/CD 工作流

---

## 1. Docker 部署

### 1.1 准备环境

服务器需要安装：

- Docker
- Docker Compose Plugin（`docker compose`）

项目使用根目录的：

- `docker-compose.yml`
- `deploy/env/docker.env`

### 1.2 准备环境变量

复制模板：

```bash
cp deploy/env/docker.env.example deploy/env/docker.env
```

至少修改这些值：

```text
MYSQL_ROOT_PASSWORD
DB_PASSWORD
EMBEDDING_API_KEY
GLM_API_KEY
```

如果使用 SCNet/Qwen3 embedding，推荐同时配置：

```text
EMBEDDING_BASE_URL=https://api.scnet.cn/api/llm/v1
EMBEDDING_MODEL=Qwen3-Embedding-8B
```

如果服务器 80/8080/8000 端口被占用，可以改：

```text
WEB_PORT
BACKEND_PORT
AI_PORT
```

### 1.3 启动 Docker 部署

```bash
bash deploy/orangepi/deploy-docker.sh
```

脚本会做这些事：

1. 读取 `deploy/env/docker.env`
2. 执行 `docker compose up -d --build`
3. 检查 ChromaDB 索引是否存在
4. 如果索引不存在且配置了 `EMBEDDING_API_KEY`、`SCNET_API_KEY` 或 `ZHIPUAI_API_KEY`，自动执行 `python src/ingest_data.py`

### 1.4 容器说明

- `mariadb`：业务数据库
- `redis`：分布式锁与缓存
- `backend`：Spring Boot 业务后端
- `ai-rag`：FastAPI Agent / RAG 服务
- `web`：Vue 管理端

### 1.5 数据持久化

Docker Compose 已配置持久化卷：

- `mariadb_data`
- `redis_data`
- `ai_rag_chroma`
- `ai_rag_logs`

其中校园规则原始文档通过只读挂载：

```text
./ai-rag/data/raw -> /app/data/raw
```

向量库索引持久化在命名卷中，不会因为重新构建镜像而丢失。

---

## 2. GitHub Actions CI

新增工作流：

- `.github/workflows/ci.yml`

CI 包含四部分：

1. `backend-test`
   - Java 17
   - 执行 `./mvnw test`
2. `web-build`
   - Node 22
   - 执行 `npm ci && npm run build`
3. `ai-check`
   - Python 3.11
   - 安装依赖并执行 `python -m compileall src`
4. `docker-config`
   - 用 `deploy/env/docker.env.example` 校验 `docker-compose.yml`

触发时机：

- `push`
- `pull_request`

---

## 3. GitHub Actions CD

新增工作流：

- `.github/workflows/cd-docker-orangepi.yml`

触发时机：

- push 到 `main`
- 手动 `workflow_dispatch`

CD 逻辑：

1. GitHub Actions 打包发布文件
2. 通过 SCP 上传到 Orange Pi
3. 通过 SSH 解压到服务器目录
4. 调用 `deploy/orangepi/deploy-docker.sh`

### 3.1 需要配置的 Secrets

在 GitHub 仓库里配置：

- `ORANGEPI_HOST`
- `ORANGEPI_USER`
- `ORANGEPI_SSH_KEY`

### 3.2 需要配置的 Repository Variables

建议配置：

- `ORANGEPI_PORT`，默认 `22`
- `ORANGEPI_APP_DIR`，例如 `/home/orangepi/apps/campus-runner`

如果不配 `ORANGEPI_APP_DIR`，工作流默认使用：

```text
/home/orangepi/apps/campus-runner
```

### 3.3 服务器首次准备

在 Orange Pi 上首次部署前，建议先手动执行：

```bash
mkdir -p /home/orangepi/apps/campus-runner/shared
cp deploy/env/docker.env.example /home/orangepi/apps/campus-runner/shared/docker.env
```

然后编辑：

```text
/home/orangepi/apps/campus-runner/shared/docker.env
```

填写真实密钥和端口配置。

CD 工作流每次发布时会优先使用这份共享环境文件：

```text
$APP_DIR/shared/docker.env
```

这样后续更新代码时不会覆盖服务器上的私有配置。

---

## 4. 推荐使用方式

### 本地开发

继续使用：

- `scripts/start-local.ps1`
- `deploy/orangepi/start-orangepi.sh`

### 服务器部署

优先使用：

```bash
bash deploy/orangepi/deploy-docker.sh
```

### 自动化发布

代码合并到 `main` 后，由 GitHub Actions 自动发布到 Orange Pi。

---

## 5. 当前方案的边界

这套 CI/CD 已经能覆盖：

- 后端测试
- 前端构建
- AI 服务基础校验
- Docker Compose 配置校验
- 代码上传服务器
- 远程 Docker 部署

但还没有做这些：

- 自动化集成测试
- Docker 镜像推送到镜像仓库
- 蓝绿发布 / 回滚
- Prometheus / Grafana 监控
- 自动告警

如果后续要继续提升，优先级建议是：

1. 增加接口级 smoke test
2. 增加镜像仓库推送
3. 增加回滚脚本
