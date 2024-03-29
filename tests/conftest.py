import pytest

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.handlers import get_routers
from tests.mocked_aiogram import MockedBot, MockedSession

async def db_pool(env: Env):
    return await asyncpg.create_pool(
        user=env("DB__USER"),
        password=env("DB__PASSWORD"),
        database=env("DB__NAME"),
        host=env("DB__HOST"),
        port=env("DB__PORT"),
        command_timeout=60,
    )

@pytest.fixture(scope="session")
def dp() -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.update.middleware.register(DbSession(pool_connect))
    dispatcher.include_routers(*get_routers())
    return dispatcher

@pytest.fixture(scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot