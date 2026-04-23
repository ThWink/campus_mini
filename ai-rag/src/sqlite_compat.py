# -*- coding: utf-8 -*-
"""Use pysqlite3 when system sqlite is too old for ChromaDB."""

import sqlite3
import sys


def _version_tuple(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    numbers = []
    for part in parts[:3]:
        try:
            numbers.append(int(part))
        except ValueError:
            numbers.append(0)
    while len(numbers) < 3:
        numbers.append(0)
    return tuple(numbers)


def patch_sqlite_for_chroma() -> None:
    if _version_tuple(sqlite3.sqlite_version) >= (3, 35, 0):
        return

    try:
        import pysqlite3
    except ImportError as exc:
        raise RuntimeError(
            "ChromaDB requires sqlite3 >= 3.35.0. "
            "Install pysqlite3-binary or upgrade libsqlite3."
        ) from exc

    sys.modules["sqlite3"] = pysqlite3
