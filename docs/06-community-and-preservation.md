# 06. Community and Preservation

For a cultural project, this step determines whether the language is used or forgotten. Start it early.

## Why involve speakers first

- Dictionaries can be incomplete or reflect older spellings.
- Kerinci has several dialects; Siulak differs from Koto Payang and from other
  varieties, and speakers will know which words feel natural in their own.
- Keywords chosen with community involvement are more likely to be adopted and respected.
- Speakers are also the audience: they decide whether the project honors the language.

KerinciLang is multi-dialect. Siulak was the first dialect and is frozen at its
v0.5 vocabulary for compatibility; Koto Payang is the second, at `review`.
There is **no standard dialect**, and no dialect may borrow another's words to
fill a gap. Adding one needs its own speakers and its own review record; see
[`09-adding-a-dialect.md`](09-adding-a-dialect.md).

## Who to approach

| Group | What they can offer |
|---|---|
| Native speakers of Siulak and other Kerinci dialects (elders and young people) | Word choices, pronunciation, naturalness |
| Local schools and teachers in Kerinci | Testing with students, classroom feedback |
| Regional cultural offices and language agencies | Credibility, access to resources and prior documentation |
| Local universities (linguistics, informatics) | Review, student contributors |
| Local developer communities | Code contributions, events |
| Diaspora and online Kerinci groups | Feedback, reach, shares |

## Process for vocabulary review

1. Share the dialect's worksheet with at least three speakers: the frozen
   Siulak record in `02-vocabulary-worksheet.md`, or the new dialect's CSV
   started through `09-adding-a-dialect.md`.
2. Ask for each word: "Does this sound natural for this meaning? Is there a better one?"
3. Record disagreements; don't hide them. Note the dialect variation.
4. Keep a changelog of vocabulary decisions with the reason and reviewer (with permission).
5. Re-review a dialect before promoting it; Siulak stays frozen for compatibility.

## Crediting and respecting contributors

- Ask permission before naming individuals.
- Credit the dictionary authors and publishers, and comply with the dictionary's licence. Do not copy large portions; cite entries.
- If any recordings or cultural material is used, get explicit consent.

## Licensing

| Part | Licence | File |
|---|---|---|
| Interpreter, tools, tests, examples, VS Code extension | MIT | `LICENSE` |
| Documentation, tutorial, vocabulary tables | CC BY-SA 4.0 | `LICENSE-DOCS.md` |

MIT lets anyone use and adapt the code with credit. CC BY-SA keeps the tutorial and vocabulary open while requiring credit and sharing improvements under the same terms, which fits a project whose purpose is to spread and preserve a language.

Before the first public release, still to do:

- [ ] Replace the copyright holder in `LICENSE` with the real name or organisation (it currently says "KerinciLang contributors").
- [ ] Copy the full legal text of CC BY-SA 4.0 from creativecommons.org into `LICENSE-DOCS.md` (it currently has the standard notice and a link).
- [ ] Check the licence of the Siulak dictionary the vocabulary comes from, and credit it in `README.md` and `docs/02-vocabulary-worksheet.md`. Do not copy large parts of the dictionary; cite entries.

## Outreach plan

| Phase | Action |
|---|---|
| Before launch | Share the Siulak checklist (`docs/02`) and the tutorial with speakers, and start any new dialect with `docs/09`; gather corrections through the issue templates in `.github/` |
| Launch | Publish source, docs, and a short demo video |
| After launch | Workshops in schools; a small coding competition; a "word of the month" post |
| Ongoing | Accept vocabulary corrections via issues; publish release notes in the language of the release |

## Outreach message template

> Halo, I'm building a programming language that uses Kerinci words from several dialects, as a way to help preserve and promote the language. Siulak was the first dialect; I am now looking for speakers of [dialect] to review its words. I'm using [dictionary or worksheet] as a starting point and would be grateful if a native speaker could check about 15 words for naturalness. It takes about 15 minutes. All contributors can be credited if they wish.

(Translate into Indonesian, and into the dialect with a speaker's help.)

## Long-term preservation

- Archive the repository (releases, docs, vocabulary table) in more than one place.
- Keep the vocabulary table in a plain, open format (CSV or Markdown).
- Document decisions so future maintainers understand the choices.
- Name co-maintainers from the community so the project outlives any one person.
- Explore adding Incung script after checking Unicode support and font availability.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Wrong or unnatural word choices | Speaker review per dialect; keep the words swappable |
| Dialect disputes | No dialect is standard; each file has its own speakers, sources, and review record |
| Project stalls | Keep scope small; recruit co-maintainers |
| Copyright issues with dictionary | Cite entries, avoid bulk copying, check the licence |
| Low adoption | Tie to schools, events, and tutorials |
