"""Regenerates the VS Code grammar from KEYWORDS. Run after editing keywords."""
import json
from kerincilang import KEYWORDS, WORD_OPERATORS, BUILTINS

def words(*names):
    return "\\b(" + "|".join(KEYWORDS[n] for n in names) + ")\\b"

grammar = {
    "scopeName": "source.krc",
    "name": "KerinciLang",
    "patterns": [
        {"name": "comment.line.number-sign.krc", "match": "#.*$"},
        {"name": "string.quoted.double.krc", "begin": "\"", "end": "\"",
         "patterns": [{"name": "constant.character.escape.krc", "match": "\\\\."}]},
        {"name": "constant.numeric.krc", "match": "\\b\\d+(\\.\\d+)?\\b"},
        {"name": "keyword.control.krc",
         "match": words("IF", "ELSE", "WHILE", "FOR", "IN", "SWITCH", "IMPORT", "TRY", "CATCH", "RAISE", "BREAK", "CONTINUE", "RETURN", "BEGIN", "END")},
        {"name": "storage.type.krc", "match": words("VAR", "CONST", "FUNC")},
        {"name": "keyword.operator.word.krc",
         "match": words("AND", "OR", "NOT")[:-3] + "|" + "|".join(WORD_OPERATORS) + ")\\b"},
        {"name": "support.function.krc", "match": words("PRINT", "INPUT")},
        {"name": "support.function.builtin.krc", "match": "\\b(" + "|".join(BUILTINS) + ")(?=\\()"},
        {"name": "constant.language.krc", "match": words("TRUE", "FALSE", "NULL")},
    ],
}
with open("vscode-extension/syntaxes/krc.tmLanguage.json", "w", encoding="utf-8") as f:
    json.dump(grammar, f, indent=2, ensure_ascii=False)
print("ok")
