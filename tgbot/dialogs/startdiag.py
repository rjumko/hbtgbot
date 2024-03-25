from datetime import datetime
from icecream import ic
from aiogram.types import User, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Checkbox, ManagedCheckbox, Back
from environs import Env
import tgbot.states
import tgbot.apsched
from tgbot.utils import prep_hb_text
from tgbot.db.db import (
    get_url_google,
    get_start_status,
    set_start_status,
    is_user_empty,
    get_users_birthday_today,
)


async def start_getter(
    dialog_manager: DialogManager, event_from_user: User, **kwargs
):  # -> dict[str, Any]:
    user_id = str(event_from_user.id)
    start_status = get_start_status(user_id)
    ic(user_id, start_status)
    await dialog_manager.find("checkbox").set_checked(checked=start_status)
    if get_url_google(user_id):
        ic()
        first_show = False
        show_start_scheduler = True
    else:
        ic()
        first_show = True
        show_start_scheduler = False
    user_empty = is_user_empty(user_id)
    scheduler_start = dialog_manager.find("checkbox").is_checked()
    return {
        "username": event_from_user.username,
        "first_show": first_show,
        "start_status": get_start_status(user_id),
        "show_start_scheduler": show_start_scheduler,
        "user_empty": user_empty,
        "scheduler_start": scheduler_start,
        "not_scheduler_start": not scheduler_start,
        "not_user_empty": not user_empty,
    }


async def hb_today_getter(
    dialog_manager: DialogManager, event_from_user: User, **kwargs
):  # -> dict[str, Any]:
    return {
        "hb_today_text": dialog_manager.dialog_data.get("hb_today_text"),
    }


async def button_settings(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    await dialog_manager.start(
        state=tgbot.states.SettingSG.start, data={"first_show": True}
    )


async def hb_today(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    user_id = str(callback.from_user.id)
    ic(user_id, "----------------hb_today")
    txt = prep_hb_text(get_users_birthday_today(user_id))
    dialog_manager.dialog_data.update(hb_today_text=txt)
    await dialog_manager.switch_to(state=tgbot.states.StartSG.hb_today)


def sched_add_cron(apscheduler, user_id):
    apscheduler.add_job(
        tgbot.apsched.send_message_cron,
        trigger="cron",
        hour=12,
        minute=0,
        # second=30,
        start_date=datetime.strptime("02.02.1978", "%d.%m.%Y"),
        id=user_id,
        kwargs={"user_id": user_id},
    )


def sched_add_interval(apscheduler, user_id):
    apscheduler.add_job(
        tgbot.apsched.send_message_cron,
        trigger="interval",
        # hour=12,
        # minute=0,
        seconds=10,
        start_date=datetime.strptime("02.02.1978", "%d.%m.%Y"),
        id=user_id,
        kwargs={"user_id": user_id},
    )


async def checkbox_scheduler(
    callback: CallbackQuery,
    checkbox: ManagedCheckbox,
    dialog_manager: DialogManager,
):
    env = Env()
    env.read_env()
    user_id = str(callback.from_user.id)
    apscheduler = dialog_manager.middleware_data["apscheduler"]
    if apscheduler.get_job(user_id):
        if checkbox.is_checked():
            apscheduler.resume_job(user_id)
            ic(user_id)
            ic(apscheduler.get_job(user_id).next_run_time)
            set_start_status(user_id, 1)
        else:
            apscheduler.pause_job(user_id)
            ic(user_id)
            ic(apscheduler.get_job(user_id).next_run_time)
            set_start_status(user_id, 0)
    else:
        if env.bool("DEV"):
            ic("DEV - TRUE")
            sched_add_interval(apscheduler, user_id)
        else:
            ic("DEV - FALSE")
            sched_add_cron(apscheduler, user_id)

        ic("-------ADD------------\n", apscheduler.get_job(user_id).next_run_time)
        ic(user_id)
        set_start_status(user_id, 1)
    dialog_manager.dialog_data.update(is_checked=checkbox.is_checked())


start_dialog = Dialog(
    Window(
        Format("Привет, {username}!"),
        # Format(
        #     text='<code>Это моноширинный текст</code>',
        # ),
        Format(
            "Укажи ссылку на google таблицу в настройках, скопируй данные из таблицы, и жми 'Включить напоминание'.",
            when="first_show",
        ),
        Format(
            "Скопируй данные из таблицы из google таблицы в настройках.",
            when="user_empty",
        ),
        Format(
            "Запущено оповещение по расписанию:\n- каждый день в 12-00 НСК",
            when="scheduler_start",
        ),
        Format(
            "Оповещение по расписанию отключено!",
            when="not_scheduler_start",
        ),
        Checkbox(
            checked_text=Const("[✔️] Включить напоминание"),
            unchecked_text=Const("[    ] Включить напоминание"),
            id="checkbox",
            on_state_changed=checkbox_scheduler,
            when="show_start_scheduler",
        ),
        Button(
            text=Const("Сегодня ДР"),
            id="hb_today",
            on_click=hb_today,
            when="not_user_empty",
        ),
        Button(text=Const("Настройки"), id="settings", on_click=button_settings),
        getter=start_getter,
        state=tgbot.states.StartSG.start,
        parse_mode="HTML",
    ),
    Window(
        Format(
            "{hb_today_text}",
        ),
        Back(Const("Назад"), id="back"),
        state=tgbot.states.StartSG.hb_today,
        getter=hb_today_getter,
        parse_mode="HTML",
    ),
)
