# Todo: tutorial-multidialect

Each item is done only when the listed check passes.

- [x] T1 `rewrite_dialect_words` maps `kw`, `op`, `fn`, and direct `bukak` mode
      strings by ID and leaves comments, strings, and user names alone.
- [x] T2 `baseline_paths()` drives the default check and
      `tests/test_tutorial.py`; both still report exactly 550 blocks.
- [x] T3 Every generated code fence gets one `# dialek: <code>` header; `.krc`
      helper files get one too, while raw-data helpers keep their bytes.
- [x] T4 Every `krc` block runs, every `krc-error` block fails, and every
      `hasil` is the real output.
- [x] T5 Inline code spans are mapped; ordinary prose is copied except for the
      dialect noun, links, and the generated footer.
- [x] T6 Relative links re-resolve from the generated directory and every link
      target exists.
- [x] T7 The build is transactional and two builds are byte-identical.
- [x] T8 Fallback IDs are reported once on stderr and their surface words are
      listed in the index.
- [x] T9 `tutorial/en/koto-payang/` and `tutorial/id/koto-payang/` are committed
      and fresh.
- [x] T10 `tests/test_tutorial_dialects.py` proves the thirteen groups in spec
      section 7.
- [x] T11 Siulak self-build matches the baseline block kinds, order, info, and
      code minus the injected header.
- [x] T12 Normalized stdout and `msg_id`-plus-arguments match the baseline for
      every generated block.
- [x] T13 All eleven suites, `cek_dialek --semua`, the generators,
      `compileall`, `build.py`, and the zipapp smoke test pass.
- [x] T14 Docs and capability map updated; the spec is marked implemented.

## Follow-ups (not part of tutorial-multidialect)

- `docs-release`: contributor guide, `docs/09-adding-a-dialect.md`, VS Code
  grammar, package data, release notes.
- A full Koto Payang glossary after the dialect reaches `approved`.
