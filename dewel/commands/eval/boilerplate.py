# SPDX-License-Identifier: MIT


def remove_boilerplate(language: str, code: str) -> str:
    match language:
        case "rust" | "rs":
            return rust_boilerplate(code)
        case "c" | "c++" | "gcc" | "g++" | "cpp":
            return c_boilerplate(code)
        case _:
            return code


def rust_boilerplate(code: str) -> str:
    if "fn main" in code:
        return code

    return f"fn main() {{\n{code}\n}}"


def c_boilerplate(code: str) -> str:
    if "main" in code:
        return code

    return f"int main() {{\n{code}\n}}"
