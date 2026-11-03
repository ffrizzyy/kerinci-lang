# KerinciLang for VS Code

Syntax highlighting for `.krc` files, generated from the dialect data in
`dialects/`.

## Install (0.6.0)

Copy this whole `vscode-extension/` folder into VS Code's extensions folder
under the name `kerincilang.kerincilang-0.6.0`:

- Windows: `%USERPROFILE%\.vscode\extensions\`
- macOS and Linux: `~/.vscode/extensions/`

Then restart VS Code and open a `.krc` file. Files ending in `.krc` get colors
for comments, strings, numbers, keywords, word operators, built-in functions,
and the `betul` / `salah` / `kosong` values (each in the reader's dialect),
plus bracket matching and `#` comment toggling.

This folder was prepared for the release but was not tested in a live VS Code
installation here; the tutorial and the interpreter work without it.

## One union grammar

The grammar is one file, `syntaxes/krc.tmLanguage.json`, and it covers **every
word every included dialect resolves to**. That includes words a dialect takes
from the neutral English base, such as `contains`, `list`, `map`, and `wait`
for Koto Payang. A word that only one dialect uses is still highlighted,
because no dialect is treated as the standard.

The line-1 header is a normal comment, so `# dialek: koto-payang` is colored
as a comment:

```krc
# dialek: koto-payang
nytak "Halo"
```

`type.*` and `mode.*` words are not highlighted: they appear as runtime output
or as string arguments, and coloring them would also color ordinary text.
`fn.*` built-ins are highlighted only when followed by `(`, as in 0.5.
Reserved words such as `kelihu` are not highlighted because they cannot be used
as names.

## No per-dialect picker in 0.6

A TextMate grammar cannot read the file to switch on `# dialek:`, so 0.6 ships
the union instead of a dialect picker. A picker is a later idea, not a
promise. The union colors every valid word and keeps the extension honest about
which dialects exist.

## Regenerate

Do not edit `syntaxes/krc.tmLanguage.json` by hand. From the repository root:

```bash
python3 make_highlight.py
```

The generator loads every dialect through `dialects/loader.py`, so adding a
dialect picks up its words automatically. It writes deterministic JSON with a
trailing newline. `tests/test_docs_release.py` fails if the committed grammar
differs from a fresh generation.

## Publish

Package the folder with `vsce`. The extension version must match the release
version in `pyproject.toml` and `kerincilang.py`.
