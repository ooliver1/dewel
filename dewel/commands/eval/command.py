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
;eval [optional language] [optional semver version matching, e.g. (1.66)]
[optional arguments split by newlines]
\`\`\`[optional language, this or the first line]
<your code, in a fenced codeblock>
\`\`\`
[optional stdin]
```
""".strip()
DESCRIPTION = r"""
Run code in a sandboxed environment.

Your input should be in the following format:
```
;eval [optional language] [optional semver version matching, e.g. (1.66)]
[optional arguments split by newlines]
\`\`\`[optional language, this or the first line]
<your code, in a fenced codeblock>
\`\`\`
[optional stdin]
```

Examples:
```
;eval \`\`\`py
print("Hello, world!")
\`\`\`
;eval python 3.11 \`\`\`py
print("Hello, world!")
\`\`\`
;eval 1.66 \`\`\`rs
println!("Hello, world!");
\`\`\`
```
""".strip()
LIST_DESCRIPTION = "List all languages, versions and runtimes I support."


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
    compile = result.get("compile", {})

    compile_code = compile.get("code", 0)
    compile_signal = compile.get("signal")
    run_code = run.get("code", 0)
    run_signal = run.get("signal")

    if compile_code or compile_signal:
        try:
            if compile_code is not None and compile_code > 128:
                compile_code -= 128

            signal = Signals(compile_code).name
        except ValueError:
            signal = None

        if compile_code:
            msg = f"Your code failed to compile, exiting with with code {run_code}"

            if run_signal:
                msg += f", killed with signal {compile_signal}"
                if signal:
                    msg += f" ({signal})"
                if signal == "SIGKILL":
                    msg += " (memory or time limit exceeded)"
        else:
            msg = f"Your code failed to run, exiting with signal {compile_signal} ({signal})"

        if compile_signal:
            msg += f", killed with signal {compile_signal}"
            if signal:
                msg += f" ({signal})"
            if signal == "SIGKILL":
                msg += " (memory or time limit exceeded)"
        if output := compile.get("output"):
            output = truncate(output.removesuffix("\n"), length=1000, lines=11)
            msg += f"\n```\n{output}\n```"
    elif run_code or run_signal:
        try:
            if run_code is not None and run_code > 128:
                run_code -= 128

            signal = Signals(run_code).name
        except ValueError:
            signal = "UNKNOWN"

        if run_code:
            msg = f"Your code failed to run, exiting with with code {run_code}"

            if run_signal:
                msg += f", killed with signal {run_signal} ({signal})"
                if signal == "SIGKILL":
                    msg += " (memory or time limit exceeded)"
        else:
            msg = (
                f"Your code failed to run, exiting with signal {run_signal} ({signal})"
            )

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


@manager.command(string_parser=parse, description=DESCRIPTION)
async def eval(
    ctx: Context, language: str, version: str, args: str, code: str, stdin: str
):
    log.info("woah")
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
                "Dewel",
                f"Could not find language {language} with version {version}."
                "See my full list of versions with `;list`.",
            )
        else:
            await bot.rest.send_message(
                "Dewel",
                f"Something unexpected happened :(\n```\n{result}\n```",
            )
        return

    await bot.rest.send_message("Dewel", get_message(result))


@manager.command(description=LIST_DESCRIPTION)
async def list(ctx: Context):
    async with bot.piston_client.get(bot.BASE_URL / "runtimes") as resp:
        runtimes = await resp.json(loads=orjson.loads)

    if resp.status != 200:
        await bot.rest.send_message(
            "Dewel",
            f"Something unexpected happened :(\n```\n{runtimes}\n```",
        )
        return

    language_list: dict[str, dict[str, Any]] = {}
    for r in runtimes:
        key = f"{r['language']} ({r['runtime']})" if "runtime" in r else r["language"]
        if existing := language_list.get(key):
            existing["versions"].append(r["version"])
            existing["aliases"].update(r["aliases"])
            language_list[key] = existing
        else:
            language_list[key] = dict(
                aliases=set(r["aliases"]),
                versions=[r["version"]],
            )

    language_string = "\n".join(
        f"{language} ({', '.join(sorted(aliases))}) - {', '.join(sorted(versions))}"
        for language, aliases, versions in (
            (language, data["aliases"], data["versions"])
            for language, data in sorted(language_list.items())
        )
    )

    await bot.rest.send_message(
        "Dewel",
        f"Here's a list of languages I can run code in:\n{language_string}",
    )


@bot.listen()
async def on_exception(event: ExceptionEvent) -> None:
    if isinstance(event.exception, CodeBlockError):
        await bot.rest.send_message("Dewel", INVALID_CODEBLOCK)
        return
    else:
        log.error("Exception in event %s", event, exc_info=event.exception)
