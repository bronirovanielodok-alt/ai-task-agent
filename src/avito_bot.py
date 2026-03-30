#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI помощник для ответов на Авито — Продажа лодок
Поддержка: OpenAI и Claude
"""

import sys
import os

# Выберите модель: "openai" или "claude"
MODEL = "openai"

API_KEY = os.getenv("ANTHROPIC_API_KEY") if MODEL == "claude" else os.getenv("OPENAI_API_KEY")

if not API_KEY:
    print("Ошибка: не найден API ключ!")
    print("Установите переменную окружения:")
    if MODEL == "claude":
        print("  export ANTHROPIC_API_KEY='ваш-ключ'")
    else:
        print("  export OPENAI_API_KEY='ваш-ключ'")
    sys.exit(1)

SYSTEM_PROMPT = """Ты — опытный продавец лодок и катеров в России.
Ты знаешь всё о лодках, катерах, моторах, прицепах.
Отвечай коротко, вежливо, по делу.
Предлагай посмотреть лодку вживую или созвониться.
Знаешь цены на рынке, можешь обосновать цену.
Стиль: профессионал, но дружелюбный."""

if MODEL == "claude":
    from anthropic import Anthropic
    client = Anthropic(api_key=API_KEY)
    
    def get_response(message: str, context: str = "") -> str:
        system_text = SYSTEM_PROMPT
        if context:
            system_text += f"\n\nКонтекст: {context}"
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            system=system_text,
            messages=[{"role": "user", "content": message}]
        )
        return response.content[0].text

else:
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY)
    
    def get_response(message: str, context: str = "") -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if context:
            messages.append({"role": "system", "content": f"Контекст: {context}"})
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content


def main():
    print("=" * 50)
    print("AI помощник для Авито — Продажа лодок")
    print(f"Модель: {MODEL.upper()}")
    print("=" * 50)
    print()
    
    # Ваша лодка
    context = """
Лодка: Катер Фрегат 550 (или ваша)
Цена: 1 500 000 руб
Год: 2020
Мотор: Yamaha 100 л.с.
Состояние: отличное
Комплект: прицеп, чехол, жилеты
"""
    
    print(f"Контекст:\n{context}")
    print()
    
    while True:
        msg = input("Сообщение клиента: ").strip()
        
        if msg.lower() in ["quit", "exit", "выход"]:
            break
        
        if not msg:
            continue
        
        print("AI думает...")
        try:
            response = get_response(msg, context)
            print(f"\nОтвет:\n{response}\n")
        except Exception as e:
            print(f"Ошибка: {e}\n")
        
        print("-" * 50)


if __name__ == "__main__":
    main()
