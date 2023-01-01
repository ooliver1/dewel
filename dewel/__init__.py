# SPDX-License-Identifier: MIT

from sail import CommandManager

from .bot import Dewel

bot = Dewel()
manager = CommandManager.with_prefix(";")
manager.bind_to_app(bot)
