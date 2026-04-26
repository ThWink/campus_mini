import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class PromptTests(unittest.TestCase):
    def test_rule_prompt_requires_campus_assistant_answer_shape(self):
        from prompts import build_rule_prompt

        prompt = build_rule_prompt(
            user_message="寝室可以使用大功率电器吗",
            history_text="无",
            context="宿舍禁止使用大功率电器。",
        )

        self.assertIn("校园助手", prompt)
        self.assertIn("先给结论", prompt)
        self.assertIn("依据", prompt)
        self.assertIn("建议", prompt)
        self.assertIn("不要编造", prompt)

    def test_chat_prompt_avoids_fake_rules_and_order_status(self):
        from prompts import build_chat_prompt

        prompt = build_chat_prompt("寝室可以睡觉吗", "无")

        self.assertIn("不要编造订单状态", prompt)
        self.assertIn("不要编造学校规定", prompt)


if __name__ == "__main__":
    unittest.main()
