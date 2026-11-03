"""Regenerate the VS Code grammar as a union of every dialect's words.

Run `python3 make_highlight.py` after adding or changing a dialect. The grammar
is one file for all dialects: a TextMate grammar cannot switch on the
`# dialek:` line, so every valid surface word from every dialect is highlighted
and no dialect is presented as the standard.

Only `kw.*`, `op.*`, and `fn.*` words are highlighted. `type.*` and `mode.*`
words are runtime output or string arguments and would color ordinary text;
`reserved.*` words are errors, not valid source. `fn.*` is colored only before
`(`, the same rule as 0.5.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from dialects.loader import available_dialects, load_dialect  # noqa: E402

GRAMMAR_PATH = ROOT / "vscode-extension" / "syntaxes" / "krc.tmLanguage.json"

# The groups keep the 0.5 scopes. The ID names are neutral; the words come from
# every dialect's resolved vocabulary.
STORAGE = {"kw.var", "kw.const", "kw.func"}
CALLS = {"kw.print", "kw.input"}
VALUES = {"kw.true", "kw.false", "kw.null"}
WORD_OPERATORS = {"kw.and", "kw.or", "kw.not"}


def _groups():
    """Every highlighted word, grouped by scope, across all dialects."""
    control, storage, operators, calls, builtins, constants = (
        set(), set(), set(), set(), set(), set())
    for code in available_dialects():
        dialect = load_dialect(code)
        for ident, word in dialect.words.items():
            namespace = ident.split(".", 1)[0]
            if namespace == "kw":
                if ident in STORAGE:
                    storage.add(word)
                elif ident in CALLS:
                    calls.add(word)
                elif ident in VALUES:
                    constants.add(word)
                elif ident in WORD_OPERATORS:
                    operators.add(word)
                else:
                    control.add(word)
            elif namespace == "op":
                operators.add(word)
            elif namespace == "fn":
                builtins.add(word)
    return {
        "control": control,
        "storage": storage,
        "operators": operators,
        "calls": calls,
        "builtins": builtins,
        "constants": constants,
    }


def _match(words, lookahead=""):
    """One bounded alternation over sorted words, with regex escaping."""
    if not words:
        return None
    body = "|".join(re.escape(word) for word in sorted(words))
    return r"\b(" + body + r")" + lookahead + r"\b"


def _patterns():
    groups = _groups()
    patterns = [
        {"name": "comment.line.number-sign.krc", "match": "#.*$"},
        {"name": "string.quoted.double.krc", "begin": "\"", "end": "\"",
         "patterns": [{"name": "constant.character.escape.krc",
                       "match": "\\\\."}]},
        {"name": "constant.numeric.krc", "match": "\\b\\d+(\\.\\d+)?\\b"},
    ]
    for name, key, lookahead in (
        ("keyword.control.krc", "control", ""),
        ("storage.type.krc", "storage", ""),
        ("keyword.operator.word.krc", "operators", ""),
        ("support.function.krc", "calls", ""),
        ("constant.language.krc", "constants", ""),
    ):
        match = _match(groups[key], lookahead)
        if match is not None:
            patterns.append({"name": name, "match": match})
    builtins = _match(groups["builtins"], "(?=\\()")
    if builtins is not None:
        patterns.append({"name": "support.function.builtin.krc",
                         "match": builtins})
    return patterns


def render():
    """The deterministic grammar text. Importing this module never writes."""
    grammar = {
        "scopeName": "source.krc",
        "name": "KerinciLang",
        "patterns": _patterns(),
    }
    return json.dumps(grammar, indent=2, ensure_ascii=False,
                      sort_keys=True) + "\n"


def main():
    GRAMMAR_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(GRAMMAR_PATH, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render())
    print("ok")


if __name__ == "__main__":
    main()
