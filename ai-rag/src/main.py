# -*- coding: utf-8 -*-
import json
import os
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from sqlite_compat import patch_sqlite_for_chroma

patch_sqlite_for_chroma()

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from response_texts import NO_RULE_DOCS_REPLY

load_dotenv()

CAMPUS_API_BASE = os.getenv("CAMPUS_API_BASE", "http://127.0.0.1:8080").rstrip("/")
CHROMA_DB_PATH = Path(os.getenv("CHROMA_DB_PATH", "data/chroma_db"))
SEARCH_K = int(os.getenv("RAG_SEARCH_K", "10"))
RAG_TOP_N = int(os.getenv("RAG_TOP_N", "3"))
BGE_RERANKER_URL = os.getenv("BGE_RERANKER_URL", "").strip()
LOG_PATH = Path(os.getenv("AGENT_LOG_PATH", "logs/agent_events.jsonl"))

STATUS_TEXT = {
    0: "待接单",
    1: "已接单",
    2: "已完成",
    3: "已取消",
    4: "已关闭",
}

RISK_PATTERNS = [
    "替考", "代考", "作弊", "刷单", "虚假评价",
    "买烟", "香烟", "电子烟", "买酒", "白酒", "啤酒",
    "毒品", "管制刀具", "危险品", "违禁品", "代签",
]


class Intent(str, Enum):
    ORDER_STATUS = "order_status"
    ORDER_LIST = "order_list"
    TASK_PUBLISH = "task_publish"
    RULE_QA = "rule_qa"
    CHAT = "chat"
    BLOCKED = "blocked"


@dataclass
class Citation:
    source: str
    snippet: str
    score: Optional[float] = None


@dataclass
class AgentState:
    request_id: str
    user_id: Optional[str]
    message: str
    history: List[Dict[str, Any]]
    intent: Intent = Intent.CHAT
    blocked_reason: Optional[str] = None
    answer: str = ""
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)


app = FastAPI(title="校园智慧服务 Agent API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sse_text(text: str) -> Iterable[str]:
    safe = (text or "").replace("\r", "").replace("\n", " ")
    yield f"data: {safe}\n\n"
    yield "data: [DONE]\n\n"


def api_get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.get(f"{CAMPUS_API_BASE}{path}", params=params, timeout=5)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{CAMPUS_API_BASE}{path}", json=payload, timeout=8)
    response.raise_for_status()
    return response.json()


def log_state(state: AgentState) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(state)
        payload["latency_ms"] = int((time.time() - state.started_at) * 1000)
        payload["started_at"] = state.started_at
        with LOG_PATH.open("a", encoding="utf-8") as file:
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"[WARN] failed to write agent log: {exc}")


def safety_check(message: str) -> Optional[str]:
    lowered = message.lower()
    for pattern in RISK_PATTERNS:
        if pattern.lower() in lowered:
            return f"这个请求包含风险内容：{pattern}。平台不能发布或协助处理这类任务。"
    return None


def route_intent(message: str) -> Intent:
    text = message.strip()
    if not text:
        return Intent.CHAT

    if is_publish_intent(text):
        return Intent.TASK_PUBLISH

    if extract_order_id(text):
        return Intent.ORDER_STATUS

    order_keywords = ["我的订单", "订单状态", "订单进度", "查订单", "我发布的订单", "我接的单", "我接取的订单", "待完成订单"]
    if any(keyword in text for keyword in order_keywords):
        return Intent.ORDER_LIST

    rule_keywords = ["学校", "校园", "规则", "制度", "规定", "宿舍", "寝室", "大功率", "电动车", "请假", "处分", "图书馆"]
    if any(keyword in text for keyword in rule_keywords):
        return Intent.RULE_QA

    return Intent.CHAT


def is_publish_intent(text: str) -> bool:
    if any(word in text for word in ["怎么", "如何", "在哪", "流程", "教程"]):
        return False
    return any(word in text for word in ["帮我发", "帮我发布", "发布一个", "发一个", "下单", "叫个跑腿", "创建跑腿"])


