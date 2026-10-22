from openai import OpenAI
from dotenv import load_dotenv
import sqlite3
import os

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

def get_response(text: str, client: OpenAI6, instructionprompt: str):
    response = client.responses.create(model="gpt-6-luna", input=text, instructions=instructionprompt)
    return response

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

if __name__ == "__main__":
    choosed_prompt = choose_prompt()
    while True:
        question = input("Вы: ")
        if question.lower() == "exit":
            print("Завершение программы.")
            break

        if question.lower() == "/change":
            print("Смена промпта")
            choosed_prompt = choose_prompt()
            continue

        answer = get_response(question, client, choosed_prompt)
        print("AI:", answer.output_text)