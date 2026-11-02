# Spec: translator

Status: **approved 2026-11-02.** Parent: `SPEC.md`. Capability map:
`translator`.
Depends on `runtime-selection`, `dialect-koto-payang`, and
`dialect-siulak-legacy`, all implemented. Date: 2026-11-02.

## 1. Objective

Add `krc terjemah`: translate one KerinciLang source file from its own dialect
to another dialect without executing it, renaming user names, reflowing the
text, or changing anything that is not a dialect word.

The translator is deliberately conservative. It translates a file only when the
result is lossless in the strong sense used by this project: a headered file
translated from A to B and back to A is byte-identical, and the target must
actually own every dialect word the file needs. When that is impossible the
command refuses with a specific error instead of guessing, falling back to
English, or silently producing a program that behaves differently.

After this module:

- `krc terjemah program.krc --ke koto-payang --out program.koto-payang.krc`
  writes a Koto Payang program.
- `krc terjemah program.krc --ke koto-payang` writes the translated source to
  stdout, so it can be piped.
- Comments, whitespace, string data, user names, numbers, punctuation, line
  endings, and a missing final newline are preserved byte for byte.
- A file that uses a word the target does not own is refused, never patched
  with an English base word.
- A user name that would collide with a target keyword, operator, built-in, or
  reserved word is refused, never renamed.
- A mixed-dialect import still runs: the translated main file and each imported
  file keep their own dialect.

## 2. Scope

### In scope

- `krc terjemah` dispatch, option parsing, usage text, and exit codes.
- Source-dialect resolution from the header, with `--dari` and Siulak as
  fallbacks.
- Lossless token rewriting for keywords, word operators, and built-in names.
- File-mode string translation in the one context where it is unambiguous:
  the second argument of a direct `bukak` call.
- Header replacement or insertion in the target dialect.
- User-symbol discovery, collision refusal, and built-in-shadowing refusal.
- Refusal when the target does not own a used ID, or when a mode/type string
  cannot be translated losslessly.
- Atomic `--out` writes, stdout mode, and `--kering`.
- `tests/test_translator.py`.
- Doc updates for the command and the lossless policy.

### Out of scope

- Translating imported files recursively, or building a cross-file symbol
  table. The translator is one file in 0.6.
- Translating arbitrary string data. Only the `bukak` mode argument is
  rewritten.
- Renaming user names, emitting a rename manifest, or rewriting code to make a
  collision go away.
- Making a translation in place. `--out` may not name the input file.
- A `--semua` directory mode, a batch tree mode, or a `--daftar-dialek` picker.
- Translating tutorial prose, messages, CLI text, or documentation.
- Executing the source to learn anything about it.
- Changing the catalogue, the loader, either dialect, or any existing test
  expectation.

## 3. Command

```bash
krc terjemah BERKAS --ke KODE
krc terjemah BERKAS --ke KODE --out BERKAS-BARU
krc terjemah BERKAS --ke KODE --out BERKAS-BARU --kering
krc terjemah BERKAS --ke KODE --dari KODE
krc terjemah --help
```

`terjemah` is a subcommand and must be the first argument, like `migrasi`.

| Form | Meaning |
|---|---|
| `BERKAS` | one existing `.krc` file |
| `--ke KODE` | required target dialect code |
| `--dari KODE` | source dialect for a file with no header; default `siulak` |
| `--out BERKAS` | write the result to this path; omit to write to stdout |
| `--kering` | with `--out`, check and report without writing |
| `--help`, `-h` | print `TERJEMAH_USAGE`, exit 0 |

Rules:

- `--ke` and `--dari` accept both `--ke kode` and `--ke=kode`.
- Exactly one input file is required. Extra positional arguments, a missing
  `--ke`, an unknown option, or an input that is not an existing `.krc` file is
  a usage error (exit 2).
- `--kering` without `--out` is a usage error (there is nothing to suppress;
  stdout mode already writes nothing).
