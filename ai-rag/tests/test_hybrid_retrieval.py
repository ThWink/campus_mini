import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class HybridRetrievalTests(unittest.TestCase):
    def test_keyword_index_ranks_exact_rule_topic_first(self):
        from hybrid_retrieval import KeywordIndex

        docs = [
            SimpleNamespace(page_content="图书馆借书需要凭校园卡办理。", metadata={"title": "图书馆"}),
            SimpleNamespace(page_content="宿舍禁止使用大功率电器，违规将处理。", metadata={"title": "宿舍"}),
        ]

        ranked = KeywordIndex(docs).rank("寝室可以用大功率电器吗", limit=2)

        self.assertEqual(ranked[0][0].metadata["title"], "宿舍")
        self.assertGreater(ranked[0][1], ranked[1][1])

    def test_merge_ranked_documents_deduplicates_and_keeps_best_rank(self):
        from hybrid_retrieval import merge_ranked_documents

        a = SimpleNamespace(page_content="宿舍禁止使用大功率电器。", metadata={"chunk_index": 1})
        b = SimpleNamespace(page_content="考试作弊按违纪处理。", metadata={"chunk_index": 2})

        merged = merge_ranked_documents(
            vector_ranked=[(b, 0.8), (a, 0.7)],
            keyword_ranked=[(a, 4.2)],
            top_n=2,
        )

        self.assertEqual(len(merged), 2)
        self.assertIs(merged[0][0], a)


if __name__ == "__main__":
    unittest.main()
