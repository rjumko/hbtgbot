import tgbot.apsched
from datetime import datetime

def sched_add_cron(apscheduler, user_id):
    apscheduler.add_job(
            tgbot.apsched.send_message_cron,
            trigger="cron",
            hour=12,
            minute=0,
            # second=30,
            start_date=datetime.strptime("02.02.1978", "%d.%m.%Y"),
            id=user_id,
            kwargs={"user_id": user_id},
        )
