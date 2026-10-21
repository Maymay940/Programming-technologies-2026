# Лабораторная работа №0. Знакомство с OpenAI API. Написание простого чат-бота.

## **Выполнил**: Студент группы ИС-23, Долгополов Максим

## **Цель работы**: научиться работать с OpenAI API, чтобы создать простого чат-бота, который может отвечать на ваши вопросы.

---

### Задание 1: Настройка окружения

Перед началом работы необходимо сделать _окружение_ для работы с зависимостями в пределах папки проекта.

Для этого необходимо в папке проекта выполнить комманду

``` python -m venv venv ```

Появится папка окружения venv. Для её активации необходимо запустить activate:

``` ./venv/Scripts/activate ```

Теперь можно устанавливать зависимости:

``` pip install openai python-dotenv```

Первая представляет собой API для работы с различными моделями нейросетей, а python-dotenv позволяет считывать переменные окружения из .env файла.

После установки зависимостей можно сохранить их список на будущее (если понадобятся именно эти версии в случае, например, потери папки проекта) командой:

``` pip freeze > requirements.txt ```

Внутри можно увидеть сами зависимости и их версии: 

[Ссылка на requirements.txt](./openai-app/requirements.txt)

<details>
<summary><strong>Посмотреть requirements.txt</strong></summary>

```
annotated-types==0.8.0
anyio==4.15.1
h11==0.16.0
httpcore2==2.15.1
httpx2==2.15.1
idna==3.20
jiter==0.17.0
openai==3.35.1
pydantic==2.14.1
pydantic_core==2.50.1
python-dotenv==1.2.4
sniffio==1.3.1
truststore==0.10.5
typing-inspection==0.4.4
typing_extensions==4.16.0

```

</details>

---

### Задание 2: Обращение к Responses API

Responses API является унифицированным интерфейсом от OpenAI, позволяющий сохранять состояние моделей во время работы приложения, а также имеющий доступ ко множеству моделей OpenAI.

Нужно создать первый .py скрипт и саму функцию вызова Responses API:

<details>
<summary><strong>Посмотреть main.py</strong></summary>

```
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def get_response(text: str, client: OpenAI):
    response = client.responses.create(model="gpt-6-luna", input=text)
    return response

```

</details>

Здесь применяются ранее полученные зависимости, загружается переменная окружения с ключом OpenAI, а также сама функция, в которой переменная response будет хранить ответ сети и возвращать значение функции. При этом хранится вызов `client.responses.create` с аргументами, коих много. Для начала используем `model` и `input`.
 
---

### Задание 3: Главный цикл

Чтобы скрипт работал и вообще была способность общения, добавим функцию `__main__` и в неё цикл `while` с условием True. В сам цикл добавим сегмент общения по-порядку - вопрос-ответ, а также ключевое слово (промпт) - exit, которое будет проверяться условием и в случае выполнения останавливать цикл при помощи `break`. В итоге скрипт будет иметь вид:

[Ссылка на main.py](./openai-app/main.py)

<details>
<summary><strong>Посмотреть main.py</strong></summary>

```
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def get_response(text: str, client: OpenAI):
    response = client.responses.create(model="gpt-6-luna", input=text)
    return response


if __name__ == "__main__":
    print("Введите ваш вопрос (или 'exit' для выхода):")
    while True:
        question = input("Вы: ")
        if question.lower() == "exit":
            print("Завершение программы.")
            break
        answer = get_response(question, client)
        print("AI:", answer.output_text)
```

</details>

---

## Самостоятельные задания 

---

### Задание 1: Системные промпты

**Описание**: Реализовать системный промпт через переменную окружения в .env либо через ручной ввод и выбор промпта с сохранением в базу данных, если в терминале выбрана соответствующая опция. В Responses API промпт передаётся параметром instructions или сообщением с ролью developer. Реализовать хотсвап между системными промптами.

Для решения задачи понадобится всё тот же `.env` и зависимости `sqlite3` и `load_dotenv`.

Для создания `.db` был создан скрипт `.py` под названием `sqlite3query.py` ([Ссылка на sqlite3query.py](./openai-app/sqlite3query.py)). Его содержимое:

<details>
<summary><strong>Посмотреть sqlite3query.py</strong></summary>

