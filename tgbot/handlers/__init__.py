from aiogram import Router

from . import basic_commands


def get_routers() -> list[Router]:
    return [
        basic_commands.router,
    ]
