from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

api_key = os.getenv("ZAI_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.z.ai/api/paas/v4/",
)

db = sqlite3.connect("prompts.db")
db.execute("CREATE TABLE IF NOT EXISTS prompts (id INTEGER PRIMARY KEY, text TEXT)")
db.commit()

def choose_prompt():
    print("1 — промпт из .env")
    print("2 — ввести новый и сохранить в базу")
    print("3 — выбрать сохранённый из базы")
    choice = input("Выбор: ").strip()

    if choice == "1":
        return os.getenv("SYSTEM_PROMPT")

    if choice == "2":
        text = input("Введите промпт: ")
        db.execute("INSERT INTO prompts (text) VALUES (?)", (text,))
        db.commit()
        return text

    rows = db.execute("SELECT id, text FROM prompts").fetchall()
    for row in rows:
        print(row[0], row[1])
    number = input("Номер: ")
    row = db.execute("SELECT text FROM prompts WHERE id = ?", (number,)).fetchone()
    return row[0]

def get_response(text: str, client: OpenAI, system_prompt: str, temperature: float, history: list):
    messages = [{"role": "system", "content": system_prompt}]
    messages += history[-6:]
    messages.append({"role": "user", "content": text})
    response = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=messages,
        temperature=temperature,
    )
    answer = response.choices[0].message.content
    history.append({"role": "user", "content": text})
    history.append({"role": "assistant", "content": answer})
    return answer

if __name__ == "__main__":
    system_prompt = choose_prompt()
    temperature = float(input("temperature от 0 до 1: "))
    history = []
    print("Вопрос, exit для выхода, swap для смены промпта, temp для смены temperature:")
    while True:
        question = input("Вы: ")
        if question.lower() == "exit":
            print("Завершение программы.")
            break
        if question.lower() == "swap":
            system_prompt = choose_prompt()
            continue
        if question.lower() == "temp":
            temperature = float(input("Новая temperature от 0 до 1: "))
            continue
        answer = get_response(question, client, system_prompt, temperature, history)
        print("AI:", answer)