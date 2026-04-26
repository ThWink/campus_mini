import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class ResponseTextTests(unittest.TestCase):
    def test_no_rule_docs_reply_is_user_facing(self):
        from response_texts import NO_RULE_DOCS_REPLY

        self.assertIn("无法给出确定答复", NO_RULE_DOCS_REPLY)
        self.assertNotIn("向量库", NO_RULE_DOCS_REPLY)
        self.assertNotIn("重建", NO_RULE_DOCS_REPLY)
        self.assertNotIn("规则片段", NO_RULE_DOCS_REPLY)


if __name__ == "__main__":
    unittest.main()
