"""Load and validate dialect files.

A dialect is data: ``dialects/<code>.json``. This module reads it, checks every
rule in ``SPEC-dialect-model.md``, and merges it with its parents and with a
neutral English base synthesized from ``core/ids.json``.

Nothing here chooses a dialect for a program; that is ``runtime-selection``.
Loading never executes a dialect: the files are JSON only.
"""
import json
import os
import pathlib
import re
import unicodedata

try:
    from importlib.resources import files as _resource_files
except ImportError:                                   # pragma: no cover - Python < 3.9
    _resource_files = None

import kerincilang
from kerincilang import CATALOG, OP_SYMBOLS, Vocabulary

IDS = CATALOG["ids"]
CORE_VERSION = CATALOG["core"]
MAX_BYTES = 1024 * 1024
MAX_CHAIN = 64

CODE_RE = re.compile(r"^[a-z0-9-]+$")
WORD_RE = re.compile(r"^[a-z][a-z0-9_]*$")
CORE_RE = re.compile(r"^(\d+)\.(\d+)$")
PLACEHOLDER_RE = re.compile(r"\{([a-z][a-z0-9_]*)\}")

STATUSES = ("draft", "review", "approved", "deprecated")

# `kw`, `op`, `reserved`, and `fn` claim a word before it can be read as a name,
# so they must be pairwise disjoint. `type` words are only printed and `mode`
# words are only passed as strings, so they may share with anything.
GUARDED = ("kw", "op", "reserved", "fn")

FIELD_TYPES = {
    "code": (str,),
    "name": (str,),
    "status": (str,),
    "core": (str,),
    "revision": (int,),
    "parent": (str, type(None)),
    "license": (str,),
    "maintainer": (str,),
    "reviewer": (str, type(None)),
    "sources": (list,),
    "orthography": (str,),
    "words": (dict,),
    "messages": (dict,),
    "notes": (str,),
}
REQUIRED = ("code", "name", "status", "core", "revision", "parent", "license",
            "maintainer", "reviewer", "sources", "orthography", "words")


# ---- problems -------------------------------------------------------------
class Problem:
    """One validation finding. `blocking` errors stop a load; warnings do not."""

    __slots__ = ("code", "id", "message", "severity")

    def __init__(self, code, id, message, severity="error"):
        self.code = code
        self.id = id
        self.message = message
        self.severity = severity

    @property
    def blocking(self):
        return self.severity == "error"

    def __str__(self):
        return "%s: %s: %s" % (self.code, self.id if self.id is not None else "-",
                               self.message)

    def __repr__(self):
        return "Problem(%r, %r, %r, %r)" % (self.code, self.id, self.message,
                                            self.severity)


class DialectError(Exception):
    """A dialect that cannot be loaded. `.problems` holds every finding."""

    def __init__(self, code, id, message, problems=None):
        self.code = code
        self.id = id
        self.message = message
        self.problems = list(problems) if problems else [Problem(code, id, message)]
        text = str(self.problems[0])
        extra = len(self.problems) - 1
        super().__init__(text + (" (%d more problem%s)" % (extra, "" if extra == 1 else "s")
                                 if extra > 0 else ""))


# ---- the report -----------------------------------------------------------
class Report:
    """What a speaker review wants to know about one dialect."""

    def __init__(self, code, own, sources, problems):
        self.code = code
        self.own = set(own)
        self.fallbacks = sorted((id, source) for id, source in sources.items()
                                if source != code)
        self.problems = list(problems)

    def tiers(self):
        """{tier: (defined by this file, total IDs in that tier)}.

        Covers every catalogue ID, messages included: `present` counts only what
        this file writes itself, so a parent or the base never inflates it.
        """
        counts = {1: [0, 0], 2: [0, 0], 3: [0, 0]}
        for id, entry in IDS.items():
            counts[entry["tier"]][1] += 1
            if id in self.own:
                counts[entry["tier"]][0] += 1
        return {tier: (present, total) for tier, (present, total) in counts.items()}

    def missing(self):
        """[(id, tier)] still coming from the base, not from the dialect chain."""
        return sorted((id, IDS[id]["tier"]) for id, source in self.fallbacks
                      if source == "base")


# ---- the vocabulary seam --------------------------------------------------
class _Suspend:
    """Context manager: quiet a DialectVocabulary's fallback notifications."""

    def __init__(self, vocab):
        self.vocab = vocab
        self.saved = None

    def __enter__(self):
        self.saved = self.vocab._notify
        self.vocab._notify = None
        return self.vocab

    def __exit__(self, *exc):
        self.vocab._notify = self.saved
        return False


