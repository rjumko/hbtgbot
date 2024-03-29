import tgbot.apsched
import logging
from datetime import datetime
from tgbot.db.dbconnect import Request
from apscheduler_di import ContextSchedulerDecorator

logger = logging.getLogger(__name__)

async def sched_add_cron(
    user_id: int, request: Request, apscheduler: ContextSchedulerDecorator, 
):
    logger.debug(request)
    apscheduler.add_job(
        tgbot.apsched.send_message_cron2,
        trigger="cron",
        hour=12,
        minute=0,
        # second=30,
        start_date=datetime.strptime("02.02.1978", "%d.%m.%Y"),
        id=str(user_id),
        kwargs={"user_id": user_id, "request": request, "apscheduler": apscheduler},
    )


async def sched_add_interval(
    user_id: int, request: Request, apscheduler: ContextSchedulerDecorator
):
    logger.debug(request)
    logger.debug(user_id)
    apscheduler.add_job(
        tgbot.apsched.send_message_cron2,
        trigger="interval",
        # hour=12,
        # minute=0,
        seconds=20,
        start_date=datetime.strptime("02.02.1978", "%d.%m.%Y"),
        id=str(user_id),
        kwargs={"user_id": user_id, "request": request, "apscheduler": apscheduler},
    )
