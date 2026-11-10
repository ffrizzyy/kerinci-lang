# 01. Vision and Goals

Status (2026-11-02): this is the original v1 vision, kept for history. The
current status is in [`07-roadmap.md`](07-roadmap.md). The language now has a
multi-dialect engine, Siulak is frozen at its v0.5 vocabulary, and Koto Payang
is the second dialect, now `approved`; see [`09-adding-a-dialect.md`](09-adding-a-dialect.md).

## Purpose

Create a working programming language that uses Kerinci vocabulary so that:

1. Speakers can see their language used in a modern, technical domain.
2. Learners get a reason to use and record Siulak words.
3. The language gets visibility among students, developers, and linguists.

## Principles

- **Preservation first.** Every design choice should favor authentic vocabulary over cleverness.
- **Small and learnable.** About 15 keywords and a tiny grammar. A beginner should write a program in 10 minutes.
- **Correctness comes from speakers.** The vocabulary is reviewed by native speakers, not assumed.
- **Open and documented.** Anyone can read, fork, and correct it.
- **Portable.** Works on any computer with Python.

## Audience

| Audience | Need |
|---|---|
| Kerinci students | A fun, culturally relevant way to learn programming |
| Teachers | Material in Siulak and Indonesian |
| Linguists and cultural groups | A showcase and a place to record vocabulary |
| Hobbyists | A small language that is easy to extend |

## Scope of version 1

**In scope:** variables, numbers, strings, booleans, arithmetic, comparison, `if/else`, `while`, functions, `print`, `input`, comments.

**Out of scope for v1 (later):** lists (`daftar`), maps (`peta`), `untuk` loops, imports (`ambik`), type conversion, file I/O, Incung script, reduplication features. See `02` for the keyword plan.

## Decisions to record

Fill these in as you decide.

- Language name: **KerinciLang** (alternative: KerinciScript)
- File extension: **.krc**
- Dialects: **no standard dialect.** Siulak is the first, frozen at its v0.5 vocabulary for compatibility; Koto Payang is the second, `approved`. A new dialect is a data file with its own speakers.
- Reference dictionary: the Siulak dictionary (record title, author, year, URL in `02`)
- Licence: see `06-community-and-preservation.md`

## Success criteria

- [ ] A "hello world" program runs with Siulak keywords
- [ ] A native speaker has reviewed every keyword
- [ ] A beginner tutorial exists in Siulak and Indonesian
- [ ] At least five people outside the project have tried it
- [ ] Source and documentation are public

## Naming the language

Pick a name only after the vocabulary work, so it reflects the dictionary. Good names are short (2-3 syllables), easy to type in Latin letters, and carry meaning to speakers. Check that the name is not already used by another programming project.