class DialectVocabulary(Vocabulary):
    """A resolved dialect, ready for `run_source(..., vocab=...)`."""

    def __init__(self, dialect):
        self.dialect = dialect
        self.code = dialect.code
        self.core = dialect.core
        self._words = dialect.words
        self._messages = dialect.messages
        self._base_ids = dialect.base_ids
        self._notify = None
        self._surface = {word: id for id, word in self._words.items()
                         if id.startswith("kw.")}
        self._modes = {word: id for id, word in self._words.items()
                       if id.startswith("mode.")}
        self._reserved = {word for id, word in self._words.items()
                          if id.startswith("reserved.")}

    def watch(self, notify):
        """Called as notify(id, word) the first time a base fallback is used."""
        self._notify = notify

    def suspend(self):
        """Silence fallback notifications (eager built-in registration)."""
        return _Suspend(self)

    def word(self, id):
        if self._notify is not None and id in self._base_ids:
            self._notify(id, self._words[id])
        return self._words[id]

    def message(self, id, args=None):
        if self._notify is not None and id in self._base_ids:
            self._notify(id, None)
        return self._messages[id].format(**(args or {}))

    def mode_id(self, word):
        return self._modes.get(word)

    def surface(self):
        return dict(self._surface)

    def operators(self):
        return {self._words[id]: symbol for id, symbol in OP_SYMBOLS.items()}

    def reserved(self):
        return set(self._reserved)


class Dialect:
    """A validated, fully resolved dialect."""

    def __init__(self, data, words, messages, sources, problems):
        self.data = data
        self.code = data["code"]
        self.name = data["name"]
        self.status = data["status"]
        self.core = data["core"]
        self.revision = data["revision"]
        self.words = words
        self.messages = messages
        self.base_ids = {id for id, source in sources.items() if source == "base"}
        own = {id for id, source in sources.items() if source == self.code}
        self.report = Report(self.code, own, sources, problems)
        self.vocab = DialectVocabulary(self)


