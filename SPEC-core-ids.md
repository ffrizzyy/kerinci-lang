# Spec: core-ids

Status: **draft for approval.** Parent: `SPEC.md`. Capability map: `core-ids`.
Date: 2026-11-02.

## 1. Objective

Freeze the neutral contract of the language and remove dialect words from the engine's logic.

After this module:

- Every meaningful word has a stable neutral ID in `core/ids.json`.
- The lexer, parser, runtime, and messages operate on neutral IDs.
- The interpreter still runs **exactly** the Siulak v0.5 language, through a built-in legacy vocabulary.
- The 271 language tests, 550 tutorial blocks, glossary generator, syntax-highlight generator, and single-file build still work.

This is the foundation for `dialect-model`. Doing it first prevents every later module from depending on Siulak words, and it makes the "add a dialect means add a file" promise possible.

## 2. Scope

### In scope

- `core/ids.json` and its schema.
- A `Vocabulary` seam and a `LegacySiulak` implementation.
- Neutral token kinds.
- Built-ins, type names, file modes, and messages keyed by neutral IDs.
- `Env.vocab`, `show(v, vocab)`, `new_global(vocab)`, and an active-vocabulary stack.
- Compatibility exports for existing tools/tests.
- Package data so the catalogue works from a checkout, a wheel, and `dist/krc.pyz`.
- New tests for catalogue integrity and neutralisation.

### Out of scope

- Loading `dialects/*.json`.
- The `# dialek:` header, `--dialek`, `--ketat`, per-file/per-module dialects.
- `krc migrasi`, `krc terjemah`.
- Worksheet tools.
- Tutorial generation.
- Section 9 language fixes.
- Any change to a Siulak word or to user-visible output.

`runtime-selection` will replace the single active vocabulary with a per-module one. The seam added here must make that replacement small.

## 3. Contract: `core/ids.json`

`core/ids.json` is the single source of truth for IDs. Dialect files only supply words. The file is UTF-8 JSON, 2-space indent, keys sorted.

```json
{
  "core": "0.6",
  "ids": {
    "kw.if": {
      "namespace": "kw",
      "tier": 1,
      "en": "if",
      "id_gloss": "jika",
      "description": "Starts a conditional block.",
      "example": "kalu x > 5 { ... }",
      "arity": null,
      "placeholders": []
    },
    "fn.length": {
      "namespace": "fn",
      "tier": 2,
      "en": "length",
      "id_gloss": "panjang",
      "description": "Number of items in a list or map, or characters in text.",
      "example": "panjang(\"kerinci\")",
      "arity": 1,
      "placeholders": []
    },
    "msg.div_zero": {
      "namespace": "msg",
      "tier": 2,
      "en": "Division by zero",
      "id_gloss": "Pembagian dengan nol",
      "description": "Raised when the right side of / or % is zero.",
      "example": "nyetak 1 / 0",
      "arity": null,
      "placeholders": []
    }
  }
}
```

Rules:

- `core` is the minimum catalogue version. For this module it is `"0.6"`.
- `ids` is keyed by the ID itself; every entry repeats `namespace`, which must match the ID prefix.
- `namespace` is one of `kw`, `op`, `fn`, `type`, `mode`, `msg`, `reserved`. `val` is **not** used (see decision D1).
- `tier` is `1`, `2`, or `3`.
- `en` is the neutral English word for a word ID, or the English template for a `msg.*` ID.
- `id_gloss` is the Bahasa Indonesia gloss for a word ID, or the Indonesian template for a `msg.*` ID.
- `description` and `example` are required for every ID. For `msg.*`, `example` is a sample rendered sentence.
- `arity` is an integer for built-ins (`fn.*`), `null` otherwise.
- `placeholders` is a list of placeholder names for `msg.*` and empty otherwise. A placeholder name matches `[a-z][a-z0-9_]*`.
- IDs are immutable after release. Changing one is an `Ask first`.
- `core/ids.json` contains **no Siulak words**. The Siulak mapping lives in the legacy vocabulary table until `dialect-siulak-legacy` externalizes it.