def extract_order_id(message: str) -> Optional[str]:
    patterns = [
        r"订单\s*号?\s*#?(\d+)",
        r"单号\s*#?(\d+)",
        r"查\s*(\d+)\s*号",
        r"(\d+)\s*号订单",
        r"order\s*#?(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def status_name(status: Any) -> str:
    try:
        return STATUS_TEXT.get(int(status), f"未知状态({status})")
    except (TypeError, ValueError):
        return f"未知状态({status})"


def order_title(order: Dict[str, Any]) -> str:
    return order.get("title") or order.get("description") or "未命名订单"


def format_order(order: Dict[str, Any]) -> str:
    runner_id = order.get("runnerId")
    runner_text = f"，接单人ID {runner_id}" if runner_id else ""
    return f"订单 {order.get('id')}《{order_title(order)}》当前状态是：{status_name(order.get('status'))}{runner_text}"


def filter_orders(orders: List[Dict[str, Any]], scope: str) -> List[Dict[str, Any]]:
    if scope == "todo":
        return [order for order in orders if order.get("status") in [0, 1]]
    return orders


def format_order_list(title: str, orders: List[Dict[str, Any]], scope: str = "all") -> str:
    orders = filter_orders(orders, scope)
    if not orders:
        return f"{title}暂无订单"
    lines = [f"{title}共 {len(orders)} 单"]
    lines.extend(format_order(order) for order in orders)
    return "；".join(lines)


@tool
def get_order_status(order_id: str, user_id: str = "") -> str:
    """查询指定订单状态。"""
    params = {"id": order_id}
    if user_id:
        params["userId"] = user_id

    data = api_get("/api/internal/order/status", params)
    if data.get("code") != 200:
        return data.get("msg") or "查询订单状态失败"

    order = data.get("data")
    return format_order(order) if order else "没有查到这个订单。"


@tool
def get_my_orders(user_id: str, scope: str = "all") -> str:
    """查询当前用户发布和接取的订单。scope 可以是 all、published、accepted、todo。"""
    if not user_id:
        return "请先登录后再查询自己的订单状态。"

    data = api_get("/api/internal/order/mine", {"userId": user_id})
    if data.get("code") != 200:
        return data.get("msg") or "查询我的订单失败"

    payload = data.get("data") or {}
    published = payload.get("published") or []
    accepted = payload.get("accepted") or []

    if scope == "published":
        return format_order_list("你发布的订单", published)
    if scope == "accepted":
        return format_order_list("你接取的订单", accepted)
    if scope == "todo":
        return "；".join([
            format_order_list("你发布的待完成订单", published, "todo"),
            format_order_list("你接取的待完成订单", accepted, "todo"),
        ])

    if not published and not accepted:
        return "你目前没有发布或接取的订单。"
    return "；".join([
        format_order_list("你发布的订单", published),
        format_order_list("你接取的订单", accepted),
    ])


def parse_publish_task(message: str) -> Tuple[Optional[str], Optional[str], Optional[float], Optional[str]]:
    reward_match = re.search(r"(?:赏金|报酬|酬劳|价格|给)\s*[:：]?\s*(\d+(?:\.\d+)?)\s*(?:元|块)?", message)
    if not reward_match:
        reward_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:元|块)", message)

    reward = float(reward_match.group(1)) if reward_match else None
    title = message
    title = re.sub(r"(?:帮我|我要)?(?:发|发布|创建|下单)(?:一个|一条)?", "", title)
    title = re.sub(r"叫个跑腿", "", title)
    title = re.sub(r"跑腿任务", "", title)
    title = re.sub(r"的?跑腿", "", title)
    title = re.sub(r"(?:赏金|报酬|酬劳|价格|给)\s*[:：]?\s*\d+(?:\.\d+)?\s*(?:元|块)?", "", title)
    title = re.sub(r"\d+(?:\.\d+)?\s*(?:元|块)", "", title)
    title = title.strip(" ，,。；;：:")

    if not title:
        return None, None, reward, "请补充任务内容，例如：帮我发一个去三食堂买饭的跑腿，赏金5块。"
    if reward is None:
        return title, title, None, "请补充赏金金额，例如：赏金5块。"
    if len(title) > 90:
        title = title[:90]

    return title, title, reward, None


