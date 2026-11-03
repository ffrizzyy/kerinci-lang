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

Already included in `vscode-extension/`. The grammar is a **union** generated
from every dialect's resolved words, so it stays in sync and no dialect is
presented as the standard:

```bash
python3 make_highlight.py
```

To try it locally, copy the `vscode-extension` folder into your VS Code
extensions directory (`~/.vscode/extensions/kerincilang`) and reload VS Code.
Files ending in `.krc` get colors for keywords, strings, numbers and comments,
plus bracket matching and `#` comment toggling. The extension README explains
the union rule. A per-dialect picker is not part of 0.6: a grammar cannot switch
on the `# dialek:` line, so every valid word from every dialect is highlighted.
To publish it, package it with `vsce`.

## Documentation set

| Document | Language | Status |
|---|---|---|
| `README.md` (front page) | English | done |
| Tutorial: 13 lessons, answers, glossary (`tutorial/`) | English, Kerinci code | done; every sample is tested |
| The same tutorial in Indonesian (`tutorial/id/`) | Indonesian, Kerinci code | done; every sample is tested |
| Generated Koto Payang tutorial (`tutorial/en/koto-payang/`, `tutorial/id/koto-payang/`) | English / Indonesian prose, Koto Payang code | done; review status, every block tested |
| Tutorial prose in Kerinci | Kerinci | **needs speakers** (guide in `tutorial/kerinci/README.md`) |
| Language reference (`docs/03-syntax-design.md`) | English | done |
| Keyword glossary (`tutorial/glossary.md`, Indonesian: `tutorial/id/glosarium.md`) | Kerinci, English, Indonesian | done; checked against the language |
| Contributing guide (`CONTRIBUTING.md`) | English (+ Indonesian summary) | done |
| Adding a dialect (`docs/09-adding-a-dialect.md`) | English | done; every command is exercised by `tests/test_docs_release.py` |
| Release checklist (`RELEASING.md`) | English | done |
| Getting-started guide (`GETTING-STARTED.md`) | English | done |

### Keeping the tutorial correct

Every code sample in the tutorial is run by `tests/test_tutorial.py`, and the output printed in the lesson must match the real output. After changing the language:

```bash
python3 tools/sinkron_tutorial.py --tulis   # refresh the printed outputs
python3 tools/buat_glosarium.py             # rewrites both glossaries; fails if a new word is missing
python3 tests/test_tutorial.py
python3 tools/sinkron_tutorial.py --bangun koto-payang   # regenerate both generated trees
python3 tests/test_tutorial_dialects.py
```

`--bangun koto-payang` reads the baseline lessons, maps words by neutral ID,
runs every generated block, and rewrites the committed
`tutorial/{en,id}/koto-payang/` trees. The generated index names any English
base fallback the dialect still needs; Koto Payang currently uses `contains`
(`fn.contains`) and `boolean` (`type.bool`). The build warns once per fallback
on stderr and still exits 0. A `.krc` helper gets a dialect header; raw-data
helpers such as `nilai.txt` keep their bytes.

## The Siulak freeze

Siulak v0.5 is committed as `dialects/siulak.json`, not as a CSV worksheet. It
is the complete legacy snapshot (69 words, 68 messages, 137 IDs), marked
`draft` so it is not mistaken for a 0.6 speaker review. `dialects/siulak.md`
holds the provenance, the grouped word table, and the change policy; `docs/02`
stays the decision history.

Do not edit the file to "fix" a v0.5 quirk. `type.bool` is the known English
placeholder `boolean`, and `tests/test_siulak_legacy.py` locks every word and
message to `LEGACY_WORDS`, `LEGACY_OPERATORS`, and `id_gloss`. A real change
needs a Siulak speaker review and a new revision.

## The Koto Payang review

Koto Payang is the worked example of the worksheet cycle, committed at
`status: review`. `dialects/src/koto-payang.csv` holds 137 rows: 85 `reviewed`,
4 `draft`, and 48 `todo`. The JSON owns the 89 accepted answers and lets the
other 48 fall back to the base.

```bash
python3 tools/lembar_kerja.py periksa --kode koto-payang --siap   # review gate
python3 tools/lembar_kerja.py laporan --kode koto-payang          # tier counts
python3 tools/cek_dialek.py --kode koto-payang                    # CI gate
```