- `--out` may not resolve to the input file (`realpath` + `normcase`); an
  in-place translation is refused with exit 2 before anything is read.
- Target and `--dari` codes are validated before the input is read. An unknown
  or invalid target is exit 2. An unknown or invalid `--dari` is exit 2, even
  when the file has a header that wins over it.
- A header naming a missing or invalid dialect is a file error (exit 1), the
  same as at runtime.
- `--help` short-circuits and exits 0 before any validation.

`USAGE` gains a `terjemah` line. `TERJEMAH_USAGE` documents the four options
and the stdout default. The command lives in `kerincilang.py`, so the wheel and
`dist/krc.pyz` need no packaging change.

## 4. Source and target dialects

Source resolution, in order:

1. A valid line-1 header: `# dialek: KODE`.
2. `--dari KODE` when there is no header.
3. `siulak` when neither is present.

This matches `runtime-selection` D1. A header always wins over `--dari`; the
translator never overrides a file's own declaration.

Target resolution is always explicit: `--ke KODE`. There is no target default
and no "same as source" shorthand.

| Case | Result |
|---|---|
| header matches `^#\s*dialek\s*:\s*([a-z0-9-]+)\s*$` | that code is the source |
| line 1 contains `dialek` but does not match | refuse: malformed header |
| no header line | `--dari`, else `siulak` |
| source code resolves to `LegacySiulak` (the frozen shim) | use its frozen words |
| target code is missing or invalid | usage error, exit 2 |
| source header code is missing or invalid | file error, exit 1 |

`base` is a valid vocabulary on both sides. It is the synthesized English base,
so translating to `base` is a debugging aid, not a spoken dialect. All IDs are
owned by `base`.

If the resolved source and target codes are identical, the command is a
validated copy: it parses the file, replaces or adds the header if needed, and
changes nothing else. User code that shadows a built-in is legal in the same
dialect and is not refused in this case.

## 5. What is translated

The rewriter scans the original text with the same master regular expression the
lexer uses, so it sees every token and every gap between tokens. It never
reconstructs the file from the AST.

| Source token | Translated? | Rule |
|---|---|---|
| `kw.*` word, including `mulai` / `habih` | yes | source word -> target word for the same ID |
| `{` `}` used instead of `mulai` / `habih` | no | punctuation is neutral |
| `op.*` word (`samo`, `lebih_daripado`, ...) | yes | source word -> target word for the same operator ID |
| operator symbol (`==`, `<`, `+`, ...) | no | symbols are neutral |
| `fn.*` built-in name | yes | source word -> target word, unless same-dialect |
| string literal that is the second argument of a direct `bukak` call | yes | source `mode.*` word -> target `mode.*` word |
| line-1 header code | yes | replaced with the target code |
| user identifier | no | never rewritten |
| string literal in any other position | no | user data; one exception is refused below |
| number, comment, whitespace, punctuation | no | byte-identical |

Example (Siulak -> Koto Payang):

```text
barang i = 0
selamo i kurang_daripado 3 {
    nyetak panjang([1, 2, 3])
    i = i + 1
}
```

becomes

```text
netakka_variabel i = 0
selamu i lebih_nik_dari 3 {
    nytak panja([1, 2, 3])
    i = i + 1
}
```

Algorithm:

1. Read the file as bytes; refuse a UTF-8 BOM or non-UTF-8 bytes.
2. Decode UTF-8, inspect line 1 with the runtime header rules, and resolve the
   source vocabulary. A malformed or unknown header is a refusal.
3. Tokenize and parse the whole file with the source vocabulary. This validates
   syntax and reserved words but never runs the program.
4. Walk the AST to collect every name the file declares: `barang` / `tetap`
   names, `guno` names and parameters, `for` loop variables, `catch` names, and
   assignment targets.
5. Scan the raw text token by token and classify each identifier as a keyword,
   an operator word, a built-in, a reserved word, or a user name. Build the set
   of dialect IDs actually used.
