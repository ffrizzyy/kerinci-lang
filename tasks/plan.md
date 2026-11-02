# Plan: cli-migration

Module: `cli-migration`. Spec: `SPEC-cli-migration.md` (approved 2026-11-02).
Depends on `runtime-selection` and `dialect-koto-payang`, both implemented.

Goal: add `krc migrasi`, recurse into literal imports, keep writes idempotent
and byte-preserving, tighten CLI usage errors, migrate the examples, and prove
the whole CLI contract with `tests/test_migration.py`.

The oracle is unchanged: every existing suite, expected output, tutorial block,
and Siulak word must stay green.

## Order

1. **CLI dispatch and usage text** - recognize `migrasi` as the first argument,
   add `MIGRASI_USAGE`, extend `USAGE`, and add `krc migrasi --help`. Keep the
   normal run path untouched.

2. **Migration core** - read bytes, refuse a BOM, inspect line 1 with the
   runtime header rules, detect the newline, and write an atomic header prefix.

3. **Import scan** - parse without executing with the effective dialect, walk
   the AST for `("import", expr)`, follow only `("lit", str)`, resolve relative
   to the importing file (exact path, then `.krc`), and dedupe real paths.

4. **Targets and reporting** - explicit `.krc` files or `--semua DIR`, sorted
   deterministic order, per-file lines, summary, `--kering`, and exit codes
   0/1/2 exactly as the spec says.

5. **CLI cleanup** - unknown flags are usage errors, extra positional arguments
   are usage errors, `-c` takes one code. Document the precedence table.

6. **Examples** - run `migrasi --semua examples`, confirm all eight headers,
   and confirm `contoh-impor.krc` output is unchanged.

7. **Tests** - `tests/test_migration.py`, all thirteen groups in spec section 9.

8. **Docs** - mark the spec implemented, check off the todo, update the
   capability map, `docs/03`, `docs/04`, and `docs/05`.

## Verification

- `python tests/test_migration.py` -> all pass.
- The eight earlier suites, unchanged and green.
- `python tools/cek_dialek.py --semua` -> exit 0.
- Both generators produce no diff; `python -m compileall -q .`.
- `python build.py`, then `dist/krc.pyz migrasi` and a normal run from a temp
  directory.
- `python kerincilang.py migrasi --semua examples` is a no-op after the commit.

## Risks

- A parse error must refuse the file, not add a header above broken code.
- A BOM would put the header on line 1 but the runtime would not see it; refuse.
- A malformed header must not be buried by a new valid header.
- Dynamic imports cannot be followed; report and exit 1, never execute.
- Do not normalize line endings or add blank lines; only prefix bytes.
- `--dialek` must be validated before the first write.
- `--semua` and explicit files are mutually exclusive.
- Running `migrasi` must never execute user code.
- Changing `-c`/REPL defaults would break existing usage; keep Siulak.
