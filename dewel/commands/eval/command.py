# SPDX-License-Identifier: MIT

from logging import getLogger
from signal import Signals

from piston_rspy import Executor, File
from sail import Context
from velum import ExceptionEvent

from dewel import bot, manager
from dewel.errors import CodeBlockError
from .parser import parse

log = getLogger(__name__)

INVALID_CODEBLOCK = r"""
Your codeblock is invalid. Please use the following format:
;eval [language]
[optional arguments split by newlines]
\`\`\`[optional language, this or the first line]
<your code>
\`\`\`
[stdin]
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


@manager.command(string_parser=parse)
async def eval(
    ctx: Context, language: str, version: str, args: str, code: str, stdin: str
):
    result = await bot.piston_client.execute(
        Executor(
            language=language,
            version=version,
            files=[File(content=code)],
            args=args.splitlines(),
            stdin=stdin,
        ),
    )

    if result.is_err():
        await bot.rest.send_message(
            "Dewel", f"Could not find language {language} with version {version}"
        )
        return

    if result.compile and (result.compile.code or result.compile.signal):
        msg = "Your code failed to compile"
        if result.compile.code:
            msg += f", exiting with with code {result.compile.code}"
            try:
                ret_code = result.compile.code
                if ret_code > 128:
                    ret_code -= 128

                signal = Signals(ret_code)
                msg += f" ({signal.name})"
            except ValueError:
                pass
        if result.compile.signal:
            msg += f", exiting with signal {result.compile.signal}"
            if result.compile.signal == "SIGKILL":
                msg += " (memory or time limit exceeded)"
        if result.compile.output:
            output = truncate(
                result.compile.output.removesuffix("\n"), length=1000, lines=10
            )
            msg += f"\n```\n{output}\n```"
    elif result.run.code or result.run.signal:
        msg = "Your code failed to run"
        if result.run.code:
            msg += f", exiting with with code {result.run.code}"
            try:
                ret_code = result.run.code
                if ret_code > 128:
                    ret_code -= 128

                signal = Signals(ret_code)
                msg += f" ({signal.name})"
            except ValueError:
                pass
        if result.run.signal:
            msg += f", exiting with signal {result.run.signal}"
            if result.run.signal == "SIGKILL":
                msg += " (memory or time limit exceeded)"
        if result.run.output:
            output = truncate(
                result.run.output.removesuffix("\n"), length=1000, lines=10
            )
            msg += f"\n```\n{output}\n```"
    else:
        if result.run.output:
            output = truncate(
                result.run.output.removesuffix("\n"), length=1000, lines=10
            )
            msg = f"Your code ran successfully!\n```\n{output}\n```"
        else:
            msg = "Your code successfully ran with no output!"

    await bot.rest.send_message("Dewel", msg)


@bot.listen()
async def on_exception(event: ExceptionEvent) -> None:
    if isinstance(event.exception, CodeBlockError):
        await bot.rest.send_message("Dewel", INVALID_CODEBLOCK)
        return
    else:
        log.error("Exception in event %s", event, exc_info=event.exception)
