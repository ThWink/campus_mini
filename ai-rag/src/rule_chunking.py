# -*- coding: utf-8 -*-
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List

try:
    from langchain_core.documents import Document
except Exception:
    @dataclass
    class Document:  # type: ignore
        page_content: str
        metadata: Dict[str, object]


TITLE_SUFFIXES = ["规定", "办法", "细则", "条例", "通知", "须知", "制度"]

KEYWORD_CATALOG = {
    "宿舍管理": ["宿舍", "寝室", "大功率", "电器", "晚归", "外宿", "卫生", "明火", "做饭"],
    "考试管理": ["考试", "作弊", "违纪", "补考", "重修", "成绩"],
    "学籍管理": ["学籍", "退学", "转专业", "转学", "休学", "复学"],
    "图书馆": ["图书馆", "借书", "还书", "校园卡"],
    "校园安全": ["安全", "电动车", "消防", "危险品", "管制刀具"],
    "奖助管理": ["奖学金", "助学金", "评优", "资助"],
}


def is_article_heading(line: str) -> bool:
    return bool(re.match(r"^第[一二三四五六七八九十百千\d]+[章节条款项]", line.strip()))


def is_title_line(line: str) -> bool:
    text = line.strip()
    if not text or is_article_heading(text) or len(text) > 40:
        return False
    return any(text.endswith(suffix) for suffix in TITLE_SUFFIXES)


def infer_category(text: str) -> str:
    for category, keywords in KEYWORD_CATALOG.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "校园规则"


def extract_keywords(text: str, limit: int = 8) -> str:
    hits: List[str] = []
    for keywords in KEYWORD_CATALOG.values():
        for keyword in keywords:
            if keyword in text and keyword not in hits:
                hits.append(keyword)
            if len(hits) >= limit:
                return ",".join(hits)
    return ",".join(hits)


def split_long_text(text: str, chunk_size: int, chunk_overlap: int) -> Iterable[str]:
    if len(text) <= chunk_size:
        yield text
        return

    start = 0
    step = max(1, chunk_size - max(0, chunk_overlap))
    while start < len(text):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            yield chunk
        start += step


def build_metadata(source: str, title: str, content: str, index: int) -> Dict[str, object]:
    joined = f"{title}\n{content}"
    article_match = re.search(r"第[一二三四五六七八九十百千\d]+[章节条款项]", content)
    return {
        "source": source,
        "title": title,
        "category": infer_category(joined),
        "keywords": extract_keywords(joined),
        "article": article_match.group(0) if article_match else "",
        "chunk_index": index,
    }


def build_rule_documents(
    raw_text: str,
    source: str,
    chunk_size: int = 500,
    chunk_overlap: int = 80,
) -> List[Document]:
    title = "校园规则制度文档"
    buffer: List[str] = []
    documents: List[Document] = []

    def flush() -> None:
        if not buffer:
            return
        content = "\n".join(item for item in buffer if item.strip()).strip()
        buffer.clear()
        if not content:
            return
        for part in split_long_text(content, chunk_size, chunk_overlap):
            index = len(documents)
            documents.append(Document(
                page_content=part,
                metadata=build_metadata(source, title, part, index),
            ))

    for raw_line in (raw_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            continue
        if is_title_line(line):
            flush()
            title = line
            continue
        if is_article_heading(line):
            flush()
        buffer.append(line)

    flush()
    return documents
