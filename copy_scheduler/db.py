import sqlite3
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s',
           )
logging.getLogger(__name__).setLevel(logging.DEBUG)

DB_URI = "my_database.sqlite"

def add_users(users: list[tuple]):
    connection = sqlite3.connect(DB_URI)
    cursor = connection.cursor()
    cursor.executemany(
        "INSERT INTO Users (phone, address, birthday, username, user_id) VALUES (?, ?, ?, ?, ?)",
        users,
    )
    connection.commit()
    connection.close()


def get_all_data():
    connection = sqlite3.connect(DB_URI)
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM Users
        """
    )
    return cursor.fetchall()


def get_users_urls():
    connection = sqlite3.connect(DB_URI)
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT user_id, url_google FROM url_google
        """
    )
    return cursor.fetchall()


def delete_all_by_userid(user_id: str) -> None:
    connection = sqlite3.connect(DB_URI)
    cursor = connection.cursor()
    cursor.execute(
        """
        DELETE FROM Users
        WHERE user_id = ?
        """,
        (user_id,),
    )
    connection.commit()
    connection.close()
    logging.info("DELETE OK")

def get_url_google(user_id: str):
    connection = sqlite3.connect(DB_URI)
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT url_google FROM url_google
        WHERE user_id=?;
        """,
        (user_id,),
    )
    res = cursor.fetchone()
    logging.info(user_id)
    logging.info(res)
    if res:
        return res[0]
    return None

