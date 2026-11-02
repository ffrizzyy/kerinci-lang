# Spec: dialect-siulak-legacy

Status: **draft for approval.** Parent: `SPEC.md`. Capability map:
`dialect-siulak-legacy`.
Depends on: `core-ids` (implemented, commit `2cb1c55`) and `dialect-model`
(implemented, commit `60f9335`). Date: 2026-11-02.

## 1. Objective

Freeze the Siulak 0.5 vocabulary as `dialects/siulak.json` so every existing
program, test, and tutorial keeps working while Siulak itself is re-reviewed
later.

After this module:

- `dialects/siulak.json` contains a complete, valid, `draft` snapshot of the
  v0.5 words, operators, types, modes, reserved word, and messages.
- `load_dialect("siulak")` resolves every one of the 137 catalogue IDs from the
  file, with no fallback to the English base.
- A program that selects Siulak explicitly (`# dialek: siulak` or
  `--dialek siulak`) produces the same output as the built-in `LegacySiulak`
  object.
- `docs/02-vocabulary-worksheet.md` stays as the decision log, and
  `dialects/siulak.md` records the freeze and the word mapping.
- No existing test expectation changes.

## 2. Scope

### In scope

- `dialects/siulak.json`: metadata, 69 word IDs, and 68 message IDs.
- `dialects/siulak.md`: provenance, freeze policy, and the legacy word table.
- `tests/test_siulak_legacy.py`: completeness, equivalence with `LegacySiulak`,
  header selection, and the `cek_dialek` gate.
- Documentation updates that mark the module implemented.

### Out of scope

- Re-reviewing Siulak spelling, grammar, or message wording. That is the later
  "completed Siulak" work.
- Changing any v0.5 word, including `type.bool` = `"boolean"`.
- Changing `LEGACY_WORDS`, `LEGACY_OPERATORS`, the loader, runtime selection,
  or `core/ids.json`.
- Adding a second Siulak file, a parent dialect, or a `base.json`.
- A generator tool. The committed JSON is the artifact; a test locks it to the
  v0.5 source.
- Making Siulak `review` or `approved`.

## 3. Contract: `dialects/siulak.json`

UTF-8 JSON, 2-space indent, keys sorted, final newline, no comments, no
executable content. The file follows the `dialect-model` schema.

```json
{
  "code": "siulak",
  "core": "0.6",
  "license": "CC BY-SA 4.0",
  "maintainer": "KerinciLang core",
  "messages": { "msg.area.name": "template", "...": "..." },
  "name": "Siulak (legacy 0.5)",
  "notes": "Frozen legacy vocabulary; do not edit. A completed Siulak re-review is a separate revision.",
  "orthography": "Frozen Siulak v0.5 spelling. Comparison words use underscores (lebih_daripado); lain kalu is two words; type.bool remains the English placeholder boolean.",
  "parent": null,
  "reviewer": null,
  "revision": 1,
  "sources": [
    "docs/02-vocabulary-worksheet.md",
    "kerincilang.py v0.5 LEGACY_WORDS and LEGACY_OPERATORS"
  ],
  "status": "draft",
  "words": { "fn.add": "tambah", "...": "..." }
}
```

The exact string values for `name`, `notes`, `orthography`, and `sources` are
part of this spec; tests may assert them.

### 3.1 Words (69)

`words` contains exactly these groups, copied from `kerincilang.py`:

| Group | Count | Source |
|---|---|---|
| `kw.*` | 26 | `LEGACY_WORDS` |
| `op.*` | 6 | `LEGACY_OPERATORS` (the word, not the symbol) |
| `fn.*` | 24 | `LEGACY_WORDS` |
| `type.*` | 9 | `LEGACY_WORDS` |
| `mode.*` | 3 | `LEGACY_WORDS` |
| `reserved.error` | 1 | `LEGACY_WORDS` |

There are no other word IDs and no missing ones. `type.bool` is `"boolean"` and
stays that way; it is a known v0.5 placeholder, not a bug to fix here.

### 3.2 Messages (68)

