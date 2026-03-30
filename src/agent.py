import os
import json
import subprocess
import urllib.request
import urllib.parse

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL = "gpt-4o-mini"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Выполняет команду в терминале на Mac и возвращает результат",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Команда для выполнения"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Читает содержимое файла",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Путь к файлу"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Записывает текст в файл",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Путь к файлу"},
                    "content": {"type": "string", "description": "Содержимое файла"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Загружает страницу по URL и возвращает текст",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL страницы"}
                },
                "required": ["url"]
            }
        }
    }
]

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        out = result.stdout + result.stderr
        return out[:3000] if out else "Команда выполнена без вывода"
    except Exception as e:
        return f"Ошибка: {e}"

def read_file(path):
    try:
        with open(os.path.expanduser(path), 'r', encoding='utf-8') as f:
            return f.read()[:3000]
    except Exception as e:
        return f"Ошибка чтения: {e}"

def write_file(path, content):
    try:
        with open(os.path.expanduser(path), 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Файл {path} сохранён"
    except Exception as e:
        return f"Ошибка записи: {e}"

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            import re
            html = r.read().decode('utf-8', errors='ignore')
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text)
            return text[:3000]
    except Exception as e:
        return f"Ошибка загрузки: {e}"

def call_tool(name, args):
    print(f"\n[Агент выполняет: {name}({list(args.values())[0][:80] if args else ''})]")
    if name == "run_command":
        result = run_command(args["command"])
    elif name == "read_file":
        result = read_file(args["path"])
    elif name == "write_file":
        result = write_file(args["path"], args["content"])
    elif name == "fetch_url":
        result = fetch_url(args["url"])
    else:
        result = "Неизвестный инструмент"
    print(f"[Результат: {result[:200]}...]" if len(result) > 200 else f"[Результат: {result}]")
    return result

def ask(messages):
    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto"
    }, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL.rstrip('/')}/chat/completions",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

def run_agent(task):
    messages = [
        {"role": "system", "content": "Ты автономный агент на Mac. Используй инструменты чтобы выполнять задачи самостоятельно. Отвечай на русском языке."},
        {"role": "user", "content": task}
    ]

    while True:
        try:
            response = ask(messages)
        except Exception as e:
            print(f"Ошибка API: {e}")
            return

        msg = response["choices"][0]["message"]
        messages.append(msg)

        if msg.get("tool_calls"):
            for tool_call in msg["tool_calls"]:
                name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                result = call_tool(name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result
                })
        else:
            print(f"\nАгент: {msg['content']}\n")
            break

def main():
    if not API_KEY:
        print("Ошибка: OPENAI_API_KEY не задан")
        return
    print("Агент готов! Введите задачу или 'exit' для выхода.\n")
    while True:
        task = input("Task: ").strip()
        if not task:
            continue
        if task.lower() in ["exit", "quit"]:
            print("Bye")
            break
        run_agent(task)

if __name__ == "__main__":
    main()