6. Apply section 6 checks. Any refusal stops before a byte is written.
7. Build non-overlapping edits for the header code, translated identifiers,
   and translated `bukak` mode strings; apply them to the original text.
8. Write the result atomically, or print it to stdout.

The tokenizer reflects `kw.begin` / `kw.end` to `{` / `}`. The rewriter does
not: it matches the source surface word first, so `mulai ... habih` becomes the
target's begin/end words while literal braces stay braces.

## 6. User symbols and losslessness

### Names the file declares

The translator collects every user name in the file and never renames one. The
AST is enough for declarations:

- `("var", name, ...)` and `("func", name, params, ...)`
- every function parameter
- `("for", var, ...)`
- the `catch` name in `("try", body, name, handler)`
- the target of `("assign", name, ...)`

Names copied into a scope by `ambik` are **not** analyzed. The translator is a
single-file tool in 0.6; cross-file symbol resolution is out of scope and is
documented as a limitation. Mixed imports still run because each file keeps its
own dialect.

### Refusals

The command refuses, without writing anything, when:

1. **A user name shadows a source built-in.** A declaration named `panjang`
   makes it impossible to know whether a later `panjang(...)` means the
   built-in or the user function. The error names the name and the built-in.
   This check does not apply when source and target codes are identical.
2. **A user name collides with a target guarded word.** If a name the file
   declares equals a target `kw.*`, `op.*`, `fn.*`, or `reserved.*` word, the
   translated file would either fail to parse or resolve a call to the wrong
   thing. The error names the name, its first line, and the target namespace.
3. **The target does not own a used ID.** "Own" means the ID comes from the
   target file or one of its parents, not from the synthesized English base. A
   fallback word is a loss on the way back and is not written. The error lists
   every missing ID, for example `fn.list`, `fn.map`, `fn.wait`, `fn.contains`.
   This is why a Koto Payang translation of `examples/contoh-berkas.krc`
   (which calls `nantik`) is refused instead of emitting `wait`.
4. **A mode or type string cannot be translated losslessly.** See below.

### Mode and type strings

A string literal is not a dialect word. The one unambiguous exception is the
file-mode argument:

```text
bukak(nama, "nambahkah")
```

Here the second argument of a direct call to the source `fn.open` built-in is a
`mode.*` value. The translator rewrites it to the target's `mode.append` word
while keeping the quotes.

Every other string is left alone. The translator refuses instead when leaving
it alone would change the program:

| Literal | Result |
|---|---|
| exactly a source `mode.*` word, direct second argument of `bukak` | translate to the target mode word |
| exactly a source `mode.*` word, any other position | refuse when the source and target words differ |
| exactly a source `type.*` word, any position | refuse when the source and target words differ |
| any other string | unchanged |

The type rule covers `kalu mecem(x) samo "kato"`. The translator does not try to
prove that the comparison is about a type; it refuses rather than guess. When
the source and target words are identical (for example `daftar` for
`type.list` in both Siulak and Koto Payang), the literal is already correct and
is allowed. A mode word stored in a variable and passed to `bukak` is refused
for the same reason: the translator only rewrites the direct argument.

### Round trip

For a file that has a header, uses only target-owned IDs, and contains no
refused string:

```text
A -> B -> A  ==  original bytes
```

The header code is the only header change each way; word replacements are
bijective by ID. A headerless file gains an explicit header, so its first round
trip is `original + header`, not byte-identical; this is stated in the docs and
tested separately.

No check requires running the program. Parsing is the only language operation
the translator performs.

## 7. Imports and mixed dialects

The translator parses import statements but does not follow them and does not
translate imported files.

- The `ambik` keyword becomes the target's import word (`impor` in Koto
  Payang); the path string is unchanged.
- An imported file keeps its own `# dialek:` header and therefore its own
  words, built-ins, and messages when the program runs.
- A translated main file that imports a module in another dialect is a supported
  mixed-dialect program. The runtime already gives every module its own
  vocabulary.