`messages` contains every `msg.*` ID in `core/ids.json`, with the template equal
to that ID's `id_gloss`. Placeholders are copied unchanged and must match the
catalogue's `placeholders` list. No message is reworded.

### 3.3 Metadata

| Field | Value | Rule |
|---|---|---|
| `code` | `siulak` | matches the filename |
| `name` | `Siulak (legacy 0.5)` | display name |
| `status` | `draft` | frozen, not re-reviewed |
| `core` | `0.6` | current catalogue |
| `revision` | `1` | first committed data revision |
| `parent` | `null` | resolves against the base only |
| `license` | `CC BY-SA 4.0` | `dialects/` scope |
| `maintainer` | `KerinciLang core` | project maintainer |
| `reviewer` | `null` | no 0.6 reviewer |
| `sources` | two strings above | provenance |
| `orthography` | string above | spelling note |
| `notes` | string above | freeze policy |

No `approved` claim is made. `reviewer` stays null until a real Siulak review.

## 4. `dialects/siulak.md`

A short Markdown note beside the data:

1. **Freeze declaration.** Siulak is frozen at v0.5 as a `draft`; the 0.6
   release does not re-review it.
2. **Provenance.** `docs/02-vocabulary-worksheet.md`, the v0.5 speaker review,
   and the `LEGACY_WORDS` / `LEGACY_OPERATORS` tables in `kerincilang.py`.
3. **Word table.** Every one of the 69 word IDs with its word and namespace,
   including the six operators, three modes, nine types, and `kelihu`.
4. **Messages.** One sentence: every `msg.*` template is the Indonesian
   `id_gloss` from `core/ids.json`, with placeholders unchanged.
5. **Change policy.** A word or message may change only in a new revision after
   a Siulak speaker review. Normalization, renaming, and "fixing" v0.5 quirks
   are out of scope. `type.bool` is recorded as a known placeholder.
6. **Authority.** `dialects/siulak.json` is the runtime data; `docs/02` is the
   decision history; `siulak.md` explains the freeze without replacing either.

The word table may be generated during implementation, but the committed
Markdown is the artifact and is not regenerated at runtime.

## 5. Runtime behavior

No runtime code change is expected. The existing loader and selection code must
handle the new file as-is:

- `load_dialect("siulak")` reads `dialects/siulak.json` and returns a complete
  `Dialect`; every ID is owned by the file (`report.fallbacks == []`,
  `report.missing() == []`).
- `report.tiers()` is `{1: (32, 32), 2: (104, 104), 3: (1, 1)}`.
- `DialectVocabulary` matches `LegacySiulak` for every ID:
  - `word(id)`, `surface()`, `operators()`, `reserved()`, and `mode_id(word)`
    for words;
  - `message(id, args)` for messages, with the same formatted text.
- A program with `# dialek: siulak` uses the file, not the `LEGACY` object, and
  prints no fallback warnings.
- `--dialek siulak` has the same result for a headerless file and for `-c`.
- `--ketat` exits 0: a complete draft has no Tier 1 base fallback.
- The missing-file special case stays: if `dialects/siulak.json` is absent,
  `resolve_dialect("siulak")` still returns `LEGACY`. Packaging and tests rely
  on that shim, and removing it is a separate decision.

The default vocabulary for a bare `run_source()` remains `LEGACY`. This module
does not change which object is the default; it only makes the explicit Siulak
path load the file.

If a test finds a behavioral difference between `DialectVocabulary` and
`LegacySiulak`, fix the data first. A code change requires a note in the spec's
implementation log and the user's approval.

## 6. Tests: `tests/test_siulak_legacy.py`

Plain-Python style, `tempfile` for temporary programs, explicit paths. Sections:

1. **File and load.** `dialects/siulak.json` exists; `load_dialect("siulak")`
   succeeds; `dialect.report.problems == []`.
2. **Completeness.** `tiers()` is complete; `fallbacks` and `missing()` are
   empty; `words` and `messages` together cover exactly the 137 catalogue IDs,
   with no extra key.
