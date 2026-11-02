# Plan: dialect-model

Module: `dialect-model`. Spec: `SPEC-dialect-model.md` (approved 2026-11-02).
Depends on `core-ids` (commit `2cb1c55`).

Goal: a dialect becomes a validated data file. Load, inherit, validate, report.
Nothing selects a dialect yet; that is `runtime-selection`.

The oracle is unchanged: `tests/test_kerincilang.py` (271 cases),
`tests/test_tutorial.py` (550 blocks), `tests/test_ids.py`. None of them may be
edited, and Siulak output must stay byte-identical.

## Order

1. **Neutral operator symbols** - `OP_SYMBOLS` in `kerincilang.py`, derived from
   `LEGACY_OPERATORS`. The symbol is neutral; only the Siulak word is dialect
   data. The loader needs it, and `core/ids.json` is out of scope.

2. **`dialects/loader.py`** - the whole module in one file:
   - `Problem(code, id, message)` with a `severity` (`error` / `warning`).
   - `DialectError(Exception)` carrying `.code` and `.problems`.
   - `Dialect` (metadata, `words`, `messages`, `vocab`, `report`).
   - `Report` (`fallbacks`, `problems`, `tiers()`, `missing()`).
   - `DialectVocabulary(Vocabulary)`.
   - `base_dialect()` from `core/ids.json`, `en` normalized to an identifier.
   - `validate_dialect(data, filename=None, root=None)`.
   - `load_dialect(code, root=None)`.
   - `available_dialects(root=None)`.

3. **Reading files safely** - code pattern before any path is built, resolved
   path inside `root`, 1 MiB cap, duplicate-key-rejecting JSON hook, UTF-8 only,
   object root only. `importlib.resources.files("dialects")` for the default
   root, with a `pathlib` fallback; no `.stat()` on a `Traversable`.

4. **Parent chains** - single parent, visited set, cycle error naming every
   member, `parent: "base"` accepted as a terminal parent.

5. **Validation** - one function per rule, one code per rule, all problems
   collected. Rules in spec section 6: `schema`, `code`, `core-version`,
   `word-empty`, `word-charset`, `word-case`, `unknown-id`, `wrong-namespace`,
   `message-placeholder`, `parent-missing`, `parent-cycle`, `reviewer-missing`,
   `source-missing`, `clash`, `path`, `size`, `json`, plus the non-blocking
   `newer-core`.

6. **Clash matrix** - `kw`/`op`/`reserved`/`fn` pairwise disjoint; `type`/`mode`
   free. Checked on the resolved table, so a parent cannot introduce a clash
   that goes unnoticed. The message names both IDs and the word.

7. **`tools/cek_dialek.py`** - `--semua`, `--kode CODE`, `--ketat`; exit 0/1/2;
   `main(argv=None, root=None)` so tests can point it at a temp root.

8. **`tests/test_dialects.py`** - one positive and one negative per rule, all
   fixtures written into `tempfile.TemporaryDirectory()` roots. No committed
   fixture dialect, so `dialects/` stays empty until `dialect-siulak-legacy`.

9. **Docs and status** - `docs/04-implementation.md` gets a "Dialect files"
   section; the spec is marked implemented; `CAPABILITY-MAP.md` points at the next
   module.

## Verification

- `python tests/test_dialects.py` -> all pass.
- `python tests/test_kerincilang.py` -> 271/271, no edits.
- `python tests/test_tutorial.py` -> 550 blocks, no edits.
- `python tests/test_ids.py` -> all pass, no edits.
- `python tools/cek_dialek.py --semua` -> exit 0 on the empty `dialects/`.
- `python tools/buat_glosarium.py`, `python make_highlight.py` -> no diff.
- `python build.py`, then `dist/krc.pyz` from a temp directory.
- `python -m compileall -q .`.

## Risks

- The base is synthesized, so a catalogue typo becomes a bad fallback.
  `test_dialects.py` validates the base itself, which turns that into a failure.
- The clash check runs on the merged table; a child overriding a parent word must
  be checked after the merge, not only per file.
- `validate_dialect` must not need the engine to run; it returns problems and
  never prints, so the CLI owns all output.
- Loading a dialect must not import or execute it. JSON only.
- `runtime-selection` will call `load_dialect` from the CLI; keep `root` a test
  argument and never expose it as a command-line flag.
