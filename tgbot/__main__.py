import asyncio
import logging
from icecream import ic
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
from environs import Env
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator
from tgbot.dialogs.settingsdiag import settings_dialog
from tgbot.dialogs.startdiag import start_dialog
from tgbot.middleware.scheduler import SchedulerMiddleware
from tgbot.middleware.dbmiddleware import DbSession
from tgbot.db.dbconnect import Request
from tgbot.add_jobs import sched_add_cron, sched_add_interval
import asyncpg
import tgbot.states


logger = logging.getLogger(__name__)


async def command_start_process(
    message: Message, dialog_manager: DialogManager, request: Request
):
    ic("ADD NEW USER")
    ic(message.from_user.id)
    if not await request.is_user_in_url_google(message.from_user.id):
        await request.add_user(message.from_user.id)
    if await request.get_google_url(message.from_user.id):
        data = {"first_show": False}
    else:
        data = {"first_show": True}
    await dialog_manager.start(
        state=tgbot.states.StartSG.start, mode=StartMode.RESET_STACK, data=data
    )


async def db_pool(env: Env):
    return await asyncpg.create_pool(
        user=env("DB__USER"),
        password=env("DB__PASSWORD"),
        database=env("DB__NAME"),
        host=env("DB__HOST"),
        port=env("DB__PORT"),
        command_timeout=60,
    )


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S %p %Z",
    )
    logger.debug("-----------------Starting bot-------------------------")
    env = Env()
    env.read_env()

    BOT_TOKEN = env("BOT_TOKEN")

    pool_connect = await db_pool(env)
    request = Request(pool_connect)
    await request.create_users_table()
    await request.create_clients_table()

    bot = Bot(token=BOT_TOKEN)

    redis = Redis(host=env("REDIS__HOST"))
    storage = RedisStorage(
        redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True)
    )
    dp = Dispatcher(storage=storage)
    jobstores = {
        "default": RedisJobStore(
            jobs_key="dispatched_trips_jobs",
            run_times_key="dispatched_trips_running",
            host=env("REDIS__HOST"),
            db=2,
        )
    }
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Asia/Novosibirsk"))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(DbSession(pool_connect))
    dp.include_router(start_dialog)
    dp.include_router(settings_dialog)
    dp.message.register(command_start_process, CommandStart())
    setup_dialogs(dp)
    scheduler.start()

    lst = await request.get_users_id_status()
    for l in lst:
        logger.debug(f"{l[0]}, {l[1]}")
        if l[1]:
            if env.bool("DEV"):
                sched_add_interval(scheduler, l[0], request)
            else:
                sched_add_cron(scheduler, l[0], request)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
