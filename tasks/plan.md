# Plan: docs-release

Module: `docs-release`. Spec: `SPEC-docs-release.md` (approved 2026-11-02).
Depends on `core-ids`, `dialect-model`, `runtime-selection`,
`worksheet-pipeline`, `dialect-siulak-legacy`, `dialect-koto-payang`,
`cli-migration`, `translator`, and `tutorial-multidialect`, all implemented.

Goal: make the 0.6 multi-dialect work teachable and shippable. A contributor
adds a dialect from one guide without touching Python; every current document,
editor file, package, and command tells the truth; 0.6.0 can be reproduced and
verified from a clean checkout.

The oracle is unchanged: the 271 language checks, 550 baseline tutorial blocks,
every dialect word, every expected output, and Koto Payang's `review` status.

## Order

1. **Scaffold command** - add `lembar_kerja.py rangka --kode CODE --nama NAME`
   that writes a validated `draft` JSON skeleton and a notes stub. Generic, no
   dialect and no word added. Exit codes match the existing tool.

2. **Contributor guide** - write `docs/09-adding-a-dialect.md` from an empty
   worksheet to a runnable dialect, using the exact section 3.2 commands and
   the placeholder `dialek-baru`. It names only commands and paths that exist.

3. **Truth audit** - fix every current reader-facing file named in spec
   section 4: `README.md`, `GETTING-STARTED.md`, `CONTRIBUTING.md`, `docs/01`
   through `docs/07`, and `docs/README.md`. History (`SPEC-*`, `docs/08`,
   `CHANGELOG.md`) keeps its dated statements.

4. **Union grammar** - rework `make_highlight.py` to load every dialect through
   `available_dialects()` and `load_dialect()` and emit one deterministic
   union grammar. Add `vscode-extension/README.md`; bump the extension to
   0.6.0.

5. **Release notes and checklist** - add the `CHANGELOG.md` 0.6.0 entry with
   the real dialect table and the "not in this release" sentence; add
   `RELEASING.md`; bump every version location to 0.6.0.

6. **Packaging** - update `pyproject.toml` description and keywords, keep the
   package data rules, and prove a fresh wheel contains both dialect JSON/MD
   files and `core/ids.json`, no CSV, and no bytecode.

7. **Tests** - add offline `tests/test_docs_release.py` for all twelve groups
   in spec section 9.1; add `tests/test_release.py` for the network-dependent
   wheel smoke in 9.2. Update `build.py` to discover the offline suite and
   skip the release smoke with one clear line.

8. **CI** - keep the version matrix; add the full offline suite, `compileall`,
   `cek_dialek --semua`, freshness diffs, the wheel smoke, and an installed
   `krc --version` plus Koto Payang run on Ubuntu 3.12.

9. **Close** - run every offline suite, the generators, `compileall`,
   `cek_dialek --semua`, `build.py`, the wheel smoke, and the zipapp smoke;
   update `CAPABILITY-MAP.md` and mark the spec implemented.

## Verification

- `python tools/lembar_kerja.py rangka` in a temporary repo produces a valid
  `draft` JSON and a notes stub; `cek_dialek --kode` exits 0.
- The walkthrough in `tests/test_docs_release.py` runs the guide commands in
  order with `dialek-baru`, fills 32 Tier 1 rows, and runs a program.
- `python make_highlight.py` -> committed grammar unchanged; a fresh generation
  is byte-identical.
- `python tests/test_docs_release.py` -> all twelve groups pass.
- All earlier suites unchanged and green; `build.py` runs every offline suite.
- `python tools/cek_dialek.py --semua` -> exit 0.
- `python -m compileall -q .` and the zipapp smoke pass.
- `python tests/test_release.py` builds a wheel from a clean copy, finds both
  dialects, installs, and runs both from outside the checkout.
- `krc --version` prints `KerinciLang 0.6.0`; all eight version locations agree.
- No baseline lesson, expected output, example, catalogue, dialect status, CLI
  text, `--ketat` behavior, or dialect word changes.

## Risks

- The guide must be executable: every command and path it names is checked by
  a test.
- A union grammar must not color ordinary text; `type.*` and `mode.*` stay out.
- Regenerating the grammar must not silently drop a Siulak word.
- A stale local `build/` can hide a packaging bug; the wheel smoke copies the
  tree without build artifacts.
- Version strings appear in eight places; missing one breaks the consistency
  test.
- `test_release.py` needs the network for an isolated build, so it must not run
  inside `build.py` or the everyday offline path.
- The stale-string audit must exempt history without letting a real stale
  instruction survive in a current file.
