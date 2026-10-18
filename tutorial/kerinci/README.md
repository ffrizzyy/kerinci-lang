# The tutorial in Kerinci

The tutorial does not exist in Kerinci yet. That is deliberate: Kerinci text should be written by speakers, so that it is correct and natural, and not machine-translated or guessed.

If you are a Kerinci speaker and want to help, this is how. **You do not need to know how to program.**

## Steps

1. Pick a lesson, for example `../01-hello-world.md` (the English version) or `../id/01-halo-dunia.md` (the Indonesian version). Translate from whichever you read more comfortably.
2. Copy it into this folder, keeping the file name: `tutorial/kerinci/01-hello-world.md`.
3. Translate **only the explanations**: headings, paragraphs, tables, summaries and exercises.
4. **Do not change** the code blocks (the ones that start with three backticks) or the `hasil` blocks, and do not change the Kerinci words that are part of the programming language.
5. If you think a programming word is not right, do not change it here. Make a note and tell us as described in [CONTRIBUTING.md](../../CONTRIBUTING.md), because a word has to be changed in one place only.
6. Check that all examples are still correct:

   ```bash
   python3 tools/sinkron_tutorial.py
   ```

   If it says `0 problems`, your translation is ready to send.

## What is most needed

In rough order of usefulness:

1. `00-setup.md` and `01-hello-world.md` (the first impression).
2. `glossary.md`: what each word means, in Kerinci itself.
3. Lessons 2 to 6.
4. The remaining lessons.

Thank you for helping to keep this language alive.
