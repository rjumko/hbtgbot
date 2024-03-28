from icecream import ic
from aiogram import Bot
import logging
from tgbot.utils import prep_hb_text
from tgbot.db.dbconnect import Request

logger = logging.getLogger(__name__)

async def send_message_cron(bot: Bot, user_id):
    logger.info(user_id)
    lst = get_users_birthday_today(user_id=user_id)
    logger.info(lst)
    await bot.send_message(user_id, prep_hb_text(lst), parse_mode="HTML")

async def send_message_cron2(bot: Bot, user_id: int, request: Request):
    logger.info(user_id)
    lst = await request.get_clients_birthday_today(user_id=user_id)
    logger.info(lst)
    await bot.send_message(user_id, prep_hb_text(lst), parse_mode="HTML")
