# -*- coding: utf-8 -*-
import os
from dataclasses import dataclass
from typing import Mapping, Optional


SCNET_BASE_URL = "https://api.scnet.cn/api/llm/v1"
SCNET_MODEL = "Qwen3-Embedding-8B"
SCNET_BATCH_SIZE = 5
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
ZHIPU_MODEL = "embedding-3"
ZHIPU_BATCH_SIZE = 1000

MISSING_EMBEDDING_CONFIG_MESSAGE = (
    "未配置 embedding API Key。请设置 EMBEDDING_API_KEY、SCNET_API_KEY 或 ZHIPUAI_API_KEY。"
)


@dataclass(frozen=True)
class EmbeddingSettings:
    api_key: str
    api_key_source: str
    base_url: str
    model: str
    request_batch_size: int


def _env_value(env: Mapping[str, str], key: str) -> str:
    return (env.get(key) or "").strip()


def _env_int(env: Mapping[str, str], key: str, default: int) -> int:
    raw = _env_value(env, key)
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def resolve_embedding_settings(env: Optional[Mapping[str, str]] = None) -> Optional[EmbeddingSettings]:
    env = env or os.environ

    generic_key = _env_value(env, "EMBEDDING_API_KEY")
    if generic_key:
        return EmbeddingSettings(
            api_key=generic_key,
            api_key_source="EMBEDDING_API_KEY",
            base_url=_env_value(env, "EMBEDDING_BASE_URL") or SCNET_BASE_URL,
            model=_env_value(env, "EMBEDDING_MODEL") or SCNET_MODEL,
            request_batch_size=_env_int(env, "EMBEDDING_BATCH_SIZE", SCNET_BATCH_SIZE),
        )

    scnet_key = _env_value(env, "SCNET_API_KEY")
    if scnet_key:
        return EmbeddingSettings(
            api_key=scnet_key,
            api_key_source="SCNET_API_KEY",
            base_url=_env_value(env, "EMBEDDING_BASE_URL") or SCNET_BASE_URL,
            model=_env_value(env, "EMBEDDING_MODEL") or SCNET_MODEL,
            request_batch_size=_env_int(env, "EMBEDDING_BATCH_SIZE", SCNET_BATCH_SIZE),
        )

    zhipu_key = _env_value(env, "ZHIPUAI_API_KEY")
    if zhipu_key:
        return EmbeddingSettings(
            api_key=zhipu_key,
            api_key_source="ZHIPUAI_API_KEY",
            base_url=ZHIPU_BASE_URL,
            model=ZHIPU_MODEL,
            request_batch_size=_env_int(env, "EMBEDDING_BATCH_SIZE", ZHIPU_BATCH_SIZE),
        )

    return None


def describe_embedding_settings(settings: Optional[EmbeddingSettings]) -> str:
    if settings is None:
        return "disabled"
    return (
        f"{settings.model} via {settings.base_url} "
        f"({settings.api_key_source}, batch={settings.request_batch_size})"
    )


def create_embeddings(settings: Optional[EmbeddingSettings] = None):
    settings = settings or resolve_embedding_settings()
    if settings is None:
        return None

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        openai_api_key=settings.api_key,
        openai_api_base=settings.base_url,
        model=settings.model,
        chunk_size=settings.request_batch_size,
    )
