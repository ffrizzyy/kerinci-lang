# Plan: tutorial-multidialect

Module: `tutorial-multidialect`. Spec: `SPEC-tutorial-multidialect.md`
(approved 2026-11-02). Depends on `runtime-selection`,
`dialect-siulak-legacy`, and `dialect-koto-payang`, all implemented.

Goal: generate the English and Indonesian Koto Payang tutorial trees from the
tested Siulak lessons, run every block in its dialect, and prove normalized
equivalence while the baseline stays at 550 blocks.

The oracle is unchanged: the existing lessons, their expected output, the 271
language cases, and every dialect word stay green.

## Order

1. **Word-rewrite seam** - expose a small `rewrite_dialect_words` function that
   the generator and translator share. It maps code words and direct `bukak`
   mode strings by ID and never touches comments, strings, or user names.

2. **Baseline discovery** - add `baseline_paths()` and make the default check
   and `tests/test_tutorial.py` use it. They must still report 550 blocks and
   must not see `tutorial/en/` or a generated dialect folder.

3. **Renderer** - parse the baseline, map code fences and inline code spans,
   add the dialect header, run each block, and replace its `hasil`. Keep the
   block order, fence kinds, and `info` strings.

4. **Prose and links** - replace the dialect noun, re-resolve relative links,
   add the review footer, build the index, and write the glossary stub.

5. **Transactional build** - collect the whole tree in memory, write it through
   a temporary directory, and only replace the destination after every block
   succeeds. Make two builds byte-identical.

6. **Fallbacks** - collect the base-fallback IDs the corpus actually uses,
   report them once on stderr, and list the surface words in the index.

7. **Commit the trees** - generate `tutorial/en/koto-payang/` and
   `tutorial/id/koto-payang/`; commit them with the generator.

8. **Tests** - `tests/test_tutorial_dialects.py`, all thirteen groups in spec
   section 7, including determinism, committed freshness, equivalence, links,
   headers, fallbacks, and usage errors.

9. **Docs** - update `CAPABILITY-MAP.md`, `docs/03`, `docs/04`, `docs/05`,
   `README.md`, and `tutorial/README.md`; mark the spec implemented.

## Verification

- `python tools/sinkron_tutorial.py` -> 550 blocks, 0 problems.
- `python tests/test_tutorial.py` -> unchanged counts and glossary check.
- `python tests/test_tutorial_dialects.py` -> all pass.
- All eleven suites, unchanged and green.
- `python tools/cek_dialek.py --semua` -> exit 0.
- `python make_highlight.py`, `python tools/buat_glosarium.py` -> no diff.
- `python -m compileall -q .`, `python build.py`, and a `dist/krc.pyz` smoke
  test from a temporary directory.
- Two builds of `koto-payang` produce identical bytes.
- No baseline lesson, expected output, example, catalogue, dialect, or runtime
  change; only the two tutorial index pages gain a pointer to the generated
  trees.

## Risks

- A generated block that uses a fallback still has to run; capture the warning
  and report it once.
- A literal string can look like a type word; the generator must not rewrite
  ordinary strings.
- Input blocks need their `masukan=` arguments preserved.
- Relative links gain a directory level; resolve them instead of prefixing.
- A failed build must not leave a half-written tree.
- The baseline test must not double-count the generated trees.
- `krc-berkas` helper files ending in `.krc` need the target header; raw-data
  helpers such as `nilai.txt` keep their bytes.
- Inline spans must not introduce a new `list` / `map` fallback; kind-table
  cells are mapped as `type.*` words.