@tool
def publish_runner_task(user_id: str, title: str, description: str, reward: float) -> str:
    """发布跑腿任务。调用 Spring Boot 后端创建 task 和 orders 记录。"""
    if not user_id:
        return "请先登录后再发布跑腿任务。"

    data = api_post("/api/internal/task/publish", {
        "userId": user_id,
        "title": title,
        "description": description,
        "reward": reward,
    })
    if data.get("code") != 200:
        return data.get("msg") or "发布失败"

    order = data.get("data") or {}
    return f"已发布跑腿任务《{title}》，赏金 {reward:g} 元，订单号是 {order.get('id')}，当前状态：待接单。"


def order_agent(state: AgentState) -> str:
    order_id = extract_order_id(state.message)
    if order_id:
        state.tool_calls.append({"tool": "get_order_status", "order_id": order_id})
        return get_order_status.invoke({"order_id": order_id, "user_id": state.user_id or ""})

    scope = "all"
    if any(word in state.message for word in ["待完成", "未完成", "还没完成"]):
        scope = "todo"
    elif "发布" in state.message:
        scope = "published"
    elif any(word in state.message for word in ["接取", "接的单", "我接"]):
        scope = "accepted"

    state.tool_calls.append({"tool": "get_my_orders", "scope": scope})
    return get_my_orders.invoke({"user_id": state.user_id or "", "scope": scope})


def task_agent(state: AgentState) -> str:
    if not state.user_id:
        return "请先登录后再发布跑腿任务。"

    title, description, reward, error = parse_publish_task(state.message)
    if error:
        return error

    risk = safety_check(f"{title} {description}")
    if risk:
        return risk

    state.tool_calls.append({"tool": "publish_runner_task", "title": title, "reward": reward})
    return publish_runner_task.invoke({
        "user_id": state.user_id,
        "title": title,
        "description": description,
        "reward": reward,
    })


def get_llm():
    glm_api_key = os.getenv("GLM_API_KEY")
    glm_base_url = os.getenv("GLM_BASE_URL")
    glm_model = os.getenv("GLM_MODEL") or "glm-4"

    if glm_api_key and glm_base_url:
        return ChatOpenAI(api_key=glm_api_key, base_url=glm_base_url, model=glm_model, temperature=0.2)
    return ChatOpenAI(model="glm-4", temperature=0.2)


def get_embeddings():
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key:
        print("[WARN] ZHIPUAI_API_KEY is not set; RAG retrieval is disabled.")
        return None

    return OpenAIEmbeddings(
        openai_api_key=api_key,
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        model="embedding-3",
    )


_retriever = None


def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    try:
        embeddings = get_embeddings()
        if embeddings is None:
            return None
        db = Chroma(persist_directory=str(CHROMA_DB_PATH), embedding_function=embeddings)
        _retriever = db.as_retriever(search_kwargs={"k": SEARCH_K})
        return _retriever
    except Exception as exc:
        print(f"[WARN] failed to initialize Chroma retriever: {exc}")
        return None


def rerank_documents(query: str, docs: List[Any]) -> List[Tuple[Any, Optional[float]]]:
    if not docs:
        return []

    if not BGE_RERANKER_URL:
        return [(doc, None) for doc in docs[:RAG_TOP_N]]

    try:
        payload = {"query": query, "documents": [doc.page_content for doc in docs]}
        response = requests.post(BGE_RERANKER_URL, json=payload, timeout=8)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", data) if isinstance(data, dict) else data
        scored: List[Tuple[int, float]] = []
        for index, item in enumerate(results):
            if isinstance(item, dict):
                scored.append((int(item.get("index", index)), float(item.get("score", item.get("relevance_score", 0)))))
            else:
                scored.append((index, float(item)))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [(docs[index], score) for index, score in scored[:RAG_TOP_N] if index < len(docs)]
    except Exception as exc:
        print(f"[WARN] BGE reranker failed, using vector order: {exc}")
        return [(doc, None) for doc in docs[:RAG_TOP_N]]


def retrieve_rule_docs(query: str) -> List[Tuple[Any, Optional[float]]]:
    retriever = get_retriever()
    if retriever is None:
        return []

    try:
        docs = retriever.invoke(query)
        return rerank_documents(query, docs)
    except Exception as exc:
        print(f"[WARN] RAG retrieve failed: {exc}")
        return []


