import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class RuleChunkingTests(unittest.TestCase):
    def test_build_rule_documents_keeps_heading_metadata(self):
        from rule_chunking import build_rule_documents

        text = """学生宿舍管理规定
第一条 学生不得在宿舍使用大功率电器，违者按学校规定处理。
第二条 学生应保持宿舍卫生。

考试管理办法
第一条 学生考试作弊将按违纪处理。
"""

        docs = build_rule_documents(text, source="rules.txt", chunk_size=80, chunk_overlap=10)

        self.assertGreaterEqual(len(docs), 2)
        dorm_doc = next(doc for doc in docs if "大功率电器" in doc.page_content)
        self.assertEqual(dorm_doc.metadata["title"], "学生宿舍管理规定")
        self.assertEqual(dorm_doc.metadata["category"], "宿舍管理")
        self.assertEqual(dorm_doc.metadata["source"], "rules.txt")
        self.assertIn("大功率", dorm_doc.metadata["keywords"])

    def test_build_rule_documents_keeps_article_boundary_when_possible(self):
        from rule_chunking import build_rule_documents

        text = """学生宿舍管理规定
第一条 学生不得在宿舍使用大功率电器。
第二条 学生应保持宿舍卫生。
"""

        docs = build_rule_documents(text, source="rules.txt", chunk_size=60, chunk_overlap=0)
        contents = [doc.page_content for doc in docs]

        self.assertTrue(any("第一条" in item and "第二条" not in item for item in contents))


if __name__ == "__main__":
    unittest.main()
