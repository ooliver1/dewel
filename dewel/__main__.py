from asyncio import run

import uvloop
from velum import JSONImpl, set_json_impl

from . import bot, commands
from .log_setup import setup_logging

# Just registers all commands.
del commands
setup_logging()
set_json_impl(impl=JSONImpl.ORJSON)
uvloop.install()


try:
    run(bot.start())
except KeyboardInterrupt:
    run(bot.close())
