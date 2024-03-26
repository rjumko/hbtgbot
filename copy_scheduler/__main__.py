import logging
import os
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
from copy_scheduler.utils import copy_data_from_table
from copy_scheduler.db import get_users_urls



def copy_data_from_google_table():
    lst = get_users_urls()

    for l in lst:
        copy_data_from_table(l[0])

def jobs():
    copy_data_from_google_table()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s',
        datefmt="%d/%m/%Y %H:%M:%S %p %Z",
           )
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    scheduler = BackgroundScheduler()
    scheduler.add_job(jobs, 'interval', seconds=300)
    scheduler.start()
    logging.info(os.getcwd())
    while True:
        sleep(1)
