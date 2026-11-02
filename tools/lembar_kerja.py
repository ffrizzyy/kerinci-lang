"""The dialect worksheet pipeline.

One canonical answer file per dialect, one validator, one reviewable DOCX, and
an export that fills an existing dialect skeleton. `core/ids.json` is read-only
here; this tool never changes the runtime or a dialect's metadata.

    python3 tools/lembar_kerja.py buat     --kode koto-payang
    python3 tools/lembar_kerja.py perbarui --kode koto-payang
    python3 tools/lembar_kerja.py periksa  --kode koto-payang --tulis
    python3 tools/lembar_kerja.py docx     --kode koto-payang
    python3 tools/lembar_kerja.py baca     --kode koto-payang --tulis
    python3 tools/lembar_kerja.py laporan  --kode koto-payang
    python3 tools/lembar_kerja.py json     --kode koto-payang

Exit codes:
    0  success (warnings do not fail)
    1  a validation or file problem
    2  bad usage
"""
import codecs
import csv
import io
import json
import os
import pathlib
import re
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dialects import loader  # noqa: E402

COLUMNS = ("id", "tier", "namespace", "en", "id_gloss", "answer", "notes",
           "status")
CATALOGUE_COLUMNS = ("tier", "namespace", "en", "id_gloss")
STATUSES = ("todo", "draft", "reviewed", "rejected")
ACCEPTED = ("draft", "reviewed")
GUARDED = ("kw", "op", "reserved", "fn")
CODE_RE = re.compile(r"^[a-z0-9-]+$")

MAX_CSV_BYTES = 2 * 1024 * 1024
MAX_DOCX_BYTES = 8 * 1024 * 1024
MAX_ZIP_ENTRIES = 32

COMMANDS = ("buat", "perbarui", "periksa", "docx", "baca", "laporan", "json")

HELP = """Usage:
  python3 tools/lembar_kerja.py COMMAND --kode CODE [options]

Commands:
  buat      create dialects/src/CODE.csv from core/ids.json
  perbarui  reconcile an existing CSV with a grown catalogue
  periksa   validate answers and print every problem by row and ID
  docx      render the CSV as a reviewable Word table
  baca      read a generated DOCX back into the CSV
  laporan   print tier counts, gaps, and readiness
  json      merge accepted answers into dialects/CODE.json

Options:
  --kode CODE   dialect code matching ^[a-z0-9-]+$ (required)
  --csv PATH    default dialects/src/CODE.csv
  --docx PATH   default dialects/src/CODE.docx
  --json PATH   default dialects/CODE.json
  --paksa       buat/docx may replace an existing file
  --tulis       periksa/baca may write the CSV
  --siap        apply the readiness gate to periksa
  -h, --help    show this help

Exit: 0 ok, 1 validation or file problem, 2 bad usage."""


# ---- catalogue ------------------------------------------------------------
def _load_catalogue():
    data = json.loads((ROOT / "core" / "ids.json").read_text(encoding="utf-8"))
    return data["ids"], data["core"]


IDS, CORE_VERSION = _load_catalogue()
ORDERED_IDS = sorted(IDS, key=lambda ident: (IDS[ident]["tier"], ident))


# ---- findings -------------------------------------------------------------
class Finding:
    """One worksheet problem, tied to a data row and a catalogue ID."""

    __slots__ = ("code", "id", "message", "severity", "row")

    def __init__(self, code, id=None, message="", severity="error", row=None):
        self.code = code
        self.id = id
        self.message = message
        self.severity = severity
        self.row = row

    @property
    def blocking(self):
        return self.severity == "error"

    def __str__(self):
        where = "row %d: " % self.row if self.row is not None else ""
        who = self.id if self.id is not None else "-"
        return "%s%s: %s: %s" % (where, who, self.code, self.message)


class Sheet:
    """Rows plus structural findings from reading one CSV."""

    def __init__(self, rows, findings):
        self.rows = rows
        self.findings = list(findings)

    @property
    def fatal(self):
        return any(f.code in ("csv-read", "csv-header") for f in self.findings)

    @property
    def structural(self):
        return [f for f in self.findings
                if f.code in ("csv-read", "csv-header", "csv-width", "csv-bom",
                              "unknown-id", "missing-id", "duplicate-id")]


