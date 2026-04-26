import os
import sys
from pathlib import Path

from sqlite_compat import patch_sqlite_for_chroma

patch_sqlite_for_chroma()

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from embedding_config import (
    MISSING_EMBEDDING_CONFIG_MESSAGE,
    create_embeddings,
    describe_embedding_settings,
    resolve_embedding_settings,
)

load_dotenv()

CHROMA_DB_PATH = Path("data/chroma_db")
SEARCH_K = 3

SYSTEM_PROMPT = """你是校园跑腿系统的智能助手，专门帮助用户解答关于跑腿服务的问题。

你的主要职责：
1. 帮用户查询订单状态
2. 解答跑腿相关问题（如如何发布任务、费用说明等）
3. 日常闲聊和引导

【参考规定】
{context}

回答要求：
- 如果【参考规定】中有相关内容，请根据规定回答
- 如果【参考规定】中没有相关内容，请用你自己的知识回答，不要说"未查到相关规定"
- 保持友好、口语化的回复风格"""


def setup_vector_store():
    print("=" * 60)
    print("江西农业大学规章制度 RAG 问答系统")
    print("=" * 60)

    print(f"\n[初始化] 加载向量数据库: {CHROMA_DB_PATH}")
    settings = resolve_embedding_settings()
    if settings is None:
        print(f"  [错误] {MISSING_EMBEDDING_CONFIG_MESSAGE}")
        sys.exit(1)

    print(f"  [配置] {describe_embedding_settings(settings)}")
    embeddings = create_embeddings(settings)
    db = Chroma(persist_directory=str(CHROMA_DB_PATH), embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": SEARCH_K})
    print(f"  [成功] 向量库加载完成，检索返回 top-{SEARCH_K} 个相关片段")
    return retriever


def setup_llm():
    print(f"\n[初始化] 连接 MiniMax 大模型")
    api_key = os.getenv("MINIMAX_API_KEY")
    base_url = os.getenv("MINIMAX_BASE_URL")

    if not api_key or not base_url:
        print("  [错误] .env 文件中未找到 MINIMAX_API_KEY 或 MINIMAX_BASE_URL")
        sys.exit(1)

    llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model="MiniMax-M2.5",
        temperature=0.1,
    )
    print(f"  [成功] MiniMax 模型连接成功 (temperature=0.1)")
    return llm


def setup_rag_chain(retriever, llm):
    print(f"\n[初始化] 构建 RAG 检索链")

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print(f"  [成功] RAG 链组装完成")
    return rag_chain


def main():
    retriever = setup_vector_store()
    llm = setup_llm()
    rag_chain = setup_rag_chain(retriever, llm)

    print(f"\n{'=' * 60}")
    print("系统已就绪！请输入您的问题（输入 'q' 或 'quit' 退出）")
    print(f"{'=' * 60}\n")

    while True:
        try:
            user_input = input("【您】请输入问题: ").strip()

            if user_input.lower() in ["q", "quit", "退出"]:
                print("\n感谢使用，再见！")
                break

            if not user_input:
                print("[提示] 请输入有效问题\n")
                continue

            print("🔍 正在查阅规章制度...")

            answer = rag_chain.invoke(user_input)

            print(f"\n【智能导办助手】\n{answer}\n")
            print("-" * 60)

        except KeyboardInterrupt:
            print("\n\n感谢使用，再见！")
            break
        except Exception as e:
            print(f"\n[错误] {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    main()
