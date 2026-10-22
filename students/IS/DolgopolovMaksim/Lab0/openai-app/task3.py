from openai import OpenAI
from dotenv import load_dotenv
import sqlite3
import os
import sys

original_stdout = sys.stdout

conn = sqlite3.connect('prompts.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM system_prompts ")
db_prompts = cursor.fetchall()
cursor.close()

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
envpromts = [
    (os.getenv("PROG_SYSTEM_PROMPT")),
    (os.getenv("GENIUS_SYSTEM_PROMPT")),
    (os.getenv("TIME_TRAVEL_SYSTEM_PROMPT"))
]

client = OpenAI(api_key=api_key)

def get_response(messages_list: list, client: OpenAI6, instructionprompt: str):
    response = client.responses.create(model="gpt-6-luna", input=messages_list, instructions=instructionprompt, reasoning={"effort": "none"}, temperature=0.0)
    return response.output_text

def choose_prompt():
    print("Способ выбора системного промпта:")
    print("1 - из переменных окружения")
    print("2 - из БД sqlite3")
    choosetype = int(input())
    if choosetype == 1:
        print("Выберите промпт:")
        print("0 - Ассистент-программист")
        print("1 - Гений")
        print("2 - Путешественник по времени")
        choose = int(input())
        final_prompt = envpromts[choose]
    elif choosetype == 2:
        print("Выберите промпт:")
        for row in db_prompts:
            prompt_id = row[0]
            prompt_name = row[1]
            prompt_text = row[2]
            print(f"[{prompt_id}] - {prompt_name}")
        choose = int(input())
        for row in db_prompts:
            if row[0] == choose:
                final_prompt = row[2]
    else:
        print("Вы выбрали неправильное значение. Будет использоваться стандартный промпт.")
        final_prompt = "Ты обычный ассистент."
    
    return final_prompt

def log_to_file(user_text: str, ai_text: str):
    with open('history.txt', 'a', encoding='utf-8') as f:
        f.write(f"Вы: {user_text}\n")
        f.write(f"AI: {ai_text}\n\n")

if __name__ == "__main__":
    choosed_prompt = choose_prompt()
    history = []

    if os.path.exists('history.txt'):
        print("--- Загрузка истории из файла ---")
        with open('history.txt', 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
            
                print(stripped.upper())
                
                if stripped.startswith("Вы:"):
                    text_content = stripped[3:].strip()
                    history.append({"role": "user", "content": text_content})
                elif stripped.startswith("AI:"):
                    text_content = stripped[3:].strip()
                    history.append({"role": "assistant", "content": text_content})

    while True:
        question = input("Вы: ")
        
        if question.lower() == "exit":
            print("Завершение программы.")
            break

        if question.lower() == "/change":
            print("Смена промпта")
            choosed_prompt = choose_prompt()
            continue

        history.append({"role": "user", "content": question})
        limited_history = history[-6:]

        answer = get_response(limited_history, client, choosed_prompt)
        print(f"AI: {answer}")

        history.append({"role": "assistant", "content": answer})
        log_to_file(question, answer)