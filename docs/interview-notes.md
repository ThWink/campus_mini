# 面试讲法

## 项目一句话

这是一个校园跑腿业务系统，我把 AI Agent 接入到真实业务流程里：订单问题走 Tool 查数据库，校园规则问题走 RAG 查向量库，发布任务可以由 Agent 调用后端业务接口完成。

## 关键亮点

- 多 Agent 状态机：Safety、Router、Order、Task、Rule、Chat。
- Tool 调用真实业务接口，不让模型编造订单状态。
- RAG 使用 ChromaDB 存校园规则向量，支持来源引用。
- 支持可选 BGE Reranker，对向量召回结果二次排序。
- Spring Boot 负责业务一致性，FastAPI 负责 AI 编排。
- 用户只能查询自己的订单，后端内部接口做权限校验。
- Docker Compose 可以部署到香橙派。

## 如何控制幻觉

订单状态必须由 OrderAgent 调用 Spring Boot 内部接口查询 MariaDB，模型只负责组织语言。校园规则必须先从 ChromaDB 检索制度片段，并在回答中附来源。如果查不到数据，系统明确返回未查到，不允许模型编造。

## Tool 调用例子

用户：`订单2状态`

```text
RouterAgent -> OrderAgent -> get_order_status
-> /api/internal/order/status?id=2&userId=1
-> orders + task
-> 返回真实状态
```

用户：`帮我发一个取快递的跑腿，赏金3块`

```text
SafetyAgent -> RouterAgent -> TaskAgent
-> publish_runner_task
-> /api/internal/task/publish
-> 写入 task + orders
```
