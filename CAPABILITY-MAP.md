# Capability Map: KerinciLang Multi-Dialect

Status: **approved 2026-11-02.** Module specs are written in dependency order.

This is the index of the initiative. Each module gets its own spec, named by module id (`SPEC-<id>.md`), written in dependency order after approval.

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| `core-ids` | Freeze `core/ids.json` (IDs, namespace, tier, arity, placeholders, English base) and move the lexer, parser, runtime, and messages onto neutral IDs. Keep Siulak compatibility shims. | - |
| `dialect-model` | Dialect JSON schema, loader, parent fallback to `base`, namespace-aware validation and clash matrix, completeness report. | `core-ids` |
| `runtime-selection` | Per-file `# dialek:` header, `--dialek` for files/REPL/`-c`, per-module dialect context, dialect output words, type names, modes, messages, fallback warnings, `--ketat`. | `dialect-model` |
| `cli-migration` | `krc migrasi` (including imports), header/precedence errors, REPL and `-c` behavior, exit codes, `--help`. | `runtime-selection` |
| `worksheet-pipeline` | Canonical CSV schema, DOCX view, generator, reader/normalizer, placeholder validation, tier/completeness reports. | `core-ids` |
| `dialect-koto-payang` | Normalized Koto Payang data (`dialects/koto-payang.json`), orthography notes, provenance, Tier 1 and 2 review record. | `worksheet-pipeline`, `runtime-selection` |
| `dialect-siulak-legacy` | Freeze the v0.5 Siulak vocabulary as `dialects/siulak.json` (draft), preserve `docs/02` as provenance, and define the legacy word mapping. | `core-ids` |
| `translator` | `krc terjemah`, lossless policy (refuse when impossible), user-symbol handling, mixed-dialect imports. | `runtime-selection`, `dialect-koto-payang`, `dialect-siulak-legacy` |
| `tutorial-multidialect` | Dialect-templated tutorial builds from the tested Siulak lessons: word-mapped code and inline spans, regenerated `hasil`, committed English/Indonesian trees, tutorial tests. | `runtime-selection`, at least one completed dialect |
| `docs-release` | Contributor guide, dialect docs, VS Code grammar/README, package data, release notes, version bump. | all |

## Dependency direction

```
core-ids
  |-- dialect-model
  |     `-- runtime-selection
  |           |-- cli-migration
  |           |-- dialect-koto-payang
  |           `-- translator
  |-- worksheet-pipeline
  |     `-- dialect-koto-payang
  `-- dialect-siulak-legacy
        `-- translator

translator + dialect-koto-payang -> tutorial-multidialect
all -> docs-release
```

No cycles. `worksheet-pipeline` and `dialect-siulak-legacy` can start as soon as `core-ids` is stable, in parallel with `dialect-model`.

## Build order

1. `core-ids`
2. `dialect-model`
3. `runtime-selection` and `worksheet-pipeline` (parallel) and `dialect-siulak-legacy`
4. `dialect-koto-payang`
5. `cli-migration`
6. `translator`
7. `tutorial-multidialect`
8. `docs-release`

Recommended first milestone (M1): 1-5. Translation and tutorial generation are M2/M3.

## Interfaces at the boundaries

| Boundary | Contract |
|---|---|
| `core-ids` -> dialect files | `core/ids.json`: `id`, `namespace`, `tier`, `en`, `id_gloss`, `arity`, `placeholders`. IDs are immutable after release. |
| `dialect-model` -> runtime | `dialects/<code>.json`: `code`, `name`, `parent`, `status`, `core`, `revision`, `orthography`, `maintainer`, `reviewer`, `sources`, `words`, `messages`. |
| `worksheet-pipeline` -> dialect data | Canonical CSV: `id`, `tier`, `namespace`, `en`, `id_gloss`, `answer`, `notes`, `status`. The first five columns mirror `core/ids.json` and are read-only. |
| `runtime-selection` -> translator | Resolved word table for a dialect plus the neutral token stream; user symbols are resolved before any rewrite. |
| `tutorial-multidialect` -> runtime | Generated `.krc` files with a valid header for every block and helper file. |

## What "adding a dialect" means

For 0.6, a new dialect is **data only**: one CSV answer sheet, one JSON file, one Markdown notes file, and a review record. It may only use IDs already in `core/ids.json`. New IDs (Tier 3 / future features) are a code change to the catalogue and follow the `Ask first` boundary.

## Gate

- [x] Module ids, dependency direction, and build order approved by the human (2026-11-02).
- [x] First milestone agreed.
- [x] `SPEC-core-ids.md` written.
- [x] `SPEC-core-ids.md` approved; `core-ids` implemented and green (`2cb1c55`).
- [x] `SPEC-dialect-model.md` approved; `dialect-model` implemented and green.
- [x] `SPEC-runtime-selection.md` approved; `runtime-selection` implemented and green.
- [x] `SPEC-worksheet-pipeline.md` written.
- [x] `SPEC-worksheet-pipeline.md` approved; `worksheet-pipeline` implemented and green (`tools/lembar_kerja.py`, `tests/test_worksheet.py`).
- [x] `SPEC-dialect-siulak-legacy.md` approved; `dialect-siulak-legacy`
      implemented and green (`dialects/siulak.json`, `tests/test_siulak_legacy.py`).
- [x] `SPEC-dialect-koto-payang.md` approved; `dialect-koto-payang`
      implemented and green (`dialects/koto-payang.json`,
      `tests/test_koto_payang.py`), status `review`.
- [x] `SPEC-cli-migration.md` approved; `cli-migration` implemented and green
      (`krc migrasi`, `tests/test_migration.py`); examples carry headers.
- [x] `SPEC-translator.md` approved; `translator` implemented and green
      (`krc terjemah`, `tests/test_translator.py`, 173 checks).
- [x] `SPEC-tutorial-multidialect.md` approved; `tutorial-multidialect`
      implemented and green (`tools/sinkron_tutorial.py --bangun`,
      `tutorial/{en,id}/koto-payang/`, `tests/test_tutorial_dialects.py`).
- [ ] Next: `docs-release`.
