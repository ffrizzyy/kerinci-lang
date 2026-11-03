# Adding a dialect

This guide takes a new Kerinci dialect from an empty worksheet to a validated,
runnable dialect. You do not need to read or change Python. A dialect is data:
one worksheet, one JSON file, and one notes file. The interpreter, the tutorial
generator, the editor grammar, and the test suites are shared by every dialect.

If you only want to check words, start with
[`tutorial/glossary.md`](../tutorial/glossary.md) and
[`02-vocabulary-worksheet.md`](02-vocabulary-worksheet.md) instead.

**Never guess a word, machine-translate one, or copy a Siulak word to fill a
gap.** A missing word falls back to the neutral English base and is reported;
that is better than a wrong word. Speakers own their dialect, not the
maintainer and not the tool.

## 1. What a dialect is

A dialect consists of three files under `dialects/`:

| File | Role |
|---|---|
| `dialects/src/<code>.csv` | The canonical worksheet, one row per catalogue ID. Contributors edit this file. |
| `dialects/<code>.json` | The runtime data. It is generated from accepted worksheet rows plus review metadata. |
| `dialects/<code>.md` | The notes: provenance, spelling rules, mapping decisions, review record, and gaps. |

The worked example is Koto Payang:

- [`dialects/src/koto-payang.csv`](../dialects/src/koto-payang.csv)
- [`dialects/koto-payang.json`](../dialects/koto-payang.json)
- [`dialects/koto-payang.md`](../dialects/koto-payang.md)

`core/ids.json` supplies the neutral IDs, tiers, English meanings, Indonesian
glosses, and message placeholders. It is read-only here. The engine never
contains a dialect's words.

The three files use the same `<code>` in their names. A dialect never changes
another dialect's file.

## 2. Before you start

Decide and write down:

- **Code.** Lowercase letters, digits, and hyphens only: `^[a-z0-9-]+$`.
  Examples: `koto-payang`, `sungai-liuk`. The code is the file name and the
  value of `# dialek:`.
- **Display name.** For example `Koto Payang`.
- **Speaker(s).** The people who will decide the words. A `reviewed` row needs
  a real speaker, not the contributor's guess.
- **Maintainer.** The person who keeps the files current. It may be a role
  (`KerinciLang core`), not necessarily a person.
- **Reviewer.** Required only for `approved`. Leave it empty until a named
  reviewer has done the second pass.
- **Source(s).** The dictionary, worksheet, recording, or named speaker
  consultation behind the answers. At least one source is required for
  `review` and `approved`.
- **Licence.** Dialect data is released under CC BY-SA 4.0. Do not copy a
  source that forbids derivative use.
- **Spelling rules.** Write them before the first row: final vowels, `ng`,
  glottal stops, hyphenated or joined forms, and whether multi-word concepts
  use underscores. Put them in the notes file and in the JSON `orthography`
  field.

Do not open the old DOCX as input. The DOCX is an optional review view, not a
source of truth, and the tool never ingests it.

## 3. Scaffold

Use the made-up code `dialek-baru` while learning the steps. **`dialek-baru` is
a placeholder. Do not commit a dialect called `dialek-baru`.**

From the repository root:

```bash
python3 tools/lembar_kerja.py buat   --kode dialek-baru
python3 tools/lembar_kerja.py rangka --kode dialek-baru --nama "Dialek Baru"
```

`buat` creates the worksheet. `rangka` creates a valid `draft` JSON skeleton
and a notes stub and validates the JSON before writing it. Both commands refuse
to replace an existing file unless you add `--paksa`.

The three files use the code in their names, in the same places as the Koto
Payang example above. The CSV is canonical: if the CSV and the JSON disagree,
the CSV wins and you regenerate the JSON.

Optional `rangka` arguments:

```text
--pemelihara TEXT   the maintainer; default pending
--ortografi TEXT    the spelling note; default a clearly pending sentence
--json PATH         write the JSON somewhere else (tests use this)
--md PATH           write the notes somewhere else (tests use this)
```

## 4. Fill the worksheet

Open the CSV in a spreadsheet or a text editor. The columns are fixed:

```text
id,tier,namespace,en,id_gloss,answer,notes,status
```

Only `answer`, `notes`, and `status` belong to you. Leave `id`, `tier`,
`namespace`, `en`, and `id_gloss` exactly as the catalogue wrote them.

Work in tier order:

1. **Tier 1** — the words a first program needs. There are 32 Tier 1 IDs.
2. **Tier 2** — the rest of the everyday language. There are 104 Tier 2 IDs.
3. **Tier 3** — rare or specialised. There is 1 Tier 3 ID.

Rules for an answer:

- One word or one joined phrase, with no spaces. Join a natural two-word form
  with `_`, for example `lebih_nik_dari`.
- Lowercase. A trailing `()` is removed by the checker, so `pisah()` and
  `pisah` are the same answer.
- No `/` or `,` alternatives in `answer`. Choose one and record the other in
  `notes` with its source.