```
import sqlite3
import os

conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), './prompts.db'))
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        prompt_text TEXT NOT NULL
    );
''')

cursor.execute('''    
    INSERT INTO system_prompts (name, prompt_text) VALUES
    ("Злодей", "Прикинься во время диалога, что ты злой злодей"),
    ("Добряк", "Прикинься во время диалога, что ты добрейшей души человек"),
    ("Космический пират", "Ты - веселый космический пират с характерным стилем общения морского пирата; ты похищаешь космические корабли и любишь выпивку"),
    ("Крутой", "Ты - крутой и общаешься с пафосом, параллельно хвастаясь сбережениями, недвижимостью и дорогими вещами")
''')
conn.commit()
conn.close()
```

</details>

Можно заметить, что здесь мы создаем при помощи привычных SQL запросов таблицу *system_prompts* с атрибутами **id** (стандартный атрибут таблицы), **name** (название промпта, или иначе - роли) и **promt_text** (текст самого промпта), а также 4 записи в эту таблицу для каждой из роли.

Ситуация с ролями в `.env` файле намного проще: здесь просто нужно добавить ключи и их значения. Пусть значениями будут сами промты, а ключи - их названия:

![Ссылка на sqlite3query.py](./assets/syspromptfromvenv.png)

Теперь нужно внедрить подключение БД, сохранение значений записей в 1 переменную, а также чтение переменных окружения:

