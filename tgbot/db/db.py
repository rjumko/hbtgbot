import sqlite3
from dataclasses import dataclass
from datetime import date
from icecream import ic
from environs import Env


env = Env()
env.read_env()
if env.bool("DEV"):
    ic("DEV - TRUE")
    connection = sqlite3.connect("my_database.sqlite")
else:
    ic("DEV - FALSE")
    connection = sqlite3.connect("/data/my_database.sqlite")


def create_table():
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        birthday DATE,
        username TEXT NOT NULL,
        user_id TEXT NOT NULL
        )
        """
    )
    connection.commit()


def create_table_url_google():
    cursor = connection.cursor()
    cursor.execute(
        """
        DROP TABLE IF EXISTS url_google
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS url_google (
        user_id TEXT PRIMARY KEY,
        url_google TEXT,
        start INTEGER
        )
        """
    )
    connection.commit()


def update_url_google(url_google: str, user_id: str) -> None:
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO url_google (user_id, url_google) VALUES(?, ?)
        ON CONFLICT(user_id) DO UPDATE SET url_google=?;
        """,
        (user_id, url_google, url_google),
    )
    connection.commit()


def get_users_ids():
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT user_id FROM url_google
        """,
    )
    return cursor.fetchall()


def get_url_google(user_id: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT url_google FROM url_google
        WHERE user_id=?;
        """,
        (user_id,),
    )
    ic("-------get_url_google", user_id)
    ic(res := cursor.fetchone())
    if res:
        return res[0]
    return None


def is_user_in_url_google(user_id: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM url_google
        WHERE user_id=?;
        """,
        (user_id,),
    )
    return True if cursor.fetchone() else False


def add_user_in_url_google(user_id: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO url_google (user_id, url_google, start) VALUES (?, Null, 0)
        """,
        (user_id,),
    )
    connection.commit()


def del_url_google(user_id: str) -> None:
    cursor = connection.cursor()
    cursor.execute(
        """
        DELETE FROM url_google
        WHERE user_id=?;
        """,
        (user_id,),
    )
    connection.commit()


def delete_all() -> None:
    cursor = connection.cursor()
    cursor.execute(
        """
        DELETE FROM Users
        """
    )
    connection.commit()
    print("DELETE OK")


def delete_all_by_userid(user_id: str) -> None:
    cursor = connection.cursor()
    cursor.execute(
        """
        DELETE FROM Users
        WHERE user_id = ?
        """,
        (user_id,),
    )
    connection.commit()
    print("DELETE OK")


def add_users(users: list[tuple]):
    cursor = connection.cursor()
    cursor.executemany(
        "INSERT INTO Users (phone, address, birthday, username, user_id) VALUES (?, ?, ?, ?, ?)",
        users,
    )
    connection.commit()


def get_users_birthday_today(user_id: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT phone, username, strftime('%d.%m.%Y', birthday) FROM users
        WHERE strftime('%m', birthday) = strftime('%m')
        AND strftime('%d', birthday) = strftime('%d')
        AND user_id = ?
        ORDER BY username
        """,
        (user_id,),
    )
    return cursor.fetchall()


def get_users_birthday_today2(user_id: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT phone, username, strftime('%d.%m.%Y', birthday) FROM users
        WHERE user_id = ?
        AND strftime('%d', birthday) = strftime('%d')
        ORDER BY username
        """,
        (user_id,),
    )
    return cursor.fetchall()


def get_users(user_id: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    )
    return cursor.fetchall()


def is_user_empty(user_id: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    )
    return False if cursor.fetchall() else True


def get_datey():
    cursor = connection.cursor()
    cursor.execute("SELECT strftime('%d')")
    return cursor.fetchall()


def add_column():
    cursor = connection.cursor()
    cursor.execute(
        """
        ALTER TABLE url_google 
        ADD COLUMN start INTEGER
        """
    )


def get_start_status(user_id: str):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT start FROM url_google
        WHERE user_id = ?
        """,
        (user_id,),
    )
    ic(user_id)
    res = cursor.fetchone()
    ic(res)
    if res:
        return True if res[0] else False
    return False


def set_start_status(user_id: str, status: int):
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE url_google SET start = ?
        WHERE user_id = ?
        """,
        (status, user_id),
    )
    connection.commit()

def get_all_users():
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM url_google
        """,
    )
    return cursor.fetchall()
