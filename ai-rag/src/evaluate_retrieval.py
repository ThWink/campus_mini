# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List

from dotenv import load_dotenv

from main import retrieve_rule_docs

load_dotenv()

CASES_PATH = Path("evals/retrieval_eval_cases.jsonl")


def load_cases(path: Path = CASES_PATH) -> Iterable[Dict[str, object]]:
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                yield json.loads(line)


def matched_terms(text: str, terms: List[str]) -> List[str]:
    return [term for term in terms if term in text]


def main() -> None:
    failures = 0
    for case in load_cases():
        query = str(case["query"])
        docs = retrieve_rule_docs(query)
        joined = "\n".join(getattr(doc, "page_content", "") for doc, _ in docs)
        must_retrieve = [str(item) for item in case.get("must_retrieve", [])]
        missing = [term for term in must_retrieve if term not in joined]
        status = "PASS" if not missing else "FAIL"
        print(f"[{status}] {case['name']} top={len(docs)} matched={matched_terms(joined, must_retrieve)}")
        if missing:
            failures += 1
            print(f"  missing: {missing}")

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