# ---- the neutral base -----------------------------------------------------
def _normalize(text):
    """`greater than` -> `greater_than`; the base word of an ID."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    return text.strip("_")


def _base_data():
    words, messages = {}, {}
    for id, entry in IDS.items():
        if id.startswith("msg."):
            messages[id] = entry["en"]
        else:
            words[id] = _normalize(entry["en"])
    return {
        "code": "base",
        "name": "English base",
        "status": "approved",
        "core": CORE_VERSION,
        "revision": 1,
        "parent": None,
        "license": "MIT",
        "maintainer": "KerinciLang core",
        "reviewer": "KerinciLang core",
        "sources": ["core/ids.json"],
        "orthography": "Neutral English fallback; not a spoken dialect.",
        "words": words,
        "messages": messages,
        "notes": "Synthesized from core/ids.json. Do not edit by hand.",
    }


_BASE = []


def base_dialect():
    """The synthesized English base, cached. There is no base.json."""
    if not _BASE:
        data = _base_data()
        sources = {id: "base" for id in IDS}
        _BASE.append(Dialect(data, dict(data["words"]), dict(data["messages"]),
                             sources, []))
    return _BASE[0]


# ---- reading files --------------------------------------------------------
class _DuplicateKey(Exception):
    def __init__(self, key):
        self.key = key


def _no_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise _DuplicateKey(key)
        seen[key] = value
    return seen


def _root(root=None):
    """The dialects directory: a checkout, a wheel, or dist/krc.pyz."""
    if root is not None:
        return pathlib.Path(root) if isinstance(root, (str, os.PathLike)) else root
    try:
        if _resource_files is not None:
            return _resource_files("dialects")
    except (ImportError, ModuleNotFoundError, FileNotFoundError, OSError):
        pass
    return pathlib.Path(__file__).parent


def _target(root, code):
    """Join a validated code onto the root; refuse anything outside it."""
    root = _root(root)
    target = root.joinpath(code + ".json")
    if isinstance(root, pathlib.Path):
        root = root.resolve()
        target = target.resolve()
        if root != target and root not in target.parents:
            raise DialectError("path", code, "the dialect path escapes the dialects directory")
    return target


def _read_one(root, code):
    """Read and parse one dialect file. Returns None when it does not exist."""
    target = _target(root, code)
    if not target.is_file():
        return None
    raw = target.read_bytes()
    if len(raw) > MAX_BYTES:
        raise DialectError("size", code, "the dialect file is larger than 1 MiB")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise DialectError("json", code, "the dialect file must be UTF-8 text")
    try:
        data = json.loads(text, object_pairs_hook=_no_duplicates)
    except _DuplicateKey as err:
        raise DialectError("json", code, "duplicate key: %r" % err.key)
    except json.JSONDecodeError as err:
        raise DialectError("json", code, "invalid JSON at line %d column %d: %s"
                           % (err.lineno, err.colno, err.msg))
    if not isinstance(data, dict):
        raise DialectError("json", code, "the dialect file must contain a JSON object")
    return data


def available_dialects(root=None):
    """The usable dialect codes in a root, sorted. `base` has no file."""
    root = _root(root)
    found = []
    for entry in root.iterdir():
        name = entry.name
        if not name.endswith(".json"):
            continue
        code = name[:-5]
        if code != "base" and CODE_RE.match(code):
            found.append(code)
    return sorted(found)


def _core_tuple(text):
    if not isinstance(text, str):
        return None
    match = CORE_RE.match(text)
    return (int(match.group(1)), int(match.group(2))) if match else None


# ---- validation -----------------------------------------------------------
def _word_problem(id, word):
    if not isinstance(word, str):
        return Problem("schema", id, "the word must be text, not %s"
                       % type(word).__name__)
    if not word.strip():
        return Problem("word-empty", id, "the word is empty")
    if unicodedata.normalize("NFC", word) != word:
        return Problem("word-charset", id, "%r is not NFC text" % word)
    if any(ch.isupper() for ch in word):
        return Problem("word-case", id, "%r has uppercase letters" % word)
    if not WORD_RE.match(word):
        return Problem("word-charset", id,
                       "%r must match ^[a-z][a-z0-9_]*$" % word)
    return None


def _message_problem(id, template):
    if not isinstance(template, str):
        return Problem("schema", id, "the message must be text, not %s"
                       % type(template).__name__)
    declared = set(IDS[id]["placeholders"])
    used = set(PLACEHOLDER_RE.findall(template))
    if used != declared:
        return Problem("message-placeholder", id,
                       "placeholders %s do not match the catalogue's %s"
                       % (sorted(used), sorted(declared)))
    return None


def _clash_problems(words):
    buckets = {}
    for id, word in words.items():
        if id.split(".", 1)[0] not in GUARDED or not isinstance(word, str):
            continue
        buckets.setdefault(word, []).append(id)
    problems = []
    for word in sorted(buckets):
        ids = buckets[word]
        if len(ids) > 1:
            problems.append(Problem("clash", word,
                                    "the word %r is used by %s"
                                    % (word, ", ".join(sorted(ids)))))
    return problems


def _validate(data, filename, root, check_clash):
    problems = []
    if not isinstance(data, dict):
        return [Problem("schema", None, "the dialect must be a JSON object")]

    # schema: unknown keys, missing keys, types, enums
    for key in sorted(set(data) - set(FIELD_TYPES)):
        problems.append(Problem("schema", key, "unknown field %r" % key))
    for key in REQUIRED:
        if key not in data:
            problems.append(Problem("schema", key, "missing required field %r" % key))
    for key in sorted(set(data) & set(FIELD_TYPES)):
        value, expected = data[key], FIELD_TYPES[key]
        if expected == (int,):
            ok = isinstance(value, int) and not isinstance(value, bool)
        else:
            ok = isinstance(value, expected)
        if not ok:
            problems.append(Problem("schema", key, "%r must be %s, not %s"
                                    % (key, "text" if expected == (str,) else
                                       " / ".join(t.__name__ for t in expected),
                                       type(value).__name__)))
    if data.get("status") not in STATUSES and isinstance(data.get("status"), str):
        problems.append(Problem("schema", "status", "status must be one of %s"
                                % ", ".join(STATUSES)))
    for key in ("name", "license", "maintainer", "orthography"):
        if isinstance(data.get(key), str) and not data[key].strip():
            problems.append(Problem("schema", key, "%r must not be empty" % key))
    if isinstance(data.get("sources"), list):
        for item in data["sources"]:
            if not isinstance(item, str) or not item.strip():
                problems.append(Problem("schema", "sources",
                                        "every source must be a non-empty text"))
                break

    # code and filename
    code = data.get("code")
    if isinstance(code, str):
        if not CODE_RE.match(code):
            problems.append(Problem("code", code,
                                    "the code must match ^[a-z0-9-]+$"))
        if filename is not None:
            stem = pathlib.PurePath(filename).stem
            if code != stem:
                problems.append(Problem("code", code,
                                        "the code %r does not match the file name %r"
                                        % (code, stem)))

    # core version
    core = _core_tuple(data.get("core"))
    if isinstance(data.get("core"), str) and core is None:
        problems.append(Problem("core-version", "core",
                                "core must be MAJOR.MINOR, not %r" % data["core"]))
    elif core is not None and core > _core_tuple(CORE_VERSION):
        problems.append(Problem("newer-core", "core",
                                "written for core %s, this runtime is %s"
                                % (data["core"], CORE_VERSION), severity="warning"))

    # review metadata
    if data.get("status") == "approved" and not data.get("reviewer"):
        problems.append(Problem("reviewer-missing", "reviewer",
                                "an approved dialect needs a reviewer"))
    if data.get("status") != "draft" and isinstance(data.get("sources"), list) \
            and not data["sources"]:
        problems.append(Problem("source-missing", "sources",
                                "a %s dialect needs at least one source"
                                % data.get("status")))

    # words
    words = data.get("words")
    if isinstance(words, dict):
        for id in sorted(words):
            word = words[id]
            if id.startswith("msg."):
                problems.append(Problem("wrong-namespace", id,
                                        "a msg.* ID belongs in messages, not words"))
                continue
            if id not in IDS:
                problems.append(Problem("unknown-id", id, "no such ID in core/ids.json"))
                continue
            found = _word_problem(id, word)
            if found:
                problems.append(found)
        if check_clash:
            problems.extend(_clash_problems(words))

    # messages
    messages = data.get("messages")
    if isinstance(messages, dict):
        for id in sorted(messages):
            template = messages[id]
            if not id.startswith("msg."):
                problems.append(Problem("wrong-namespace", id,
                                        "%r belongs in words, not messages" % id))
                continue
            if id not in IDS:
                problems.append(Problem("unknown-id", id, "no such ID in core/ids.json"))
                continue
            found = _message_problem(id, template)
            if found:
                problems.append(found)

    return problems


def _walk_chain(code, root, first_data=None):
    """Follow `parent` from a leaf upward, stopping before `base`."""
    chain, problems, seen = [], [], []
    current, data = code, first_data
    while current and current != "base":
        if current in seen:
            problems.append(Problem("parent-cycle", current,
                                    "the parent chain loops: %s"
                                    % " -> ".join(seen + [current])))
            break
        if len(seen) >= MAX_CHAIN:
            problems.append(Problem("parent-cycle", current,
                                    "the parent chain is longer than %d" % MAX_CHAIN))
            break
        seen.append(current)
        if data is None:
            try:
                data = _read_one(root, current)
            except DialectError as err:
                problems.extend(err.problems)
                break
            if data is None:
                problems.append(Problem("missing" if not chain else "parent-missing",
                                        current,
                                        ("no dialect file named %r" % (current + ".json"))
                                        if not chain else
                                        ("the parent %r does not exist" % current)))
                break
        chain.append((current, data))
        parent = data.get("parent")
        current = parent if isinstance(parent, str) and parent else None
        data = None
    return chain, problems


def validate_dialect(data, filename=None, root=None):
    """Every problem in one file, including its parent chain. Never prints."""
    problems = _validate(data, filename, root, check_clash=True)
    if isinstance(data, dict):
        code = data.get("code")
        if isinstance(code, str) and CODE_RE.match(code):
            _, parent_problems = _walk_chain(code, root, data)
            problems.extend(parent_problems)
    seen, unique = set(), []
    for problem in problems:
        key = (problem.code, problem.id, problem.message)
        if key not in seen:
            seen.add(key)
            unique.append(problem)
    return unique


def load_dialect(code, root=None):
    """Load, validate, and resolve one dialect. Raises `DialectError`."""
    if not isinstance(code, str) or not CODE_RE.match(code):
        raise DialectError("path", code, "the dialect code must match ^[a-z0-9-]+$")
    if code == "base":
        return base_dialect()

    chain, problems = _walk_chain(code, root)
    for item_code, data in chain:
        problems.extend(_validate(data, item_code, root, check_clash=False))

    blocking = [p for p in problems if p.blocking]
    if blocking:
        raise DialectError(blocking[0].code, blocking[0].id, blocking[0].message,
                           problems)

    # Merge: the base first, then ancestors, then the file. The leaf wins.
    words = {id: _normalize(entry["en"]) for id, entry in IDS.items()
             if not id.startswith("msg.")}
    messages = {id: entry["en"] for id, entry in IDS.items() if id.startswith("msg.")}
    sources = {id: "base" for id in IDS}
    for item_code, data in reversed(chain):
        for id, word in data.get("words", {}).items():
            words[id] = word
            sources[id] = item_code
        for id, template in data.get("messages", {}).items():
            messages[id] = template
            sources[id] = item_code

    problems.extend(_clash_problems(words))
    blocking = [p for p in problems if p.blocking]
    if blocking:
        raise DialectError(blocking[0].code, blocking[0].id, blocking[0].message,
                           problems)

    leaf = chain[0][1]
    return Dialect(leaf, words, messages, sources, problems)
