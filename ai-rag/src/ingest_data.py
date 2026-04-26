# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

from sqlite_compat import patch_sqlite_for_chroma
from storage_utils import reset_directory_contents

patch_sqlite_for_chroma()

from dotenv import load_dotenv
from langchain_chroma import Chroma
from embedding_config import (
    MISSING_EMBEDDING_CONFIG_MESSAGE,
    create_embeddings,
    describe_embedding_settings,
    resolve_embedding_settings,
)
from rule_chunking import build_rule_documents

load_dotenv()

RAW_DATA_PATH = Path(os.getenv("RAG_RAW_DATA_PATH", "data/raw/jxau_real_rules.txt"))
CHROMA_DB_PATH = Path(os.getenv("CHROMA_DB_PATH", "data/chroma_db"))

CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "200"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "30"))
BATCH_SIZE = int(os.getenv("RAG_INGEST_BATCH_SIZE", "16"))


def get_embeddings():
    settings = resolve_embedding_settings()
    if settings is None:
        print(f"[ERROR] {MISSING_EMBEDDING_CONFIG_MESSAGE}")
        sys.exit(1)

    print(f"[INFO] embedding provider: {describe_embedding_settings(settings)}")
    return create_embeddings(settings)


def main():
    print("=" * 60)
    print("校园规则制度 RAG 向量化脚本")
    print("=" * 60)

    if not RAW_DATA_PATH.exists():
        print(f"[ERROR] raw data file not found: {RAW_DATA_PATH}")
        sys.exit(1)

    raw_text = RAW_DATA_PATH.read_text(encoding="utf-8")
    print(f"[1/4] loaded raw rules, {len(raw_text)} chars")

    chunks = build_rule_documents(
        raw_text,
        source=str(RAW_DATA_PATH),
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
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
