from datetime import datetime
from icecream import ic
import pandas as pd
from tgbot.db.db import get_url_google, delete_all_by_userid, add_users


def get_sheet_id(url: str) -> str:
    return "Неверный URL" if len(url.split("/")) < 7 else url.split("/")[5]


def get_table_from_google(url: str, user_id: str) -> list[tuple]:
    sheet_id = get_sheet_id(url)
    df = pd.read_csv(
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
        header=0,
    ).values.tolist()
    lst = list(tuple(sub) for sub in df)
    print(lst)
    return [
        (l[0], l[1], datetime.strptime(l[2].strip(), "%d.%m.%Y"), l[3], user_id)
        for l in lst
    ]

def get_table_from_google2(url: str, user_id: int) -> list[tuple]:
    sheet_id = get_sheet_id(url)
    df = pd.read_csv(
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
        header=0,
    )
    df = df.fillna("").values.tolist()
    lst = list(tuple(sub) for sub in df)
    for sub in df:
        print(str(sub[0]))
    # print(lst)
    return [
        (str(l[0]), l[1], datetime.strptime(l[2].strip(), "%d.%m.%Y"), l[3], user_id)
        for l in lst
    ]

def prep_hb_text(lst: list):
    if lst:
        ic("День рождения у")
        text = "День рождения у:\n"
        for l in lst:
            text += f"<b><code>{l[0]}</code></b>, {l[1]}, {l[2]}\n"
        return text  # "День рождения у:\n" + "\n".join(", ".join(l) for l in lst)
    return "Нет день рождений"


def copy_data_from_table(usr_id: str):
    url = get_url_google(usr_id)
    if url:
        ic(usr_id, url)
        delete_all_by_userid(usr_id)
        add_users(
            get_table_from_google(
                url,
                usr_id,
            )
        )
        return True
    return False


# ic(prep_hb_text(["sdfds", "rtytrytr"]))