- A `msg.*` row is an error message, not a word. Keep the neutral placeholders
  exactly as the catalogue declares them — `{name}`, `{message}`, `{arity}`,
  `{line}`, `{path}` — and translate only the surrounding text.
- An answer must be a valid identifier after normalization:
  `^[a-z][a-z0-9_]*$`.

Rules for `status`:

| Status | Meaning |
|---|---|
| `todo` | No answer yet. The answer cell must be empty. |
| `draft` | A proposed answer, not yet checked by a speaker. |
| `reviewed` | A speaker has checked and accepted this answer. |
| `rejected` | Considered and refused. Keep the answer and the reason in `notes`. |

`json` reads only `draft` and `reviewed` rows. A `rejected` row keeps its record
but never enters the runtime file.

`periksa --tulis` normalizes the answers in the CSV (NFC, trim, lowercase,
spaces to underscores, trailing `()` removed). Run it before you spend time
reviewing formatting by eye.

## 5. Check and convert

Run these in order:

```bash
python3 tools/lembar_kerja.py periksa --kode dialek-baru
python3 tools/lembar_kerja.py periksa --kode dialek-baru --tulis
python3 tools/lembar_kerja.py laporan --kode dialek-baru
python3 tools/lembar_kerja.py json    --kode dialek-baru
```

- `periksa` prints every problem by row and ID: unknown ID, duplicate row, a
  missing answer, an alternative, an invalid identifier, a clash, a missing
  placeholder, and the catalogue columns that changed.
- `periksa --tulis` also writes the normalized answers back to the CSV. It
  writes nothing if the CSV structure is broken.
- `laporan` prints tier counts, the missing Tier 1 IDs, error and warning
  counts, and whether the worksheet is ready for `review` or `approved`.
- `json` merges only accepted rows into the JSON skeleton, validates the merged
  file, and refuses to write on a blocking problem. It preserves the metadata
  already in the JSON — name, maintainer, sources, reviewer, orthography,
  notes — and replaces only `words` and `messages`.

A successful run ends like this:

```text
wrote dialects/dialek-baru.json: 32 words, 0 messages
```

`periksa --siap` adds the readiness gate. It reads the `status` in the JSON
skeleton, so promote the skeleton first (section 7), then run:

```bash
python3 tools/lembar_kerja.py periksa --kode dialek-baru --siap
```

Once the rows are filled and the skeleton is promoted, this is the whole
sequence in one place:

```bash
python3 tools/lembar_kerja.py buat --kode dialek-baru
python3 tools/lembar_kerja.py rangka --kode dialek-baru --nama "Dialek Baru"
python3 tools/lembar_kerja.py periksa --kode dialek-baru
python3 tools/lembar_kerja.py laporan --kode dialek-baru
python3 tools/lembar_kerja.py json --kode dialek-baru
python3 tools/cek_dialek.py --kode dialek-baru
python3 tools/cek_dialek.py --kode dialek-baru --ketat
python3 tools/sinkron_tutorial.py --bangun dialek-baru
python3 make_highlight.py
python3 build.py
```

## 6. Write the notes file

`rangka` writes a stub with the required headings. Replace every placeholder.
The file must contain:

1. **Provenance** — who supplied the words, which worksheet or dictionary,
   which speaker, the date, and the licence.
2. **Orthography** — the spelling rules you decided in section 2.
3. **Mapping decisions** — one line for every non-obvious choice: a joined
   phrase, a word used for two IDs, a word deliberately not used, an English
   fallback. Include the worksheet row or ID.
4. **Review record** — who reviewed what and when. `draft` is not `review`.
   Never write a review that did not happen.
5. **Gaps** — every ID still missing, with the concept and what has been tried.
   A gap is honest; a guess is not.

Use [`dialects/koto-payang.md`](../dialects/koto-payang.md) as the worked
example. The DOCX rendered by `lembar_kerja.py docx` is an optional review view
for speakers. Do not treat it as the canonical file, and do not read it back
unless you generated it with this tool.

## 7. Promote the status

The status ladder has four values:

| Status | Gate |
|---|---|
| `draft` | The default. A skeleton, or partly filled. No promise of review. |
| `review` | All 32 Tier 1 rows are `reviewed`, and the JSON has at least one source. |
| `approved` | All Tier 1 and Tier 2 rows are `reviewed`, the JSON has a named reviewer, and it has at least one source. |
| `deprecated` | Kept for history. Do not start a new program in it. |

Promotion is an explicit edit:

1. Open the JSON skeleton and change `"status": "draft"` to `"review"`.
2. Fill `sources` with the real source strings.
3. Run `periksa --siap`, then `json`, then `cek_dialek` (section 8).
4. For `approved`, also fill `reviewer` with the named person, then repeat the
   checks.

Do not mark a dialect `approved` to make a test pass or to make a release look
complete. `approved` is the speaker's decision, not the contributor's.

## 8. Validate

```bash
python3 tools/cek_dialek.py --kode dialek-baru
python3 tools/cek_dialek.py --kode dialek-baru --ketat
```

`cek_dialek --kode` loads the file, checks every rule, and prints tier counts.
It exits 0 when the file is valid.

