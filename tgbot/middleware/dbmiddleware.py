from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
import asyncpg

# from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types.base import TelegramObject
from apscheduler_di import ContextSchedulerDecorator
from tgbot.db.dbconnect import Request


class DbSession(BaseMiddleware):

    def __init__(self, connector: asyncpg.pool.Pool):
        super().__init__()
        self.connector = connector

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        async with self.connector.acquire() as connect:
            data['request'] = Request(connect)
            return await handler(event, data)
