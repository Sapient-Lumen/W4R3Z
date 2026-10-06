import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
archive_index = (ROOT / "ARCHIVE_INDEX.md").read_text(encoding="utf-8")

m = re.search(r"\[?(rev\d{4})\]?", changelog)
if not m:
    print("CHANGELOG.md missing rev header")
    sys.exit(1)
rev = m.group(1)
if rev not in archive_index:
    print(f"ARCHIVE_INDEX.md missing {rev}")
    sys.exit(1)

print("check_revision_sync: OK")
