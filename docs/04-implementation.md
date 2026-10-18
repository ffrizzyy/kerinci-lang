# 04. Implementation

## Repository layout

```
README.md                  front page (English)
GETTING-STARTED.md         step-by-step guide for a newly unzipped copy
kerincilang.py             the whole interpreter (one file, no dependencies)
pyproject.toml             packaging: provides the `krc` command
build.py                   runs all tests, then builds dist/krc.pyz
make_highlight.py          generates the VS Code grammar from the keyword table
examples/                  example programs (.krc)
tutorial/                  13 lessons, answers, glossary in English; tutorial/id/ is the Indonesian copy (every code sample is tested)
tests/                     test_kerincilang.py (language) and test_tutorial.py (tutorial + glossary)
tools/                     sinkron_tutorial.py (check/refresh tutorial output), buat_glosarium.py
docs/                      design documents (this folder)
vscode-extension/          syntax highlighting for .krc files
.github/                   CI workflow and issue templates
```

The full source of the interpreter is `kerincilang.py` (read it top to bottom: keyword tables, lexer, parser, built-ins, interpreter, command line).

## Architecture

```
source (.krc)  ->  Lexer  ->  tokens  ->  Parser  ->  AST  ->  Interpreter  ->  output
                     ^
               KEYWORDS table (Siulak words)
```

| Stage | Responsibility | Where in `kerincilang.py` |
|---|---|---|
| Keyword table | Internal name to Kerinci word; checked for duplicates at startup | `KEYWORDS`, `SURFACE` |
| Lexer | Text to tokens; `mulai`/`habih` become `{`/`}` | `tokenize()` |
| Parser | Tokens to AST, recursive descent, one method per grammar rule | `class Parser` |
| Interpreter | Walks the AST; scopes via `Env`; lists are Python lists; built-ins live in a parent scope (`new_global()`); `balik`/`putuh`/`lanjut` via exceptions | `run()`, `ev()`, `Env` |
| Errors | One `LangError` type, Indonesian messages with line numbers | `LangError` |

## Running

```bash
krc contoh.krc                    # after `pip install .`
python3 krc.pyz contoh.krc        # single-file build
python3 kerincilang.py contoh.krc # from source
python3 tests/test_kerincilang.py   # the language
python3 tests/test_tutorial.py      # every tutorial sample + glossary coverage
```

Python 3.9 or newer (3.11 or newer recommended: it allows function calls to nest 400 deep instead of 80); no packages needed.

## Command line

| Command | What it does | Exit code |
|---|---|---|
| `krc` | REPL; keeps reading while `{`, `(`, `[` (or `mulai`) are still open | 0 |
| `krc file.krc` | Runs the program | 0, or 1 on a program error |
| `krc -c "code"` | Runs one piece of code | 0 / 1 |
| `krc --version`, `krc --help` | Information | 0 |
| missing file or bad encoding | Message in Indonesian | 2 |

Closed pipes (`krc program.krc | head`) and Ctrl+C are handled without a traceback. `tanyo()` returns an empty text when input ends.

## Packaging and building

| File | Role |
|---|---|
| `pyproject.toml` | Declares the package and the `krc` command (`krc = kerincilang:main`), so `pip install .` works |
| `build.py` | Runs the test suite, then builds `dist/krc.pyz` (a Python zipapp, about 20 KB) and copies the examples into `dist/` |

To release a new version: change `__version__` in `kerincilang.py` and `version` in `pyproject.toml`, run `python3 build.py`, and share `dist/krc.pyz`. To publish on PyPI later, run `python3 -m build` and `twine upload dist/*` (needs an account and the `build` and `twine` packages).

## How it works

**Lexer.** One regular expression with named groups. Identifiers use `[^\W\d]\w*`, so any Unicode letter works and words like `kurang_daripado` are single tokens. An identifier in `WORD_OPERATORS` becomes the matching symbol token, one in `SURFACE` becomes a keyword token, and one in `RESERVED` (`kelihu`) is rejected.

**Parser.** Each precedence level calls the next-higher one (`expression` -> `and_` -> `equality` -> ... -> `call` -> `primary`), which is why `1 + 2 * 3` is 7. `lain kalu` is just `lain` followed by another `kalu` statement, so any chain length works. The parser tracks loop depth so `putuh`/`lanjut` outside `selamo` are caught before the program runs.

**Lists and `untuk`.** `[ ... ]` is parsed in `primary()`, and indexing `xs[i]` is handled in the same loop as function calls, so `m[1][0]` and `f(x)[2]` work. `xs[i] = v` is recognised after parsing an expression: if the left side is an index, it becomes a `setindex` statement. `untuk <name> alem <source>` evaluates its source once, turns it into a sequence (`iterate()`, lists and text only), and runs the body in a fresh scope per item. Counting loops use `jarak(n)`, which builds a list (capped at `MAX_JARAK`).

**Maps.** A `peta` is a Python dict. The literal `{ key: value, ... }` is parsed in `primary()` (a `{` at the start of an expression is a map; after a condition it is a block, because blocks are only parsed where a statement list is expected). Keys are limited to text and whole numbers by `check_key`. Indexing goes through `get_item` and assignment through the `setindex` branch, so lists, text and maps share the `xs[i]` syntax.

