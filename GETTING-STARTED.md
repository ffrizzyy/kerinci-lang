# Getting started

A step-by-step guide for a freshly unzipped copy of KerinciLang. Each step says what to do and what you should see. If something does not match, see **Troubleshooting** at the end.

## 1. Unzip

Unzip `kerincilang-0.5.0.zip`. You get one folder, `kerincilang-0.5.0`. Everything below happens inside it.

## 2. Check that Python is installed

KerinciLang needs **Python 3.9 or newer** (3.11 or newer is recommended). Open a terminal and type:

```bash
python3 --version
```

You should see something like `Python 3.12.3`.

- **Windows:** the command is usually `python --version` or `py --version`. Use `python` or `py` wherever this guide says `python3`.
- **No Python?** Install it from https://www.python.org/downloads/ (on Windows, tick "Add python.exe to PATH" in the installer), then open a new terminal.

## 3. Open a terminal inside the folder

- **Windows:** open the `kerincilang-0.5.0` folder in File Explorer, click the address bar, type `cmd`, and press Enter.
- **macOS:** right-click the folder and choose "New Terminal at Folder" (or in Terminal, type `cd ` and drag the folder into the window).
- **Linux:** right-click inside the folder and choose "Open in Terminal", or `cd` to it.

Check that you are in the right place:

```bash
python3 kerincilang.py --version
```

You should see `KerinciLang 0.5.0`.

## 4. Run your first program

```bash
python3 dist/krc.pyz examples/contoh.krc
```

(On Windows: `python dist\krc.pyz examples\contoh.krc`.) You should see these nine lines:

```text
Halo, Budi
120
1
2
4
5
Cukup
betul
kosong
```

That program uses `barang` (variables), `guno` (functions), `kalu` / `lain` (decisions), and `selamo` (a loop). `dist/krc.pyz` is the whole language in a single file; you can copy it anywhere.

## 5. Try the interactive prompt (REPL)

```bash
python3 dist/krc.pyz
```

Type lines and press Enter after each:

```text
>>> nyetak 2 + 3
5
>>> barang nama = "Budi"
>>> nyetak "Halo, " + nama
Halo, Budi
```

Press `Ctrl+D` (on Windows: `Ctrl+Z`, then Enter) to leave.

## 6. Write your own program

1. Open any text editor and type this line:

   ```
   nyetak "Halo, dunia"
   ```

2. Save it as `halo.krc` inside the `kerincilang-0.5.0` folder. Use the UTF-8 encoding (most editors do this by default; in Notepad choose it under "Save as").
3. Run it:

   ```bash
   python3 dist/krc.pyz halo.krc
   ```

   You should see `Halo, dunia`.

## 7. Learn the language

Open **[tutorial/README.md](tutorial/README.md)** and work through the 13 lessons in order. Every example in the lessons can be copied and run exactly as shown, and its output is printed underneath. When you meet a word you do not know, look it up in the **[glossary](tutorial/glossary.md)**.

More programs to read and run are in the `examples/` folder:

| File | What it shows |
|---|---|
| `contoh.krc` | functions, loops, decisions |
| `contoh-daftar.krc` | lists and the `untuk` loop |
| `contoh-peta.krc` | maps, `pilih`, converting kinds |
| `contoh-teks.krc` | splitting and joining text |
| `contoh-berkas.krc` | reading and writing files |
| `contoh-kesalahan.krc` | handling errors (`cubo` / `tangkap` / `ngangkat`); type an age when it asks |
| `contoh-impor.krc` | loading another file with `ambik` |

## 8. Optional: install the `krc` command

Instead of typing `python3 dist/krc.pyz`, you can install a short command:

```bash
pip install .
krc --version
krc examples/contoh.krc
```

If `krc` is "not found" afterwards, your Python scripts folder is not on your PATH; just keep using `python3 dist/krc.pyz`, which always works.

## 9. Optional: colours in VS Code

The folder `vscode-extension/` adds syntax highlighting for `.krc` files. Copy that whole folder into VS Code's extensions folder under the name `kerincilang.kerincilang-0.5.0`:

- Windows: `%USERPROFILE%\.vscode\extensions\`
- macOS and Linux: `~/.vscode/extensions/`

Then restart VS Code and open a `.krc` file. (This was prepared for you but could not be tested here, so if the colours do not appear, the tutorial and everything else still work without them.)

## 10. Optional: check that everything works

```bash
python3 tests/test_kerincilang.py
python3 tests/test_tutorial.py
```

Each should end with `ALL PASSED`. The first runs 271 tests of the language; the second runs all 550 code blocks in the tutorial and compares their output with what the lessons print. To rebuild `dist/krc.pyz` after changing anything, run `python3 build.py` (it runs both test files first).

## 11. What is in the folder

```text
README.md              what KerinciLang is
GETTING-STARTED.md     this guide
kerincilang.py         the whole interpreter (one file, no dependencies)
dist/krc.pyz           the same interpreter, ready to run
examples/              example programs
tutorial/              the 13-lesson tutorial (English; Indonesian copy in tutorial/id/)
docs/                  design documents; docs/02 is the vocabulary and review checklist
tests/                 automated tests
tools/                 helpers that keep the tutorial and glossary correct
vscode-extension/      syntax highlighting for VS Code
CONTRIBUTING.md        how speakers, teachers and programmers can help
CHANGELOG.md           what changed in each version
LICENSE, LICENSE-DOCS.md   the licences
.github/               automated testing and issue templates for GitHub
```

## 12. Before you publish the project

Everything works, but a few things need your input first:

1. **Credit the dictionary.** Fill in the dictionary title, authors and year in `LICENSE-DOCS.md` (and check the dictionary's own licence). Add the names of speakers who agreed to be credited.
2. **Fix the licence files.** In `LICENSE`, replace "KerinciLang contributors" with the real name or organisation. In `LICENSE-DOCS.md`, paste the full legal text of CC BY-SA 4.0 from https://creativecommons.org/licenses/by-sa/4.0/legalcode.
3. **Create the repository** (for example on GitHub), then from inside the folder:

   ```bash
   git init
   git add .
   git commit -m "KerinciLang v0.5.0"
   git branch -M main
   git remote add origin <the address of your new repository>
   git push -u origin main
   ```

   The automated tests in `.github/workflows/tests.yml` then run on Python 3.9 to 3.13 (and on Windows and macOS).
4. **Publish a release.** On the repository's Releases page, create `v0.5.0` and attach `dist/krc.pyz` so people can download the single file.

## Troubleshooting

| Problem | What to do |
|---|---|
| `python3: command not found` | On Windows use `python` or `py`; otherwise install Python (step 2). |
| `Kesalahan: Berkas tidak ditemukan: ...` | The file name or folder is wrong. Check you are inside `kerincilang-0.5.0` and spelled the name correctly. |
| `Kesalahan: Baris 1: karakter tidak dikenal ...` | Usually a missing closing quotation mark. |
| Any other `Kesalahan: ...` message | The messages are in Indonesian; [tutorial/glossary.md](tutorial/glossary.md#error-messages) explains the common ones. |
| Strange characters in output on Windows | Run `chcp 65001` first, or use Windows Terminal; save your programs as UTF-8. |
| A tutorial example behaves differently | Run `python3 tests/test_tutorial.py`; if it reports a problem, please open an issue. |
