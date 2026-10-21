
from openai import OpenAI, RateLimitError, AuthenticationError, APIConnectionError
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
prompts = {
    "1": os.getenv("SYSTEM_PROMPT_HELPER"),
    "2": os.getenv("SYSTEM_PROMPT_PIRATE"),
    "3": os.getenv("SYSTEM_PROMPT_JSON")
}
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")


def get_response(text: str, client: OpenAI, system_prompt: str,
                 history: list, reasoning_effort: str):
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    messages.extend(history)
    messages.append({"role": "user", "content": text})

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        extra_body={"reasoning_effort": reasoning_effort}
    )

    return response.choices[0].message.content


def choose_prompt():
    print("\nВыберите системный промпт:")
    print("1. Обычный помощник")
    print("2. Пират")
    print("3. JSON-бот")

    while True:
        choice = input("Ваш выбор: ").strip()

        if choice in prompts:
            if not prompts[choice]:
                print("Ошибка: выбранный промпт отсутствует в .env.")
                continue

            print("Системный промпт успешно выбран!")
            return prompts[choice]

        print("Неверный выбор. Попробуйте снова.")


def choose_reasoning():
    print("\nВыберите уровень рассуждения:")
    print("1. low")
    print("2. medium")
    print("3. high")

    levels = {
        "1": "low",
        "2": "medium",
        "3": "high"
    }

    while True:
        choice = input("Ваш выбор: ").strip()

        if choice in levels:
            print("Уровень reasoning:", levels[choice])
            return levels[choice]

        print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    system_prompt = choose_prompt()
    reasoning_effort = choose_reasoning()
    history = []

    print("\nВведите ваш вопрос.")
    print("Для смены промпта введите '/prompt'.")
    print("Для смены reasoning введите '/reasoning'.")
    print("Для выхода введите 'exit'.")

    while True:
        question = input("\nВы: ").strip()

        if question.lower() == "exit":
            print("Завершение программы.")
            break

        if question.lower() == "/prompt":
            system_prompt = choose_prompt()
            history.clear()
            print("История диалога очищена.")

            print("\nВведите ваш вопрос.")
            print("Для смены промпта введите '/prompt'.")
            print("Для смены уровня рассуждения введите '/reasoning'.")
            print("Для выхода введите 'exit'.")
            continue

        if question.lower() == "/reasoning":
            reasoning_effort = choose_reasoning()
            history.clear()
            print("История диалога очищена.")
            continue

        if not question:
            continue

        try:
            answer = get_response(
                question, client, system_prompt, history, reasoning_effort
            )
            print("AI:", answer)

            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": answer})

            history = history[-6:]

        except RateLimitError:
            print("Ошибка: превышен лимит запросов или исчерпана квота API.")

        except AuthenticationError:
            print("Ошибка: неверный API-ключ.")

        except APIConnectionError:
            print("Ошибка: не удалось подключиться к серверу Groq.")
