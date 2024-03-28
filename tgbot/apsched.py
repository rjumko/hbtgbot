from aiogram import Bot
import logging
from tgbot.utils import prep_hb_text
from tgbot.db.dbconnect import Request
from aiogram.exceptions import TelegramForbiddenError
from apscheduler_di import ContextSchedulerDecorator


logger = logging.getLogger(__name__)


async def send_message_cron2(
    bot: Bot, user_id: int, request: Request, apscheduler: ContextSchedulerDecorator
):
    logger.info(user_id)
    lst = await request.get_clients_birthday_today(user_id=user_id)
    logger.info(lst)
    try:
        await bot.send_message(user_id, prep_hb_text(lst), parse_mode="HTML")
    except TelegramForbiddenError:
        await request.set_start_status(user_id, False)
        apscheduler.pause_job(str(user_id))