- Computed imports are not special to the translator: the expression is
  translated normally and the path is left to the runtime.
- When `--out` is used, the translator resolves each literal import from the
  output file's directory with the same rules as the runtime (exact path, then
  `.krc`). A literal import that would no longer resolve prints a warning and
  the command still exits 0, because the user may move the whole tree. Without
  `--out` there is no output directory to check.

Cross-file user symbols are not analyzed. A module that exports a name equal to
a target guarded word is outside this module's guarantee; the docs say so
plainly.

## 8. Output and exit codes

### Output

- Without `--out`, stdout is exactly the translated source. No summary is
  printed, so `krc terjemah a.krc --ke koto-payang > b.krc` is clean.
- With `--out`, the result is written atomically (temporary file in the same
  directory, then `os.replace`) and stdout gets one line:
  `terjemah: wrote BERKAS (siulak -> koto-payang)`.
- `--kering` with `--out` prints
  `terjemah: would write BERKAS (siulak -> koto-payang)` and writes nothing.
- Warnings and errors go to stderr with a `terjemah:` prefix.
- A refusal never leaves a partial output file. An existing `--out` file is
  untouched unless the whole translation succeeds.
- The output is UTF-8 without a BOM. The input BOM is refused, not stripped.
- The header line ending follows the file's first newline (`\r\n` or `\n`); a
  file with no newline gets `\n`. The rest of the file keeps its bytes.

### Exit codes

| Situation | Exit |
|---|---|
| translation or validated copy succeeded | 0 |
| `--kering` succeeded | 0 |
| BOM, non-UTF-8, malformed header, unknown source header dialect, parse error | 1 |
| target does not own a used ID, user-name collision, built-in shadowing, untranslatable mode/type string, write failure | 1 |
| missing/unknown target, unknown `--dari`, missing input, non-`.krc` input, `--out` same as input, `--kering` without `--out`, unknown option, extra argument, missing value | 2 |
| `--help` | 0 |

A warning about an import that would not resolve from a moved output directory
does not change the exit code.

## 9. Examples

```bash
# Translate a Siulak example to Koto Payang in a new file
python3 kerincilang.py terjemah examples/contoh.krc \
    --ke koto-payang --out /tmp/contoh.koto-payang.krc

# Preview the translation on stdout
python3 kerincilang.py terjemah examples/contoh.krc --ke koto-payang

# A headerless file needs --dari; Siulak is the default, so this is optional
python3 kerincilang.py terjemah old.krc --dari siulak --ke koto-payang

# Check without writing
python3 kerincilang.py terjemah examples/contoh.krc --ke koto-payang \
    --out /tmp/out.krc --kering
```

For the committed examples, with Koto Payang as the target (verified against
the token stream, not comments):

- `contoh.krc`, `contoh-kesalahan.krc`, `contoh-impor.krc`,
  `contoh-teks.krc`, and `perkakas.krc` translate and round-trip byte for byte.
- `contoh-berkas.krc` is refused because it calls `nantik` (`fn.wait`), which
  Koto Payang does not own.
- `contoh-daftar.krc` is refused because it calls `isi` (`fn.contains`).
- `contoh-peta.krc` is refused because it calls `isi` (`fn.contains`).

Words that appear only in a comment or a string (`daftar`, `peta`, `isi` in
prose) do not trigger a refusal; only real tokens do. No example is edited by
this module.

## 10. Tests: `tests/test_translator.py`

Plain-Python style, all work in `tempfile.TemporaryDirectory()`. The suite
covers the thirteen groups below and should land near 100 checks.

1. **Basic translation.** A Siulak program with every keyword, word operator,
   and built-in round-trips to Koto Payang with the expected exact text. Braces,
   `mulai` / `habih`, comments, indentation, blank lines, and trailing spaces
   are preserved; the header becomes `# dialek: koto-payang`.
