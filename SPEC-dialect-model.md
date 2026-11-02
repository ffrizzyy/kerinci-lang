# Spec: dialect-model

Status: **draft for approval.** Parent: `SPEC.md`. Capability map: `dialect-model`.
Depends on: `core-ids` (implemented, commit `2cb1c55`). Date: 2026-11-02.

## 1. Objective

Make a dialect a **data file**, not code: load, validate, and resolve it, with a
neutral English base as the final fallback.

After this module:

- `load_dialect("koto-payang")` returns a `Vocabulary` the engine can run.
- Every validation rule from the review has a specific, tested error.
- A dialect can inherit from another dialect and then from the English base.
- `tools/cek_dialek.py` reports tier completeness and fallbacks, and is the CI gate.
- Nothing selects a dialect yet: that is `runtime-selection`.

## 2. Scope

### In scope

- `dialects/<code>.json` schema and loader.
- The synthesized English base (no `base.json` duplicate).
- Parent chains and cycle detection.
- Namespace-aware validation (the clash matrix) and identifier rules.
- `core` version semantics.
- `DialectVocabulary` implementing the `Vocabulary` seam.
- `tools/cek_dialek.py`.
- `tests/test_dialects.py`.

### Out of scope

- The `# dialek:` header, `--dialek`, `--ketat` exit behavior, per-module scopes.
- `dialects/siulak.json` (that is `dialect-siulak-legacy`).
- `dialects/koto-payang.json` (that is `dialect-koto-payang`).
- Worksheet generation and normalization.
- `krc migrasi`, `krc terjemah`.
- Any change to `core/ids.json` or to Siulak output.

## 3. Contract: `dialects/<code>.json`

UTF-8 JSON, 2-space indent, keys sorted, no comments, no executable content.

```json
{
  "code": "koto-payang",
  "name": "Koto Payang",
  "status": "draft",
  "core": "0.6",
  "revision": 1,
  "parent": null,
  "license": "CC BY-SA 4.0",
  "maintainer": "Nama Pengurus <email>",
  "reviewer": null,
  "sources": ["Translation Worksheet (Koto Payang), 2026"],
  "orthography": "Final -u (kalu, selamu); nga for and; underscore for multi-word concepts.",
  "words": {
    "kw.if": "kalu",
    "op.eq": "samo",
    "fn.length": "panja"
  },
  "messages": {
    "msg.value.div_zero": "Pembagian dengan nol"
  }
}
```

| Field | Type | Required | Rule |
|---|---|---|---|
| `code` | string | yes | `^[a-z0-9-]+$`; must equal the filename stem |
| `name` | string | yes | non-empty display name |
| `status` | string | yes | `draft`, `review`, `approved`, or `deprecated` |
| `core` | string | yes | `MAJOR.MINOR`; the minimum catalogue version |
| `revision` | integer | yes | `>= 1`; bumps on every accepted change |
| `parent` | string or null | yes | another dialect `code`, or `null` |
| `license` | string | yes | e.g. `CC BY-SA 4.0` |
| `maintainer` | string | yes | non-empty |
| `reviewer` | string or null | yes | must be non-null when `status == "approved"` |
| `sources` | list of strings | yes | may be empty only for `draft` |
| `orthography` | string | yes | spelling notes for reviewers |
| `words` | object | yes | `word ID -> word`; may be partial |
| `messages` | object | no | `msg ID -> template`; may be partial |
| `notes` | string | no | free-form provenance |

Unknown top-level keys are an error, so a typo cannot be ignored.

`words` and `messages` may be partial. A missing ID falls back to `parent`, then
to its parent, then to the base. Every fallback is recorded in the report.

## 4. The base vocabulary (decision D1)

There is no `dialects/base.json`. The base is **synthesized from
`core/ids.json`**, because a second English table would drift.

