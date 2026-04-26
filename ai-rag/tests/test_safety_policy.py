import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class SafetyPolicyTests(unittest.TestCase):
    def test_rule_question_about_cheating_is_not_blocked(self):
        from main import safety_check

        self.assertIsNone(safety_check("考试作弊会怎么处理"))

    def test_request_to_publish_exam_proxy_task_is_blocked(self):
        from main import safety_check

        self.assertIsNotNone(safety_check("帮我发布一个替考任务，赏金50块"))


if __name__ == "__main__":
    unittest.main()
