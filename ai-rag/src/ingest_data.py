# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

from sqlite_compat import patch_sqlite_for_chroma
from storage_utils import reset_directory_contents

patch_sqlite_for_chroma()

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

RAW_DATA_PATH = Path(os.getenv("RAG_RAW_DATA_PATH", "data/raw/jxau_real_rules.txt"))
CHROMA_DB_PATH = Path(os.getenv("CHROMA_DB_PATH", "data/chroma_db"))

CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "200"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "30"))
BATCH_SIZE = int(os.getenv("RAG_INGEST_BATCH_SIZE", "16"))


def get_embeddings():
    api_key = os.environ.get("ZHIPUAI_API_KEY")
    if not api_key:
        print("[ERROR] ZHIPUAI_API_KEY is missing in .env")
        sys.exit(1)

    return OpenAIEmbeddings(
        openai_api_key=api_key,
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
        model="embedding-3",
    )


def main():
    print("=" * 60)
    print("校园规则制度 RAG 向量化脚本")
    print("=" * 60)

    if not RAW_DATA_PATH.exists():
        print(f"[ERROR] raw data file not found: {RAW_DATA_PATH}")
        sys.exit(1)

    loader = TextLoader(str(RAW_DATA_PATH), encoding="utf-8")
    documents = loader.load()
    total_chars = sum(len(doc.page_content) for doc in documents)
    print(f"[1/4] loaded {len(documents)} document(s), {total_chars} chars")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = index
        chunk.metadata["source"] = str(RAW_DATA_PATH)
    print(f"[2/4] split into {len(chunks)} chunks")

    embeddings = get_embeddings()
    print("[3/4] embedding model ready")

    reset_directory_contents(CHROMA_DB_PATH)

    db = None
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        if db is None:
            db = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=str(CHROMA_DB_PATH),
            )
        else:
            db.add_documents(batch)
        print(f"[4/4] indexed {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}")

    print("=" * 60)
    print(f"done: {len(chunks)} chunks persisted to {CHROMA_DB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
