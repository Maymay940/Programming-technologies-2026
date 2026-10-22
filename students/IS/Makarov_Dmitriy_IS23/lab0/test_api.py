
from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

api_key = os.getenv("ZAI_API_KEY")
system_prompt = os.getenv(
    "SYSTEM_PROMPT",
    "Ты полезный ассистент."
)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.z.ai/api/paas/v4/"
)

MODEL = "glm-4.7-flash"

connection = sqlite3.connect("prompts.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    content TEXT NOT NULL
)
""")
connection.commit()

history = []

temperature = 0.7


def save_prompt():
    name = input("Название промпта: ")
    content = input("Текст промпта: ")

    cursor.execute(
        "INSERT INTO prompts (name, content) VALUES (?, ?)",
        (name, content)
    )
    connection.commit()

    print("Промпт сохранён.")


def change_prompt():
    global system_prompt

    cursor.execute("SELECT * FROM prompts")
    prompts = cursor.fetchall()

    if not prompts:
        print("Сохранённых промптов нет.")
        return

    for prompt in prompts:
        print(f"{prompt[0]}. {prompt[1]}")

    try:
        prompt_id = int(input("Выберите ID: "))
    except ValueError:
        print("Некорректный ID.")
        return

    cursor.execute(
        "SELECT content FROM prompts WHERE id = ?",
        (prompt_id,)
    )

    result = cursor.fetchone()

    if result:
        system_prompt = result[0]
        print("Системный промпт изменён.")
    else:
        print("Промпт не найден.")


def change_temperature():
    global temperature

    try:
        value = float(
            input("Введите temperature (0-1): ")
        )

        if 0 <= value <= 1:
            temperature = value
            print("Temperature:", temperature)
        else:
            print("Введите число от 0 до 1.")

    except ValueError:
        print("Некорректное значение.")


def get_response(text: str, client: OpenAI):
    global history

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": text
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature
    )

    answer = response.choices[0].message.content

    history.append({
        "role": "user",
        "content": text
    })

    history.append({
        "role": "assistant",
        "content": answer
    })

    history = history[-6:]

    return answer


if __name__ == "__main__":

    print("Чат-бот Z.AI")
    print("Модель:", MODEL)

    print("\nКоманды:")
    print("/save - сохранить промпт")
    print("/switch - сменить промпт")
    print("/temp - изменить temperature")
    print("/history - показать историю")
    print("/clear - очистить историю")
    print("exit - выход")

    try:
        while True:
            question = input("\nВы: ").strip()

            if question.lower() == "exit":
                print("Завершение программы.")
                break

            elif question == "/save":
                save_prompt()

            elif question == "/switch":
                change_prompt()

            elif question == "/temp":
                change_temperature()

            elif question == "/history":
                for message in history:
                    print(
                        message["role"],
                        ":",
                        message["content"]
                    )

            elif question == "/clear":
                history.clear()
                print("История очищена.")

            elif question:
                try:
                    answer = get_response(question, client)
                    print("AI:", answer)

                except Exception as error:
                    print("Ошибка API:", error)

    finally:
        connection.close()
