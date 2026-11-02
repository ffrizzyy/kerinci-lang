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

## Dialect worksheets

The canonical answer file for a dialect is `dialects/src/<code>.csv`: UTF-8
without a BOM, LF line endings, with the exact header
`id,tier,namespace,en,id_gloss,answer,notes,status`. The first five columns come
from `core/ids.json` and are read-only. The speaker fills `answer` and `notes`;
`status` is one of `todo`, `draft`, `reviewed`, or `rejected`.

The cycle is one tool:

```bash
python3 tools/lembar_kerja.py buat     --kode koto-payang   # create the sheet
python3 tools/lembar_kerja.py perbarui --kode koto-payang   # add new catalogue IDs
python3 tools/lembar_kerja.py periksa  --kode koto-payang --tulis
python3 tools/lembar_kerja.py docx     --kode koto-payang   # reviewable table
python3 tools/lembar_kerja.py baca     --kode koto-payang --tulis
python3 tools/lembar_kerja.py laporan  --kode koto-payang
python3 tools/lembar_kerja.py json     --kode koto-payang
```

`periksa` reports every problem by CSV row and catalogue ID. It normalizes word
answers (NFC, trim, lowercase, whitespace to `_`, one trailing `()` removed) and
message answers (NFC and trim only), then calls the dialect loader so word,
message, and clash rules cannot drift. Alternatives such as `kalu/lamun` are
errors for a human to resolve. `--tulis` writes only when there are no errors;
`--siap` applies the target skeleton's readiness gate. `laporan` prints tier
counts, missing Tier 1 IDs, and readiness.

`docx` writes an A4 landscape table with grey read-only columns and repeating
headers; the same CSV gives byte-identical bytes. `baca` updates only `answer`
and `notes`, turns a changed answer into `draft`, clears an empty answer to
`todo`, and never sets `reviewed` itself. `json` merges only accepted answers
into an existing `dialects/<code>.json`, preserves metadata and `revision`, and
writes nothing unless the merged file validates.

The old `Translation Worksheet (Koto Payang).docx` cannot be read by `baca`: it
has no ID column and 287 rows for 137 IDs. Map it by hand during the
`dialect-koto-payang` second speaker pass.

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
