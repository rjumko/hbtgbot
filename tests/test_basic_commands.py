from unittest.mock import Mock

from environs import Env
import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs
from aiogram_dialog.test_tools import BotClient, MockMessageManager
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator
from tgbot.handlers import get_routers
from tgbot.dialogs.startdiag import start_dialog
from tgbot.dialogs.settingsdiag import settings_dialog
from tgbot.middleware.dbmiddleware import DbSession
from tgbot.middleware.scheduler import SchedulerMiddleware


async def db_pool(env: Env):
    return await asyncpg.create_pool(
        user=env("DB__USER"),
        password=env("DB__PASSWORD"),
        database=env("DB__NAME"),
        host=env("DB__HOST"),
        port=env("DB__PORT"),
        command_timeout=60,
    )


@pytest.mark.asyncio
async def test_click():
    env = Env()
    env.read_env()
    pool_connect = await db_pool(env)
    usecase = Mock()
    start_getter = Mock(side_effect=["username"])
    dp = Dispatcher(
        usecase=usecase,
        start_getter=start_getter,
        storage=MemoryStorage(),
    )
    dp.include_router(*get_routers())
    dp.include_router(start_dialog)
    dp.include_router(settings_dialog)
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Asia/Novosibirsk"))
    # scheduler.ctx.add_instance(bot, declared_class=Bot)
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(DbSession(pool_connect))

    client = BotClient(dp)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

    # start
    await client.send("/start")
    first_message = message_manager.one_message()
    start_getter.assert_not_called()

    assert (
        first_message.text
        == "Привет, None!\nУкажи ссылку на google таблицу"
        " в настройках, и жми 'Включить напоминание'."
    )
    assert first_message.reply_markup
    start_getter.assert_not_called()

    # redraw
    message_manager.reset_history()
    await client.send("whatever")

    first_message = message_manager.one_message()
    assert (
        first_message.text
        == "Привет, None!\nУкажи ссылку на google таблицу"
        " в настройках, и жми 'Включить напоминание'."
    )

    # click next
    message_manager.reset_history()
    callback_id = await client.click(
        first_message,
        InlineButtonTextLocator("Настройки"),
    )

    message_manager.assert_answered(callback_id)
    # usecase.assert_called()
    second_message = message_manager.one_message()
    print(second_message.text)
    assert second_message.text == "Настройки."
    assert second_message.reply_markup.inline_keyboard

    callback_id = await client.click(
        second_message,
        InlineButtonTextLocator("Назад"),
    )
    message_manager.assert_answered(callback_id)
    third_message = message_manager.last_message()
    assert (
        third_message.text
        == "Привет, None!\nУкажи ссылку на google таблицу"
        " в настройках, и жми 'Включить напоминание'."
    )
    assert third_message.reply_markup

    # user_getter.assert_called_once()
