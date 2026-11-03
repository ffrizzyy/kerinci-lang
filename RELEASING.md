# Releasing KerinciLang

This is the maintainer checklist for a release. It assumes the repository is
`kerinci-lang` and the release is `v0.6.0`. Change the numbers, not the order.

## 1. Start clean

```bash
git switch main
git pull
git status
```

The tree must be clean, and every earlier change must be pushed. Do not tag a
dirty tree.

## 2. Agree on the version

These locations must all say `0.6.0`:

| Location | Field |
|---|---|
| `kerincilang.py` | `__version__` |
| `pyproject.toml` | `version` |
| `vscode-extension/package.json` | `version` |
| `README.md` | `Version **0.6.0**` |
| `GETTING-STARTED.md` | folder, banner, extension folder, tag, release name |
| `CHANGELOG.md` | top heading `## 0.6.0 (YYYY-MM-DD)` |
| `RELEASING.md` | the tag in step 7 |
| `docs/07-roadmap.md` | the `v0.6.0` milestone |

`core/ids.json` stays `"core": "0.6"`. It is a MAJOR.MINOR compatibility tuple,
not the package version. A patch release does not change it.

## 3. Regenerate, then check for a diff

```bash
python3 tools/buat_glosarium.py
python3 make_highlight.py
python3 tools/sinkron_tutorial.py --bangun koto-payang
git diff --exit-code
```

If any generated file changed, review the change, commit it, and start the
release again. Never hand-edit a generated glossary, grammar, or tutorial tree.

## 4. Run the offline gate

```bash
python3 build.py
python3 tools/cek_dialek.py --semua
python3 -m compileall -q .
```

`build.py` runs every offline suite, includes `tests/test_docs_release.py`,
skips the network-dependent wheel smoke with one line, and rebuilds
`dist/krc.pyz`. `cek_dialek --semua` must exit 0. Repeat this step after any
fix.

## 5. Run the wheel smoke

```bash
python3 tests/test_release.py
```

This copies the repository without `.git`, `build`, `dist`, `*.egg-info`,
`__pycache__`, and `*.pyc`; builds a wheel with `python -m pip wheel . --no-deps`;
checks that the wheel contains `core/ids.json`, `dialects/siulak.json`,
`dialects/siulak.md`, `dialects/koto-payang.json`, and
`dialects/koto-payang.md`; checks that it contains no `dialects/src/*.csv`, no
`__pycache__`, and no `.pyc`; installs it into a target directory; and runs both
dialects from a cwd outside the checkout.

CI runs this suite on Ubuntu with Python 3.12. The other matrix jobs and the
Windows/macOS smoke jobs run the offline suites only.

## 6. Smoke the zipapp

From a temporary directory, with no checkout on the path:

```bash
python3 /path/to/kerinci-lang/dist/krc.pyz --version
python3 /path/to/kerinci-lang/dist/krc.pyz program-siulak.krc
python3 /path/to/kerinci-lang/dist/krc.pyz program-koto-payang.krc
```

Use one program per dialect; the Koto Payang program needs a
`# dialek: koto-payang` header. Both must print the expected output and exit 0.
A missing word warning belongs on stderr, never in stdout.

## 7. Commit, tag, push, publish

```bash
git add -A
git commit -m "release: v0.6.0"
git tag -a v0.6.0 -m "KerinciLang 0.6.0"
git push
git push origin v0.6.0
```

On the GitHub Releases page, create `v0.6.0` from the tag and attach
`dist/krc.pyz`. Paste the dialect status table from `CHANGELOG.md` into the
release notes. Do not attach a dialect file separately; it is inside the
zipapp.

## 8. After the release

Install the wheel in a clean environment and run:

```bash
krc --version
krc program-siulak.krc
krc program-koto-payang.krc
```

Then confirm the release page shows the asset and the notes. If a check fails,
do not move the tag: publish a patch release.

## Changing the release scope

A dialect may appear in a release only after its file exists and its speaker
record is written. To add one:

1. Add and review `dialects/<code>.json`, `dialects/<code>.md`, and its
   worksheet.
2. Generate its tutorial tree and add it to `tests/test_tutorial_dialects.py`.
3. Regenerate the grammar and the tutorial indexes.
4. Add the dialect row to `CHANGELOG.md` and to the release notes.
5. Update the version if the scope changes the compatibility tuple.

Never attach a dialect name to a release before its file exists, and never
promote `review` to `approved` without the second speaker pass. The 0.6.0 scope
is Siulak (frozen `draft`) and Koto Payang (`review`); Semurup, Sungai Liuk,
and Rawang are not included.
