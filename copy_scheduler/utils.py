from datetime import datetime
from icecream import ic
import pandas as pd
import logging
from copy_scheduler.db import get_url_google, delete_all_by_userid, add_users

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s',
           )
logging.getLogger(__name__).setLevel(logging.DEBUG)


def get_sheet_id(url: str) -> str:
    return "Неверный URL" if len(url.split("/")) < 7 else url.split("/")[5]


def get_table_from_google(url: str, user_id: str) -> list[tuple]:
    sheet_id = get_sheet_id(url)
    df = pd.read_csv(
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
        header=0,
    ).values.tolist()
    lst = list(tuple(sub) for sub in df)
    logging.info(lst)
    return [
        (l[0], l[1], datetime.strptime(l[2].strip(), "%d.%m.%Y"), l[3], user_id)
        for l in lst
    ]


def copy_data_from_table(usr_id: str):
    url = get_url_google(usr_id)
    if url:
        logging.info(usr_id)
        logging.info(url)
        delete_all_by_userid(usr_id)
        add_users(
            get_table_from_google(
                url,
                usr_id,
            )
        )
        return True
    return False
