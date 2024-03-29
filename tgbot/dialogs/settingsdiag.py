from aiogram.types import Message, User, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import MessageInput, TextInput, ManagedTextInput
from tgbot.utils import copy_data_from_table
from tgbot.db.dbconnect import Request
import tgbot.states


async def go_start(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.start(
        state=tgbot.states.StartSG.start,
        mode=StartMode.RESET_STACK,
        data={"user_id": callback.from_user.id},
    )


async def settings_getter(
    dialog_manager: DialogManager, event_from_user: User, **kwargs
):
    if dialog_manager.start_data:
        getter_data = {"first_show": True}
        dialog_manager.start_data.clear()
    else:
        getter_data = {
            "copy_status": dialog_manager.dialog_data.get("copy_status"),
            "first_show": False,
        }
    return getter_data


async def change_url(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.switch_to(state=tgbot.states.SettingSG.url_copy)
    dialog_manager.dialog_data.update(
        copy_status="Ссылка изменилась.\nКопирование выполнено"
    )


async def cancel(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    await dialog_manager.switch_to(state=tgbot.states.SettingSG.start)


def url_check(url: str) -> str:
    if len(url.split("/")) > 6 and url.startswith(
        "https://docs.google.com/spreadsheets/d/"
    ):
        return url
    raise ValueError


# Хэндлер, который сработает, если пользователь ввел корректный возраст
async def correct_age_handler(
    message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str
) -> None:
    request: Request = dialog_manager.middleware_data["request"]
    await request.update_google_url(google_url=message.text, user_id=message.from_user.id)
    await copy_data_from_table(request, message.from_user.id)
    await dialog_manager.switch_to(state=tgbot.states.SettingSG.start)


# Хэндлер, который сработает на ввод некорректного возраста
async def error_age_handler(
    message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str
):
    await message.answer(text="Ты ввел некорректную ссылку, попробуй еще раз.")


settings_dialog = Dialog(
    Window(
        Format("Настройки.\n{copy_status}", when="copy_status"),
        Format("Настройки.", when="first_show"),
        Button(
            text=Const("Изменить ссылку на google sheet"),
            id="change_url",
            on_click=change_url,
        ),
        Button(text=Const("Назад"), id="start_timer", on_click=go_start),
        getter=settings_getter,
        state=tgbot.states.SettingSG.start,
    ),
    Window(
        Const(text="Скопируй сюда адрес гугл таблицы:"),
        TextInput(
            id="age_input",
            type_factory=url_check,
            on_success=correct_age_handler,
            on_error=error_age_handler,
        ),
        Button(text=Const("Отмена"), id="start_timer", on_click=cancel),
        state=tgbot.states.SettingSG.url_copy,
    ),
)