3. **Word mapping.** Every `LEGACY_WORDS` entry and every `LEGACY_OPERATORS`
   word equals the file's value; no word ID is missing or extra.
4. **Message mapping.** Every `msg.*` template equals `id_gloss`; placeholders
   match the catalogue; count is 68.
5. **Vocabulary equivalence.** For all 69 word IDs, `DialectVocabulary` and
   `LegacySiulak` agree on `word`, `surface`, `operators`, `reserved`, and
   `mode_id`; for all 68 messages they format identically with sample values for
   every declared placeholder.
6. **Selection.** A temporary `.krc` with `# dialek: siulak` runs with no
   fallback warning on stderr; `--dialek siulak` does the same for a headerless
   program; output equals the same program run with `LEGACY`.
7. **Gate.** `python tools/cek_dialek.py --kode siulak` exits 0 and prints
   `tier 1 32/32, tier 2 104/104, tier 3 1/1`; `--ketat` also exits 0.
8. **No regression.** The six earlier suites stay green and unedited,
   `compileall`, `build.py`, and `dist/krc.pyz` still pass.

Test names and failure messages are English. The test never writes into
`dialects/`; it reads the committed file.

## 7. Boundaries

### Always

- Freeze complete data, not a partial file that silently falls back.
- Copy v0.5 values exactly, including `boolean` and every message template.
- Keep `docs/02` as the decision log and add `siulak.md` as the freeze note.
- Keep the `LegacySiulak` shim and the missing-file fallback.
- Keep existing tests and tutorial expectations unchanged.

### Ask first

- Changing any frozen word, operator, type, mode, reserved word, or message.
- Changing `status` from `draft`, or setting a `reviewer`.
- Adding a parent, a second Siulak file, or normalizing v0.5 spelling.
- Removing `LegacySiulak` or changing the default `run_source()` vocabulary.
- Adding a generator tool or a new worksheet column.

### Never

- Edit an existing test to make the freeze pass.
- "Fix" `type.bool` or any other v0.5 quirk in this module.
- Mark Siulak `review` or `approved` without a speaker review.
- Modify `core/ids.json`, the loader, or runtime selection to special-case data.
- Drop an ID and let the English base supply it silently.

## 8. Success criteria

1. `dialects/siulak.json` loads with no problems and owns all 137 IDs.
2. `siulak.md` records provenance, the 69-word table, the message rule, and the
   change policy.
3. `DialectVocabulary` and `LegacySiulak` agree on every word and message.
4. A `# dialek: siulak` program and `--dialek siulak` produce v0.5-identical
   output with no fallback warnings.
5. `cek_dialek --kode siulak` and `--ketat` exit 0; `cek_dialek --semua` exits 0.
6. All existing suites, `compileall`, `build.py`, and `dist/krc.pyz` pass.

## 9. Decisions

| # | Decision | Recommendation |
|---|---|---|
| D1 | Complete snapshot, not a partial file. | Yes: all 69 words and 68 messages; zero fallbacks. |
| D2 | Status `draft`, revision 1, reviewer null. | Yes: frozen is not reviewed. |
| D3 | The v0.5 source of truth is `LEGACY_WORDS` / `LEGACY_OPERATORS` plus `id_gloss`. | Yes: a test locks the data to it. |
| D4 | Keep `LegacySiulak` and the missing-file path. | Yes: compatibility shim for packaging and `run_source()`. |
| D5 | Keep `docs/02`; add `dialects/siulak.md`. | Yes: history and runtime data stay separate. |
| D6 | Preserve every quirk, including `type.bool` = `"boolean"`. | Yes: a re-review is a later, explicit change. |
| D7 | No generator tool. | Yes: one committed artifact, one equivalence test. |

## 10. Next step

On approval: write `tasks/plan.md` and `tasks/todo.md` for this module, add
`dialects/siulak.json`, `dialects/siulak.md`, and
`tests/test_siulak_legacy.py`, then run all six existing suites plus this one,
`cek_dialek`, the generators, `compileall`, `build.py`, and `dist/krc.pyz` from a
temp directory.
