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
    imports = []
    lines = ["int main() {"]

    # Someone out there will decide that they will not like the beloved \n.
    # This splits everything by `;` to check for includes, and then recombines.
    original_lines = code.replace(";", ";\n").split("\n")
    for line in original_lines:
        if line.lstrip().startswith("#include"):
            imports.append(line)
        else:
            lines.append(line)

    lines.append("}")
    return "\n".join(imports + lines).replace(";\n", ";")
