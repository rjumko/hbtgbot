import logging
from icecream import ic
from aiogram.types import User, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Checkbox, ManagedCheckbox, Back
from environs import Env
import tgbot.states
import tgbot.apsched
from tgbot.utils import prep_hb_text
from tgbot.db.dbconnect import Request
from tgbot.add_jobs import sched_add_cron, sched_add_interval


logger = logging.getLogger(__name__)


async def start_getter(
    dialog_manager: DialogManager, event_from_user: User, **kwargs
):  # -> dict[str, Any]:
    request: Request = dialog_manager.middleware_data["request"]
    user_id = event_from_user.id
    if await request.get_google_url(user_id):
        first_show = False
        show_start_scheduler = True
    else:
        first_show = True
        show_start_scheduler = False
    user_empty = await request.is_clients_empty(user_id)
    scheduler_start = dialog_manager.find("checkbox").is_checked()
    return {
        "username": event_from_user.username,
        "first_show": first_show,
        "start_status": await request.get_start_status(user_id),
        "show_start_scheduler": show_start_scheduler,
        "user_empty": user_empty,
        "scheduler_start": scheduler_start,
        "not_scheduler_start": not scheduler_start and not first_show,
        "not_user_empty": not user_empty,
    }


async def on_start(data, dialog_manager: DialogManager):
    user_id = data["user_id"]
    request: Request = dialog_manager.middleware_data["request"]
    start_status = await request.get_start_status(user_id)
    logger.info(start_status)
    await dialog_manager.find("checkbox").set_checked(checked=start_status)


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
    request: Request = dialog_manager.middleware_data["request"]
    user_id = callback.from_user.id
    txt = prep_hb_text(await request.get_clients_birthday_today(user_id))
    dialog_manager.dialog_data.update(hb_today_text=txt)
    await dialog_manager.switch_to(state=tgbot.states.StartSG.hb_today)



async def checkbox_scheduler(
    callback: CallbackQuery,
    checkbox: ManagedCheckbox,
    dialog_manager: DialogManager,
):
    env = Env()
    env.read_env()
    logger.info(checkbox.is_checked())
    user_id = callback.from_user.id
    apscheduler = dialog_manager.middleware_data["apscheduler"]
    request: Request = dialog_manager.middleware_data["request"]
    job_id = str(user_id)
    logger.info(job_id)
    logger.info(apscheduler.get_job(job_id))
    if checkbox.is_checked():
        if apscheduler.get_job(job_id):
            apscheduler.resume_job(job_id)
            logger.debug(f"Job resume: {apscheduler.get_job(job_id)}")
            await request.set_start_status(user_id, True)
        else:
            # if env.bool("DEV"):
            #     sched_add_interval(
            #         user_id=user_id, request=request, apscheduler=apscheduler
            #     )
            # else:
            #     sched_add_cron(
            #         user_id=user_id, request=request, apscheduler=apscheduler
            #     )
            # logger.debug(f"Job add: {apscheduler.get_job(job_id)}")
            await request.set_start_status(user_id, True)
    else:
        if apscheduler.get_job(job_id):
            apscheduler.pause_job(job_id)
            logger.debug(f"Job pause: {apscheduler.get_job(job_id)}")
            await request.set_start_status(user_id, False)
    dialog_manager.dialog_data.update(is_checked=checkbox.is_checked())


start_dialog = Dialog(
    Window(
        Format("Привет, {username}!"),
        # Format(
        #     text='<code>Это моноширинный текст</code>',
        # ),
        Format(
            "Укажи ссылку на google таблицу в настройках, и жми 'Включить напоминание'.",
            when="first_show",
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
            # default="start_status",
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
    on_start=on_start,
)
