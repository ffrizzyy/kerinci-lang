# Spec: tutorial-multidialect

Status: **implemented 2026-11-02.** Parent: `SPEC.md`. Capability map:
`tutorial-multidialect`.
Depends on `runtime-selection`, `dialect-siulak-legacy`, and
`dialect-koto-payang`, all implemented. Date: 2026-11-02.

## 1. Objective

Teach the same 14 lessons in more than one dialect without maintaining a second
copy of the prose. The Siulak tutorial is already tested block by block; it
becomes the canonical lesson source. A generator maps its code and inline code
words to another dialect, runs every block in that dialect, refreshes the
printed `hasil`, and writes a checked-in tree:

```text
tutorial/en/koto-payang/
tutorial/id/koto-payang/
```

After this module:

- A learner can read the whole English or Indonesian course with Koto Payang
  code and Koto Payang output.
- Every generated block runs with a `# dialek: koto-payang` header, and a
  `krc-berkas` helper carries the same header.
- The generated output is the real output of the real interpreter, not a
  hand edit.
- Regenerating the tree is deterministic and byte-identical.
- The existing lesson files, their expected output, and their count do not
  change; only the two tutorial index pages gain a pointer to the generated
  trees, and `tests/test_tutorial.py` still checks exactly the same 550 blocks.

## 2. Scope

### In scope

- A dialect-build mode in `tools/sinkron_tutorial.py`.
- Word mapping for code fences and inline code spans.
- Header injection into every generated code fence and helper file.
- Re-running every generated block and rewriting its `hasil`.
- Relative-link re-resolution and dialect-name replacement in generated prose.
- A generated index, answers page, and a glossary stub per tree.
- Review-status fallbacks shown honestly in the generated index and warnings.
- `tests/test_tutorial_dialects.py`.
- Narrowing `tests/test_tutorial.py` and the default generator pass to the
  baseline lesson paths only, so the 550 count is unchanged.
- Doc updates for the generated tutorial.

### Out of scope

- Editing the existing Siulak lessons, their expected output, or their count.
- Translating the prose into Kerinci; that stays a speaker-led task.
- Translating message text in prose; only code words are rewritten.
- Generating a full dialect glossary. The generated tree links to the Siulak
  glossary and explains the delay.
- Generating the `tutorial/kerinci/` tree.
- Generating a tree for a dialect whose status is `draft` as a committed
  artifact. `draft` may be generated into a temporary directory for tests.
- Adding a dialect, changing a word, changing the catalogue, or changing the
  runtime.
- A web or VS Code tutorial viewer.
- Committing a second `tutorial/src/` copy of the prose (see D1).

## 3. Tool interface

The existing command keeps its current job and gains a build mode:

```bash
python3 tools/sinkron_tutorial.py                  # check the baseline, 550 blocks
python3 tools/sinkron_tutorial.py --tulis          # refresh baseline hasil
python3 tools/sinkron_tutorial.py --bangun KODE    # write tutorial/{en,id}/KODE/
python3 tools/sinkron_tutorial.py --bangun KODE --prosa en
python3 tools/sinkron_tutorial.py --bangun KODE --keluaran DIR
python3 tools/sinkron_tutorial.py --semua-dialek   # every review/approved dialect
```

| Option | Meaning |
|---|---|
| `--bangun KODE` | build one dialect tree |
| `--semua-dialek` | build every dialect whose status is `review` or `approved` |
| `--prosa en\|id\|semua` | prose axis to build; default `semua` |
| `--keluaran DIR` | destination root; default `tutorial/` |
| `--tulis` | unchanged: refresh the baseline `hasil` blocks |

Rules:

- `--bangun` and `--semua-dialek` are mutually exclusive.
- `--tulis` may not be combined with a build mode (`--bangun` or
  `--semua-dialek`).
- `--prosa` and `--keluaran` require a build mode.
- An unknown dialect, or a dialect file that fails the loader, is a usage error
  (exit 2) before any file is written.
- `siulak` and `base` may be built into a temporary directory for tests, but
  `--semua-dialek` does not build them. `siulak` is the canonical source, and
  `base` is not a spoken tutorial.
