"""Regenerate the VS Code grammars from the dialect data.

Run `python3 make_highlight.py` after adding or changing a dialect. It writes:

- `syntaxes/krc.tmLanguage.json`, the union of every dialect. It is the default
  for a `.krc` file with no header and the fallback for an unknown code.
- `syntaxes/krc-<code>.tmLanguage.json`, one grammar per dialect. The extension
  switches to it when line 1 says `# dialek: <code>`.
- `dialects.json`, the small catalogue `extension.js` reads at runtime.

A TextMate grammar cannot read the file it colors, so the dialect grammars stay
declarative and the extension module only picks one. Every grammar is
deterministic and ends with one newline.

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

from dialects.loader import (  # noqa: E402
    available_dialects,
    load_dialect,
)

EXTENSION = ROOT / "vscode-extension"
GRAMMAR_DIR = EXTENSION / "syntaxes"
UNION_PATH = GRAMMAR_DIR / "krc.tmLanguage.json"
DIALECTS_PATH = EXTENSION / "dialects.json"

UNION_LANGUAGE = "kerincilang"
UNION_SCOPE = "source.krc"

# The groups keep the 0.5 scopes. The ID names are neutral; the words come from
# each grammar's vocabulary.
STORAGE = {"kw.var", "kw.const", "kw.func"}
CALLS = {"kw.print", "kw.input"}
VALUES = {"kw.true", "kw.false", "kw.null"}
WORD_OPERATORS = {"kw.and", "kw.or", "kw.not"}


def _groups(dialects):
    """Every highlighted word, grouped by scope, across the given dialects."""
    control, storage, operators, calls, builtins, constants = (
        set(), set(), set(), set(), set(), set())
    for dialect in dialects:
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


def _patterns(groups):
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


def _render(grammar):
    return json.dumps(grammar, indent=2, ensure_ascii=False,
                      sort_keys=True) + "\n"


def _language(code):
    return "%s-%s" % (UNION_LANGUAGE, code)


def _scope(code):
    return "%s.%s" % (UNION_SCOPE, code.replace("-", "_"))


def dialect_grammar_path(code):
    return GRAMMAR_DIR / ("krc-%s.tmLanguage.json" % code)


def render():
    """The union grammar text. Importing this module never writes."""
    dialects = [load_dialect(code) for code in available_dialects()]
    grammar = {
        "scopeName": UNION_SCOPE,
        "name": "KerinciLang",
        "patterns": _patterns(_groups(dialects)),
    }
    return _render(grammar)


def render_dialect(code):
    """One dialect's grammar text, with no other dialect's words."""
    dialect = load_dialect(code)
    grammar = {
        "scopeName": _scope(code),
        "name": "KerinciLang (%s)" % dialect.name,
        "patterns": _patterns(_groups([dialect])),
    }
    return _render(grammar)


def render_catalogue():
    """The runtime catalogue `extension.js` reads, with no VS Code import."""
    dialects = []
    for code in available_dialects():
        dialect = load_dialect(code)
        dialects.append({
            "code": code,
            "name": dialect.name,
            "status": dialect.status,
            "language": _language(code),
            "scopeName": _scope(code),
            "grammar": "syntaxes/krc-%s.tmLanguage.json" % code,
        })
    data = {
        "union": {
            "language": UNION_LANGUAGE,
            "name": "KerinciLang",
            "scopeName": UNION_SCOPE,
            "grammar": "syntaxes/krc.tmLanguage.json",
        },
        "dialects": dialects,
    }
    return _render(data)


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main():
    _write(UNION_PATH, render())
    keep = {UNION_PATH.name}
    for code in available_dialects():
        path = dialect_grammar_path(code)
        _write(path, render_dialect(code))
        keep.add(path.name)
    _write(DIALECTS_PATH, render_catalogue())
    # A dialect that was removed must not leave a grammar behind.
    for path in GRAMMAR_DIR.glob("krc-*.tmLanguage.json"):
        if path.name not in keep:
            path.unlink()
    print("ok")


if __name__ == "__main__":
    main()
