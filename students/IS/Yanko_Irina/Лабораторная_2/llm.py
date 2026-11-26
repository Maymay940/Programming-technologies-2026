import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError
from schemas import ExtractedData

load_dotenv()

client = OpenAI(
    base_url=os.environ["LM_STUDIO_BASE_URL"],
    api_key=os.environ["LM_STUDIO_API_KEY"],
    timeout=float(os.getenv("LLM_TIMEOUT", "120")),
    max_retries=0,
)

MODEL = os.environ["LM_STUDIO_MODEL"]
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
SYSTEM_PROMPT = """
Ты — система извлечения информации из обращений читателей библиотеки.

ТВОЯ ЗАДАЧА:
Проанализировать сообщение читателя и извлечь только те сведения,
которые он сам сообщил.

Ты НЕ библиотекарь-консультант.
Ты НЕ отвечаешь на вопросы читателя.
Ты НЕ выполняешь запрошенные действия.
Ты НЕ дополняешь обращение собственными знаниями.

Верни ровно один JSON-объект с шестью полями:
category, summary, book_code, reader_card,
requested_period, details.

ПРАВИЛА ЗАПОЛНЕНИЯ:

1. category — одна из четырёх категорий:
   borrow — читатель хочет взять книгу;
   renew — читатель хочет продлить книгу;
   availability — читатель спрашивает о наличии книги;
   other — все остальные обращения.
2. summary — кратко опиши, с какой просьбой
   или вопросом обратился читатель.
   Не отвечай на его вопрос.
   Не описывай запрашиваемое действие как уже выполненное.
3. book_code — только каталожный код,
   явно указанный в сообщении.
   Не определяй код по названию книги.
   Если кода нет, используй null.
4. reader_card — только номер читательского билета,
   явно указанный в сообщении.
   Если номера нет, используй null.
5. requested_period — дата или период,
   которые явно указаны в сообщении.
   Сохраняй исходные слова дословно.
   Не переводи, не пересчитывай и не изменяй формулировку.
   Если периода нет, используй null.
6. details — только дополнительные факты,
   которые читатель САМ СООБЩИЛ в тексте
   и которые не вошли в остальные поля.
   Не добавляй информацию самостоятельно.
   Если дополнительных фактов нет, используй null.

ВАЖНО:
- Вопрос читателя не содержит ответа на самого себя.
- Если читатель спрашивает, где находится помещение,
  это НЕ означает, что его расположение известно.
- Если читатель спрашивает о расписании,
  это НЕ означает, что расписание известно.
- Не придумывай адреса, этажи, часы работы,
  наличие книг и другие сведения.
- Не используй знания, полученные при обучении.
- Все шесть полей обязательны.
- Не добавляй лишних полей.
- Возвращай только JSON без Markdown и пояснений.

ПРИМЕР 1.
Сообщение:
"Хочу продлить книгу BK-118 ещё на неделю.
Мой читательский билет R-302."

Ответ:
{
  "category": "renew",
  "summary": "Запрос на продление книги BK-118.",
  "book_code": "BK-118",
  "reader_card": "R-302",
  "requested_period": "ещё на неделю",
  "details": null
}
"""

class InvalidLLMResponse(Exception): pass

def extract_data(message: str) -> ExtractedData:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        temperature=TEMPERATURE,
        max_tokens=500,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "library_request",
                "strict": True,
                "schema": ExtractedData.model_json_schema(),
            },
        },
    )
    print("Причина завершения:", response.choices[0].finish_reason)

    content = response.choices[0].message.content

    print("Ответ Qwen:")
    print(repr(content)) 

    if not content:
        raise InvalidLLMResponse("Модель вернула пустой ответ")

    try:
        raw = json.loads(content)
        if not isinstance(raw, dict):
            raise ValueError("Ожидался JSON-объект")
        return ExtractedData.model_validate(raw)

    except (ValueError, ValidationError) as exc:
        raise InvalidLLMResponse(
            "Ответ модели не соответствует схеме"
        ) from exc