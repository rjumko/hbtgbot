import pytest
import pytest_asyncio
import asyncpg
from environs import Env

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tests.mocked_aiogram import MockedBot, MockedSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from tgbot.handlers import get_routers
from tgbot.dialogs.startdiag import start_dialog
from tgbot.dialogs.settingsdiag import settings_dialog
from tgbot.db.dbconnect import Request
from tgbot.handlers import get_routers

@pytest_asyncio.fixture(autouse = True, scope="function")
async def db_pool():
    env = Env()
    env.read_env()
    ret = await asyncpg.create_pool(
        user=env("DB__USER"),
        password=env("DB__PASSWORD"),
        database=env("DB__NAME"),
        host=env("DB__HOST"),
        port=env("DB__PORT"),
        command_timeout=60,
    )
    return Request(ret)

@pytest_asyncio.fixture(scope="function")
async def dp(db_pool) -> Dispatcher:
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Asia/Novosibirsk"))
    dp = Dispatcher(
        apscheduler=scheduler,
        request=db_pool,
        storage=MemoryStorage(),
    )
    dp.include_router(*get_routers())
    dp.include_router(start_dialog)
    dp.include_router(settings_dialog)
    return dp

@pytest.fixture(scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot