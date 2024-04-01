import pytest
from unittest.mock import Mock

from aiogram_dialog import setup_dialogs
from aiogram_dialog.test_tools import MockMessageManager, BotClient
from aiogram_dialog.test_tools.keyboard import InlineButtonTextLocator

async def tst():
    return (
        "Привет, None!\nУкажи ссылку на google таблицу"
        " в настройках, и жми 'Включить напоминание'."
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "is_win, expected_message2",
    [
        [1, "Успех!"],
        # [2, "В другой раз повезёт!"]
    ]
)
async def test_click(dp, is_win, expected_message2):
# async def test_click(dp):
    text_user_not_in_db = (
        "Привет, None!\nУкажи ссылку на google таблицу"
        " в настройках, и жми 'Включить напоминание'."
    )
    text_user_in_db_start = (
        "Привет, None!\n"
        "Запущено оповещение по расписанию:\n- каждый день в 12-00 НСК"
    )
    text_user_in_db = "Привет, None!\n" "Оповещение по расписанию отключено!"
   
    
    is_win1 = 483392289
    expected_message = await tst()
    
    start_getter = Mock(side_effect=["username"])

    client = BotClient(dp, user_id=is_win)
    message_manager = MockMessageManager()
    setup_dialogs(dp, message_manager=message_manager)

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

#     # user_getter.assert_called_once()
# @pytest.mark.asyncio
# async def test_click2(dp):
# # async def test_click(dp):
#     text_user_not_in_db = (
#         "Привет, None!\nУкажи ссылку на google таблицу"
#         " в настройках, и жми 'Включить напоминание'."
#     )
#     text_user_in_db_start = (
#         "Привет, None!\n"
#         "Запущено оповещение по расписанию:\n- каждый день в 12-00 НСК"
#     )
#     text_user_in_db = "Привет, None!\n" "Оповещение по расписанию отключено!"
   
    
#     is_win1 = 483392289
#     expected_message = await tst()
    
#     start_getter = Mock(side_effect=["username"])

#     client = BotClient(dp, user_id=1)
#     message_manager = MockMessageManager()
#     setup_dialogs(dp, message_manager=message_manager)

#     client = BotClient(dp, user_id=2)
#     message_manager = MockMessageManager()
#     setup_dialogs(dp, message_manager=message_manager)

#     # start
#     await client.send("/start")
#     first_message = message_manager.one_message()
#     start_getter.assert_not_called()

#     assert first_message.text == expected_message
#     assert first_message.reply_markup
#     start_getter.assert_not_called()

#     # redraw
#     message_manager.reset_history()
#     await client.send("whatever")

#     first_message = message_manager.one_message()
#     assert first_message.text == expected_message

#     # click next
#     message_manager.reset_history()
#     callback_id = await client.click(
#         first_message,
#         InlineButtonTextLocator("Настройки"),
#     )

#     message_manager.assert_answered(callback_id)
#     # usecase.assert_called()
#     second_message = message_manager.one_message()
#     print(second_message.text)
#     assert second_message.text == "Настройки."
#     assert second_message.reply_markup.inline_keyboard

#     callback_id = await client.click(
#         second_message,
#         InlineButtonTextLocator("Назад"),
#     )
#     message_manager.assert_answered(callback_id)
#     third_message = message_manager.last_message()
#     assert third_message.text == expected_message
#     assert third_message.reply_markup