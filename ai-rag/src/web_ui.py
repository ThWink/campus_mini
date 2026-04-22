import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

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


@st.cache_resource
def setup_vector_store():
    api_key = os.environ.get("ZHIPUAI_API_KEY")
    if not api_key:
        raise ValueError("未找到 ZHIPUAI_API_KEY")
    embeddings = OpenAIEmbeddings(
        openai_api_key=api_key,
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        model="embedding-3"
    )
    db = Chroma(persist_directory=str(CHROMA_DB_PATH), embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": SEARCH_K})
    return retriever


@st.cache_resource
def setup_llm():
    api_key = os.getenv("MINIMAX_API_KEY")
    base_url = os.getenv("MINIMAX_BASE_URL")
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model="MiniMax-M2.5",
        temperature=0.1,
    )
    return llm


def setup_rag_chain(retriever, llm):
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
    return rag_chain


def main():
    st.set_page_config(
        page_title="江西农业大学智慧导办 AI",
        page_icon="🎓",
        layout="centered"
    )

    st.title("🎓 江西农业大学智慧导办 AI")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "rag_chain" not in st.session_state:
        with st.spinner("正在初始化系统，请稍候..."):
            retriever = setup_vector_store()
            llm = setup_llm()
            st.session_state.rag_chain = setup_rag_chain(retriever, llm)
        st.success("系统初始化完成！")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("请输入您的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 正在查阅规章制度..."):
                try:
                    response = st.session_state.rag_chain.invoke(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"抱歉，发生了错误：{type(e).__name__}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


if __name__ == "__main__":
    main()
