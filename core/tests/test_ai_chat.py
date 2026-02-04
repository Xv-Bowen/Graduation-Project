from django.conf import settings
from django.test import TestCase

from core.services.ai_chat import parse_ai_payload, contains_risk


class AIChatTests(TestCase):
    def test_parse_payload_truncates(self):
        payload = {
            "provider": "deepseek",
            "deep_think": True,
            "messages": [
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hello"},
                {"role": "user", "content": "how are you"},
            ],
        }
        settings.CHAT_HISTORY_LIMIT = 2
        parsed = parse_ai_payload(payload)
        self.assertEqual(len(parsed.messages), 2)
        self.assertEqual(parsed.messages[0]["content"], "hello")

    def test_parse_payload_rejects_long_content(self):
        payload = {
            "messages": [{"role": "user", "content": "x" * (settings.AI_MAX_INPUT_CHARS + 1)}]
        }
        with self.assertRaises(ValueError):
            parse_ai_payload(payload)

    def test_contains_risk(self):
        self.assertTrue(contains_risk("我想自杀"))
        self.assertFalse(contains_risk("今天心情还好"))
