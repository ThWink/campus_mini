# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

import requests

API_URL = "http://127.0.0.1:8000/chat"
CASES_PATH = Path("evals/agent_eval_cases.jsonl")


def load_cases():
    with CASES_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                yield json.loads(line)


def sse_to_text(raw: str) -> str:
    chunks = []
    for line in raw.splitlines():
        if line.startswith("data:"):
            data = line[5:].strip()
            if data != "[DONE]":
                chunks.append(data)
    return "".join(chunks)


def main():
    failures = 0
    for case in load_cases():
        response = requests.post(
            API_URL,
            json={"message": case["message"], "user_id": case.get("user_id")},
            timeout=30,
        )
        response.raise_for_status()
        answer = sse_to_text(response.text)
        missing = [item for item in case.get("must_contain", []) if item not in answer]
        ok = not missing
        failures += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] {case['name']}: {answer}")
        if missing:
            print(f"  missing: {missing}")

    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