- A word ID's base word is its `en` value normalized to an identifier: lowercased,
  runs of characters outside `[a-z0-9_]` replaced by `_`, leading/trailing `_`
  stripped. Examples: `greater than` -> `greater_than`, `whole number` ->
  `whole_number`, `begin block` -> `begin_block`.
- A `msg.*` ID's base template is its `en` value, used as-is.
- `code` is `base`, `parent` is `null`, `status` is `approved`.

`tests/test_dialects.py` asserts the synthesized base passes every validation
rule, so the catalogue can never produce an unusable fallback.

## 5. Loading and resolution

```python
load_dialect(code, root=None) -> Dialect
```

- `code` is validated before any path is built: `^[a-z0-9-]+$`.
- `root` defaults to the packaged `dialects/` directory (works from a checkout, a
  wheel, and `dist/krc.pyz`, the same way `core/ids.json` does). `root` is a
  developer/test argument, never a CLI value.
- The resolved path must stay inside `root` (`os.path.realpath` prefix check).
- File size is capped at **1 MiB**.
- JSON is parsed with a duplicate-key rejecting hook; a duplicate key is an error.
- The root value must be an object.
- Errors are `DialectError` with a stable `code` (see section 6) and a message.
- Parent chains are followed with a visited set; a cycle is an error about every
  member, longest-first.

`Dialect` exposes:

| Member | Meaning |
|---|---|
| `.code`, `.name`, `.status`, `.core`, `.revision` | metadata |
| `.vocab` | a `DialectVocabulary`, ready for `run_source(..., vocab=...)` |
| `.report` | `Report` with `fallbacks`, `tiers`, `problems` |
| `.words` | the resolved `ID -> word` table (file, parents, base merged) |
| `.messages` | the resolved `ID -> template` table |

Resolution order for one ID: the file, then its parent chain, then the base. The
first value wins. `report.fallbacks` holds `(id, source)` where source is the
dialect code or `base`.

## 6. Validation rules

### 6.1 Schema and identifiers

| Code | Rule |
|---|---|
| `schema` | required field missing, wrong type, unknown top-level key, or bad enum |
| `code` | filename stem and `code` disagree, or `code` is invalid |
| `core-version` | `core` is not `MAJOR.MINOR` |
| `word-empty` | a word is empty or whitespace |
| `word-charset` | a word is not NFC, or does not match `^[a-z][a-z0-9_]*$` |
| `word-case` | a word has uppercase letters (reported separately for a clear fix) |
| `unknown-id` | `words` or `messages` uses an ID not in `core/ids.json` |
| `wrong-namespace` | a `words` key is a `msg.*` ID, or a `messages` key is not `msg.*` |
| `message-placeholder` | a message's placeholder set differs from the catalogue |
| `parent-missing` | `parent` names a dialect that does not exist |
| `parent-cycle` | the parent chain loops |
| `reviewer-missing` | `status == "approved"` but `reviewer` is null |
| `source-missing` | a non-draft dialect has an empty `sources` list |

### 6.2 The clash matrix (resolved table)

Words are checked **after fallback**, because a parent or the base can introduce a
clash.

```
            kw      op    reserved    fn     type    mode
  kw        E       E        E         E       ok      ok
  op        E       E        E         E       ok      ok
  reserved  E       E        E         E       ok      ok
  fn        E       E        E         E       ok      ok
  type      ok      ok       ok        ok      ok      ok
  mode      ok      ok       ok        ok      ok      ok
```

In one sentence: `kw`, `op`, `reserved`, and `fn` must be pairwise disjoint;
`type` and `mode` may share with anything.

Why: the lexer claims a word before it becomes a name, so a built-in that shares a
keyword is unreachable; `type` words are only ever printed, and `mode` words are
only ever passed as strings.

| Code | Rule |
|---|---|
| `clash` | two IDs from `kw`/`op`/`reserved`/`fn` resolve to the same word |
| `clash-detail` | the message names both IDs and the word |

