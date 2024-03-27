import logging
import os
import asyncpg
import asyncio
from environs import Env
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from copy_scheduler.utils import copy_data_from_table
from copy_scheduler.dbconnect import Request


async def copy_data_from_google_table(db: Request):
    lst = await db.get_users_urls()

    for l in lst:
        await copy_data_from_table(db, l[0])


async def jobs(db: Request):
    await copy_data_from_google_table(db)


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
    env = Env()
    env.read_env()
    pool_connect = await db_pool(env)
    db = Request(pool_connect)
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] #%(levelname)-8s %(filename)s:"
        "%(lineno)d - %(name)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S %p %Z",
    )
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(jobs, "interval", seconds=300, kwargs={"db": db})
    scheduler.start()
    logging.info(os.getcwd())
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
