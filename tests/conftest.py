import pytest
import pytest_asyncio
from unittest.mock import Mock

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.handlers import get_routers
from tests.mocked_aiogram import MockedBot, MockedSession

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from tgbot.handlers import get_routers
from tgbot.dialogs.startdiag import start_dialog
from tgbot.dialogs.settingsdiag import settings_dialog
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


@pytest_asyncio.fixture(scope="session")
async def dp() -> Dispatcher:
    # apscheduler = Mock()
    # request = Mock()
    dp = Dispatcher(
        # request=request,
        # usecase=usecase,
        # start_getter=start_getter,
        storage=MemoryStorage(),
    )
    
    dp.include_router(*get_routers())
    dp.include_router(start_dialog)
    dp.include_router(settings_dialog)
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Asia/Novosibirsk"))
    # scheduler.ctx.add_instance(bot, declared_class=Bot)
    dp.update.middleware.register(scheduler)
    
    # dispatcher = Dispatcher(storage=MemoryStorage())
    # dispatcher.include_routers(*get_routers())
    return dp

@pytest.fixture(scope="session")
def bot() -> MockedBot:
    bot = MockedBot()
    bot.session = MockedSession()
    return bot