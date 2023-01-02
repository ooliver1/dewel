# SPDX-License-Identifier: MIT

from typing import Optional

from sail import Context

from dewel import bot, manager

NL = "\n"


@manager.command(
    string_parser=lambda h: ([h], {}),
    description="Get help for a command or a list of all commands.",
)
async def help(ctx: Context, command: str):
    if command == "":
        command_list = "\n".join(
            f"`;{cmd.name}` - {cmd.description.split(NL, 1)[0]}"
            for cmd in manager.commands
        )
        await bot.rest.send_message(
            "Dewel",
            "**Dewel** a bot to assist in development.\n\n"
            f"My Commands:\n{command_list}\nRun `;help <command>` for more info.",
        )
    else:
        cmd = manager._commands.get(command)
        if cmd is None:
            await bot.rest.send_message("Dewel", f"Command `{command}` not found.")
            return

        await bot.rest.send_message(
            "Dewel",
            f"**{cmd.name}**\n\n{cmd.description}",
        )
