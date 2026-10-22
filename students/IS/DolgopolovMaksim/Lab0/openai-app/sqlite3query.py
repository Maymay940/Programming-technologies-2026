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