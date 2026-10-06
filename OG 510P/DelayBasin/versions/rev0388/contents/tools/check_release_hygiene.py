import pathlib
import sys

from release_hygiene_lib import iter_release_paths

ROOT = pathlib.Path(__file__).resolve().parents[1]
MAX_BYTES = 1_000_000
FORBIDDEN_SUFFIXES = {
    ".pdf", ".ppt", ".pptx", ".doc", ".docx", ".xls", ".xlsx",
    ".odt", ".ods", ".odp", ".ipynb", ".sqlite", ".db", ".tar", ".gz", ".bz2", ".7z", ".rar"
}
TEXTISH_SUFFIXES = {
    ".md", ".txt", ".json", ".py", ".toml", ".yaml", ".yml", ".csv", ".ts", ".js", ".html", ".css", ".sh", ".c", ".cc", ".cpp", ".h", ".hpp", ".rs", ".nix"
}

problems = []

for path in iter_release_paths(ROOT):
    rel = path.relative_to(ROOT)
    suffix = path.suffix.lower()
    size = path.stat().st_size
    if suffix in FORBIDDEN_SUFFIXES:
        problems.append(f"forbidden artifact in repo: {rel}")
        continue
    if size > MAX_BYTES and suffix not in TEXTISH_SUFFIXES:
        problems.append(f"large non-text artifact in repo ({size} bytes): {rel}")

if problems:
    for p in problems:
        print(p)
    sys.exit(1)

print('check_release_hygiene: OK')
