import sqlite3
from dataclasses import dataclass
from datetime import date
from icecream import ic


@dataclass
class Client:
    full_name: str
    phone: str
    address: str
    birthday: date


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


def add_user(user: Client):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO Users (username, phone, address, birthday) VALUES (?, ?, ?, ?)",
        (user.full_name, user.phone, user.address, user.birthday),
    )
    connection.commit()


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


# print(set_start_status("48339289", 1))
# start_status = get_start_status(2018452772)
# print(start_status)
# ic(is_user_empty("4834392289"))
# ic(get_users("483392289"))
# ic(get_users_birthday_today2("483392289"), "-----------------------------")
ic(get_users_ids())
# ic(is_user_in_url_google("4833922894"))
# add_column()
# print(get_users_birthday_today("483392289"))
# del_url_google("483392289")
# create_table_url_google()
# update_url_google(url_google="fdhdgh444dfhdfh", user_id="483392289")
# delete_all()
# print(get_url_google("483392289"))
# # print(split_str(IN_STR))
# # add_user(split_str(IN_STR))
# # add_1000_users()
# # delete_user("Фигулин Петр Васильевич")
# users = get_users_birthday_today()
# for i in users:
#     print(i)
# print(len(users))
# # print(get_datey())


# connection.close()
