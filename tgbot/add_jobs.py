import tgbot.apsched
from datetime import datetime


def sched_add_cron(apscheduler, user_id, request):
    apscheduler.add_job(
        tgbot.apsched.send_message_cron2,
        trigger="cron",
        hour=12,
        minute=0,
        # second=30,
        start_date=datetime.strptime("02.02.1978", "%d.%m.%Y"),
        id=str(user_id),
        kwargs={"user_id": user_id, "request": request},
    )

def sched_add_interval(apscheduler, user_id, request):
    apscheduler.add_job(
        tgbot.apsched.send_message_cron2,
        trigger="interval",
        # hour=12,
        # minute=0,
        seconds=10,
        start_date=datetime.strptime("02.02.1978", "%d.%m.%Y"),
        id=str(user_id),
        kwargs={"user_id": user_id, "request": request},
    )
