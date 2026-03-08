"""
AI Agent - принимает задачу от пользователя и выполняет её через ИИ.
"""

import os
import json
from dataclasses import dataclass, field
from typing import Optional
from openai import OpenAI


@dataclass
class TaskResult:
    """Результат выполнения задачи."""
    success: bool
    result: str
    error: Optional[str] = None


@dataclass
class AIAgent:
    """
    AI-агент, который принимает задачу и выполняет её.
    """
    name: str = "TaskAgent"
    model: str = "gpt-4o-mini"
    client: Optional[OpenAI] = field(default=None, repr=False)
    
    def __post_init__(self):
        if self.client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY не найден. Установите переменную окружения.")
            self.client = OpenAI(api_key=api_key)
    
    def execute_task(self, task: str) -> TaskResult:
        """
        Выполняет задачу, поставленную пользователем.
        
        Args:
            task: Описание задачи от пользователя
            
        Returns:
            TaskResult с результатом выполнения
        """
        try:
            # Анализируем задачу и генерируем план выполнения
            plan = self._create_plan(task)
            
            # Выполняем задачу на основе плана
            result = self._execute_plan(plan, task)
            
            return TaskResult(success=True, result=result)
            
        except Exception as e:
            return TaskResult(success=False, result="", error=str(e))
    
    def _create_plan(self, task: str) -> str:
        """Создаёт план выполнения задачи."""
        prompt = f"""
Ты - AI-агент. Проанализируй задачу и создай краткий план её выполнения.

Задача: {task}

Верни план в формате:
1. <шаг 1>
2. <шаг 2>
...
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    
    def _execute_plan(self, plan: str, task: str) -> str:
        """Выполняет задачу на основе плана."""
        prompt = f"""
Ты - AI-агент. Выполни задачу, следуя плану.

Задача: {task}

План:
{plan}

Выполни задачу и верни результат. Если задача требует действий - выполни их.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content


def main():
    """Главная функция - запускает агента в интерактивном режиме."""
    print("=" * 50)
    print("AI Task Agent - Выполнение задач через ИИ")
    print("=" * 50)
    print()
    print("Для выхода введите 'quit' или 'exit'")
    print()
    
    try:
        agent = AIAgent(name="TaskBot")
    except ValueError as e:
        print(f"Ошибка: {e}")
        print("\nДля запуска необходимо:")
        print("1. Получить API ключ на https://platform.openai.com/")
        print("2. Установить ключ: export OPENAI_API_KEY='ваш-ключ'")
        return
    
    while True:
        try:
            task = input("\nЗадача: ").strip()
            
            if task.lower() in ["quit", "exit", "выход"]:
                print("До свидания!")
                break
            
            if not task:
                continue
            
            print("\nВыполняю задачу...")
            result = agent.execute_task(task)
            
            if result.success:
                print(f"\nРезультат:\n{result.result}")
            else:
                print(f"\nОшибка: {result.error}")
                
        except KeyboardInterrupt:
            print("\n\nДо свидания!")
            break


if __name__ == "__main__":
    main()