The 12 intentional Siulak overlaps (`guno`, `kosong`, `kato`, `peta`, `bilangan`,
`daftar`, `pecahan`, `betul`, `salah`, `baco`, `tulis`, `nambahkah`) are legal
because they cross into `type` or `mode`, never within `kw`/`op`/`reserved`/`fn`.

### 6.3 Security

| Code | Rule |
|---|---|
| `path` | `code` fails the pattern, or the resolved path escapes `root` |
| `size` | the file is larger than 1 MiB |
| `json` | malformed JSON, duplicate key, or a non-object root |

No dialect content is ever executed. Loading never imports a Python file.

## 7. `core` version semantics (decision D3)

- `core` is the **minimum** catalogue version the file was written against.
- Compare as `(major, minor)` tuples.
- File `core` newer than the runtime's `CATALOG["core"]` -> warning
  `newer-core`, and loading continues. Any ID the runtime does not know is still a
  hard `unknown-id` error, so a newer file cannot silently do the wrong thing.
- File `core` older than the runtime -> accepted silently.
- Unknown IDs -> hard error, never ignored.

## 8. Completeness report

```python
report.tiers()   # {1: (present, total), 2: (present, total), 3: (present, total)}
report.missing() # [(id, tier)] still coming from beyond the parent chain
report.fallbacks # [(id, source)]
```

`present` means the dialect's own file defines the ID (not a parent or the base).
This is the number a speaker review cares about: "how much of Tier 1 is in my
words?".

Rules:

- An `approved` dialect with any Tier 1 fallback from `base` is a failure in
  strict mode (exit 2).
- A `draft` dialect may fall back; the report lists what is missing.

## 9. API

```python
from kerincilang import Vocabulary

class DialectVocabulary(Vocabulary):
    def __init__(self, dialect): ...
    def word(self, id): ...          # resolved word
    def message(self, id, args): ... # resolved template, formatted
    def mode_id(self, word): ...
    def surface(self): ...           # kw words only
    def operators(self): ...         # op word -> symbol
    def reserved(self): ...
```

Public functions:

```python
load_dialect(code, root=None) -> Dialect
validate_dialect(data, filename=None, root=None) -> list[Problem]
base_dialect() -> Dialect              # the synthesized base, cached
available_dialects(root=None) -> list[str]
```

`Problem` is a small record: `code`, `id`, `message`.