## 4. ID inventory

This is the v0.6 live set. The legacy column is the Siulak v0.5 word, used by `LegacySiulak` and the compatibility exports; it is not part of the neutral contract.

### Keywords (`kw.*`, tier 1)

| ID | Old kind | English | Siulak v0.5 |
|---|---|---|---|
| `kw.var` | `VAR` | variable | `barang` |
| `kw.const` | `CONST` | constant | `tetap` |
| `kw.func` | `FUNC` | function | `guno` |
| `kw.return` | `RETURN` | return | `balik` |
| `kw.if` | `IF` | if | `kalu` |
| `kw.else` | `ELSE` | else | `lain` |
| `kw.while` | `WHILE` | while | `selamo` |
| `kw.for` | `FOR` | for | `untuk` |
| `kw.in` | `IN` | in | `alem` |
| `kw.switch` | `SWITCH` | switch | `pilih` |
| `kw.import` | `IMPORT` | import | `ambik` |
| `kw.try` | `TRY` | try | `cubo` |
| `kw.catch` | `CATCH` | catch | `tangkap` |
| `kw.raise` | `RAISE` | raise | `ngangkat` |
| `kw.break` | `BREAK` | break | `putuh` |
| `kw.continue` | `CONTINUE` | continue | `lanjut` |
| `kw.print` | `PRINT` | print | `nyetak` |
| `kw.input` | `INPUT` | input | `tanyo` |
| `kw.true` | `TRUE` | true | `betul` |
| `kw.false` | `FALSE` | false | `salah` |
| `kw.null` | `NULL` | null | `kosong` |
| `kw.and` | `AND` | and | `ngan` |
| `kw.or` | `OR` | or | `apo` |
| `kw.not` | `NOT` | not | `idak` |
| `kw.begin` | `BEGIN` | begin block | `mulai` |
| `kw.end` | `END` | end block | `habih` |

### Comparison words (`op.*`, tier 1)

| ID | Symbol | English | Siulak v0.5 |
|---|---|---|---|
| `op.eq` | `==` | equal | `samo` |
| `op.ne` | `!=` | not equal | `dak_samo` |
| `op.gt` | `>` | greater than | `lebih_daripado` |
| `op.lt` | `<` | less than | `kurang_daripado` |
| `op.ge` | `>=` | greater or equal | `lebih_samo` |
| `op.le` | `<=` | less or equal | `kurang_samo` |

### Built-in functions (`fn.*`, tier 2)

| ID | English | Siulak v0.5 | Arity |
|---|---|---|---|
| `fn.length` | length | `panjang` | 1 |
| `fn.list` | list | `daftar` | variadic |
| `fn.add` | add | `tambah` | 2 |
| `fn.sub` | subtract | `kurang` | 2 |
| `fn.mul` | multiply | `kali` | 2 |
| `fn.div` | divide | `bagi` | 2 |
| `fn.range` | range | `jarak` | 1-3 |
| `fn.append` | append | `nambahkah` | 2 |
| `fn.contains` | contains | `isi` | 2 |
| `fn.sort` | sort | `milih` | 1 |
| `fn.reverse` | reverse | `pulang` | 1 |
| `fn.int` | integer | `bilangan` | 1 |
| `fn.float` | decimal | `pecahan` | 1 |
| `fn.text` | text | `kato` | 1 |
| `fn.type` | type | `mecem` | 1 |
| `fn.map` | map | `peta` | variadic |
| `fn.split` | split | `pisah` | 1-2 |
| `fn.join` | join | `disatu` | 1-2 |
| `fn.open` | open | `bukak` | 1-2 |
| `fn.read` | read | `baco` | 1 |
| `fn.write` | write | `tulis` | 2 |
| `fn.close` | close | `tutup` | 1 |
| `fn.delete` | delete | `hapus` | 1 |
| `fn.wait` | wait | `nantik` | 1 |