`cek_dialek --ketat` is the strict view. It refuses an `approved` dialect that
still borrows a Tier 1 word from the neutral base. It does not fail a `draft`
or `review` dialect for a gap.

Now run a real program. Create a temporary file with the dialect header on the
first line:

```krc
# dialek: dialek-baru
nyetak "halo"
```

`nyetak` is the Siulak spelling of `print`. Replace it with your dialect's own
word for the print function. Run the file with `krc` (or
`python3 dist/krc.pyz`) and check the output.

If your dialect does not own a word the program needs, the runtime uses the
English base and prints one warning per missing ID on stderr. Stdout stays
clean. A warning is not an error; it is a to-do for the next speaker pass.

## 9. Tutorial

Generate a local tutorial tree to see your dialect in the lessons:

```bash
python3 tools/sinkron_tutorial.py --bangun dialek-baru
```

This writes English and Indonesian trees under `tutorial/`. It runs every
block in your dialect, compares normalized output with the Siulak baseline, and
refuses to replace the destination if a block fails.

- Only commit a generated tree for a dialect that is at least `review`.
- Run `python3 tools/sinkron_tutorial.py --semua-dialek` when every
  `review` / `approved` dialect should be regenerated.
- Extend [`tests/test_tutorial_dialects.py`](../tests/test_tutorial_dialects.py)
  with a case for the new dialect before you commit its tree.
- Never edit generated tutorial output by hand. Regenerate it.

A generated tree lists the surface words that fell back to English, so a
speaker can see exactly which gaps remain.

## 10. Editor and glossary

- `python3 make_highlight.py` reads every dialect through the loader and
  regenerates one union VS Code grammar. Your words are picked up
  automatically; do not hand-edit the grammar.
- `python3 tools/buat_glosarium.py` remains the Siulak glossary. It is not
  regenerated for a new dialect.
- A generated tutorial tree gets a glossary stub with local error-message
  headings. A full glossary waits until the dialect is `approved`.

## 11. Tests and CI

Run the full offline build before every commit:

```bash
python3 build.py
```

`build.py` runs the language suite, the baseline tutorial, the dialect suites,
the worksheet suite, the migration suite, the translator suite, the generated
tutorial suite, and the docs-release suite. It stops on the first failure.

Before a release, run the wheel smoke described in [`RELEASING.md`](../RELEASING.md):

```bash
python3 tests/test_release.py
```

The shared suites already validate your JSON, load it, run it, and check its
tutorial tree. Add a focused test module beside
[`tests/test_koto_payang.py`](../tests/test_koto_payang.py) only when your
dialect pins exact words or exact messages that the shared tests cannot know.

## 12. Checklist and common errors

Before you open a pull request:

- [ ] The code matches `^[a-z0-9-]+$`, and the three file names use it.
- [ ] Tier 1 is complete; Tier 2 is as complete as the speakers can make it.
- [ ] Every `reviewed` row has a real speaker behind it.
- [ ] The notes file has provenance, orthography, mapping decisions, review
      record, and gaps.
- [ ] `periksa --siap`, `laporan`, `json`, and `cek_dialek` pass.
- [ ] A program with `# dialek: <code>` runs.
- [ ] If the dialect is `review`, its tutorial trees are generated and fresh.
- [ ] `python3 build.py` passes, and `python3 make_highlight.py` left no diff.
- [ ] No Siulak word was copied to fill a gap and no status was overstated.

Common errors:

| Message or problem | Cause and fix |
|---|---|
| `unknown-id` | The CSV row's ID is not in `core/ids.json`. Restore the catalogue ID; never invent one. |
| `duplicate-id` | The ID appears twice. Keep one row. |
| `answer-choice` | The answer contains `/` or `,`. Choose one form; put the other in `notes`. |
| `word-charset` / `word-case` | The word is not lowercase `^[a-z][a-z0-9_]*$`. Join with `_`, remove spaces and punctuation. |
| `clash` | A word is used by two guarded IDs (`kw`, `op`, `reserved`, `fn`). Pick a different word for one of them. |
| `message-placeholder` | A message lost or renamed a placeholder. Restore the exact `{...}` names from the catalogue. |
| `answer-empty` | A `draft` or `reviewed` row has no answer. Fill it or set the row to `todo`. |
| `source-missing` | A `review` or `approved` dialect needs at least one source. Add the dictionary or speaker record. |
| `reviewer-missing` | An `approved` dialect needs a named reviewer. Do not invent one. |
| `status: not ready for review` | Tier 1 still has unreviewed rows. Finish them or stay at `draft`. |
| `status: not ready for approved` | Tier 1 or Tier 2 still has unreviewed rows. Finish them or stay at `review`. |
| `skeleton-missing` | `json` or `periksa --siap` cannot find the JSON. Run `rangka` first. |
| A fallback warning on stderr | The dialect does not own that ID. It is using the English base. Record it as a gap; do not guess a word. |

The full history of the multi-dialect design is in
[`08-multi-dialect-plan-review.md`](08-multi-dialect-plan-review.md). The
runtime details are in [`04-implementation.md`](04-implementation.md).
