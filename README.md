# Campus Runner

校园跑腿与校园规则智能问答系统，采用前后端分离和 AI/RAG 服务独立部署的工程结构。

## 目录结构

```text
campus-runner/
├─ backend/                 Spring Boot 后端服务
├─ frontend/
│  ├─ miniprogram/          微信小程序
│  └─ web-client/           Vue 管理端
├─ ai-rag/                  FastAPI + LangChain + ChromaDB 校园规则 RAG 服务
├─ deploy/
│  ├─ env/                  环境变量模板
│  ├─ sql/                  数据库初始化 SQL
│  └─ orangepi/             香橙派部署脚本
├─ docs/                    架构、Agent、RAG、部署和面试说明
├─ scripts/                 Windows 本地启动/停止脚本
├─ docker-compose.yml       Docker Compose 部署编排
└─ README.md
```

## AI Agent 能力

当前 AI 助手已经拆成显式状态机：

```text
SafetyAgent -> RouterAgent -> OrderAgent / TaskAgent / RuleAgent / ChatAgent
```

支持能力：

- 查询我的订单、订单状态、待完成订单
- 校验用户只能查询自己的订单
- 自然语言发布跑腿任务
- 每日订单和人员信息同步到飞书表格
- 风险任务拦截，例如替考、烟酒、危险品
- 校园规则 RAG 问答，回答带来源片段
- 可选 BGE Reranker 二次排序
- JSONL 记录 Agent 路由、Tool 调用和耗时

详细说明见：

- `docs/architecture.md`
- `docs/ai-agent-state-machine.md`
- `docs/rag-reranker.md`
- `docs/feishu-sheet-sync.md`
- `docs/interview-notes.md`

## 本地运行

确认本机已经安装 Java 17、Node.js、Python 3 和 Redis。

本地开发数据库使用项目脚本自动准备的便携 MariaDB，数据目录在：

```text
%USERPROFILE%\.campus-runner\mariadb
```

首次运行会从清华镜像下载 MariaDB，并自动创建 `campus_runner` 数据库、 用户和基础表。

后端本地私有配置文件为：

```text
backend/src/main/resources/application.yaml
```

AI/RAG 本地私有配置文件为：

```text
ai-rag/.env
```

这两个文件包含本机地址、数据库密码或 API Key，不提交到仓库。

一键启动：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-local.ps1
```

启动后访问：

- 后端：`http://localhost:8080`
- AI/RAG：`http://127.0.0.1:8000`
- Web 管理端：`http://127.0.0.1:5173/`

停止服务：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-local.ps1
```

如果只想启动或停止本地数据库：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-local-db.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\stop-local-db.ps1
```

## 数据库

新建数据库后执行：

```sql
source deploy/sql/schema.sql;
```

本地开发默认连接：

```text
host: 127.0.0.1
port: 3306
database: 
username: 
password: 
```

开发账号：

- 管理员：
- 普通用户：
- 普通用户：

## 微信小程序

微信开发者工具导入目录：

```text
frontend/miniprogram
```

本地模拟器可访问 `127.0.0.1:8080`。真机或香橙派部署时，需要把小程序请求地址改成香橙派局域网 IP 或正式 HTTPS 域名。

## 香橙派部署

部署目标建议为：

```text
Spring Boot 后端 :8080
FastAPI RAG     :8000
MariaDB         :3306
Redis           :6379
```

香橙派上先安装 Java 17、Maven/使用 Maven Wrapper、Node.js、Python 3、MariaDB、Redis，然后参考：

```bash
bash deploy/orangepi/start-orangepi.sh
```

生产部署时建议使用 systemd 管理后端和 AI/RAG 服务，Web 管理端执行 `npm run build` 后交给 Nginx 托管。

也可以直接使用 Docker Compose：

```bash
docker compose up -d --build
```
