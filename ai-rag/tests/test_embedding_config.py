import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from embedding_config import resolve_embedding_settings


class EmbeddingConfigTests(unittest.TestCase):
    def test_scnet_key_uses_qwen3_embedding_defaults(self):
        settings = resolve_embedding_settings({"SCNET_API_KEY": "sk-test"})

        self.assertEqual(settings.api_key, "sk-test")
        self.assertEqual(settings.api_key_source, "SCNET_API_KEY")
        self.assertEqual(settings.base_url, "https://api.scnet.cn/api/llm/v1")
        self.assertEqual(settings.model, "Qwen3-Embedding-8B")

    def test_generic_embedding_env_overrides_provider_defaults(self):
        settings = resolve_embedding_settings({
            "EMBEDDING_API_KEY": "sk-test",
            "EMBEDDING_BASE_URL": "https://example.com/v1",
            "EMBEDDING_MODEL": "custom-embedding",
        })

        self.assertEqual(settings.api_key, "sk-test")
        self.assertEqual(settings.api_key_source, "EMBEDDING_API_KEY")
        self.assertEqual(settings.base_url, "https://example.com/v1")
        self.assertEqual(settings.model, "custom-embedding")

    def test_zhipu_key_keeps_old_embedding_defaults(self):
        settings = resolve_embedding_settings({"ZHIPUAI_API_KEY": "zhipu-test"})

        self.assertEqual(settings.api_key, "zhipu-test")
        self.assertEqual(settings.api_key_source, "ZHIPUAI_API_KEY")
        self.assertEqual(settings.base_url, "https://open.bigmodel.cn/api/paas/v4/")
        self.assertEqual(settings.model, "embedding-3")

    def test_zhipu_fallback_ignores_generic_scnet_defaults_without_generic_key(self):
        settings = resolve_embedding_settings({
            "ZHIPUAI_API_KEY": "zhipu-test",
            "EMBEDDING_BASE_URL": "https://api.scnet.cn/api/llm/v1",
            "EMBEDDING_MODEL": "Qwen3-Embedding-8B",
        })

        self.assertEqual(settings.base_url, "https://open.bigmodel.cn/api/paas/v4/")
        self.assertEqual(settings.model, "embedding-3")

    def test_missing_key_returns_none(self):
        self.assertIsNone(resolve_embedding_settings({}))


if __name__ == "__main__":
    unittest.main()
