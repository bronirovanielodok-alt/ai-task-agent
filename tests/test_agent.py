"""
Тесты для AI агента.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.agent import AIAgent, TaskResult


class TestTaskResult(unittest.TestCase):
    """Тесты для класса TaskResult."""
    
    def test_success_result(self):
        """Тест успешного результата."""
        result = TaskResult(success=True, result="Тестовый результат")
        self.assertTrue(result.success)
        self.assertEqual(result.result, "Тестовый результат")
        self.assertIsNone(result.error)
    
    def test_error_result(self):
        """Тест ошибочного результата."""
        result = TaskResult(success=False, result="", error="Ошибка!")
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Ошибка!")


class TestAIAgent(unittest.TestCase):
    """Тесты для класса AIAgent."""
    
    def test_agent_initialization(self):
        """Тест инициализации агента с моком API ключа."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.agent.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                agent = AIAgent(name="TestBot")
                
                self.assertEqual(agent.name, "TestBot")
                self.assertEqual(agent.model, "gpt-4o-mini")
    
    def test_agent_without_api_key(self):
        """Тест ошибки при отсутствии API ключа."""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError) as context:
                AIAgent()
            
            self.assertIn("OPENAI_API_KEY", str(context.exception))


if __name__ == "__main__":
    unittest.main()
