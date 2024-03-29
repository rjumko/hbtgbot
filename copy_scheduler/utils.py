from datetime import datetime
import pandas as pd
import logging
from copy_scheduler.dbconnect import Request

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s',
           )
logging.getLogger(__name__).setLevel(logging.DEBUG)


async def get_sheet_id(url: str) -> str:
    return "Неверный URL" if len(url.split("/")) < 7 else url.split("/")[5]


async def get_table_from_google(url: str, user_id: int) -> list[tuple]:
    sheet_id = await get_sheet_id(url)
    df = pd.read_csv(
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
        header=0,
    ).values.tolist()
    lst = list(tuple(sub) for sub in df)
    logging.info(lst)
    return [
        (str(l[0]), l[1], datetime.strptime(l[2].strip(), "%d.%m.%Y"), l[3], user_id)
        for l in lst
    ]


async def copy_data_from_table(db: Request, usr_id: int, backup: bool=False):
    url = await db.get_url_google(usr_id)
    if url:
        logging.info(usr_id)
        logging.info(url)
        if not backup:
            await db.delete_all_by_userid(usr_id)
        await db.add_clients(
            await get_table_from_google(
                url,
                usr_id,
            )
        )
        return True
    return False
