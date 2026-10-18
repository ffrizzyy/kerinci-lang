# 06. Community and Preservation

For a cultural project, this step determines whether the language is used or forgotten. Start it early.

## Why involve speakers first

- Dictionaries can be incomplete or reflect older spellings.
- Siulak differs from other Kerinci dialects; speakers will know which words feel natural.
- Keywords chosen with community involvement are more likely to be adopted and respected.
- Speakers are also the audience: they decide whether the project honors the language.

## Who to approach

| Group | What they can offer |
|---|---|
| Native Siulak speakers (elders and young people) | Word choices, pronunciation, naturalness |
| Local schools and teachers in Kerinci | Testing with students, classroom feedback |
| Regional cultural offices and language agencies | Credibility, access to resources and prior documentation |
| Local universities (linguistics, informatics) | Review, student contributors |
| Local developer communities | Code contributions, events |
| Diaspora and online Kerinci groups | Feedback, reach, shares |

## Process for vocabulary review

1. Share the draft table from `02-vocabulary-worksheet.md` with at least three speakers.
2. Ask for each word: "Does this sound natural for this meaning? Is there a better one?"
3. Record disagreements; don't hide them. Note the dialect variation.
4. Keep a changelog of vocabulary decisions with the reason and reviewer (with permission).
5. Re-review before each major release.

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
| Before launch | Share `docs/02-vocabulary-worksheet.md` (its checklist) and the tutorial with speakers; gather corrections through the issue templates in `.github/` |
| Launch | Publish source, docs, and a short demo video |
| After launch | Workshops in schools; a small coding competition; a "word of the month" post |
| Ongoing | Accept vocabulary corrections via issues; publish release notes in Siulak |

## Outreach message template

> Halo, I'm building a programming language that uses Siulak Kerinci words, as a way to help preserve and promote the language. I'm using [dictionary name] as a starting point and would be grateful if a native speaker could review about 15 words to check they sound natural. It takes about 15 minutes. All contributors can be credited if they wish.

(Translate into Indonesian, and into Siulak with a speaker's help.)

## Long-term preservation

- Archive the repository (releases, docs, vocabulary table) in more than one place.
- Keep the vocabulary table in a plain, open format (CSV or Markdown).
- Document decisions so future maintainers understand the choices.
- Name co-maintainers from the community so the project outlives any one person.
- Explore adding Incung script after checking Unicode support and font availability.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Wrong or unnatural word choices | Speaker review; keep the keyword table swappable |
| Dialect disputes | Document Siulak as the reference; allow variant tables later |
| Project stalls | Keep scope small; recruit co-maintainers |
| Copyright issues with dictionary | Cite entries, avoid bulk copying, check the licence |
| Low adoption | Tie to schools, events, and tutorials |