### Type names (`type.*`, tier 2)

| ID | English | Siulak v0.5 |
|---|---|---|
| `type.int` | int | `bilangan` |
| `type.float` | float | `pecahan` |
| `type.str` | text | `kato` |
| `type.list` | list | `daftar` |
| `type.map` | map | `peta` |
| `type.func` | function | `guno` |
| `type.null` | null | `kosong` |
| `type.bool` | boolean | `boolean` (placeholder) |
| `type.file` | file | `berkas` |

### File modes (`mode.*`, tier 2)

| ID | English | Siulak v0.5 |
|---|---|---|
| `mode.read` | read | `baco` |
| `mode.write` | write | `tulis` |
| `mode.append` | append | `nambahkah` |

### Reserved (`reserved.*`, tier 3)

| ID | English | Siulak v0.5 |
|---|---|---|
| `reserved.error` | error | `kelihu` |

### Messages (`msg.*`, tier 2)

There are **61 `LangError` raise sites and 59 unique templates** in v0.5, plus the CLI/REPL prefix (out of scope here). The implementation must inventory every site into `core/ids.json`; the worksheet's 24 message rows are a subset, not the whole set.

Naming: `msg.<area>.<name>`, for example:

- `msg.syntax.expected`, `msg.syntax.unexpected`, `msg.syntax.bad_char`, `msg.syntax.reserved`, `msg.syntax.escape`
- `msg.name.undefined`, `msg.name.undeclared`, `msg.name.constant`
- `msg.value.div_zero`, `msg.value.operator`, `msg.value.convert`, `msg.value.index_range`, `msg.value.index_type`, `msg.value.key_missing`, `msg.value.key_type`, `msg.value.text_immutable`
- `msg.call.arity`, `msg.call.not_function`, `msg.call.depth`
- `msg.file.not_found`, `msg.file.closed`, `msg.file.wrong_mode`, `msg.file.is_dir`, `msg.file.permission`, `msg.file.io`, `msg.file.not_utf8`
- `msg.import.not_text`, `msg.import.not_found`, `msg.import.circular`, `msg.import.in_module`
- `msg.loop.break`, `msg.loop.continue`, `msg.func.return`
- `msg.try.requires_catch`

Rules:

- Every placeholder is declared in `core/ids.json`.
- `en` and `id_gloss` use the **same** placeholder set.
- Templates use `{name}` only. `!r`, `!s`, and positional fields are not used; callers pass display-ready strings.
- A missing key in formatting is a bug and must fail a test. In production, render a safe diagnostic rather than a Python traceback.
- The user's own `ngangkat` text is **not** a catalogue message; it passes through unchanged.

## 5. Vocabulary seam

```python
class Vocabulary:
    core: str
    def word(self, id: str) -> str: ...
    def message(self, id: str) -> str: ...
    def mode_id(self, word: str) -> str | None: ...
    def surface(self) -> dict[str, str]: ...   # word -> token ID
    def operators(self) -> dict[str, str]: ... # word -> symbol
    def reserved(self) -> set[str]: ...
```

`LegacySiulak` implements it from the table in section 4, plus the message templates.

`get_active_vocab()` returns the current vocabulary. `run_source` and `run_file` push it for the duration of a run; `do_import` pushes the imported module's vocabulary. `Env` stores `vocab` and inherits it from its parent.

For M1 there is one vocabulary per run. `runtime-selection` will push the callee's vocabulary around function calls. Record this in `docs/04-implementation.md` so it is not forgotten.

Public API additions (backward compatible):

```python
run_source(src, env=None, vocab=None)
run_file(path, env=None, vocab=None)
tokenize(src, vocab=None)
new_global(vocab=None)
show(value, vocab=None)
```

All existing one-argument calls keep working.

## 6. Lexer, parser, and runtime changes

### Token kinds

Semantic token kinds become IDs:

- Keyword: `("kw.if", "kw.if", line)`
- Comparison: `("op.eq", "==", line)`; the token text is the neutral symbol, not the dialect word
- Arithmetic/punctuation: `("OP", "+", line)` (unchanged)
- `IDENT`, `NUMBER`, `STRING`, `EOF` (unchanged)

`kw.begin` and `kw.end` still produce `("OP", "{", line)` and `("OP", "}", line)`, as today, so `is_incomplete` and the parser's brace handling do not change.

`tokenize` builds the surface map once per call from `vocab.surface()` and `vocab.operators()`. Do not rebuild it per token.

### Parser

- `Parser(tokens, vocab=None)`.
- Replace every `"VAR"`, `"IF"`, ... with `"kw.var"`, `"kw.if"`, ...
- `STATEMENT_STARTS` uses `kw.*` IDs.
- `equality` uses `op.eq`/`op.ne`; `comparison` uses `op.gt`/`op.lt`/`op.ge`/`op.le`.
- `unary` uses `kw.not`.
- `binary_op` continues to receive symbols (`"=="`, `"+"`), so its behavior is unchanged.
- `ev` compares `o == "kw.and"` / `"kw.or"` (not `KEYWORDS["AND"]`).
- Every parser error is a `msg.*` with the same rendered text as v0.5.

A `display(kind, text, vocab)` helper reproduces the old error text for `expect`/`unexpected`: punctuation stays as-is, an ID becomes the dialect's word. This is the only place the parser is allowed to ask the vocabulary for a word.

### Runtime

- `LangError` carries `msg_id` and `args` in addition to `text`.
- `msg(id, **args)` builds a `Message`; `LangError` renders it immediately with the active vocabulary and stores the result. `str(err)` is unchanged.
- `Env` gains `vocab`.
- `new_global(vocab)` registers each built-in under `vocab.word(fn_id)` and stores the `fn.*` ID in the builtin tuple (for display).
- `b_mecem` returns `vocab.word("type.*")`.
- `b_bukak` translates the mode string with `vocab.mode_id`, stores `mode.*` on `Berkas`, and compares mode IDs in `need_handle`/`iterate`. The default mode is `mode.read`.
- `show(v, vocab)` uses `vocab.word("kw.true"/"kw.false"/"kw.null")`, `vocab.word("type.file")`, `vocab.word("kw.func")`, and `vocab.word(fn_id)` for builtins.
- `do_import` wraps errors with `msg.import.in_module` and pushes the module vocabulary (the same one in M1).
- No internal `raise LangError("literal")` remains; every internal raise uses `msg(...)`. The only plain-string `LangError` is user `ngangkat`.

## 7. Compatibility layer

These names are imported or read by tests and tools. Keep them with exactly the same shape and values for Siulak v0.5:

| Export | Shape | Used by |
|---|---|---|
| `KEYWORDS` | `{"VAR": "barang", ...}` | `tests/test_kerincilang.py:426`, `make_highlight.py`, `tools/buat_glosarium.py` |
| `SURFACE` | `{"barang": "VAR", ...}` | internal compatibility |
| `WORD_OPERATORS` | `{"samo": "==", ...}` | `make_highlight.py`, `tools/buat_glosarium.py` |
| `BUILTINS` | `{"panjang": (1, fn), ...}` | `make_highlight.py`, `tools/buat_glosarium.py` |
| `TYPE_NAMES` | `{"int": "bilangan", ...}` | compatibility |
| `MODES` | `{"baco": "r", ...}` | compatibility |
| `RESERVED` | `{"kelihu"}` | `tools/buat_glosarium.py` |
| `ENABLE_WORD_OPERATORS` | `True` | compatibility |

Generate them from `LegacySiulak`; do not hand-maintain a second table.

`make_highlight.py` and `tools/buat_glosarium.py` must run and produce no diff in `vscode-extension/syntaxes/krc.tmLanguage.json`, `tutorial/glossary.md`, and `tutorial/id/glosarium.md`.

## 8. Project structure and packaging