- With `--keluaran DIR`, the output is `DIR/en/<code>/` and/or
  `DIR/id/<code>/`. The committed default is `tutorial/`.
- No option lets the build write into the baseline files.

## 4. Canonical source and generated layout

The source of truth is the baseline tutorial:

```text
tutorial/*.md              English, Siulak
tutorial/id/*.md           Indonesian, Siulak
tutorial/kerinci/          Kerinci prose guide (not generated)
```

A build reads those files and writes:

```text
tutorial/en/<code>/README.md
tutorial/en/<code>/00-setup.md ... 13-project.md
tutorial/en/<code>/answers.md
tutorial/en/<code>/glossary.md          stub
tutorial/id/<code>/README.md
tutorial/id/<code>/00-persiapan.md ... 13-proyek.md
tutorial/id/<code>/jawaban.md
tutorial/id/<code>/glosarium.md        stub
```

The generated tree is committed for `koto-payang`. It is not committed for
`siulak` (the baseline already is) or for any `draft` dialect.

The generator reads the baseline with UTF-8 and preserves line endings. The
baseline currently uses LF in the repository; generated files use LF as well.
No BOM is written.

### Why not `tutorial/src/` yet (D1)

The parent plan proposed `tutorial/src/` with `{{id}}` placeholders. For 0.6
that would duplicate roughly 175 KB of English and Indonesian prose, and every
prose edit would have to be made twice. The tested Siulak lessons already are
the single written copy; the generator maps words by neutral ID, so the same
"write once, generate every dialect" property holds without the second copy.
If a placeholder source is still wanted later, `docs-release` can introduce it
without changing the generator contract.

## 5. What is generated and what is copied

| Part | Treatment |
|---|---|
| `krc` and `krc-error` code fence | word-mapped, given a dialect header, run, and paired with fresh `hasil` |
| `krc-berkas` helper fence | a helper ending in `.krc` is word-mapped and given a dialect header; any other helper is raw data and is copied byte for byte; both are written to the temp project before later blocks |
| `hasil` fence | replaced with the real output of the block above |
| inline code span `` `...` `` in prose | word-mapped with the same rules |
| ordinary prose | copied byte for byte, except dialect-name and link fixes |
| other fences (`bash`, `text`, ...) | copied byte for byte |
| `# dialek:` header already in a block | replaced with the target code, never duplicated |

### Word mapping

The mapping is the same one the translator uses, by neutral ID:

- `kw.*`, `op.*`, `fn.*`, and `reserved.*` words are replaced with the target
  word for the same ID.
- The direct second argument of a `bukak` call is replaced as a `mode.*` word.
- Comments, string data, numbers, punctuation, user names, and formatting are
  not rewritten.
- `{` `}` stay braces; `mulai` / `habih` in a block are rewritten as words
  because they are lexed code, exactly as `krc terjemah` does.
- A target word that is not a valid identifier, or that collides with a name
  the block declares, fails the build with the file and block location. It is
  never silently renamed.

The generator may reuse the translator's scanner through a small public
function rather than importing a private name. That function returns the
rewritten text and the set of IDs used. It does not execute the program.

### Inline code spans

A code span `` `...` `` is mapped with the same scanner, with three refinements
that keep prose readable and avoid inventing a base fallback that the corpus
does not need:

- A span that looks like an expression (more than one word, or containing
  `()[]{}.,=<>!+-*/%`) is passed through `rewrite_dialect_words`.
- A bare identifier span takes the target word for a matching ID only when the
  target owns that ID; `fn.contains` and `type.bool` may use their base
  fallbacks. The generator never adds a new fallback such as `list` or `map`
  merely to translate prose.
- A cell in a Markdown table column headed `Kind` or `Jenis` is mapped as a
  `type.*` word, so the type table in lesson 2 names the target dialect's type
  words rather than a built-in function with the same spelling.

If a span cannot be mapped under these rules, it is left as written. A bare
prose mention of a word outside backticks is never guessed at.

### Headers

Every generated `krc`, `krc-error`, and `.krc` helper fence begins with:

```text
# dialek: <code>
```

