# SPDX-License-Identifier: MIT

import re
from typing import Sequence

from dewel.errors import CodeBlockError

# onerandomusername/monty-python:exts/eval/__init__.py for the codeblock regex.
CODE_RE = re.compile(
    r"(?: *(?P<cmdlang>\S*?)\s*|\s*)"
    # Optional language, followed by whitespace.
    r"(?: \(+(?P<version>\S*?)\)\s*|\s*)"
    # Optional version, followed by whitespace.
    r"(?:\n(?P<args>(?:[^\n\r\f\v]+\n?)*?)\s*|\s*)?"
    # Optional arguments, split by newline, followed by whitespace.
    r"(?P<delim>(?P<block>```)|``?)"
    # Code delimiter: 1-3 backticks; (?P=block) only matches if it's a block.
    r"(?(block)(?:(?P<blocklang>[a-z]+)\n)?)"
    # If we're in a block, match optional language (only letters plus newline).
    r"(?:[ \t]*\n)*"
    # Any blank (empty or tabs/spaces only) lines before the code.
    r"(?P<code>.*?)"
    # Extract all code inside the markup.
    r"\s*"
    # Any more whitespace before the end of the code markup.
    r"(?P=delim)"
    # Match the exact same delimiter from the start again.
    r"(?:\n(?P<stdin>.*))?",
    # Anything after the end delimiter is considered stdin.
    re.DOTALL | re.IGNORECASE,  # "." also matches newlines, case insensitive.
)


def parse(user_input: str) -> tuple[Sequence[str], dict[str, Sequence[str]]]:
    """Parse a codeblock into its components."""
    match = CODE_RE.match(user_input)

    if not match:
        raise CodeBlockError

    language = match.group("cmdlang") or match.group("blocklang")

    if not language:
        raise CodeBlockError

    version = match.group("version") or "*"
    args = match.group("args") or ""
    code = match.group("code")
    stdin = match.group("stdin") or ""

    return [language, version, args, code, stdin], {}