`load_dialect` validates and raises `DialectError` on the first blocking problem
(after collecting all of them into the exception's `.problems`).

## 10. CLI: `tools/cek_dialek.py`

```bash
python3 tools/cek_dialek.py --semua
python3 tools/cek_dialek.py --kode koto-payang
python3 tools/cek_dialek.py --kode koto-payang --ketat
```

| Exit | Meaning |
|---|---|
| 0 | every requested dialect is valid; strict mode found no blocking fallback |
| 1 | a validation error (schema, clash, identifier, path, JSON) |
| 2 | strict mode: an `approved` dialect falls back to `base`, or the file's `core` is newer |

Output is one line per problem: `<code>: <id or ->: <message>`, then a tier
summary per dialect. Non-zero exits are CI failures.

## 11. Code style

```python
# BAD: trusting a filename from the user
path = os.path.join(DIALECT_DIR, code + ".json")

# GOOD: validate first, then keep the resolved path inside root
if not CODE_RE.match(code):
    raise DialectError("path", None, "dialect code must match [a-z0-9-]+")
path = (root / (code + ".json")).resolve()
if root.resolve() not in path.parents:
    raise DialectError("path", None, "dialect path escapes the dialects directory")
```

- Pure standard library: `json`, `os`, `re`, `unicodedata`, `importlib.resources`.
- No `dataclasses` requirement; a small class or namedtuple is fine.
- Validation returns problems; it does not print.
- One rule, one code, one test.

## 12. Testing (`tests/test_dialects.py`)

Positive:

1. The synthesized base validates and resolves every live ID.
2. A minimal valid dialect loads; `run_source(..., vocab=...)` runs a program.
3. A parent chain (child -> parent -> base) resolves in that order.
4. `available_dialects` lists files and ignores `__init__.py`.

Negative, one test per code: `schema`, `code`, `core-version`, `word-empty`,
`word-charset`, `word-case`, `unknown-id`, `wrong-namespace`,
`message-placeholder`, `parent-missing`, `parent-cycle`, `reviewer-missing`,
`source-missing`, `clash`, `path`, `size`, `json` (malformed, duplicate key,
non-object root).

Also:

- A `type` word equal to a `fn` word is accepted (overlap allowed).
- A `mode` word equal to a `kw` word is accepted.
- An `fn` word equal to a `kw` word is rejected and names both IDs.
- `--ketat` exit codes are tested through `main()` with a temp root.
- A child dialect can override a parent word and the override wins.
- A dialect with `core` newer than the runtime warns but loads.
- A file over 1 MiB is rejected.

Fixtures are written into `tempfile.TemporaryDirectory()` roots; no fake dialect
is committed.

## 13. Boundaries

### Always

- Validate on load; never trust a file.
- Keep `dialects/` data-only.
- Record `maintainer`, `reviewer`, `sources`, and `license`.
- Keep the base synthesized from `core/ids.json`.
- Return problems, let the caller print.
- Reject unknown IDs.

### Ask first

- Changing the dialect schema or adding a required field.
- Adding a namespace or changing the clash matrix.
- Adding a fallback source beyond parent + base.
- Shipping a committed test dialect.

### Never

- Load a dialect from a path outside `dialects/`.
- Execute dialect content.
- Let an unknown ID fall back silently.
- Duplicate the English base in a second file.
- Weaken a validation rule to make a draft pass.

## 14. Success criteria

1. `load_dialect` resolves a file, a parent chain, and the base in that order.
2. Every rule in section 6 has a test that produces its code.
3. The clash matrix accepts the 12 intentional Siulak overlaps and rejects an
   `fn`/`kw` clash.
4. `python3 tools/cek_dialek.py --semua` exits 0 on an empty `dialects/`, and gives
   the documented exit codes on temp fixtures.
5. A dialect with an unknown ID, a bad identifier, or a traversal code is rejected
   with a specific message.
6. `run_source("...", vocab=load_dialect(...).vocab)` runs a program in a test
   dialect, proving the seam is usable by `runtime-selection`.
7. `python3 tests/test_kerincilang.py`, `test_tutorial.py`, and `test_ids.py` stay
   green and unchanged.
8. `python3 -m compileall -q .` passes.

## 15. Decisions

| # | Decision | Recommendation |
|---|---|---|
| D1 | The English base is synthesized from `core/ids.json` (`en` normalized to an identifier); no `base.json`. | Yes; one source of truth. |
| D2 | The clash matrix is `kw`/`op`/`reserved`/`fn` pairwise disjoint; `type`/`mode` free. | Yes; fixes review B1. |
| D3 | `core` is a minimum version; newer warns, unknown IDs are hard errors. | Yes; fixes review B8. |
| D4 | Unknown top-level keys are errors, not warnings. | Yes; catches typos. |
| D5 | `parent` is a single dialect code, not a list. | Yes; simple chains are enough for 0.6. |
| D6 | Dialect codes are `^[a-z0-9-]+$`; the filename must match. | Yes; blocks traversal. |
| D7 | `validate_dialect` returns all problems; `load_dialect` raises with all of them. | Yes; one CI pass shows everything. |
| D8 | `tools/cek_dialek.py` is the CI gate and never imports a dialect. | Yes. |

## 16. Next step

On approval: write `tasks/plan.md` and `tasks/todo.md` for `dialect-model`, then
implement. `runtime-selection` starts only after this module is green.
