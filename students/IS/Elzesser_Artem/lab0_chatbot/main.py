
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Системные промпты
prompts = {
    "default": os.getenv("SYSTEM_PROMPT"),
    "humor": os.getenv("HUMOR_PROMPT"),
    "short": os.getenv("SHORT_PROMPT")
}

current_prompt = "default"
reasoning_effort = "medium"

# История диалога
history = []


def get_response(text):
    global history

    # Добавляем новый вопрос к истории
    messages = history[-6:] + [
        {"role": "user", "content": text}
    ]

    response = client.responses.create(
        model="openai/gpt-oss-20b",
        instructions=prompts[current_prompt],
        input=messages,
        reasoning={"effort": reasoning_effort}
    )

    answer = response.output_text

    # Сохраняем вопрос и ответ
    history.append({
        "role": "user",
        "content": text
    })

    history.append({
        "role": "assistant",
        "content": answer
    })

    # Оставляем только последние 6 сообщений
    history = history[-6:]

    return answer


print("Чат-бот запущен!")
print("/default - обычный режим")
print("/humor - режим юмора")
print("/short - краткие ответы")
print("/effort - уровень рассуждения")
print("/history - показать историю")
print("/clear - очистить историю")
print("exit - выход")

while True:
    question = input("\nВы: ").strip()

    if question.lower() == "exit":
        print("Программа завершена.")
        break

    elif question == "/default":
        current_prompt = "default"
        print("Обычный режим включён!")

    elif question == "/humor":
        current_prompt = "humor"
        print("Режим юмора включён!")

    elif question == "/short":
        current_prompt = "short"
        print("Режим кратких ответов включён!")

    elif question == "/effort":
        value = input(
            "Выбери low, medium или high: "
        ).strip().lower()

        if value in ["low", "medium", "high"]:
            reasoning_effort = value
            print("Установлен уровень:", reasoning_effort)
        else:
            print("Неверное значение!")

    elif question == "/history":
        print("\nИстория диалога:")

        if not history:
            print("История пуста.")

        for message in history:
            print(message["role"] + ":", message["content"])

    elif question == "/clear":
        history.clear()
        print("История очищена!")

    elif question:
        answer = get_response(question)
        print("\nAI:", answer)
        print("Уровень рассуждения:", reasoning_effort)