```
core/
  __init__.py             NEW (empty; makes data importable)
  ids.json                NEW
dialects/
  __init__.py             NEW (empty; data package for the next module)
kerincilang.py            existing engine, refactored
tests/
  test_ids.py             NEW
  test_kerincilang.py     existing, unchanged
  test_tutorial.py        existing, unchanged
build.py                  updated to include core/ and dialects/
pyproject.toml            updated packages + package-data
docs/04-implementation.md updated with the vocabulary seam
```

Loading rule:

```python
from importlib.resources import files
import json

def load_catalog():
    data = files("core").joinpath("ids.json").read_text(encoding="utf-8")
    return json.loads(data)
```

This works from a checkout, an installed wheel (`core` is a package with package-data), and a zipapp (`build.py` copies `core/` into the archive). `dialects/` gets the same treatment in `dialect-model`.

`python kerincilang.py ...` must keep working. Do not convert the engine to a package in this module.

`pyproject.toml`:

```toml
[tool.setuptools]
py-modules = ["kerincilang"]
packages = ["core", "dialects"]

[tool.setuptools.package-data]
core = ["*.json"]
dialects = ["*.json", "*.md"]
```

`build.py` copies `kerincilang.py`, `core/`, and `dialects/` into the temporary zipapp directory. `__main__.py` stays as it is.

## 9. Code style

```python
# BAD: dialect words in the engine, literal message
if tok.text == "ngan":
    ...
raise LangError("Pembagian dengan nol")

# GOOD: neutral ID, message ID, vocabulary only at the boundary
if tok.kind == "kw.and":
    ...
raise LangError(msg("msg.value.div_zero"))

# GOOD: resolve the surface map once
surface = vocab.surface()
operators = vocab.operators()
```

Conventions:

- IDs are `namespace.snake_case`; message IDs are `msg.area.name`.
- No dialect word appears in `kerincilang.py` outside `LEGACY_WORDS`, `LegacySiulak`, and the compatibility views.
- No user-facing string is built with an f-string in the engine; use `msg(...)`.
- Keep the existing 4-space style, double quotes, and ~100-column lines.
- Keep Python 3.9 compatibility (`from __future__` is not needed; do not use `match`, `|` types, or `str.removeprefix`).
- JSON is 2-space indented and sorted.

## 10. Testing strategy

### Existing oracle

- `python tests/test_kerincilang.py` passes **271/271** unchanged.
- `python tests/test_tutorial.py` passes **550 blocks** unchanged.
- `python tools/buat_glosarium.py` passes and produces no diff.
- `python make_highlight.py` passes and produces no diff.
- `python build.py && python dist/krc.pyz examples/contoh.krc` works.

The existing tests are the oracle for message text and output. Do not update them to fit the refactor.

### New `tests/test_ids.py`

1. `core/ids.json` parses, has `core == "0.6"`, and every entry has all required fields.
2. Every `namespace` matches the ID prefix and is in the allowed set.
3. Every `tier` is 1, 2, or 3.
4. Every `fn.*` has an integer arity or `null` for variadic; every non-`fn.*` has `arity: null`.
5. Every `msg.*` has a non-empty `placeholders` list or an explicitly empty one; `en` and `id_gloss` use the same placeholder set.
6. `LegacySiulak` covers every live ID and no unknown ID.
7. Siulak keyword words are unique; comparison words are unique and disjoint from keywords; built-in words are disjoint from keywords and comparison words. Type and mode words may overlap anything (the namespace matrix).
8. A synthetic vocabulary (every ID mapped to a unique nonsense word) runs a small program covering variables, if/else, loops, functions, lists, maps, files (temp), errors, and `mecem`, proving the engine is neutral.
9. A second synthetic vocabulary with different true/false/null and type words proves `show` and `mecem` use the active vocabulary.
10. AST scan: every internal `LangError` call uses `msg(...)`; the only plain-string sites are the user `ngangkat` path (allowlist by line/function).
11. AST scan: every `msg("...")` ID exists in `core/ids.json`.
12. `show`, `mecem`, and `bukak` use the active vocabulary, not a module constant.

