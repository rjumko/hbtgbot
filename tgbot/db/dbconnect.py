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
                client_id BIGINT PRIMARY KEY,
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
