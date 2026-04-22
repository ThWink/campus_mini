# 部署说明

## 本地开发

Windows 本地运行：

```powershell
Copy-Item .\deploy\env\backend.env.example .\deploy\env\backend.env
notepad .\deploy\env\backend.env
powershell -ExecutionPolicy Bypass -File .\scripts\start-local.ps1
```

`scripts/start-local.ps1` 会自动读取 `deploy/env/backend.env`。这个文件放数据库、Redis、AI 和飞书配置，只留在本机，不提交 Git。

发布前本地检查：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-before-deploy.ps1
```

服务地址：

- Backend: `http://localhost:8080`
- AI/RAG: `http://127.0.0.1:8000`
- Web: `http://127.0.0.1:5173`
- MariaDB: `127.0.0.1:3306`
- Redis: `127.0.0.1:6379`

## Docker Compose

复制环境变量：

```bash
cp deploy/env/ai-rag.env.example .env
```

按需填写：

```text
ZHIPUAI_API_KEY=
GLM_API_KEY=
GLM_BASE_URL=
GLM_MODEL=
BGE_RERANKER_URL=
```

启动：

```bash
docker compose up -d --build
```

查看日志：

```bash
docker compose logs -f backend
docker compose logs -f ai-rag
```

## 香橙派部署建议

香橙派推荐使用 Docker Compose 管理：

- `mariadb`: 业务数据库
- `redis`: 缓存
- `backend`: Spring Boot 后端
- `ai-rag`: FastAPI Agent
- `web`: Nginx 托管 Vue 管理端

微信小程序真机测试时，后端地址需要改成香橙派局域网 IP；正式上线需要 HTTPS 域名。

## 非 Docker 香橙派发布

首次部署：

```bash
sudo mkdir -p /opt/campus-runner
sudo chown -R "$USER:$USER" /opt/campus-runner
git clone <你的仓库地址> /opt/campus-runner
cd /opt/campus-runner
cp deploy/env/backend.env.example deploy/env/backend.env
nano deploy/env/backend.env
cp deploy/env/ai-rag.env.example ai-rag/.env
nano ai-rag/.env
bash deploy/orangepi/init-db.sh
bash deploy/orangepi/start-orangepi.sh
```

以后更新：

```bash
cd /opt/campus-runner
bash deploy/orangepi/update.sh
```

如果需要手动回滚到某个版本：

```bash
cd /opt/campus-runner
git fetch --tags
git checkout v1.1.0
bash deploy/orangepi/start-orangepi.sh
```

## 版本迭代

本地开发一个功能时：

```bash
git checkout -b feature/feishu-sync
git add .
git commit -m "feat: sync daily data to feishu sheet"
git push origin feature/feishu-sync
```

测试通过后合并主分支并打版本：

```bash
git checkout main
git merge feature/feishu-sync
git tag v1.3.0
git push origin main --tags
```