`periksa --siap` passes for `review` and prints that `approved` is not ready
(51 Tier 2 rows unreviewed). Do not promote the file, fill a `todo` with a
guess, or borrow a Siulak word to make the counts look complete. The generated
Koto Payang tutorial is honest about this: it lists `contains` and `boolean`
as base words in both indexes until speakers supply the dialect's own terms.
The second speaker pass supplies the 42 messages, 6 words, and 4 draft
confirmations; only then can the file carry a named reviewer and
`status: approved`.

## Migrating old programs

`krc migrasi` gives a v0.5 source its explicit header and does the same for its
literal `ambik` imports:

```bash
python3 kerincilang.py migrasi examples/contoh.krc
python3 kerincilang.py migrasi --semua examples
python3 kerincilang.py migrasi program.krc --dialek koto-payang
python3 kerincilang.py migrasi program.krc --kering   # preview, no writes
```

The default code is `siulak`. The command parses each file to find imports but
never runs it. It adds one line and preserves every other byte, including CRLF
and a missing final newline. A file with a valid header is never rewritten, so
re-running is a no-op; `migrasi --semua examples` currently reports eight files
already migrated.

It refuses instead of repairing: a UTF-8 BOM, a malformed line-1 header, a
syntax error, an unknown header dialect, a computed import, or a missing import
is reported and the affected file is unchanged. Exit 0 is success, 1 is a
refused file, and 2 is a usage error (including an unknown `--dialek`, checked
before any write).

## Translating between dialects

`krc terjemah` moves one file from its own dialect to another without executing
it or reformatting it:

```bash
python3 kerincilang.py terjemah contoh.krc --ke koto-payang --out contoh.kot
python3 kerincilang.py terjemah contoh.krc --ke koto-payang   # stdout
python3 kerincilang.py terjemah old.krc --dari siulak --ke koto-payang
python3 kerincilang.py terjemah contoh.krc --ke koto-payang \
    --out contoh.kot --kering                                  # preview
```

The policy is deliberately conservative. Only keywords, word operators,
built-in names, the line-1 header, and the direct second argument of a `bukak`
call are rewritten. User-declared names, comments, ordinary strings, numbers,
spacing, line endings, and a missing final newline are byte-identical. The
translator parses the file but never runs it.

It refuses with exit 1, and writes nothing, when the target does not own an ID
the file uses (for example Koto Payang has no `fn.wait`, `fn.list`, `fn.map`, or
`fn.contains` yet), when a user name collides with a target keyword, operator,
built-in, or reserved word, when a user name shadows a source built-in, or when
a mode/type string cannot be translated without changing the meaning. A
refusal is intentional: emitting an English base fallback would break the
round-trip promise.

For a headered file that uses only target-owned IDs, `A -> B -> A` is
byte-identical. Same-dialect translation is a validated copy, and a headerless
file gains exactly one header. Imports are not followed; every imported file
keeps its own header, so mixed-dialect programs still run. `--out` is atomic,
may not equal the input, and `--kering` writes nothing. Exit 0 is success, 1 is
a refused file, and 2 is a usage error.

## Dialect worksheets

The canonical answer file for a new dialect is `dialects/src/<code>.csv`: UTF-8
without a BOM, LF line endings, with the exact header
`id,tier,namespace,en,id_gloss,answer,notes,status`. The first five columns come
from `core/ids.json` and are read-only. The speaker fills `answer` and `notes`;
`status` is one of `todo`, `draft`, `reviewed`, or `rejected`.

The cycle is one tool:

```bash
python3 tools/lembar_kerja.py buat     --kode koto-payang   # create the sheet
python3 tools/lembar_kerja.py rangka   --kode koto-payang --nama "Koto Payang"
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
has no ID column and 287 rows for 137 IDs. It was mapped by hand into
`dialects/src/koto-payang.csv`; the remaining gaps are part of the second
speaker pass, not a script.

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
- Automated tests on every change: `.github/workflows/tests.yml` runs the offline suites, the freshness diffs, and the wheel smoke on Python 3.9 to 3.13, with Windows and macOS smoke jobs
