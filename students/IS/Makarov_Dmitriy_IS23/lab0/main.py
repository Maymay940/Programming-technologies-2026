from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(
    dotenv_path=Path(__file__).resolve().parent / ".env",
    override=True
)

api_key = os.getenv("ZAI_API_KEY")

print("Ключ загружен:", bool(api_key))

client = OpenAI(
    api_key=api_key,
    base_url="https://api.z.ai/api/paas/v4/"
)

def get_response(text: str, client: OpenAI):
    response = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=[
            {"role": "user", "content": text}
        ]
    )
    return response

if __name__ == "__main__":
    print("Введите ваш вопрос (или 'exit' для выхода):")

    while True:
        question = input("Вы: ")

        if question.lower() == "exit":
            print("Завершение программы.")
            break

        answer = get_response(question, client)

        print("AI:", answer.choices[0].message.content)