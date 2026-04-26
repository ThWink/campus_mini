# -*- coding: utf-8 -*-
import math
import re
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple


DOMAIN_TERMS = [
    "大功率", "电器", "宿舍", "寝室", "晚归", "外宿", "处分", "处罚",
    "考试", "作弊", "违纪", "补考", "重修", "学籍", "奖学金", "图书馆",
    "借书", "电动车", "请假", "转专业", "退学",
]


def tokenize(text: str) -> List[str]:
    lowered = (text or "").lower()
    tokens = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]", lowered)
    chinese_chars = [token for token in tokens if re.match(r"[\u4e00-\u9fff]", token)]
    tokens.extend("".join(chinese_chars[index:index + 2]) for index in range(len(chinese_chars) - 1))
    tokens.extend(term for term in DOMAIN_TERMS if term in text)
    return [token for token in tokens if token.strip()]


def document_key(doc: Any) -> str:
    metadata = getattr(doc, "metadata", {}) or {}
    source = metadata.get("source", "")
    chunk_index = metadata.get("chunk_index", metadata.get("chunk", ""))
    if source or chunk_index != "":
        return f"{source}#{chunk_index}"
    return getattr(doc, "page_content", str(id(doc)))


class KeywordIndex:
    def __init__(self, docs: Iterable[Any]):
        self.docs = list(docs)
        self.doc_tokens: List[List[str]] = [tokenize(getattr(doc, "page_content", "")) for doc in self.docs]
        self.doc_freq: Dict[str, int] = defaultdict(int)
        for tokens in self.doc_tokens:
            for token in set(tokens):
                self.doc_freq[token] += 1
        self.avg_len = sum(len(tokens) for tokens in self.doc_tokens) / max(1, len(self.doc_tokens))

    def score(self, query: str, doc_index: int) -> float:
        query_tokens = tokenize(query)
        if not query_tokens or doc_index >= len(self.doc_tokens):
            return 0.0

        tokens = self.doc_tokens[doc_index]
        if not tokens:
            return 0.0

        counts = Counter(tokens)
        score = 0.0
        total_docs = max(1, len(self.docs))
        k1 = 1.5
        b = 0.75
        doc_len = len(tokens)

        for token in query_tokens:
            tf = counts.get(token, 0)
            if not tf:
                continue
            df = self.doc_freq.get(token, 0)
            idf = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
            denom = tf + k1 * (1 - b + b * doc_len / max(1.0, self.avg_len))
            score += idf * (tf * (k1 + 1)) / denom
        return score

    def rank(self, query: str, limit: int = 10) -> List[Tuple[Any, float]]:
        scored = [
            (doc, self.score(query, index))
            for index, doc in enumerate(self.docs)
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        if not scored or scored[0][1] <= 0:
            return []
        return scored[:limit]


def merge_ranked_documents(
    vector_ranked: List[Tuple[Any, Optional[float]]],
    keyword_ranked: List[Tuple[Any, Optional[float]]],
    top_n: int,
) -> List[Tuple[Any, Optional[float]]]:
    docs_by_key: Dict[str, Any] = {}
    fused_scores: Dict[str, float] = defaultdict(float)

    def add(items: List[Tuple[Any, Optional[float]]], weight: float) -> None:
        for rank, (doc, raw_score) in enumerate(items, start=1):
            key = document_key(doc)
            docs_by_key.setdefault(key, doc)
            score_bonus = 0.0 if raw_score is None else min(float(raw_score), 10.0) / 100.0
            fused_scores[key] += weight * (1.0 / (60 + rank) + score_bonus)

    add(vector_ranked, 1.0)
    add(keyword_ranked, 1.25)

    ordered = sorted(fused_scores.items(), key=lambda item: item[1], reverse=True)
    return [(docs_by_key[key], score) for key, score in ordered[:top_n]]


def hybrid_rank(
    query: str,
    vector_ranked: List[Tuple[Any, Optional[float]]],
    keyword_docs: Iterable[Any],
    top_n: int,
    keyword_limit: int = 10,
) -> List[Tuple[Any, Optional[float]]]:
    keyword_ranked = KeywordIndex(keyword_docs).rank(query, keyword_limit)
    return merge_ranked_documents(vector_ranked, keyword_ranked, top_n)
