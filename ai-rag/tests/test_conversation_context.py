import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class ConversationContextTests(unittest.TestCase):
    def test_formats_recent_history_without_welcome_noise(self):
        from conversation_context import format_history

        history = [
            {"role": "ai", "content": "你好！我是智能跑腿助手，有什么可以帮你的吗？"},
            {"role": "user", "content": "寝室可以用大功率电器吗"},
            {"role": "ai", "content": "目前没有找到与这个问题直接相关的校园规定。"},
        ]

        text = format_history(history)

        self.assertNotIn("你好！我是智能跑腿助手", text)
        self.assertIn("用户：寝室可以用大功率电器吗", text)
        self.assertIn("助手：目前没有找到", text)

    def test_build_contextual_query_includes_follow_up_and_previous_topic(self):
        from conversation_context import build_contextual_query

        history = [
            {"role": "user", "content": "寝室可以用大功率电器吗"},
            {"role": "ai", "content": "目前没有找到与这个问题直接相关的校园规定。"},
        ]

        query = build_contextual_query("那会被处分吗", history)

        self.assertIn("寝室可以用大功率电器吗", query)
        self.assertIn("那会被处分吗", query)


if __name__ == "__main__":
    unittest.main()
