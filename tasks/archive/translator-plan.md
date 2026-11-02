# Plan: translator

Module: `translator`. Spec: `SPEC-translator.md` (approved 2026-11-02).
Depends on `runtime-selection`, `dialect-koto-payang`, and
`dialect-siulak-legacy`, all implemented.

Goal: add `krc terjemah`, translate one file losslessly, refuse when the target
cannot express the source, preserve every non-word byte, and prove the policy
with `tests/test_translator.py`.

The oracle is unchanged: every earlier suite, expected output, tutorial block,
and dialect word stays green.

## Order

1. **CLI dispatch and usage text** - recognize `terjemah` as the first argument,
   add `TERJEMAH_USAGE`, extend `USAGE`, and add `krc terjemah --help`. Keep the
   normal run, `migrasi`, REPL, and `-c` paths untouched.

2. **Source and target resolution** - read the line-1 header with the runtime
   rules, fall back to `--dari` then Siulak, validate `--ke` and `--dari` before
   reading the input, and handle the same-dialect validated-copy case.

3. **Lossless scan** - scan with `MASTER`, classify identifiers against the
   source keyword, operator, built-in, and reserved maps, build non-overlapping
   edits, and preserve comments, strings, spacing, and line endings.

4. **Symbol checks** - collect declared names from the AST, refuse source
   built-in shadowing, refuse target guarded-word collisions, and refuse any
   used ID the target does not own.

5. **Strings** - translate only the direct second argument of a source
   `fn.open` call; refuse other mode/type string literals whose target word
   differs; leave every other string alone.

6. **Output** - stdout mode, atomic `--out`, `--kering`, a moved-output import
   warning, and the exit-code table.

7. **Tests** - `tests/test_translator.py`, all thirteen groups in spec section
   10, including the examples, mixed imports, and the zipapp.

8. **Docs** - mark the spec implemented, check off the todo, update the
   capability map, `docs/03`, `docs/04`, `docs/05`, and `README.md`.

## Verification

- `python tests/test_translator.py` -> all pass.
- The nine earlier suites, unchanged and green.
- `python tools/cek_dialek.py --semua` -> exit 0.
- Both generators produce no diff; `python -m compileall -q .`.
- `python build.py`, then `dist/krc.pyz terjemah` from a temp directory.
- `examples/` is unchanged by this module.

## Risks

- Reconstructing from the AST would lose formatting; rewrite spans in place.
- A keyword-looking user name must be refused if it is guarded in the target.
- A target base fallback is a silent loss; refuse and name the ID.
- A mode word in a variable is not safe to rewrite; refuse.
- A malformed header, BOM, or syntax error must never be repaired or copied.
- `--out` must never equal the input; writes must be atomic.
- Same-dialect translation must still parse but must not refuse legal
  built-in shadowing.
- The translator must never execute the source.