**`pilih`.** Parsed as a statement with a list of (values, block) clauses and an optional default. At run time the subject is evaluated once and compared with `binary_op("==", ...)`; the first matching clause runs and the rest are skipped.

**Imports.** `ambik` evaluates to a file name, resolves it against `IMPORT_STACK` (the directory of the file currently running), and runs the file once in its own scope (`LOADED` caches it; `LOADING` catches cycles). The module's top-level names are then copied into the importing scope. Functions keep the closure of their own module, so private helpers still work. `run_file()` sets up the import directory for the main program.

**Files.** `bukak` returns a `Berkas` object (path, mode, Python file handle, closed flag), and every open one is tracked in `OPEN_FILES` so `run_file()` and `main()` can close them when the program ends. The mode is one of the words `"baco"`, `"tulis"`, `"nambahkah"`, mapped to Python's `r`, `w`, `a` in `MODES`. All Python `OSError`s are turned into `LangError`s by `file_error()`, so `kelihu` can catch them. Lines come from iterating the handle (`untuk b alem f`), through the same `iterate()` used for lists and maps.

**Errors (`cubo`, `tangkap`, `ngangkat`).** The parser reads `cubo <block> tangkap [name] <block>` into a `try` node and `ngangkat <expression>` into a `raise` node. At run time the first block runs in its own scope, and a `LangError` (or `RecursionError`) sends control to the handler with the message bound to the name. `ngangkat` simply raises a `LangError` with the given text, so there is only one kind of error in the interpreter. Control-flow signals (`balik`, `putuh`, `lanjut`) are Python exceptions of other types, so they pass through untouched. `kelihu` ("error") is in `RESERVED`, so using it as a name is rejected by the lexer.

**Text functions.** `pisah` and `disatu` are ordinary built-ins that wrap Python's `str.split` and `str.join` (with `pisah(text)` splitting on whitespace and an empty separator splitting into letters).

**Recursion.** Each language-level call adds several Python frames. `CALL_DEPTH` counts nested calls and raises a normal error beyond `MAX_CALL_DEPTH` (400 on Python 3.11+, where the recursion limit is raised to 12000; 80 on older versions). A stray `RecursionError` is converted into the same error, so runaway recursion can never crash the interpreter.

**Text escapes.** The lexer's `STRING` pattern allows backslash pairs, and `unescape()` converts `\n`, `\t`, `\"` and `\\` when the literal is parsed; anything else is an error with a line number.

**Conversions.** `bilangan` and `pecahan` accept numbers and ASCII number text only (a regular expression, so Unicode digits and `1_000` are rejected). `mecem` reads its names from `TYPE_NAMES`, where the boolean name is a marked placeholder.

**Built-ins.** `BUILTINS` maps a name to (argument count, Python function). `new_global()` puts them in a parent scope of the program's global scope, so user code can redefine any of them without touching the originals. To add one, write a Python function, add a line to `BUILTINS`, and add tests. Functions that change their argument (`nambahkah`) return `None`; the others return new values.

**Interpreter.** `Env` objects chain to their parent for lexical scope, and a function value stores the `Env` it was defined in, which is what makes closures work. `tetap` names are recorded in the scope's `consts` set and rejected on reassignment.

## Test suite

`tests/test_kerincilang.py` has 151 valid-program tests, 84 error tests, 9 import tests that build temporary multi-file projects, and 27 file tests that work in a temporary folder. `tests/test_tutorial.py` runs all 550 code blocks in `tutorial/` (English and Indonesian) (comparing real output with the output printed in the lesson) and checks that the glossary mentions every keyword and built-in (precedence, string joining, logic operators, `lain kalu` chains, comparison words, `mulai/habih`, loops, break/continue, recursion, closures, constants, Unicode names, and every error message).

## Next steps

| Step | Feature | Keywords |
|---|---|---|
| 0.2 ✅ | Lists, indexing, `panjang()`, `untuk` loop, arithmetic built-ins | `daftar`, `panjang`, `untuk`, `tambah`, `kurang`, `kali`, `bagi` |
| 0.2.1 ✅ | Loop and list helpers from speaker vocabulary | `alem`, `jarak`, `nambahkah`, `isi`, `milih`, `pulang` |
| 0.3 ✅ | Type conversion, maps, `pilih`, imports | `bilangan`, `pecahan`, `kato`, `mecem`, `peta`, `pilih`, `ambik` |
| 0.5 ✅ | Speaker vocabulary for errors and text; tutorial; repository packaging | `cubo`, `tangkap`, `ngangkat`, `pisah`, `disatu`; 13 tested lessons |
| 0.4 ✅ | Files, waiting, error handling, string escapes, safe recursion | `bukak`, `baco`, `tulis`, `tutup`, `hapus`, `nantik` |
| later | More text tools (case, find, replace, trim: need words), random numbers, dates, error values (`kelihu`), newline-terminated statements, bytecode VM, browser playground (transpile to JS) | |

## Adding a keyword (recipe)

1. Add it to `KEYWORDS` (right-hand side is the Kerinci word).
2. Add parsing in `Parser.statement()` or `Parser.primary()`.
3. Add execution in `run()` or `ev()`.
4. Add it to `make_highlight.py` and run it.
5. Add tests and a line to `03-syntax-design.md`.

## Learning resources

- *Crafting Interpreters* by Robert Nystrom (free online), Part I follows this design.