2. **User names.** Declared variables, constants, functions, parameters, loop
   variables, catch names, and assignment targets are unchanged. A user name
   that looks like a dialect word in another namespace (`kato`, `tulis`) is
   unchanged when it is not a guarded word.
3. **Strings and comments.** A string containing `barang`, `nyetak`, `samo`, or
   a mode/type word as ordinary text is unchanged; a comment containing any
   word is unchanged; numbers and punctuation are unchanged.
4. **Operators.** Word operators translate; the same comparisons written as
   symbols stay symbols. `ngan` / `apo` / `idak` and the begin/end words
   translate; `{` `}` stay braces.
5. **Round trip.** `contoh.krc`, `contoh-kesalahan.krc`, `contoh-impor.krc`,
   `contoh-teks.krc`, and `perkakas.krc` go Siulak -> Koto Payang -> Siulak
   with byte-identical output. A headerless file gains a header and otherwise
   round-trips.
6. **Same dialect.** `--ke siulak` on a Siulak file is byte-identical, and on a
   headerless file adds `# dialek: siulak`. A same-dialect file that shadows a
   built-in is copied without a refusal.
7. **Target gaps.** `nantik(0.5)`, `daftar(...)`, `peta(...)`, and `isi(...)`
   are each refused when translating to Koto Payang, with `fn.wait`,
   `fn.list`, `fn.map`, and `fn.contains` named and exit 1; no output file is
   created or changed. The same refusal is proved on the committed
   `contoh-berkas.krc`, `contoh-daftar.krc`, and `contoh-peta.krc`.
8. **Collisions and shadowing.** A Siulak user name `ndik` is refused for a
   Koto Payang target because it is a target keyword; a name equal to a target
   operator or built-in is refused too; a declaration that shadows a source
   built-in is refused with the built-in named.
9. **Mode and type strings.** `bukak(nama, "nambahkah")` becomes
   `bukuak(nama, "tambah")`; a mode word in a variable, in a read call, or as
   plain data is refused; a type word like `"kato"` is refused, while a type
   word shared by both dialects (`"daftar"`) is allowed.
10. **Headers and refusals.** A valid header is replaced in place; a
    malformed header, unknown source header dialect, BOM, non-UTF-8 file, and
    syntax error each exit 1 and leave the input and any existing output
    untouched. `--dari` is ignored for source selection when a header exists
    but is still validated.
11. **Line endings and bytes.** A CRLF file keeps CRLF, a file without a final
    newline keeps that property, and a headerless file gets a header with the
    file's newline style.
12. **CLI and output.** stdout mode prints only the translated source;
    `--out` writes atomically and prints one summary line; `--kering` writes
    nothing; `--out` equal to the input, `--kering` without `--out`, a missing
    `--ke`, an unknown target, an unknown `--dari`, a non-`.krc` input, an
    unknown option, and extra arguments each exit 2; `--help` exits 0 and
    documents the options.
13. **Imports and packaging.** A translated main file that imports a
    Koto Payang module runs and prints the same output as before; the imported
    file is unchanged; a moved `--out` with a broken literal import warns but
    exits 0. A zipapp containing `kerincilang.py`, `core/`, `dialects/`, and a
    `__main__.py` runs `terjemah` from a clean temporary directory.

## 11. Boundaries

### Always

- Translate only on an explicit `--ke`; never guess a target.
- Preserve every byte that is not a dialect word or the header.
- Refuse when the target does not own a used ID.
- Refuse when a user name collides with a target guarded word.
- Refuse when a mode/type string cannot be translated losslessly.
- Parse only; never execute the source.
- Keep stdout clean in stdout mode.
- Keep `--out` atomic and refuse in-place translation.
- Keep the existing suites, expected outputs, tutorial blocks, and both
  dialect files unchanged.

### Ask first

- Recursing into imports or building a cross-file symbol table.
- Translating arbitrary string literals.
- Renaming a user symbol instead of refusing.
- Adding a batch/tree mode or an in-place mode.
- Changing the `--ke` / `--dari` syntax, the header syntax, or the source
  precedence.