The header is inside the fence, so a reader can copy the block and run it.
The runner supplies the same header to helper files. A headerless baseline
block therefore gains exactly one line in the generated tree.

A `krc-berkas` helper whose name does not end in `.krc` is data, not code: its
bytes are copied unchanged and it gets no header. The tutorial corpus includes
`nilai.txt`; adding a header there would corrupt the file the lesson reads.

### Fallbacks

The generator does **not** refuse when the target lacks an ID the way
`krc terjemah` does. A tutorial must still teach the feature. It uses the
dialect's base fallback, records the ID, and reports it:

- `koto-payang` currently falls back for `fn.contains` and `type.bool` in the
  tutorial corpus, which prints as `contains` and `boolean`.
- The generated index lists the fallback words that actually occur.
- A warning goes to stderr once per ID per build, naming the ID and the word.
- The build exits 0; fallbacks are a review fact, not a generation failure.

No invented word is allowed. If a dialect has no word and no base fallback, the
build fails; the catalogue guarantees a fallback today.

## 6. Output, prose, links, and glossary

### Output

- The real stdout of the block goes into the `hasil` fence.
- A `krc-error` block's output is `Kesalahan: <real message>`, exactly as the
  baseline harness prints it.
- Trailing spaces are preserved inside `hasil`; the block always ends with a
  newline before the closing fence.
- The build fails if a `krc` block raises, if a `krc-error` block succeeds, if a
  `hasil` block is missing, or if a fence is unclosed.

### Prose

- Every generated lesson ends with a generated footer:

  ```text
  ---
  *Generated from the Siulak lesson. Code and inline code use Koto Payang
  (status: review).*
  ```

  The Indonesian tree uses an Indonesian footer with the same facts.
- The source dialect noun is replaced with the target display name (`Siulak`
  becomes `Koto Payang`). This is a proper-noun replacement, not a word
  translation.
- No other prose sentence is rewritten. A bare mention of a dialect word that
  is not inside backticks stays as written; the generator does not guess.
- Inline code spans are mapped, so the "New words" table in the index shows the
  target words.

### Links

Every Markdown link that is relative is re-resolved from the generated file's
directory to the same target it had from the source file. This fixes the extra
directory level:

- `../CONTRIBUTING.md` becomes `../../../CONTRIBUTING.md` in the English tree.
- `../../CONTRIBUTING.md` becomes `../../../CONTRIBUTING.md` in the Indonesian
  tree.
- Cross-tree links (`README`, `id/`, `../README.md`) point at the generated
  sibling tree where one exists, or at the baseline otherwise.
- Fragments (`#lesson-1`, `#error-messages`) are preserved.
- The build fails if a link target inside the repository does not exist after
  re-resolution.

### Glossary

A generated glossary is a stub, not a translated word table. English:

```text
# Glossary

This tutorial is generated for Koto Payang (status: review). The full glossary
is still the Siulak one: [glossary](../../glossary.md). A Koto Payang glossary
follows when the dialect is approved.

## Error messages

The error messages are explained in the [Siulak glossary's error
messages section](../../glossary.md#error-messages). They will be
listed here when the dialect is approved.
```

The Indonesian tree writes `glosarium.md` with the same notice in Indonesian,
links to `../../id/glosarium.md`, and gives the local section the heading
`Kesalahan` so a `#kesalahan` fragment resolves. The local `#error-messages` /
`#kesalahan` headings keep the existing fragment links useful even before a
full dialect glossary exists. The stub exists so every link in the lessons
resolves.

## 7. Tests: `tests/test_tutorial_dialects.py`

Plain-Python style, all work in `tempfile.TemporaryDirectory()`, and it exits 1
on any failure. The suite covers:

1. **Determinism.** Building `koto-payang` twice into two temp roots produces
   identical bytes for every file.
2. **Committed tree matches.** The committed `tutorial/en/koto-payang/` and
   `tutorial/id/koto-payang/` are byte-identical to a fresh build.
3. **Baseline untouched.** The baseline lesson files still have no generated
   header or footer, and `tests/test_tutorial.py` still reports 550 blocks.
4. **Siulak self-build.** Building `siulak` into a temp root produces code
   blocks whose text minus the injected header equals the baseline block text,
   with the same block kinds, order, and `info` strings.
