# 05. Tooling and Documentation

## REPL

Included: run `krc` with no arguments. Multi-line blocks and lists work (the prompt changes to `...` while a `{`, `(` or `[` is open), and Ctrl+C cancels the current input. Possible improvements:

- Show a welcome message in Siulak and Indonesian.
- Add command history with Python's `readline` module.
- The welcome message and prompt are in Indonesian now; add Kerinci once speakers confirm wording.

## Error messages

Good errors matter most for beginners.

Principles:

- Always include the **line number**.
- Say what was expected and what was found.
- Keep messages short; one sentence.
- Put the message in a table so languages can be switched:

```python
MESSAGES = {
    "undefined": {"ind": "Nama belum didefinisikan: {0}", "kea": "<Siulak text>: {0}"},
    "div_zero":  {"ind": "Pembagian dengan nol",        "kea": "<Siulak text>"},
}
```

- Offer bilingual output (Siulak and Indonesian) until Siulak phrasing is reviewed by speakers.

| Error | Where | Needs translating |
|---|---|---|
| Unexpected character | lexer | yes |
| Expected X, got Y | parser | yes |
| Undefined name | interpreter | yes |
| Assign to undeclared name | interpreter | yes |
| Division by zero | interpreter | yes |
| Wrong argument count | interpreter | yes |
| Not a function | interpreter | yes |

## Editor support

### VS Code syntax highlighting

Already included in `vscode-extension/`. It is generated from the keyword table, so it stays in sync:

```bash
python3 make_highlight.py
```

To try it locally, copy the `vscode-extension` folder into your VS Code extensions directory (`~/.vscode/extensions/kerincilang`) and reload VS Code. Files ending in `.krc` get colors for keywords, strings, numbers and comments, plus bracket matching and `#` comment toggling. To publish it, package it with `vsce`.

## Documentation set

| Document | Language | Status |
|---|---|---|
| `README.md` (front page) | English | done |
| Tutorial: 13 lessons, answers, glossary (`tutorial/`) | English, Kerinci code | done; every sample is tested |
| The same tutorial in Indonesian (`tutorial/id/`) | Indonesian, Kerinci code | done; every sample is tested |
| Tutorial prose in Kerinci | Kerinci | **needs speakers** (guide in `tutorial/kerinci/README.md`) |
| Language reference (`docs/03-syntax-design.md`) | English | done |
| Keyword glossary (`tutorial/glossary.md`, Indonesian: `tutorial/id/glosarium.md`) | Kerinci, English, Indonesian | done; checked against the language |
| Contributing guide (`CONTRIBUTING.md`) | English (+ Indonesian summary) | done |
| Getting-started guide (`GETTING-STARTED.md`) | English | done |

### Keeping the tutorial correct

Every code sample in the tutorial is run by `tests/test_tutorial.py`, and the output printed in the lesson must match the real output. After changing the language:

```bash
python3 tools/sinkron_tutorial.py --tulis   # refresh the printed outputs
python3 tools/buat_glosarium.py             # rewrites both glossaries; fails if a new word is missing
python3 tests/test_tutorial.py
```

## Teaching materials

- Printable keyword poster (Siulak word, Indonesian meaning, example)
- Flash cards for vocabulary
- Classroom exercises that use local themes (village names, crops, festivals)
- A "word of the day" tied to a keyword to strengthen vocabulary learning

## Project hygiene

- Repository layout: see `docs/04-implementation.md`
- Version control (the folder is ready to be a git repository; `.gitignore` is included)
- Versioning: `0.x` while the language and vocabulary are still being reviewed by speakers
- `CHANGELOG.md` records every release
- Automated tests on every change: `.github/workflows/tests.yml` runs both test files on Python 3.9 to 3.13