### Packaging test

`tests/test_ids.py` builds a temporary zipapp (or invokes `build.py` into a temp dir), runs `krc.pyz examples/contoh.krc` from a directory that is not the repo, and asserts the output. It also imports `core` from the installed layout in CI (`pip install .`).

### Golden output

Before the refactor, capture the output of every `examples/*.krc` and the tutorial harness result. After the refactor, diff. The 271/550 suites already cover most of this; the golden check catches examples that the suites do not execute.

## 11. Boundaries

### Always

- Run both suites plus `test_ids.py` before every commit.
- Add an ID to `core/ids.json` before using it.
- Keep `KEYWORDS`, `WORD_OPERATORS`, `BUILTINS`, `TYPE_NAMES`, `MODES`, `RESERVED` working.
- Keep the engine free of dialect words.
- Keep `python kerincilang.py` working.
- Keep `build.py`, `make_highlight.py`, and `buat_glosarium.py` green.

### Ask first

- Changing a Siulak word or a message's rendered text.
- Changing a compatibility export's shape.
- Removing `val.*` is decided (D1); re-adding it is an `Ask first`.
- Changing the package layout (for example, converting `kerincilang.py` to a package).
- Adding an ID that is not in the v0.6 inventory.
- Changing `core/ids.json` field names.

### Never

- Change expected test output to make the refactor pass.
- Put a dialect word in the lexer/parser/runtime logic.
- Keep two hand-maintained vocabulary tables.
- Break the single-file build or the wheel.
- Rename an ID after this module is released.
- Let `core/ids.json` contain a Siulak word.

## 12. Success criteria

1. `core/ids.json` validates and covers 26 keywords, 6 comparison words, 24 built-ins, 9 type names, 3 modes, 1 reserved word, and every message raised by the engine.
2. The compatibility exports have the same keys and values as v0.5.
3. `tests/test_kerincilang.py` passes 271/271 and `tests/test_tutorial.py` passes 550 blocks, with no test edits.
4. `tests/test_ids.py` passes all cases in section 10, including the synthetic vocabulary and the AST scans.
5. `make_highlight.py` and `buat_glosarium.py` run with no output diff.
6. `python build.py` produces a `dist/krc.pyz` that runs `examples/contoh.krc` from a clean directory; `pip install .` works.
7. `python -m compileall -q .` passes.
8. `docs/04-implementation.md` documents the vocabulary seam and the M1 single-vocabulary limitation.

## 13. Decisions

These are the calls I made in this spec. Correct any before implementation.

| # | Decision | Recommendation |
|---|---|---|
| D1 | `val.*` is removed; true/false/null are `kw.true`/`kw.false`/`kw.null`. `type.null` remains output-only. | Yes; it removes the double-count from review B2. |
| D2 | `reserved.error` covers `kelihu`; it is tier 3. | Yes; other dialects can map it or leave it out. |
| D3 | Semantic token kinds are IDs (`kw.if`), not the legacy uppercase kinds (`IF`). | Yes; one naming system. |
| D4 | `core/` and `dialects/` become importable data packages (`__init__.py`), while `python kerincilang.py` stays. | Yes; it is the least disruptive way to make wheel + zipapp work. |
| D5 | Message IDs are `msg.<area>.<name>` (dot-separated), not flat. | Yes; easier to review and group. |
| D6 | `LangError` renders at construction with the active vocabulary and also exposes `msg_id`/`args`. | Yes; `str(err)` stays stable after the run ends. |
| D7 | All compatibility exports stay through 0.6 and are removed only in a later release. | Yes; they keep the 271 tests and generators working. |
| D8 | `run_source`/`run_file`/`tokenize`/`new_global`/`show` gain an optional `vocab` argument now. | Yes; it is the seam `runtime-selection` needs. |

## 14. Next step

On approval: write `tasks/plan.md` and `tasks/todo.md` for `core-ids`, then implement in the task order. No later module starts until this one is green.