5. **Every generated block runs.** For both prose axes, every `krc` block runs
   without error, every `krc-error` block fails, and every `hasil` matches the
   real output.
6. **Helper files.** A lesson with `krc-berkas` writes each `.krc` helper with
   the target header and leaves a non-`.krc` helper as raw bytes, and the later
   blocks import the helper successfully.
7. **Normalized equivalence.** For every baseline block and its generated
   counterpart, stdout matches after normalizing dialect output words and
   message templates to neutral IDs, and errors match by `msg_id` plus
   normalized arguments. This is the parent's equivalence rule.
8. **Fallbacks.** The generated tree contains exactly the expected fallback
   surfaces for Koto Payang (`contains` in code, `boolean` in output), the
   index lists them, and the build warning names `fn.contains` and `type.bool`.
   No other base word appears in a code fence.
9. **Headers.** Every `krc` / `krc-error` fence and every `.krc` helper in the
   generated tree starts with `# dialek: koto-payang`; no baseline fence does.
   A raw-data helper keeps its bytes.
10. **Links and index.** Every relative link in the generated tree resolves to
    an existing file (fragments ignored), each generated `README.md` links all
    14 lessons, and the glossary stub exists.
11. **Prose fidelity.** Outside code fences and links, the generated prose
    equals the baseline prose after the documented dialect-name and footer
    changes; no other sentence changed.
12. **Usage errors.** An unknown dialect, `--tulis` with `--bangun`, `--prosa`
    without a build, and `--bangun` with no value each exit 2 and write
    nothing. `--semua-dialek` builds exactly `koto-payang` today.
13. **No output on refusal.** A deliberately broken temp lesson (a `krc` block
    that raises) makes the build exit 1 and leaves the destination unchanged.

The suite should land near 80 checks, dominated by the per-lesson loop but
reported as one PASS per group plus a count.

## 8. Boundaries

### Always

- Keep the baseline lesson code and its 550-block count unchanged; the index
  pages may gain a pointer to the generated trees.
- Write only under the requested output root; never into the baseline files.
- Map words by neutral ID; never invent a word.
- Run every generated block with its dialect header.
- Regenerate `hasil` from the real interpreter.
- Report base fallbacks in the index and on stderr.
- Re-resolve links and fail on a broken one.
- Keep the build deterministic and repeated builds byte-identical.

### Ask first

- Translating prose, or writing a Kerinci-prose tutorial.
- Generating a full dialect glossary.
- Committing a tree for a `draft` dialect.
- Introducing `tutorial/src/` and a second prose copy.
- Adding a new dialect or changing a word to make a tutorial read better.
- Changing the 550-block baseline or any expected baseline output.

### Never

- Hand-edit a generated lesson or a `hasil` block.
- Edit a baseline lesson to make generation easier.
- Rewrite a comment, ordinary string, user name, number, or formatting.
- Emit an invented or guessed word.
- Hide a base fallback or write a warning to stdout.
- Change the runtime, the catalogue, a dialect file, or an earlier test
  expectation.
- Run user code outside the temporary lesson directory.

## 9. Success criteria

1. `python3 tools/sinkron_tutorial.py` still reports 550 blocks and 0 problems.
2. `python3 tests/test_tutorial.py` passes with the same lesson counts and the
   glossary check.
3. `python3 tools/sinkron_tutorial.py --bangun koto-payang` is deterministic,
   writes both prose trees, and warns only about the fallbacks actually used.
4. `tutorial/en/koto-payang/` and `tutorial/id/koto-payang/` are committed,
   every lesson has 14 links, and every block runs in Koto Payang.
5. Normalized output and error identity match the Siulak baseline for every
   block.
6. No baseline lesson, expected output, catalogue entry, dialect word, example,
   or runtime behaviour changes; only the two index pages point at the new
   trees.
7. `tests/test_tutorial_dialects.py` passes and all earlier suites stay green;
   `cek_dialek --semua`, the generators, `compileall`, and `build.py` pass.
8. `CAPABILITY-MAP.md`, `docs/03`, `docs/04`, `docs/05`, `README.md`, and
   `tutorial/README.md` describe the generated trees and the review caveats.

