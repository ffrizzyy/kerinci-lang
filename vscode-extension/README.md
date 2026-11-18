# KerinciLang for VS Code

Syntax highlighting and a per-file dialect picker for `.krc` files, generated
from the dialect data in `dialects/`.

## Install (0.6.1)

Copy this whole `vscode-extension/` folder into VS Code's extensions folder
under the name `kerincilang.kerincilang-0.6.1`:

- Windows: `%USERPROFILE%\.vscode\extensions\`
- macOS and Linux: `~/.vscode/extensions/`

Then restart VS Code and open a `.krc` file. Files ending in `.krc` get colors
for comments, strings, numbers, keywords, word operators, built-in functions,
and the `betul` / `salah` / `kosong` values, plus bracket matching and `#`
comment toggling.

This folder was prepared for the release but was not tested in a live VS Code
installation here; the tutorial and the interpreter work without it.

## Highlighting follows the file

VS Code picks a grammar from the language mode, not from the file's contents, so
the extension ships one grammar per dialect next to the union grammar:

| Language mode | Grammar | Used for |
|---|---|---|
| KerinciLang | `syntaxes/krc.tmLanguage.json` | no header, an unknown code, or auto-detect turned off |
| KerinciLang (Siulak) | `syntaxes/krc-siulak.tmLanguage.json` | line 1 `# dialek: siulak` |
| KerinciLang (Koto Payang) | `syntaxes/krc-koto-payang.tmLanguage.json` | line 1 `# dialek: koto-payang` |

When a `.krc` file opens, and whenever line 1 changes, the extension reads the
same rule as the interpreter:

```text
^\s*#\s*dialek\s*:\s*([a-z0-9-]+)\s*$
```

If the code names an included dialect, it switches the language mode to that
dialect. A header is an ordinary comment, so it stays colored as one:

```krc
# dialek: koto-payang
nytak "Halo"
```

No header means the file's dialect depends on `--dialek` at run time, so the
union grammar stays in charge and highlights every valid word from every
dialect. A word that only one dialect uses is highlighted in that dialect's
grammar and not in the others, so a Siulak file does not color `meriksu`.

## The picker

Open the Command Palette and run **KerinciLang: Pilih Dialek**, or click the
language name in the status bar. The list has:

- **Otomatis (ikuti baris 1)** - go back to following the header.
- **Union (semua dialek)** - color every dialect's words.
- **Siulak**, **Koto Payang** - use that dialect's grammar.

A manual choice lasts until the file is closed. It changes the language mode in
the editor only; the file is never edited. Set `kerincilang.autoDetectDialect`
to `false` in Settings to stop the header from switching the mode.

`type.*` and `mode.*` words are not highlighted: they appear as runtime output
or as string arguments, and coloring them would also color ordinary text.
`fn.*` built-ins are highlighted only when followed by `(`, as in 0.5.
Reserved words such as `kelihu` are not highlighted because they cannot be used
as names.

## Regenerate

Do not edit anything in `syntaxes/` or `dialects.json` by hand. From the
repository root:

```bash
python3 make_highlight.py
```

The generator loads every dialect through `dialects/loader.py` and writes:

- the union grammar, `syntaxes/krc.tmLanguage.json`;
- one grammar per dialect, `syntaxes/krc-<code>.tmLanguage.json`;
- `dialects.json`, the catalogue this extension reads at runtime;
- and removes stale `krc-*.tmLanguage.json` files for dialects that no longer
  exist.

Every file is deterministic JSON with a trailing newline.
`tests/test_docs_release.py` fails if any committed file differs from a fresh
generation, if a dialect word is missing from its grammar, or if another
dialect's word leaks into it.

## Publish

Package the folder with `vsce`. The extension version must match the release
version in `pyproject.toml` and `kerincilang.py`.
