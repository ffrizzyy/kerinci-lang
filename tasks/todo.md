# Todo: translator

Each item is done only when the listed check passes.

- [x] T1 `krc terjemah` is dispatched only as the first argument; normal runs,
      `migrasi`, the REPL, and `-c` are unchanged.
- [x] T2 Source resolution follows header > `--dari` > Siulak; `--ke` is
      required and validated before the input is read.
- [x] T3 Keywords, word operators, built-in names, and the header are
      translated; braces, symbols, comments, strings, numbers, spacing, and
      line endings are byte-identical.
- [x] T4 User-declared names are never rewritten; target guarded-word
      collisions and source built-in shadowing are refused.
- [x] T5 A used ID the target does not own is refused with the ID named; no
      base fallback is written.
- [x] T6 Only the direct second argument of `bukak` is translated; other
      mode/type string literals that differ are refused.
- [x] T7 Same-dialect translation is a validated copy and allows legal
      built-in shadowing.
- [x] T8 stdout mode, atomic `--out`, `--kering`, and the import-location
      warning behave exactly as the spec says; `--out` may not equal the input.
- [x] T9 BOM, non-UTF-8, malformed header, unknown source header dialect, and
      parse error are refused with exit 1 and no write.
- [x] T10 Usage and target errors exit 2; `terjemah --help` exits 0 and
      documents every option.
- [x] T11 `tests/test_translator.py` proves all thirteen groups in spec section
      10, including the examples, mixed imports, and the zipapp.
- [x] T12 All ten suites, `cek_dialek --semua`, both generators, `compileall`,
      `build.py`, and `dist/krc.pyz terjemah` pass.
- [x] T13 Docs updated; the spec is marked implemented.

## Follow-ups (not part of translator)

- `tutorial-multidialect`: dialect-templated lessons.
- `docs-release`: contributor guide, VS Code grammar, release notes.
