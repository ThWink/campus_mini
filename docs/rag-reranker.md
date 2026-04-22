# RAG 与 BGE Reranker

## 文档向量化

校园规则制度文档通过 `ai-rag/src/ingest_data.py` 入库。

```text
原始规则文本
  -> TextLoader 读取
  -> RecursiveCharacterTextSplitter 切 chunk
  -> Embedding 模型生成向量
  -> ChromaDB 持久化
```

每个 chunk 会保存：

- `page_content`: 原文片段
- `source`: 原始文件路径
- `chunk_index`: chunk 编号
- `embedding`: 语义向量

## 用户提问检索

```text
用户问题
  -> 转成 query embedding
  -> ChromaDB 使用 HNSW 向量索引召回 top-k
  -> 可选 BGE Reranker 二次排序
  -> 取 top-n 片段
  -> 大模型基于片段回答并附来源
```

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

Embedding 检索负责粗召回，BGE Reranker 负责精排。这样可以减少无关 chunk 进入大模型上下文，提高 RAG 准确率并降低幻觉。
