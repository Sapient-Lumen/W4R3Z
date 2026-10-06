import json
import pathlib
import re
import sys
import urllib.parse

from validation_toolchain_lib import build_validation_toolchain

ROOT = pathlib.Path(__file__).resolve().parents[1]

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
LOCAL_REF_RE = re.compile(
    r"^(?P<base>(?:docs|tools)/[^#\s]+|[A-Z][A-Z0-9-]+\.json|[a-z0-9_.-]+\.json|Makefile|README\.md|START_HERE\.md|AGENTS\.md|CHANGELOG\.md|ARCHIVE_INDEX\.md)(?:#.+)?$"
)
CRITICAL_JSON = [
    "REVISION-RECEIPT.json",
    "SURFACE-STATUS.json",
    "RELEASE-MANIFEST.json",
    "context-pack.json",
    "innovation-packet.json",
    "frontier-ticket.json",
    "replay-capsule.json",
    "compact-surface-bundle.json",
    "VALIDATION-INDEX.json",
    "REENTRY-CONTRACT.json",
    "REENTRY-SURFACE-CONFORMANCE.json",
]


def normalize_markdown_target(raw: str) -> str:
    target = raw.strip().split()[0].strip('<>')
    target = urllib.parse.unquote(target)
    return target.split('#', 1)[0]


def check_markdown_links() -> list[str]:
    problems: list[str] = []
    for path in ROOT.rglob("*.md"):
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding="utf-8")
        for raw in MARKDOWN_LINK_RE.findall(text):
            target = normalize_markdown_target(raw)
            if not target or target.startswith(("http://", "https://", "mailto:", "/")):
                continue
            dest = (path.parent / target).resolve()
            try:
                rel_dest = dest.relative_to(ROOT.resolve())
            except ValueError:
                continue
            if not dest.exists():
                problems.append(f"{path.relative_to(ROOT)} links to missing local surface: {target} -> {rel_dest}")
    return problems


def walk_strings(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)
    elif isinstance(value, str):
        yield value


def check_critical_json_refs() -> list[str]:
    problems: list[str] = []
    for rel in CRITICAL_JSON:
        path = ROOT / rel
        if not path.exists():
            problems.append(f"missing critical JSON surface: {rel}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for value in walk_strings(data):
            if value.startswith("DelayBasin-rev") and value.endswith(".zip"):
                continue
            match = LOCAL_REF_RE.fullmatch(value)
            if not match:
                continue
            base = match.group("base")
            if not (ROOT / base).exists():
                problems.append(f"{rel} references missing archive surface: {value}")
    return problems


def check_validation_toolchain_refs() -> list[str]:
    problems: list[str] = []
    for tool in build_validation_toolchain(ROOT):
        if not (ROOT / "tools" / tool).exists():
            problems.append(f"validation toolchain references missing tool: tools/{tool}")
    return problems


problems = []
problems.extend(check_markdown_links())
problems.extend(check_critical_json_refs())
problems.extend(check_validation_toolchain_refs())

if problems:
    for problem in problems:
        print(problem)
    sys.exit(1)

print("check_internal_surface_references: OK")
