import sqlite3
import os

DB_NAME = "cyber_trener.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor() #do wykonywania poleceń

    cursor.execute(
        'CREATE TABLE IF NOT EXISTS treningi '
        '(id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'data TEXT DEFAULT (date("now")), '
        'powtorzenia INTEGER NOT NULL, '
        'technika TEXT NOT NULL)')

    conn.commit() #zapis do bazy

    conn.close()


def save_training(powtorzenia, technika):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('INSERT INTO treningi (powtorzenia, technika) VALUES (?, ?)', (powtorzenia, technika))

    conn.commit()
    conn.close()


def get_training_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT data, powtorzenia, technika FROM treningi ORDER BY id DESC')

    rows = cursor.fetchall() #pobranie danych z bazy do listy

    conn.close()

    return rows