# ---- small helpers --------------------------------------------------------
def _atomic_write_bytes(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=str(path.parent), prefix=".lembar-",
                                suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(temp, path)
    except BaseException:
        try:
            os.unlink(temp)
        except OSError:
            pass
        raise


def _atomic_write_text(path, text):
    _atomic_write_bytes(path, text.encode("utf-8"))


def _csv_bytes(rows):
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(COLUMNS)
    for row in rows:
        writer.writerow([row.get(column, "") for column in COLUMNS])
    return out.getvalue().encode("utf-8")


def _write_csv(path, rows):
    _atomic_write_bytes(path, _csv_bytes(rows))


def _catalogue_row(ident):
    entry = IDS[ident]
    return {
        "id": ident,
        "tier": str(entry["tier"]),
        "namespace": entry["namespace"],
        "en": entry["en"],
        "id_gloss": entry["id_gloss"],
        "answer": "",
        "notes": "",
        "status": "todo",
    }


def _rows_by_id(rows):
    found = {}
    for row in rows:
        found.setdefault(row["id"], row)
    return found


def _default_paths(code):
    base = ROOT / "dialects"
    return {
        "csv": base / "src" / (code + ".csv"),
        "docx": base / "src" / (code + ".docx"),
        "json": base / (code + ".json"),
    }


# ---- reading the CSV ------------------------------------------------------
def read_sheet(path):
    """Read a canonical CSV. Reports structure; answers are checked later."""
    findings, rows, seen = [], [], set()
    path = pathlib.Path(path)
    try:
        raw = path.read_bytes()
    except OSError as err:
        return Sheet([], [Finding("csv-read", None,
                                  "cannot read %s: %s" % (path, err.strerror or err))])
    if len(raw) > MAX_CSV_BYTES:
        return Sheet([], [Finding("csv-read", None,
                                  "%s is larger than 2 MiB" % path)])
    if raw.startswith(codecs.BOM_UTF8):
        findings.append(Finding("csv-bom", None,
                                "the file starts with a UTF-8 BOM"))
        raw = raw[len(codecs.BOM_UTF8):]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return Sheet([], findings + [Finding("csv-read", None,
                                             "the file is not UTF-8 text")])
    try:
        parsed = list(csv.reader(io.StringIO(text, newline="")))
    except csv.Error as err:
        return Sheet([], findings + [Finding("csv-read", None,
                                             "the CSV cannot be parsed: %s" % err)])
    if not parsed:
        return Sheet([], findings + [Finding("csv-header", None,
                                             "the CSV is empty; expected the eight-column header")])
    if tuple(parsed[0]) != COLUMNS:
        return Sheet([], findings + [Finding(
            "csv-header", None,
            "expected %r, found %r" % (",".join(COLUMNS), ",".join(parsed[0])))])

    for number, values in enumerate(parsed[1:], 1):
        if len(values) != len(COLUMNS):
            findings.append(Finding(
                "csv-width", None,
                "expected %d fields, found %d" % (len(COLUMNS), len(values)),
                row=number))
            continue
        row = dict(zip(COLUMNS, values))
        row["_row"] = number
        ident = row["id"]
        if not ident:
            findings.append(Finding("unknown-id", None,
                                    "the row has an empty ID", row=number))
            continue
        if ident in seen:
            findings.append(Finding("duplicate-id", ident,
                                    "the ID appears more than once", row=number))
            continue
        seen.add(ident)
        if ident not in IDS:
            findings.append(Finding("unknown-id", ident,
                                    "no such ID in core/ids.json", row=number))
            continue
        rows.append(row)

    for ident in ORDERED_IDS:
        if ident not in seen:
            findings.append(Finding("missing-id", ident,
                                    "the catalogue ID has no row"))
    return Sheet(rows, findings)


# ---- normalizing and checking answers -------------------------------------
def _nfc(text):
    return unicodedata.normalize("NFC", text)


def normalize_word(text):
    """NFC, trim, lowercase, whitespace to `_`, one trailing `()` removed."""
    text = _nfc(text).strip().lower()
    text = re.sub(r"\s+", "_", text)
    if text.endswith("()"):
        text = text[:-2]
    return text


def normalize_message(text):
    """NFC and trim only; placeholders are never renamed."""
    return _nfc(text).strip()


def _normalized_answer(row):
    if row["namespace"] == "msg":
        return normalize_message(row["answer"])
    return normalize_word(row["answer"])


def _synthetic(code, words, messages):
    """A draft dialect with no invented reviewer or review status."""
    return {
        "code": code,
        "name": code,
        "status": "draft",
        "core": CORE_VERSION,
        "revision": 1,
        "parent": None,
        "license": "CC BY-SA 4.0",
        "maintainer": "worksheet",
        "reviewer": None,
        "sources": [],
        "orthography": "Worksheet draft; not a released spelling.",
        "words": words,
        "messages": messages,
    }


def _word_alternative(answer):
    return "/" in answer or "," in answer


def check_sheet(sheet, code):
    """Every section-6 rule. Returns findings, words, and messages."""
    findings = list(sheet.findings)
    by_id = _rows_by_id(sheet.rows)
    words, messages = {}, {}

    for row in sheet.rows:
        ident = row["id"]
        entry = IDS[ident]
        for column in CATALOGUE_COLUMNS:
            expected = str(entry["tier"]) if column == "tier" else entry[column]
            if row[column] != expected:
                findings.append(Finding(
                    "catalogue-value", ident,
                    "%s is %r, the catalogue says %r"
                    % (column, row[column], expected), row=row["_row"]))
        for column in COLUMNS:
            value = row[column]
            if value and value[0] in "=+-@":
                findings.append(Finding(
                    "csv-formula", ident,
                    "the %s cell starts with %r; the tool never evaluates it"
                    % (column, value[0]), severity="warning",
                    row=row["_row"]))

        status, answer = row["status"], row["answer"]
        if status not in STATUSES:
            findings.append(Finding(
                "status", ident,
                "unknown status %r; expected todo, draft, reviewed, or rejected"
                % status, row=row["_row"]))
        elif status == "todo" and answer.strip():
            findings.append(Finding(
                "status", ident,
                "a todo row must have an empty answer", row=row["_row"]))
        elif status in ("draft", "reviewed", "rejected") and not answer.strip():
            findings.append(Finding(
                "answer-empty", ident,
                "a %s row needs an answer" % status, row=row["_row"]))

        if not answer.strip():
            continue
        if entry["namespace"] == "msg":
            messages[ident] = normalize_message(answer)
            continue
        if _word_alternative(answer):
            findings.append(Finding(
                "answer-choice", ident,
                "choose one alternative, not %r" % answer, row=row["_row"]))
            continue
        normalized = normalize_word(answer)
        if not normalized:
            findings.append(Finding(
                "answer-empty", ident,
                "the answer is empty after normalization", row=row["_row"]))
            continue
        words[ident] = normalized

    data = _synthetic(code, words, messages)
    for problem in loader.validate_dialect(data, filename=code,
                                           root=ROOT / "dialects"):
        row = by_id.get(problem.id)
        if problem.code == "clash":
            involved = []
            for candidate in sheet.rows:
                if candidate["namespace"] in GUARDED \
                        and not _word_alternative(candidate["answer"]) \
                        and normalize_word(candidate["answer"]) == problem.id:
                    involved.append(candidate)
            if involved:
                involved.sort(key=lambda item: item["_row"])
                findings.append(Finding(
                    "clash", involved[0]["id"], problem.message,
                    "warning" if problem.severity == "warning" else "error",
                    row=involved[0]["_row"]))
                continue
        if row is not None:
            findings.append(Finding(
                problem.code, problem.id, problem.message, problem.severity,
                row=row["_row"]))
        else:
            findings.append(Finding(
                "internal", problem.id,
                "unmapped %s problem: %s" % (problem.code, problem.message),
                problem.severity))
    return findings, words, messages


def _counts(findings):
    errors = sum(1 for finding in findings if finding.blocking)
    warnings = sum(1 for finding in findings if not finding.blocking)
    return errors, warnings


def _print_findings(findings, stream=None):
    stream = stream or sys.stdout
    for finding in findings:
        print(finding, file=stream)


def _normalized_rows(rows):
    result = []
    for row in rows:
        copy = dict(row)
        copy["answer"] = _normalized_answer(row)
        result.append(copy)
    return result


# ---- tier math ------------------------------------------------------------
def _stats(rows):
    by_id = _rows_by_id(rows)
    totals = {tier: 0 for tier in (1, 2, 3)}
    answered = {tier: 0 for tier in (1, 2, 3)}
    reviewed = {tier: 0 for tier in (1, 2, 3)}
    missing_tier1 = []
    for ident in ORDERED_IDS:
        tier = IDS[ident]["tier"]
        totals[tier] += 1
        row = by_id.get(ident)
        if row is None:
            if tier == 1:
                missing_tier1.append(ident)
            continue
        if row["answer"].strip():
            answered[tier] += 1
        elif tier == 1:
            missing_tier1.append(ident)
        if row["status"] == "reviewed":
            reviewed[tier] += 1
    unreviewed = {tier: totals[tier] - reviewed[tier] for tier in (1, 2, 3)}
    return totals, answered, reviewed, missing_tier1, unreviewed


def _readiness(rows, tier):
    totals, _, reviewed, _, _ = _stats(rows)
    if tier == "review":
        unmet = totals[1] - reviewed[1]
        if not unmet:
            return True, ""
        return False, "tier 1 has %d unreviewed" % unmet
    unmet1 = totals[1] - reviewed[1]
    unmet2 = totals[2] - reviewed[2]
    parts = []
    if unmet1:
        parts.append("tier 1 has %d unreviewed" % unmet1)
    if unmet2:
        parts.append("tier 2 has %d unreviewed" % unmet2)
    return not parts, ", ".join(parts)


def _readiness_finding(rows, status, ident):
    if status not in ("review", "approved"):
        return None
    ready, why = _readiness(rows, status)
    if ready:
        return None
    return Finding("status", ident,
                   "not ready for %s: %s" % (status, why))


# ---- docx writing ---------------------------------------------------------
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"

DOCX_HEADERS = ("ID", "Tier", "English", "Indonesian", "Answer", "Notes")
DOCX_WIDTHS = (2200, 900, 2800, 2800, 3200, 3238)
GREY = "D9D9D9"

CONTENT_TYPES = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

ROOT_RELS = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

LEGEND = ("Grey columns come from the catalogue (core/ids.json) and must not "
          "be edited. Fill in Answer and Notes, then save this file.")


def _add_run_text(paragraph, text, bold=False):
    run = ET.SubElement(paragraph, W + "r")
    if bold:
        properties = ET.SubElement(run, W + "rPr")
        ET.SubElement(properties, W + "b")
    lines = str(text).split("\n")
    for index, line in enumerate(lines):
        if index:
            ET.SubElement(run, W + "br")
        node = ET.SubElement(run, W + "t")
        node.set(XML_SPACE, "preserve")
        node.text = line


def _add_cell(table_row, text, width, grey=False, bold=False):
    cell = ET.SubElement(table_row, W + "tc")
    properties = ET.SubElement(cell, W + "tcPr")
    width_node = ET.SubElement(properties, W + "tcW")
    width_node.set(W + "w", str(width))
    width_node.set(W + "type", "dxa")
    if grey:
        shading = ET.SubElement(properties, W + "shd")
        shading.set(W + "val", "clear")
        shading.set(W + "color", "auto")
        shading.set(W + "fill", GREY)
    paragraph = ET.SubElement(cell, W + "p")
    _add_run_text(paragraph, text, bold=bold)


def _document_xml(code, rows):
    document = ET.Element(W + "document")
    body = ET.SubElement(document, W + "body")

    legend = ET.SubElement(body, W + "p")
    _add_run_text(legend, "%s worksheet. %s" % (code, LEGEND), bold=True)

    table = ET.SubElement(body, W + "tbl")
    properties = ET.SubElement(table, W + "tblPr")
    width = ET.SubElement(properties, W + "tblW")
    width.set(W + "w", "0")
    width.set(W + "type", "auto")
    borders = ET.SubElement(properties, W + "tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = ET.SubElement(borders, W + side)
        border.set(W + "val", "single")
        border.set(W + "sz", "4")
        border.set(W + "space", "0")
        border.set(W + "color", "auto")
    layout = ET.SubElement(properties, W + "tblLayout")
    layout.set(W + "type", "fixed")

    grid = ET.SubElement(table, W + "tblGrid")
    for column_width in DOCX_WIDTHS:
        grid_column = ET.SubElement(grid, W + "gridCol")
        grid_column.set(W + "w", str(column_width))

    header_row = ET.SubElement(table, W + "tr")
    header_properties = ET.SubElement(header_row, W + "trPr")
    ET.SubElement(header_properties, W + "tblHeader")
    for header, column_width in zip(DOCX_HEADERS, DOCX_WIDTHS):
        _add_cell(header_row, header, column_width, bold=True)

    for row in rows:
        entry = IDS[row["id"]]
        values = (
            row["id"],
            str(entry["tier"]),
            entry["en"],
            entry["id_gloss"],
            row["answer"],
            row["notes"],
        )
        table_row = ET.SubElement(table, W + "tr")
        for index, (value, column_width) in enumerate(zip(values, DOCX_WIDTHS)):
            _add_cell(table_row, value, column_width, grey=index < 4)

    section = ET.SubElement(body, W + "sectPr")
    page_size = ET.SubElement(section, W + "pgSz")
    page_size.set(W + "w", "16838")
    page_size.set(W + "h", "11906")
    page_size.set(W + "orient", "landscape")
    margins = ET.SubElement(section, W + "pgMar")
    for side in ("top", "right", "bottom", "left"):
        margins.set(W + side, "850")
    margins.set(W + "header", "708")
    margins.set(W + "footer", "708")
    margins.set(W + "gutter", "0")

    return ET.tostring(document, encoding="utf-8", xml_declaration=True)


def _zip_entry(archive, name, data):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 0
    info.external_attr = 0
    archive.writestr(info, data)


def docx_bytes(code, rows):
    """A deterministic, dependency-free DOCX with one table."""
    document = _document_xml(code, rows)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        _zip_entry(archive, "[Content_Types].xml", CONTENT_TYPES)
        _zip_entry(archive, "_rels/.rels", ROOT_RELS)
        _zip_entry(archive, "word/document.xml", document)
    return buffer.getvalue()


def _docx_rows(sheet):
    """Catalogue order; catalogue columns come from core/ids.json."""
    by_id = _rows_by_id(sheet.rows)
    rows = []
    for ident in ORDERED_IDS:
        row = by_id.get(ident)
        if row is None:
            continue
        rows.append({"id": ident, "answer": row["answer"], "notes": row["notes"]})
    return rows


# ---- docx reading ---------------------------------------------------------
def _paragraph_text(node):
    parts = []
    for child in node.iter():
        if child.tag == W + "t":
            parts.append(child.text or "")
        elif child.tag == W + "br":
            parts.append("\n")
        elif child.tag == W + "tab":
            parts.append("\t")
    return "".join(parts)


def _cell_text(cell):
    paragraphs = cell.findall(W + "p")
    if paragraphs:
        return "\n".join(_paragraph_text(paragraph) for paragraph in paragraphs)
    return _paragraph_text(cell)


def _table_rows(table):
    return table.findall(W + "tr")


def _table_cells(table_row):
    return table_row.findall(W + "tc")


def read_docx(path):
    """Read a sheet this tool generated. Returns ({id: {answer, notes}}, findings)."""
    path = pathlib.Path(path)
    findings = []
    try:
        raw = path.read_bytes()
    except OSError as err:
        return {}, [Finding("docx-format", None,
                            "cannot read %s: %s" % (path, err.strerror or err))]
    if len(raw) > MAX_DOCX_BYTES:
        return {}, [Finding("docx-format", None,
                            "%s is larger than 8 MiB" % path)]
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except (zipfile.BadZipFile, OSError):
        return {}, [Finding("docx-format", None,
                            "%s is not a readable DOCX archive" % path)]
    with archive:
        infos = archive.infolist()
        if len(infos) > MAX_ZIP_ENTRIES:
            return {}, [Finding("docx-format", None,
                                "the archive has more than %d entries"
                                % MAX_ZIP_ENTRIES)]
        if sum(info.file_size for info in infos) > MAX_DOCX_BYTES:
            return {}, [Finding("docx-format", None,
                                "the archive is larger than 8 MiB uncompressed")]
        try:
            document = archive.read("word/document.xml")
        except KeyError:
            return {}, [Finding("docx-format", None,
                                "the archive has no word/document.xml")]
        except (zipfile.BadZipFile, OSError, RuntimeError):
            return {}, [Finding("docx-format", None,
                                "word/document.xml cannot be read")]
    try:
        root = ET.fromstring(document)
    except ET.ParseError as err:
        return {}, [Finding("docx-format", None,
                            "word/document.xml is not valid XML: %s" % err)]

    body = root.find(W + "body")
    if body is None:
        return {}, [Finding("docx-format", None,
                            "the DOCX has no document body")]
    tables = body.findall(W + "tbl")
    if not tables:
        return {}, [Finding("docx-format", None,
                            "the DOCX has no worksheet table")]

    data_tables, other_tables = [], []
    for table in tables:
        rows = _table_rows(table)
        if not rows:
            continue
        cells = _table_cells(rows[0])
        if cells and _cell_text(cells[0]).strip() == "ID":
            data_tables.append(table)
        elif any(_cell_text(cell).strip() for cell in cells):
            other_tables.append(table)
    if not data_tables:
        return {}, [Finding(
            "docx-format", None,
            "the DOCX has no ID column; the old Koto Payang sheet has to be "
            "mapped by hand")]
    if other_tables:
        return {}, [Finding(
            "docx-format", None,
            "the DOCX contains a second table with a different header")]

    answers = {}
    for table in data_tables:
        rows = _table_rows(table)
        header_cells = _table_cells(rows[0])
        headers = [_cell_text(cell).strip() for cell in header_cells]
        if len(set(headers)) != len(headers) \
                or set(headers) != set(DOCX_HEADERS) \
                or len(headers) != len(DOCX_HEADERS):
            findings.append(Finding(
                "docx-format", None,
                "the table header must contain exactly %s, found %s"
                % (", ".join(DOCX_HEADERS), ", ".join(headers) or "nothing")))
            continue
        index = {header: position for position, header in enumerate(headers)}
        for number, table_row in enumerate(rows[1:], 1):
            cells = _table_cells(table_row)
            texts = [_cell_text(cell) for cell in cells]
            id_index = index["ID"]
            ident = texts[id_index].strip() if id_index < len(texts) else ""
            if not ident and not any(value.strip() for value in texts):
                continue
            if len(cells) != len(headers):
                findings.append(Finding(
                    "docx-format", ident or None,
                    "the row has %d cells, the header has %d"
                    % (len(cells), len(headers)), row=number))
                continue
            if not ident:
                findings.append(Finding("docx-format", None,
                                        "the row has an empty ID", row=number))
                continue
            if ident in answers:
                findings.append(Finding("docx-format", ident,
                                        "the ID appears more than once",
                                        row=number))
                continue
            answers[ident] = {
                "answer": texts[index["Answer"]],
                "notes": texts[index["Notes"]],
            }
    return answers, findings


# ---- commands -------------------------------------------------------------
def _selection(options, key):
    if key in options["explicit"]:
        return pathlib.Path(options[key])
    return _default_paths(options["kode"])[key]


def cmd_buat(options):
    code = options["kode"]
    path = _selection(options, "csv")
    if path.exists() and not options["paksa"]:
        print("lembar_kerja: write: %s already exists; use --paksa or perbarui"
              % path)
        return 1
    docx_path = _selection(options, "docx") if "docx" in options["explicit"] else None
    if docx_path is not None and docx_path.exists() and not options["paksa"]:
        print("lembar_kerja: write: %s already exists; use --paksa" % docx_path)
        return 1
    rows = [_catalogue_row(ident) for ident in ORDERED_IDS]
    try:
        _write_csv(path, rows)
    except OSError as err:
        print("lembar_kerja: write: cannot write %s: %s" % (path, err))
        return 1
    print("wrote %s: %d rows" % (path, len(rows)))
    if docx_path is not None:
        return _write_docx(code, rows, docx_path, True)
    return 0


def cmd_perbarui(options):
    path = _selection(options, "csv")
    sheet = read_sheet(path)
    structural = [finding for finding in sheet.structural
                  if finding.code != "missing-id"]
    if structural:
        _print_findings(structural)
        return 1
    by_id = _rows_by_id(sheet.rows)
    rows = []
    for ident in ORDERED_IDS:
        row = by_id.get(ident)
        if row is None:
            rows.append(_catalogue_row(ident))
            continue
        refreshed = _catalogue_row(ident)
        refreshed["answer"] = row["answer"]
        refreshed["notes"] = row["notes"]
        refreshed["status"] = row["status"]
        rows.append(refreshed)
    try:
        _write_csv(path, rows)
    except OSError as err:
        print("lembar_kerja: write: cannot write %s: %s" % (path, err))
        return 1
    added = sum(1 for row in rows if row["id"] not in by_id)
    print("updated %s: %d rows, %d added" % (path, len(rows), added))
    return 0


def cmd_periksa(options):
    code = options["kode"]
    path = _selection(options, "csv")
    sheet = read_sheet(path)
    findings, _, _ = check_sheet(sheet, code)
    if options["siap"]:
        status, problem = _skeleton_status(_selection(options, "json"), code)
        if problem is not None:
            findings.append(problem)
        else:
            ready = _readiness_finding(sheet.rows, status, code)
            if ready is not None:
                findings.append(ready)
    _print_findings(findings)
    errors, warnings = _counts(findings)
    answered = sum(1 for row in sheet.rows if row["answer"].strip())
    reviewed = sum(1 for row in sheet.rows if row["status"] == "reviewed")
    print("checked %d rows: %d answered, %d reviewed, %d error%s, %d warning%s"
          % (len(sheet.rows), answered, reviewed, errors, "" if errors == 1 else "s",
             warnings, "" if warnings == 1 else "s"))
    if errors:
        return 1
    if options["tulis"] and not sheet.fatal:
        try:
            _write_csv(path, _normalized_rows(sheet.rows))
        except OSError as err:
            print("lembar_kerja: write: cannot write %s: %s" % (path, err))
            return 1
        print("wrote normalized answers to %s" % path)
    return 0


def _write_docx(code, rows, path, force):
    if path.exists() and not force:
        print("lembar_kerja: write: %s already exists; use --paksa" % path)
        return 1
    try:
        _atomic_write_bytes(path, docx_bytes(code, rows))
    except OSError as err:
        print("lembar_kerja: write: cannot write %s: %s" % (path, err))
        return 1
    print("wrote %s: %d rows" % (path, len(rows)))
    return 0


def cmd_docx(options):
    code = options["kode"]
    sheet = read_sheet(_selection(options, "csv"))
    structural = sheet.structural
    if structural:
        _print_findings(structural)
        return 1
    return _write_docx(code, _docx_rows(sheet), _selection(options, "docx"),
                       options["paksa"])


def cmd_baca(options):
    code = options["kode"]
    path = _selection(options, "csv")
    sheet = read_sheet(path)
    structural = sheet.structural
    if structural:
        _print_findings(structural)
        return 1
    answers, findings = read_docx(_selection(options, "docx"))
    if findings:
        _print_findings(findings)
        return 1

    by_id = _rows_by_id(sheet.rows)
    docx_ids = set(answers)
    csv_ids = set(by_id)
    if docx_ids - csv_ids:
        _print_findings([Finding("docx-format", ident,
                                 "the ID is not in the CSV")
                         for ident in sorted(docx_ids - csv_ids)])
        return 1
    if csv_ids - docx_ids:
        _print_findings([Finding("docx-format", ident,
                                 "the ID is missing from the DOCX")
                         for ident in sorted(csv_ids - docx_ids)])
        return 1

    rows, changes = [], []
    for row in sheet.rows:
        update = answers[row["id"]]
        new_answer = update["answer"]
        new_notes = update["notes"]
        copy = dict(row)
        if new_answer != row["answer"]:
            copy["answer"] = new_answer
            copy["status"] = "todo" if not new_answer else "draft"
            changes.append("row %d: %s: answer %r -> %r (%s)"
                           % (row["_row"], row["id"], row["answer"], new_answer,
                              copy["status"]))
        elif new_notes != row["notes"]:
            changes.append("row %d: %s: note changed (%s)"
                           % (row["_row"], row["id"], row["status"]))
        copy["notes"] = new_notes
        rows.append(copy)

    for change in changes:
        print(change)
    if not changes:
        print("no changes")
    if options["tulis"]:
        try:
            _write_csv(path, rows)
        except OSError as err:
            print("lembar_kerja: write: cannot write %s: %s" % (path, err))
            return 1
        print("wrote %s" % path)
    return 0


def cmd_laporan(options):
    code = options["kode"]
    path = _selection(options, "csv")
    sheet = read_sheet(path)
    findings, _, _ = check_sheet(sheet, code)
    _print_findings(findings)
    errors, warnings = _counts(findings)
    totals, answered, reviewed, missing_tier1, _ = _stats(sheet.rows)
    print("%s: %d ids" % (code, len(ORDERED_IDS)))
    for tier in (1, 2, 3):
        print("tier %d: %d/%d answered, %d reviewed"
              % (tier, answered[tier], totals[tier], reviewed[tier]))
    print("missing tier 1: %s"
          % (", ".join(missing_tier1) if missing_tier1 else "none"))
    print("errors: %d, warnings: %d" % (errors, warnings))
    ready_review, why_review = _readiness(sheet.rows, "review")
    print("ready for review: %s"
          % ("yes" if ready_review else "no (%s)" % why_review))
    ready_approved, why_approved = _readiness(sheet.rows, "approved")
    print("ready for approved: %s"
          % ("yes" if ready_approved else "no (%s)" % why_approved))
    return 1 if sheet.fatal else 0


def _skeleton_status(path, code):
    path = pathlib.Path(path)
    if not path.is_file():
        return None, Finding("skeleton-missing", code,
                             "the skeleton %s does not exist" % path)
    try:
        raw = path.read_bytes()
    except OSError as err:
        return None, Finding("skeleton-missing", code,
                             "cannot read %s: %s" % (path, err))
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        return None, Finding("status", code,
                             "the skeleton is not readable JSON: %s" % err)
    if not isinstance(data, dict):
        return None, Finding("status", code,
                             "the skeleton must contain a JSON object")
    if data.get("code") != code:
        return None, Finding("status", code,
                             "the skeleton code is %r, expected %r"
                             % (data.get("code"), code))
    status = data.get("status")
    if status not in loader.STATUSES:
        return None, Finding("status", code,
                             "the skeleton status %r is not one of %s"
                             % (status, ", ".join(loader.STATUSES)))
    return status, None


def cmd_json(options):
    code = options["kode"]
    sheet = read_sheet(_selection(options, "csv"))
    findings, words, messages = check_sheet(sheet, code)
    if any(finding.blocking for finding in findings):
        _print_findings(findings)
        print("nothing written")
        return 1

    path = _selection(options, "json")
    if not path.is_file():
        _print_findings([Finding("skeleton-missing", code,
                                 "the skeleton %s does not exist" % path)])
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as err:
        _print_findings([Finding("status", code,
                                 "the skeleton cannot be read: %s" % err)])
        return 1
    if not isinstance(data, dict) or data.get("code") != code:
        _print_findings([Finding("status", code,
                                 "the skeleton must be a JSON object whose code is %r"
                                 % code)])
        return 1

    before = loader.validate_dialect(data, filename=code, root=path.parent)
    if before:
        _print_findings([Finding("status", code,
                                 "the skeleton does not load: %s" % problem)
                         for problem in before])
        return 1

    selected = [row for row in sheet.rows if row["status"] in ACCEPTED]
    merged = dict(data)
    merged["words"] = {row["id"]: words[row["id"]] for row in selected
                       if row["namespace"] != "msg"}
    merged["messages"] = {row["id"]: messages[row["id"]] for row in selected
                          if row["namespace"] == "msg"}

    problems = loader.validate_dialect(merged, filename=code, root=path.parent)
    if problems:
        _print_findings([Finding("status", code, "the merged file does not load: %s"
                                 % problem) for problem in problems])
        print("nothing written")
        return 1

    ready = _readiness_finding(sheet.rows, data.get("status"), code)
    if ready is not None:
        _print_findings([ready])
        print("nothing written")
        return 1

    text = json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    try:
        _atomic_write_text(path, text)
    except OSError as err:
        print("lembar_kerja: write: cannot write %s: %s" % (path, err))
        return 1
    print("wrote %s: %d words, %d messages"
          % (path, len(merged["words"]), len(merged["messages"])))
    return 0


DISPATCH = {
    "buat": cmd_buat,
    "perbarui": cmd_perbarui,
    "periksa": cmd_periksa,
    "docx": cmd_docx,
    "baca": cmd_baca,
    "laporan": cmd_laporan,
    "json": cmd_json,
}


# ---- command line ---------------------------------------------------------
class UsageError(Exception):
    pass


def _parse(argv):
    if not argv:
        raise UsageError("a command is required")
    if argv[0] in ("-h", "--help"):
        return {"help": True}
    command = argv[0]
    if command not in DISPATCH:
        raise UsageError("unknown command %r" % command)
    options = {
        "command": command,
        "kode": None,
        "csv": None,
        "docx": None,
        "json": None,
        "paksa": False,
        "tulis": False,
        "siap": False,
        "explicit": set(),
    }
    value_flags = {"--kode": "kode", "--csv": "csv", "--docx": "docx",
                   "--json": "json"}
    bool_flags = {"--paksa": "paksa", "--tulis": "tulis", "--siap": "siap"}
    index = 1
    while index < len(argv):
        argument = argv[index]
        if argument in ("-h", "--help"):
            return {"help": True}
        if argument in value_flags:
            index += 1
            if index >= len(argv):
                raise UsageError("%s needs a value" % argument)
            options[value_flags[argument]] = argv[index]
            options["explicit"].add(value_flags[argument])
        elif argument.startswith("--") and "=" in argument:
            flag, value = argument.split("=", 1)
            if flag in value_flags and value:
                options[value_flags[flag]] = value
                options["explicit"].add(value_flags[flag])
            else:
                raise UsageError("unknown argument %r" % argument)
        elif argument in bool_flags:
            options[bool_flags[argument]] = True
        else:
            raise UsageError("unknown argument %r" % argument)
        index += 1
    if not options["kode"]:
        raise UsageError("--kode is required")
    if not CODE_RE.match(options["kode"]):
        raise UsageError("--kode must match ^[a-z0-9-]+$")
    return options


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        options = _parse(argv)
    except UsageError as err:
        print("lembar_kerja: %s\n\n%s" % (err, HELP), file=sys.stderr)
        return 2
    if options.get("help"):
        print(HELP)
        return 0
    return DISPATCH[options["command"]](options)


if __name__ == "__main__":
    sys.exit(main())
