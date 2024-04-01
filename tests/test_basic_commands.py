from unittest.mock import Mock

from aiogram_dialog import setup_dialogs
from aiogram_dialog.test_tools import MockMessageManager
import asyncpg
from environs import Env

import pytest

from aiogram_dialog.test_tools import BotClient
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator
from tgbot.middleware.dbmiddleware import DbSession


async def db_pool():
    env = Env()
    env.read_env()
    return await asyncpg.create_pool(
        user=env("DB__USER"),
        password=env("DB__PASSWORD"),
        database=env("DB__NAME"),
        host=env("DB__HOST"),
        port=env("DB__PORT"),
        command_timeout=60,
    )



@pytest.mark.asyncio
# @pytest.mark.parametrize(
#     "is_win, expected_message",
#     [
#         [
#             1,
#             "Привет, None!\nУкажи ссылку на google таблицу в настройках, и жми 'Включить напоминание'.",
#         ],
#         [483392289, "Привет, None!\n" "Оповещение по расписанию отключено!"],
#     ],
# )
# async def test_click(dp, is_win: int, expected_message: str):
async def test_click(dp):
    text_user_not_in_db = (
        "Привет, None!\nУкажи ссылку на google таблицу"
        " в настройках, и жми 'Включить напоминание'."
    )
    text_user_in_db_start = (
        "Привет, None!\n"
        "Запущено оповещение по расписанию:\n- каждый день в 12-00 НСК"
    )
    text_user_in_db = "Привет, None!\n" "Оповещение по расписанию отключено!"
   
    
    dp.update.middleware.register(DbSession(db_pool()))

    
    is_win = 483392289
    expected_message = text_user_in_db
    
    usecase = Mock()
    start_getter = Mock(side_effect=["username"])
    # dp = Dispatcher(
    #     usecase=usecase,
    #     start_getter=start_getter,
    #     storage=MemoryStorage(),
    # )
    # dp.include_router(*get_routers())
    # dp.include_router(start_dialog)
    # dp.include_router(settings_dialog)
    # scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Asia/Novosibirsk"))
    # # scheduler.ctx.add_instance(bot, declared_class=Bot)
    # dp.update.middleware.register(SchedulerMiddleware(scheduler))
    # dp.update.middleware.register(DbSession(pool_connect))

    client = BotClient(dp, user_id=is_win)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

    # start
    await client.send("/start")
    first_message = message_manager.one_message()
    start_getter.assert_not_called()

    assert first_message.text == expected_message
    assert first_message.reply_markup
    start_getter.assert_not_called()

    # redraw
    message_manager.reset_history()
    await client.send("whatever")

    first_message = message_manager.one_message()
    assert first_message.text == expected_message

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
    assert third_message.text == expected_message
    assert third_message.reply_markup

    # user_getter.assert_called_once()