## 10. Decisions

| # | Decision | Recommendation |
|---|---|---|
| D1 | Use the tested Siulak lessons as the canonical source; defer `tutorial/src/` prose duplication. | Yes: one written copy, no drift, ~175 KB less duplication. |
| D2 | Commit only the Koto Payang generated trees; keep Siulak in place. | Yes: no duplicate baseline. |
| D3 | Put `# dialek: <code>` inside every generated code fence. | Yes: copy-paste blocks run as-is. |
| D4 | Allow base fallbacks in generated code and show them in the index. | Yes: a review dialect must still teach the feature; refusing would drop lessons. |
| D5 | Regenerate `hasil` by running the block; never hand-edit. | Yes: the printed output is the oracle. |
| D6 | Generate a glossary stub, not a translated glossary. | Yes: avoids a second unreviewed word table; a full glossary is `docs-release`. |
| D7 | Narrow `test_tutorial.py` discovery to the baseline paths. | Yes: created trees must not double-count or be run as baseline. |
| D8 | Keep prose English/Indonesian; map inline code only. | Yes: parent decision; bare prose mentions are not guessed at. |
| D9 | Reuse the translator's word scanner through a small public helper. | Yes: one rewriting rule, tested twice. |
| D10 | Fail on a broken relative link or an unexpandable block. | Yes: a generated tutorial with dead links is not shippable. |

## 11. Next step

On approval: archive the translator plan/todo, write `tasks/plan.md` and
`tasks/todo.md`, add the build mode and the public word-rewrite helper, narrow
the baseline discovery, generate and commit both Koto Payang trees, add
`tests/test_tutorial_dialects.py`, run all eleven suites plus
`cek_dialek --semua`, the generators, `compileall`, `build.py`, and the zipapp
smoke test, update the docs and capability map, commit, and push.

## 12. Implementation log

Implemented 2026-11-02 as specified.

- `tools/sinkron_tutorial.py` gained `--bangun`, `--semua-dialek`, `--prosa`,
  and `--keluaran`. The default check and `tests/test_tutorial.py` use
  `baseline_paths()`, so the generated trees are not checked twice and the
  baseline still reports exactly 550 blocks.
- `kerincilang.py` exposes `rewrite_dialect_words` for code spans and
  `dialect_declared_names` for the collision check. The build uses the same
  scanner as `krc terjemah`; it never runs code to map words.
- Both Koto Payang trees are committed under `tutorial/en/koto-payang/` and
  `tutorial/id/koto-payang/`: 34 files and 268 runnable blocks. Every generated
  block was run again after writing and matched its regenerated `hasil`.
  `.gitattributes` pins those two trees to LF so a Windows checkout is still
  byte-identical to a fresh build.
- The only base fallbacks the corpus uses are `fn.contains` (`contains`) and
  `type.bool` (`boolean`). The index lists both and the build writes one stderr
  warning per ID; the build still exits 0.
- A `.krc` helper gets the dialect header and is word-mapped. `nilai.txt` is raw
  data, so it keeps its bytes and gets no header; the lesson's file code runs
  unchanged.
- Inline spans use the policy in section 5. The lesson 2 type table maps
  kind-column cells as `type.*`, so the table names `bilangan_buluak`,
  `bilangan_bakoma`, `tulisan`, `daftar`, `kamus`, `boolean`, and `kusao`
  instead of reading as function calls.
- The glossary stubs link to the Siulak glossary and add local
  `## Error messages` / `## Kesalahan` sections, so existing fragments resolve.
- `tests/test_tutorial_dialects.py` reports 20 checks covering the thirteen
  groups: determinism, the committed tree, the untouched baseline, the Siulak
  self-build, every generated block, helper headers, normalized equivalence,
  fallbacks, headers, links/index/glossary, prose fidelity, usage errors, and
  transactional failure.
- All eleven suites, `cek_dialek --semua`, `make_highlight.py`,
  `buat_glosarium.py`, `compileall`, `build.py`, and a `dist/krc.pyz` run pass.
  No baseline lesson, expected output, catalogue entry, dialect word, or
  earlier test expectation changed.
