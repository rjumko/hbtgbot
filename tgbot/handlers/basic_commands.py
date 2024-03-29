from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from tgbot.db.dbconnect import Request
import tgbot.states

router = Router(name="Basic Commands Router")


@router.message(CommandStart())
async def cmd_start(message: Message, dialog_manager: DialogManager, request: Request):
    if not await request.is_user_in_url_google(message.from_user.id):
        await request.add_user(message.from_user.id)
    if await request.get_google_url(message.from_user.id):
        data = {"first_show": False, "user_id": message.from_user.id}
    else:
        data = {"first_show": True, "user_id": message.from_user.id}
    await dialog_manager.start(
        state=tgbot.states.StartSG.start, mode=StartMode.RESET_STACK, data=data
    )