[Ссылка на отрывок task1.py](./openai-app/task1.py#L4-L22)

<details>
<summary><strong>Посмотреть отрывок task1.py</strong></summary>

```
...
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
...
```

</details>

Как можно заметить, промпты из `.env` мы сохраняем в список, а из-за особенностей работы .fetchall() в sqlite3 мы сохраняем в db_prompts список списков (т.е. матрицу).

Когда у нас уже появились промпты, осталось реализовать выбор и хот-свап промпта. Для этого была создана функция `choose_prompt()`:

[Ссылка на choose_prompt() в task1.py](./openai-app/task1.py#L28-L55)

<details>
<summary><strong>Ссылка на choose_prompt() в task1.py</strong></summary>

```
...
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
...
```

</details>

Все что останется добавить - первый вызов функции и условие для повторного вызова во время диалога (по аналогии с `exit`):

[Ссылка на __main__ в task1.py](./openai-app/task1.py#L57-L71)

<details>
<summary><strong>Ссылка на __main__ в task1.py</strong></summary>

```
...
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
```

</details>

Результаты работы промптов, а также работа их hot-swap'а - на скриншоте: 

![Промпт1](./assets/changeprompt1.png)

![Промпт2](./assets/changeprompt2.png)

---

## Задание 2: Изменение усилия модели

**Описание**: Поэкспериментировать и описать в отчёте, как меняется ответ. На reasoning-моделях (gpt-6-luna и другие GPT-5/GPT-6) меняйте reasoning.effort: none, low, medium, high. У gpt-6-luna по умолчанию medium. Параметр temperature на них принимается только вместе с reasoning={"effort": "none"}; без этого API отклоняет значение, отличное от 1. На более старых моделях без reasoning (gpt-4o, gpt-4.1) меняйте temperature.

**Замечание**: В ходе работы не удалось найти модель gpt, которой не были бы нужны токены для работы. Работа была осуществлена только с параметром `effort`.

Теперь необходимо попробовать разные значения `effort` на модели. Будет все также взята модель `gpt-6-luna`.

Как говорилось в начале, запрос `client.responses.create` принимает множество значений, в том числе и `effort`, добавим её в функцию:

[Ссылка на get_response в task2.py](./openai-app/task2.py#L24-L26)

<details>
<summary><strong>Ссылка на get_response в task2.py</strong></summary>

```
...
client = OpenAI(api_key=api_key)

def get_response(text: str, client: OpenAI6, instructionprompt: str):
    response = client.responses.create(model="gpt-6-luna" input=text, instructions=instructionprompt, reasoning={"effort": "high"})
    return response

def choose_prompt():
...
```

</details>

С значением `high` модель выдает более качественные ответы, но они стоят дороже обычных. С `low` наоборот. Значение `medium`, как правило, стоит по-умолчанию у моделей. А `none` выключает рассуждения и ответы выдаются быстро без расхода токенов, хоть и некачественные.
Всего были проведены 3 теста на решение задачи на смекалку с целью увидеть развернутый ответ на первых трех режимах. Текст задачи:

```
На складе три автомата выдают напитки (чай, кофе, случайный). На этикетках перепутали все. Сколько монет надо бросить, чтобы гарантированно определить, где какой автомат?
```

Её решение моделями с разным мышлением:

### 1. `low`

![loweffort](./assets/loweffort.png)

### 2. `medium`

![mediumeffort](./assets/mediumeffort.png)

### 3. `high`

![higheffort](./assets/higheffort.png)

**P.S.** _Ответ, если что: нужно бросить монету в автомат с наклейкой "Случайный"._

И тут можно заметить расхождение в ответах, а также в размерах рассуждения.
На значении `low` модель дала невнятный и неправильный ответ, ибо чтобы получить напиток и определить автомат все-таки нужна монета.
На значении `medium` модель дала правильный, но краткий ответ. Пользователю может быть непонятно до конца, почему именно этот ответ.
А на значении `high` модель дала и правильный, и развернутый ответ на задачу, дак ещё и с примером.
Соответственно при решении логических задач или иных, где нужно **подумать**, то годится `medium`, но больше конечно `high`.

---

## Задание 3: Хранение контекста диалога

**Описание**: Реализовать ведение истории диалога, чтобы модель помнила предыдущие реплики. В input передавайте список сообщений и ограничивайте его шестью последними: 3 от пользователя и 3 от ассистента. Также можете попробовать использовать Conversation API. 
*P.S. Conversation API не использовался*

Для сохранения контекста необходимо две вещи: 1. где-то хранить диалог; 2. правильно хранить диалог в переменной.

Собственно, хранить вне скрипта контекст будем в текстовом документе **history.txt**, а на время работы - в списке `history`.

Для реализации понадобится модифицировать существующую функцию `__main__`, а точнее создать список `history`, использовать `open()` для открытия нашего **history.txt** и взятия оттуда контекста (если ранее он записывался), а также вызвать новую функцию `log_to_file()`, в которой через тот же `open()` будем открывать **history.txt** и сохранять диалог между пользователем и нейросетью, ограниченный 6 строками (3 вопроса - 3 ответа). Причем, наш контекст мы передаем после каждого нашего вопроса, так как это фактически не влияет на диалог.

 Так это выглядит в коде:

[Ссылка на функции в task3.py](./openai-app/task3.py#L60-105)

<details>
<summary><strong>Ссылка на функции в task3.py</strong></summary>

```
...
client = OpenAI(api_key=api_key)

def get_response(text: str, client: OpenAI6, instructionprompt: str):
    response = client.responses.create(model="gpt-6-luna" input=text, instructions=instructionprompt, reasoning={"effort": "high"})
    return response

def choose_prompt():
...
```

</details>

А так я задал 3 вопроса нейросети про ВКР, и вышел через `exit`. Затем после очередного запуска и вопроса про предыдущий диалог, она, получив контекст из **history.txt**, "вспомнила" диалог:

![ask](./assets/history.png)

Вот также содержание **history.txt**:

[Ссылка на history.txt](./openai-app/history.txt)

<details>
<summary><strong>Открыть history.txt</strong></summary>

```
Вы: Привет, как настроение?
AI: Привет! Всё отлично, спасибо 😊 А у тебя как?

Вы: Нормально. Готовлю свою ВКР
AI: Здорово! На какую тему ВКР? Могу помочь с планом, поиском источников, формулировками или проверкой текста.

Вы: Да все по ней есть, только приступить надо и вовсю делать
AI: Понимаю — часто самое трудное именно начать. Попробуй не ставить цель «сделать ВКР», а выделить один маленький шаг на сегодня: открыть документ, набросать план ближайшего раздела или написать черновик на 20 минут. Не обязательно сразу хорошо — главное, чтобы появился первый материал.

Если хочешь, напиши тему и срок сдачи — помогу разбить работу на посильные этапы.

Вы: Помнишь предыдущий диалог?
AI: Да. Ты сказал, что готовишь ВКР, всё необходимое у тебя уже есть, но нужно наконец приступить и активно работать. Я предложил начать с небольшого шага — например, 20 минут черновика.
```

</details>

---

###

**Заключение**: в ходе выполнения лабораторной работы я ознакомился с зависимостями OpenAI и python_dotenv, научился разворачивать модель и настраивать её параметры, а также подключать **системные промпты** и менять их во время диалога, менять **усилие** сети и хранить и подключать к модели **контекст** общения.