- Adding catalogue IDs for translator text.
- Changing a Siulak or Koto Payang word.

### Never

- Emit an English base word because the target lacks an ID.
- Rewrite a user-declared name.
- Rewrite a comment, a non-mode string, a number, or formatting.
- Execute the source to discover declarations, imports, or types.
- Add a header above a malformed header, a BOM, or a syntax error.
- Write a partial or in-place output.
- Change a test expectation, tutorial output, or dialect word to make this
  pass.

## 12. Success criteria

1. `krc terjemah a.krc --ke koto-payang` prints a correct Koto Payang program
   with the target header and the source's formatting intact.
2. `--out` writes atomically, `--kering` writes nothing, and stdout mode prints
   only the program.
3. `contoh.krc`, `contoh-kesalahan.krc`, `contoh-impor.krc`,
   `contoh-teks.krc`, and `perkakas.krc` round-trip byte for byte;
   `contoh-berkas.krc` is refused for `fn.wait`, and `contoh-daftar.krc` and
   `contoh-peta.krc` for `fn.contains`.
4. Every declared user name is byte-identical in the output; a target collision
   or a source built-in shadow is refused with a precise error.
5. A mode string is translated only as the direct second argument of `bukak`;
   every other mode/type string that would change is refused.
6. A translated main file with a mixed-dialect import runs with the same
   output, and the imported file is untouched.
7. A BOM, malformed header, unknown source dialect, parse error, missing target
   ID, collision, or untranslatable string exits 1 without writing; usage and
   target errors exit 2.
8. `tests/test_translator.py` passes, all earlier suites stay green,
   `cek_dialek --semua`, both generators, `compileall`, `build.py`, and
   `dist/krc.pyz terjemah` pass, and `CAPABILITY-MAP.md` and the docs are
   updated.

## 13. Decisions

| # | Decision | Recommendation |
|---|---|---|
| D1 | Translate one file; do not recurse into imports. | Yes: review #17; mixed imports still run because each file has its own dialect. |
| D2 | Refuse when the target does not own a used ID; never emit a base fallback. | Yes: removes the round-trip loss called out in review B7. |
| D3 | Refuse a user-name collision instead of renaming. | Yes: parent open question 11. |
| D4 | Refuse a source name that shadows a built-in. | Yes: a word-based rewriter cannot resolve which use is the built-in. |
| D5 | Translate only the direct `bukak` mode string; refuse other mode/type strings that differ. | Yes: the only statically unambiguous case; variables and computed arguments are refused. |
| D6 | Leave all other strings and comments untouched. | Yes: they are user data, not vocabulary. |
| D7 | Header wins; `--dari` only fills in for a headerless file; default Siulak. | Yes: matches `runtime-selection` D1. |
| D8 | stdout when `--out` is omitted; `--out` is atomic and may not equal the input. | Yes: pipe-friendly and never destructive. |
| D9 | `--kering` requires `--out`. | Yes: stdout mode already writes nothing. |
| D10 | Same-dialect translation is a validated copy and skips symbol refusals. | Yes: no word changes, so no loss. |
| D11 | Translator output is English toolchain text, not a `msg.*` entry. | Yes: same precedent as `migrasi`; no catalogue or dialect churn. |
| D12 | Implement `terjemah` in `kerincilang.py`. | Yes: works in the wheel and zipapp without a packaging change. |

## 14. Next step

On approval: archive the `cli-migration` plan/todo, write
`tasks/plan.md` and `tasks/todo.md`, implement `terjemah` plus
`TERJEMAH_USAGE` and the `USAGE` line, add `tests/test_translator.py`, then run
all ten suites, `cek_dialek --semua`, both generators, `compileall`, `build.py`,
and `dist/krc.pyz terjemah` from a temporary directory. Update the docs and
`CAPABILITY-MAP.md`, commit, and push.
