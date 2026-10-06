import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
path = ROOT / "ARCHIVE_INDEX.md"
lines = path.read_text(encoding="utf-8").splitlines()

if len(lines) < 5 or lines[0] != "# Archive index" or lines[1] != "":
    raise SystemExit("ARCHIVE_INDEX.md must begin with title, blank line, header, separator, then bundle rows")
if lines[2].strip() != "| Bundle | Date | Notes |":
    raise SystemExit("ARCHIVE_INDEX.md table header must be the first table line")
if lines[3].strip() != "| --- | --- | --- |":
    raise SystemExit("ARCHIVE_INDEX.md table separator must immediately follow the header")

headers = [i for i, line in enumerate(lines) if line.strip() == "| Bundle | Date | Notes |"]
separators = [i for i, line in enumerate(lines) if line.strip() == "| --- | --- | --- |"]
if headers != [2] or separators != [3]:
    raise SystemExit("ARCHIVE_INDEX.md must contain exactly one table header and one separator")

rows = [line for line in lines[4:] if line.strip()]
if not rows:
    raise SystemExit("ARCHIVE_INDEX.md has no bundle rows")
for row in rows:
    if not row.startswith("| DelayBasin-rev"):
        raise SystemExit(f"ARCHIVE_INDEX.md non-bundle row inside table: {row}")
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
    if len(cells) != 3:
        raise SystemExit(f"ARCHIVE_INDEX.md row must have three cells: {row}")

bundle = manifest.get("bundle")
if f"| {bundle} |" not in rows[0]:
    raise SystemExit("ARCHIVE_INDEX.md first data row must match RELEASE-MANIFEST bundle")
if receipt.get("revision") != manifest.get("revision"):
    raise SystemExit("receipt and manifest revisions must match for archive index shape check")
if receipt.get("resolved_question") not in rows[0] or receipt.get("next_open_question") not in rows[0]:
    raise SystemExit("ARCHIVE_INDEX.md first row must name current resolved and successor questions")

revs = []
for row in rows:
    m = re.search(r"DelayBasin-rev(\d{4})-", row)
    if not m:
        raise SystemExit(f"ARCHIVE_INDEX.md row missing revision bundle pattern: {row}")
    revs.append(int(m.group(1)))
if len(revs) != len(set(revs)):
    raise SystemExit("ARCHIVE_INDEX.md contains duplicate revision rows")
if any(a <= b for a, b in zip(revs, revs[1:])):
    raise SystemExit("ARCHIVE_INDEX.md rows must be strictly descending by revision")

print("check_archive_index_table_shape: OK")
