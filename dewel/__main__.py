from asyncio import run

import uvloop
from velum import JSONImpl, set_json_impl

from .bot import Dewel
from .log_setup import setup_logging

setup_logging()
set_json_impl(impl=JSONImpl.ORJSON)
uvloop.install()


bot = Dewel()


try:
    run(bot.start())
except KeyboardInterrupt:
    run(bot.close())
