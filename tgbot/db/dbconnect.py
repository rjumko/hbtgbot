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
