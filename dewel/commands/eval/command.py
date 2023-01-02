# SPDX-License-Identifier: MIT

from logging import getLogger
from signal import Signals
from typing import Any

import orjson
from sail import Context
from velum import ExceptionEvent

from dewel import bot, manager
from dewel.errors import CodeBlockError

from .boilerplate import remove_boilerplate
from .parser import parse

log = getLogger(__name__)

INVALID_CODEBLOCK = r"""
Your codeblock is invalid. Please use the following format:
```
;eval [language] [optional semver version matching, e.g. (1.66)]
[optional arguments split by newlines]
\`\`\`[optional language, this or the first line]
<your code, in a fenced codeblock>
\`\`\`
[stdin]
```
""".strip()


def truncate(string: str, *, length: int, lines: int) -> str:
    line_count = string.count("\n")

    if line_count > 0:
        text = [f"{i:03d} | {line}" for i, line in enumerate(string.split("\n"), 1)]
        text = text[:lines]
        string = "\n".join(text)

    if line_count > lines:
        if len(string) >= length:
            string = f"{string[:length]}\n... (truncated - too long, too many lines)"
        else:
            string = f"{string}\n... (truncated - too many lines)"
    elif len(string) >= length:
        string = f"{string[:length]}\n... (truncated - too long)"

    return string


def get_message(result: Any) -> str:
    run = result["run"]
    compile = result.get("compile")

    if compile and compile.get("code", 0) != 0:
        ret_code = compile["code"]
        exit_signal = compile.get("signal")
        output = compile.get("output")
        msg = f"Your code failed to compile, exiting with with code {ret_code}"

        try:
            if ret_code > 128:
                ret_code -= 128

            signal = Signals(ret_code)
            msg += f" ({signal.name})"
        except ValueError:
            pass

        if exit_signal:
            msg += f", killed with signal {result.compile.signal}"
            if exit_signal == "SIGKILL":
                msg += " (memory or time limit exceeded)"
        if output:
            output = truncate(output.removesuffix("\n"), length=1000, lines=11)
            msg += f"\n```\n{output}\n```"
    elif exit_code := run.get("code", 0):
        msg = f"Your code failed to run, exiting with with code {exit_code}"

        try:
            if exit_code > 128:
                exit_code -= 128

            signal = Signals(exit_code)
            msg += f" ({signal.name})"
        except ValueError:
            pass

        if signal := run.get("signal"):
            msg += f", killed with signal {signal}"
            if signal == "SIGKILL":
                msg += " (memory or time limit exceeded)"
        if output := run.get("output"):
            output = truncate(output.removesuffix("\n"), length=1000, lines=11)
            msg += f"\n```\n{output}\n```"
    else:
        if output := run.get("output"):
            output = truncate(output.removesuffix("\n"), length=1000, lines=11)
            msg = f"Your code ran successfully!\n```\n{output}\n```"
        else:
            msg = "Your code successfully ran with no output!"

    return msg


@manager.command(string_parser=parse)
async def eval(
    ctx: Context, language: str, version: str, args: str, code: str, stdin: str
):
    async with bot.piston_client.post(
        bot.BASE_URL / "execute",
        json=dict(
            language=language,
            version=version,
            files=[dict(content=remove_boilerplate(language, code))],
            args=args.splitlines(),
            stdin=stdin,
        ),
    ) as resp:
        result = await resp.json(loads=orjson.loads)

    if resp.status != 200:
        if "runtime is unknown" in result["message"]:
            await bot.rest.send_message(
                "Dewel", f"Could not find language {language} with version {version}"
            )
        else:
            await bot.rest.send_message(
                "Dewel",
                f"Something unexpected happened :(\n```\n{result}\n```",
            )
        return

    await bot.rest.send_message("Dewel", get_message(result))


@bot.listen()
async def on_exception(event: ExceptionEvent) -> None:
    if isinstance(event.exception, CodeBlockError):
        await bot.rest.send_message("Dewel", INVALID_CODEBLOCK)
        return
    else:
        log.error("Exception in event %s", event, exc_info=event.exception)
