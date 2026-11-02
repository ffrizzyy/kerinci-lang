# Todo: cli-migration

Each item is done only when the listed check passes.

- [x] T1 `krc migrasi` is dispatched only as the first argument; normal runs are
      unchanged.
- [x] T2 A headerless file gains exactly `# dialek: CODE` as line 1, with every
      original byte preserved and the file's newline style.
- [x] T3 A valid header makes the file a no-op on every later run.
- [x] T4 Literal `ambik` imports are followed recursively and deduped by real
      path; a dynamic or missing import is reported and exits 1.
- [x] T5 A BOM, malformed header, parse error, and unknown header dialect are
      refused: file unchanged, exit 1.
- [x] T6 `--semua DIR`, `--dialek CODE`, and `--kering` behave exactly as the
      spec says; `--dialek` is validated before any write.
- [x] T7 Usage errors exit 2: no target, both modes, non-`.krc`, unknown flag,
      bad `-c`, extra arguments.
- [x] T8 `krc migrasi --help` exits 0 and documents every flag.
- [x] T9 `tests/test_migration.py` proves all thirteen groups in spec section 9,
      including the zipapp.
- [x] T10 `examples/*.krc` all carry `# dialek: siulak` and their output is
      unchanged.
- [x] T11 All nine suites, `cek_dialek --semua`, both generators, `compileall`,
      `build.py`, and `dist/krc.pyz` pass.
- [x] T12 Docs updated; the spec is marked implemented.

## Follow-ups (not part of cli-migration)

- `translator`: `krc terjemah`.
- `tutorial-multidialect`: dialect-templated lessons.
- `docs-release`: contributor guide, VS Code grammar, release notes.