def citation_from_doc(doc: Any, score: Optional[float]) -> Citation:
    metadata = getattr(doc, "metadata", {}) or {}
    source = metadata.get("source") or metadata.get("file_path") or "校园规则制度文档"
    chunk = metadata.get("chunk") or metadata.get("chunk_index")
    if chunk is not None:
        source = f"{source}#chunk-{chunk}"
    snippet = " ".join((doc.page_content or "").split())[:180]
    return Citation(source=source, snippet=snippet, score=score)


def append_citations(answer: str, citations: List[Citation]) -> str:
    if not citations:
        return answer

    lines = [answer.rstrip(), "来源："]
    for index, citation in enumerate(citations, start=1):
        score = f"，相关度 {citation.score:.3f}" if citation.score is not None else ""
        lines.append(f"[{index}] {citation.source}{score}：{citation.snippet}")
    return " ".join(lines)


def rule_agent(state: AgentState) -> str:
    docs = retrieve_rule_docs(state.message)
    state.citations = [citation_from_doc(doc, score) for doc, score in docs]
    state.tool_calls.append({"tool": "chroma_retrieval", "top_k": SEARCH_K, "reranker": bool(BGE_RERANKER_URL)})

    if not docs:
        return NO_RULE_DOCS_REPLY

    context = "\n\n".join(f"[来源{idx}] {doc.page_content}" for idx, (doc, _) in enumerate(docs, start=1))
    prompt = f"""你是校园跑腿系统的规则问答 Agent。请只基于下面的校园规则片段回答用户问题。

用户问题：{state.message}

校园规则片段：
{context}

要求：
1. 如果片段能回答，给出明确结论。
2. 如果片段不能回答，不要编造规定。
3. 回答末尾简短标注使用了哪些来源编号。
"""
    try:
        result = get_llm().invoke([HumanMessage(content=prompt)]).content
    except Exception as exc:
        print(f"[WARN] LLM rule answer failed: {exc}")
        result = f"检索到相关规则片段，但大模型暂时不可用。关键片段：{state.citations[0].snippet}"

    return append_citations(result, state.citations)


def chat_agent(state: AgentState) -> str:
    prompt = f"""你是校园跑腿系统的智能助手。
请简洁回答用户问题。不要编造订单状态、学校规定或系统未实现的能力。

用户问题：{state.message}
"""
    try:
        return get_llm().invoke([HumanMessage(content=prompt)]).content
    except Exception:
        return "你好，我可以帮你查询订单状态、发布跑腿任务，或者回答校园规则相关问题。"


def run_state_machine(state: AgentState) -> str:
    risk = safety_check(state.message)
    if risk:
        state.intent = Intent.BLOCKED
        state.blocked_reason = risk
        return risk

    state.intent = route_intent(state.message)
    if state.intent == Intent.ORDER_STATUS or state.intent == Intent.ORDER_LIST:
        return order_agent(state)
    if state.intent == Intent.TASK_PUBLISH:
        return task_agent(state)
    if state.intent == Intent.RULE_QA:
        return rule_agent(state)
    return chat_agent(state)


@app.post("/chat")
async def chat(request: Request):
    try:
        data = json.loads(await request.body())
    except Exception:
        return StreamingResponse(sse_text("请求体不是合法 JSON。"), media_type="text/event-stream; charset=utf-8")

    state = AgentState(
        request_id=str(uuid.uuid4()),
        user_id=str(data.get("user_id") or data.get("userId") or "") or None,
        message=data.get("message") or "",
        history=data.get("history") or [],
    )

    try:
        state.answer = run_state_machine(state)
    except Exception as exc:
        state.answer = f"AI 助手处理失败：{exc}"
    finally:
        log_state(state)

    return StreamingResponse(sse_text(state.answer), media_type="text/event-stream; charset=utf-8")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "校园智慧服务 Agent", "version": "2.0.0"}


@app.get("/")
async def root():
    return {
        "service": "校园智慧服务 Agent API",
        "version": "2.0.0",
        "state_machine": ["SafetyAgent", "RouterAgent", "OrderAgent", "TaskAgent", "RuleAgent", "ChatAgent"],
        "endpoints": {"chat": "POST /chat", "health": "GET /health"},
        "reranker": "enabled" if BGE_RERANKER_URL else "disabled",
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("校园智慧服务 Agent API 启动中...")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
