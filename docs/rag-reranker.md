# RAG 与 BGE Reranker

## 文档向量化

校园规则制度文档通过 `ai-rag/src/ingest_data.py` 入库。

```text
原始规则文本
  -> rule_chunking 按标题/条款切 chunk
  -> Qwen3-Embedding-8B 生成语义向量
  -> ChromaDB 持久化
```

## Embedding 模型

当前准备使用 SCNet 的 `Qwen3-Embedding-8B` 作为校园规则文档和用户问题的向量化模型，通过 `langchain_openai.OpenAIEmbeddings` 以 OpenAI-compatible API 方式调用。

代码位置：

- 入库阶段：`ai-rag/src/ingest_data.py`
- 查询阶段：`ai-rag/src/main.py`

实际配置：

```python
import os

OpenAIEmbeddings(
    openai_api_key=os.environ.get("EMBEDDING_API_KEY") or os.environ.get("SCNET_API_KEY"),
    openai_api_base="https://api.scnet.cn/api/llm/v1",
    model="Qwen3-Embedding-8B",
    chunk_size=5,
)
```

SCNet embedding 的直接 HTTP 接口地址是：

```text
POST https://api.scnet.cn/api/llm/v1/embeddings
```

在 `OpenAIEmbeddings` 里通常不要把 `openai_api_base` 写到 `/embeddings`，而是写到上一级 OpenAI-compatible base URL：`https://api.scnet.cn/api/llm/v1`。如果服务商 SDK 文档明确要求完整 endpoint，再按服务商文档调整，并用 `python src/ingest_data.py` 做一次入库验证。

环境变量：

- `EMBEDDING_API_KEY`: 推荐使用的通用 embedding API Key。
- `EMBEDDING_BASE_URL`: embedding OpenAI-compatible base URL。SCNet 默认为 `https://api.scnet.cn/api/llm/v1`。
- `EMBEDDING_MODEL`: embedding 模型名。SCNet 当前使用 `Qwen3-Embedding-8B`。
- `EMBEDDING_BATCH_SIZE`: 每次请求 embedding 接口的文本条数。SCNet 当前限制最多 5 条，建议填 `5`。
- `SCNET_API_KEY`: SCNet API Key。缺失时无法生成向量，ChromaDB 向量召回不可用。
- `ZHIPUAI_API_KEY`: 旧配置兼容变量。如果不填新变量，代码仍可继续使用智谱 `embedding-3`。
- `CHROMA_DB_PATH`: ChromaDB 持久化目录，Docker 中默认为 `/app/data/chroma_db`。
- `RAG_RAW_DATA_PATH`: 原始校园规则文本路径，Docker 中默认为 `/app/data/raw/jxau_real_rules.txt`。
- `RAG_CHUNK_SIZE`: 文档切块大小。
- `RAG_CHUNK_OVERLAP`: 文档切块重叠长度。
- `RAG_INGEST_BATCH_DELAY`: 入库时每批 embedding 请求之间的等待秒数。遇到 429 限流时可设置为 `3` 到 `5`。

不要把真实 `sk-...` API Key 写进仓库文档或代码。应写入服务器环境变量、`shared/docker.env` 或 GitHub Actions Secret。

选择 embedding 模型的原因：

- 校园规则问答需要按语义召回文档，不适合只靠关键词匹配。
- 用户提问通常是自然语言表达，例如“考试作弊会怎么处理”，和制度原文可能不完全一致。
- `Qwen3-Embedding-8B` 能把用户问题和规则片段映射到同一语义空间，便于 ChromaDB 找到相近的制度片段。
- 使用 OpenAI-compatible 接口，后续如果要替换为其他 embedding 模型，主要改 `model`、`base_url` 和 API Key。

使用边界：

- Embedding 只负责把文本变成向量，不负责生成回答。
- Embedding 不能弥补知识库缺失。如果原始规则文件没有宿舍用电规定，再好的向量模型也无法检索出准确依据。
- 当前系统已经加入关键词/BM25 兜底检索。即使 embedding 服务余额不足或暂时不可用，规则问答仍可尝试通过关键词检索命中已有文档。

每个 chunk 会保存：

- `page_content`: 原文片段
- `source`: 原始文件路径
- `chunk_index`: chunk 编号
- `title`: 规则标题
- `category`: 规则分类
- `keywords`: 片段关键词
- `article`: 条款编号
- `embedding`: 语义向量，保存在 ChromaDB 中

## 用户提问检索

```text
用户问题
  -> 转成 query embedding
  -> ChromaDB 使用 HNSW 向量索引召回 top-k
  -> 关键词/BM25 检索召回候选片段
  -> 融合向量候选和关键词候选
  -> 可选 BGE Reranker 二次排序
  -> 取 top-n 片段
  -> 大模型基于片段回答并附来源
```

当前线上链路不是只靠向量检索，而是混合检索：

- 向量检索负责语义召回。
- 关键词/BM25 检索负责精确词兜底，例如“作弊”“转专业”“处分”等制度关键词。
- 融合排序会去重并综合两路候选，减少相关片段漏召回。
- 如果配置 `BGE_RERANKER_URL`，会在融合候选后再做二次排序。

## BGE Reranker 接口

系统支持可选的 `BGE_RERANKER_URL`。

请求格式：

```json
{
  "query": "寝室可以使用大功率电器吗？",
  "documents": [
    "学生宿舍禁止使用大功率电器。",
    "学生应按时归寝。"
  ]
}
```

返回格式支持两种：

```json
[
  {"index": 0, "score": 0.95},
  {"index": 1, "score": 0.31}
]
```

或：

```json
{
  "results": [
    {"index": 0, "score": 0.95},
    {"index": 1, "score": 0.31}
  ]
}
```

如果未配置 `BGE_RERANKER_URL`，系统会直接使用 ChromaDB 的向量召回顺序。

## 面试表达

Embedding 模型负责把校园规则片段和用户问题转成语义向量，ChromaDB 根据向量相似度做粗召回。为了提高准确率，系统又加入了关键词/BM25 检索作为兜底，再把两路结果融合排序。如果配置了 BGE Reranker，会在候选片段上做精排。这样可以减少无关 chunk 进入大模型上下文，提高 RAG 准确率并降低幻觉。
