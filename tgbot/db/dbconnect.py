import asyncpg
import logging


class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector
        self.logger = logging.getLogger(__name__)

    async def add_data(self, user_id, user_name):
        await self.connector.execute(
            """
            INSERT INTO datausers (user_id, user_name) VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET user_name=$2;
            """,
            user_id,
            user_name,
        )
        self.logger.info(f"User {user_id} add in BD")

    async def create_clients_table(self):
        await self.connector.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                client_id SERIAL PRIMARY KEY,
                phone VARCHAR(50),
                address VARCHAR(500),
                birthday date,
                client_name VARCHAR(500),
                user_id BIGINT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users (user_id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )
            """
        )
        self.logger.info(f"User add in BD")

    async def create_users_table(self):
        await self.connector.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                google_url VARCHAR(500),
                start_schedul BOOL
            )
            """
        )
        self.logger.info(f"User add in BD")

    async def is_user_in_url_google(self, user_id: int):
        row = await self.connector.fetchval(
            """
            SELECT * FROM users
            WHERE user_id=$1;
            """,
            user_id,
        )
        return True if row else False

    async def add_user(self, user_id: int):
        await self.connector.execute(
            """
            INSERT INTO users (user_id, google_url, start_schedul) VALUES ($1, Null, false)
            ON CONFLICT DO NOTHING
            """,
            user_id,
        )

    async def get_google_url(self, user_id: int):
        row = await self.connector.fetchrow(
            """
            SELECT google_url FROM users
            WHERE user_id=$1;
            """,
            user_id,
        )
        return row.get("google_url", None) if row else None

    async def update_google_url(self, google_url: str, user_id: int) -> None:
        await self.connector.execute(
            """
            INSERT INTO users (user_id, google_url, start_schedul) VALUES($1, $2, false)
            ON CONFLICT(user_id) DO UPDATE SET google_url=$2;
            """,
            user_id,
            google_url,
        )

    async def get_start_status(self, user_id: int) -> bool | None:
        row = await self.connector.fetchrow(
            """
            SELECT start_schedul FROM users
            WHERE user_id = $1
            """,
            user_id,
        )
        return row.get("start_schedul") if row else None
    
    async def get_users_id_status(self):
        row = await self.connector.fetch(
            """
            SELECT user_id, start_schedul FROM users
            """,
        )
        return row if row else None

    async def set_start_status(self, user_id: int, start_schedul: bool):
        await self.connector.execute(
            """
            UPDATE users SET start_schedul = $1
            WHERE user_id = $2
            """,
            start_schedul, 
            user_id,
        )

    async def is_clients_empty(self, user_id: int) -> bool:
        row = await self.connector.fetchrow(
            """
            SELECT * FROM clients
            WHERE user_id = $1
            """,
            user_id,
        )
        return False if row else True
    
    async def get_clients_birthday_today(self, user_id: int):
        rows = await self.connector.fetch(
            """
            SELECT phone, client_name, birthday FROM clients
            WHERE date_part('month', birthday) = date_part('month', CURRENT_DATE)
            AND date_part('day', birthday) = date_part('day', CURRENT_DATE)
            AND user_id = $1
            ORDER BY client_name
            """,
            user_id,
        )
        return rows
    
    async def delete_all_by_userid(self, user_id: int) -> None:
        await self.connector.execute(
            """
            DELETE FROM clients
            WHERE user_id = $1
            """,
            user_id,
        )


    async def add_clients(self, clients: list[tuple]):
        await self.connector.executemany(
            "INSERT INTO clients (phone, address, birthday, client_name, user_id) VALUES ($1, $2, $3, $4, $5)",
            clients,
        )

    async def add_users(self, users: list[tuple]):
        await self.connector.executemany(
            """
            INSERT INTO users (user_id, google_url, start_schedul) VALUES($1, $2, $3)
            ON CONFLICT(user_id) DO NOTHING;
            """,
            users
        )

    async def delete_all_users(self):
        await self.connector.execute(
            """
            DELETE FROM users
            """,
        )