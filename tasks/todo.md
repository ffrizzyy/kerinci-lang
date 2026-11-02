# Todo: docs-release

Each item is done only when the listed check passes.

- [ ] T1 `lembar_kerja.py rangka` writes a validated `draft` JSON skeleton and
      a notes stub, refuses an existing file without `--paksa`, and leaves the
      exit codes and help unchanged apart from the new command.
- [ ] T2 `docs/09-adding-a-dialect.md` covers the twelve required sections, uses
      the exact scaffold commands, and marks `dialek-baru` as a placeholder.
- [ ] T3 The walkthrough in `tests/test_docs_release.py` scaffolds
      `dialek-baru`, fills 32 Tier 1 rows, merges 32 words, passes
      `cek_dialek`, and runs a headered program.
- [ ] T4 `README.md`, `GETTING-STARTED.md`, `CONTRIBUTING.md`, `docs/01`-`07`,
      and `docs/README.md` describe the two-dialect status truthfully and index
      `08`, `09`, and `RELEASING.md`.
- [ ] T5 The stale-string audit passes in current reader-facing files; history
      files are exempt.
- [ ] T6 `make_highlight.py` emits a deterministic union grammar from
      `available_dialects()` / `load_dialect()`, and the committed grammar is
      byte-identical to a fresh generation.
- [ ] T7 `vscode-extension/README.md` explains the union rule and the missing
      picker; `package.json` is 0.6.0 and names both dialects.
- [ ] T8 `CHANGELOG.md` has a 0.6.0 entry with the real tier table and the
      "not in this release" sentence naming Semurup, Sungai Liuk, and Rawang.
- [ ] T9 `RELEASING.md` gives the repeatable release checklist and is linked
      from `CONTRIBUTING.md`, `docs/README.md`, and `docs/09`.
- [ ] T10 All eight version locations say 0.6.0 and `krc --version` agrees.
- [ ] T11 `tests/test_docs_release.py` proves the twelve groups in spec section
      9.1 and runs in `build.py`.
- [ ] T12 `tests/test_release.py` builds a clean-copy wheel, checks its
      contents, installs it, and runs both dialects from outside the checkout.
- [ ] T13 CI runs the full offline suite, `compileall`, `cek_dialek --semua`,
      the freshness diffs, the wheel smoke, and an installed run on 3.12.
- [ ] T14 All offline suites, `cek_dialek --semua`, the generators,
      `compileall`, `build.py`, the wheel smoke, and the zipapp smoke pass;
      the baseline is still 550 blocks / 271 checks and Koto Payang is `review`.
- [ ] T15 `CAPABILITY-MAP.md` is updated and `SPEC-docs-release.md` is marked
      implemented with its implementation log.

## Follow-ups (not part of docs-release)

- Koto Payang second speaker pass, then `approved`.
- Semurup, Sungai Liuk, Rawang: speaker-approved files, then the guide.
- A per-dialect VS Code picker, if it ever earns its complexity.
- A full Koto Payang glossary after `approved`.
- Tag and publish `v0.6.0` only after the human confirms.
