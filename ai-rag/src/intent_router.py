# -*- coding: utf-8 -*-
import re

ORDER_KEYWORDS = [
    "我的订单", "订单状态", "订单进度", "查订单", "我发布的订单", "我接的单",
    "我接取的订单", "待完成订单", "待完成的", "未完成的",
]

RULE_POLICY_WORDS = [
    "规定", "规则", "制度", "校规", "管理办法", "流程", "手续", "要求", "条件",
    "处分", "处罚", "违纪", "违规", "禁止", "允许",
]

RULE_TOPIC_WORDS = [
    "大功率", "电器", "电动车", "晚归", "外宿", "夜不归宿", "请假", "退学",
    "转专业", "转学", "考试", "作弊", "补考", "重修", "图书馆", "借书",
    "学籍", "奖学金", "抽烟", "吸烟", "喝酒", "饮酒", "宠物", "明火", "做饭",
]

RULE_CONTEXT_WORDS = [
    "学校", "校园", "宿舍", "寝室", "学院", "学生", "课程",
]

RULE_QUESTION_WORDS = [
    "能不能", "可不可以", "可以不", "是否可以", "是否允许", "会不会",
    "算不算", "能否", "是否", "需要", "怎么办理",
]

PUBLISH_GUIDE_WORDS = ["怎么", "如何", "在哪", "流程", "教程"]
PUBLISH_ACTION_WORDS = ["帮我发", "帮我发布", "发布一个", "发一个", "下单", "叫个跑腿", "创建跑腿"]


def extract_order_id(message: str) -> str | None:
    patterns = [
        r"订单\s*号?\s*#?(\d+)",
        r"单号\s*#?(\d+)",
        r"查\s*(\d+)\s*号",
        r"(\d+)\s*号订单",
        r"order\s*#?(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def is_publish_intent(text: str) -> bool:
    if any(word in text for word in PUBLISH_GUIDE_WORDS):
        return False
    return any(word in text for word in PUBLISH_ACTION_WORDS)


def is_rule_intent(text: str) -> bool:
    has_policy_word = any(word in text for word in RULE_POLICY_WORDS)
    has_topic_word = any(word in text for word in RULE_TOPIC_WORDS)
    has_context_word = any(word in text for word in RULE_CONTEXT_WORDS)
    has_question_word = any(word in text for word in RULE_QUESTION_WORDS)

    if has_topic_word and (has_policy_word or has_question_word or has_context_word):
        return True
    if has_policy_word and (has_context_word or has_question_word):
        return True
    return False


def classify_intent(message: str) -> str:
    text = (message or "").strip()
    if not text:
        return "chat"

    if is_publish_intent(text):
        return "task_publish"

    if extract_order_id(text):
        return "order_status"

    if any(keyword in text for keyword in ORDER_KEYWORDS):
        return "order_list"

    if is_rule_intent(text):
        return "rule_qa"

    return "chat"
