import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class IntentRouterTests(unittest.TestCase):
    def test_dorm_sleeping_is_plain_chat(self):
        from intent_router import classify_intent

        self.assertEqual(classify_intent("寝室可以睡觉吗"), "chat")

    def test_dorm_high_power_appliance_is_rule_qa(self):
        from intent_router import classify_intent

        self.assertEqual(classify_intent("寝室可以使用大功率电器吗"), "rule_qa")

    def test_punishment_follow_up_uses_previous_rule_topic(self):
        from conversation_context import build_contextual_query
        from intent_router import classify_intent

        query = build_contextual_query(
            "那会被处分吗",
            [{"role": "user", "content": "寝室可以使用大功率电器吗"}],
        )

        self.assertEqual(classify_intent(query), "rule_qa")

    def test_order_follow_up_stays_business_intent(self):
        from conversation_context import build_contextual_query
        from intent_router import classify_intent

        query = build_contextual_query(
            "那待完成的呢",
            [{"role": "user", "content": "我的订单状态"}],
        )

        self.assertEqual(classify_intent(query), "order_list")


if __name__ == "__main__":
    unittest.main()
