#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from archive_meta import GENERATED, ROOT, SOURCES_DIR, current_notes_from_index, current_revision, generated_at_utc

CURRENT_REV = current_revision()
CATALOG = SOURCES_DIR / "source_catalog.json"
SOURCE_KEYS = SOURCES_DIR / "source_keys.json"



def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalize_group(group: dict) -> dict:
    title = " ".join(str(group.get("title", "")).split())
    publisher = " ".join(str(group.get("publisher", "")).split())
    url = str(group.get("url", "")).strip()
    if url:
        parts = urlsplit(url)
        filtered_query = []
        for key, value in parse_qsl(parts.query, keep_blank_values=True):
            low = key.lower()
            if low.startswith("utm_") or low in {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src"}:
                continue
            filtered_query.append((key, value))
        query = urlencode(filtered_query, doseq=True)
        url = urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))
        if url.endswith("/"):
            url = url.rstrip("/")
    out = {"title": title, "publisher": publisher, "url": url}
    source_key = str(group.get("source_key", "")).strip()
    if source_key:
        out["source_key"] = source_key
    return out


def dedupe_groups(notes: dict[str, dict]) -> dict[str, dict]:
    cleaned: dict[str, dict] = {}
    for note, payload in sorted(notes.items()):
        seen = set()
        groups = []
        for raw_group in payload.get("groups", []):
            group = normalize_group(raw_group)
            key = (group.get("title"), group.get("publisher"), group.get("url"))
            if key in seen:
                continue
            seen.add(key)
            groups.append(group)
        cleaned[note] = {"groups": groups}
    return cleaned


def note_title(note_file: str) -> str:
    path = ROOT / note_file
    if not path.exists():
        return Path(note_file).name
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return Path(note_file).name


def render_markdown(notes: dict[str, dict]) -> str:
    current_notes = current_notes_from_index()
    lines: list[str] = [
        "# Sources",
        "",
        f"Generated from `sources/source_catalog.json` for `{CURRENT_REV}`.",
        "",
        f"## Sources used for {CURRENT_REV}",
        "",
        "Current notes:",
        "",
    ]
    for note in current_notes:
        lines.append(f"- `{Path(note).name}`")
    lines.extend([
        "",
        "These source entries are compact grounding anchors. The archive cites them rather than importing reports, storing PDFs, or quoting sources at length.",
        "",
    ])
    for note in current_notes:
        payload = notes.get(note, {"groups": []})
        lines.append(f"### {note_title(note)}")
        lines.append("")
        if not payload.get("groups"):
            lines.append("- No source groups declared.")
        for group in payload.get("groups", []):
            title = group.get("title", "Untitled")
            publisher = group.get("publisher", "Unknown publisher")
            url = group.get("url", "")
            source_key = group.get("source_key")
            prefix = f"`{source_key}` — " if source_key else ""
            if url:
                lines.append(f"- {prefix}{publisher}. *{title}*. {url}")
            else:
                lines.append(f"- {prefix}{publisher}. *{title}*.")
        lines.append("")

    source_key_count = len({
        group.get("source_key")
        for payload in notes.values()
        for group in payload.get("groups", [])
        if group.get("source_key")
    })
    lines.extend([
        "---",
        "",
        "## Historical catalog location",
        "",
        "The complete historical source catalog is intentionally omitted from this Markdown reader surface.",
        "Use `sources/source_catalog.json` for the complete editable historical note-to-source map. `generated/SOURCES.json` is intentionally limited to the current revision route, source-key registry snapshot, counts, and catalog hashes.",
        "",
        f"Historical notes with source rows: `{len(notes)}`.",
        f"Distinct source keys in source rows: `{source_key_count}`.",
        "",
        "This keeps the current revision's human source route visible without forcing every reader to reopen the full historical catalog on each turn.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    source_keys = json.loads(SOURCE_KEYS.read_text(encoding="utf-8")) if SOURCE_KEYS.exists() else {"keys": {}}
    notes = dedupe_groups(catalog.get("notes", {}))
    current_notes = current_notes_from_index()
    current_note_map = {note: notes.get(note, {"groups": []}) for note in current_notes}
    distinct_catalog_source_keys = sorted({
        group.get("source_key")
        for payload in notes.values()
        for group in payload.get("groups", [])
        if group.get("source_key")
    })
    registry = source_keys.get("keys", {})
    data = {
        "revision": CURRENT_REV,
        "generated_at_utc": generated_at_utc(),
        "source_catalog": str(CATALOG.relative_to(ROOT)),
        "source_key_registry": str(SOURCE_KEYS.relative_to(ROOT)) if SOURCE_KEYS.exists() else None,
        "source_scope": "current_revision_route_and_registry_snapshot",
        "historical_catalog_policy": "Complete historical note-to-source rows remain canonical in sources/source_catalog.json; generated/SOURCES.json carries the current revision route and source-key registry snapshot only.",
        "catalog_sha256": sha256_file(CATALOG),
        "source_key_registry_sha256": sha256_file(SOURCE_KEYS) if SOURCE_KEYS.exists() else None,
        "counts": {
            "historical_notes_with_source_rows": len(notes),
            "current_revision_notes": len(current_notes),
            "source_key_registry_keys": len(registry),
            "distinct_source_keys_in_catalog": len(distinct_catalog_source_keys),
        },
        "source_keys": registry,
        "current_notes": current_notes,
        "notes": current_note_map,
    }
    # Keep this generated surface as a route and registry snapshot, not a second
    # full historical catalog. The complete note-to-source history remains in
    # sources/source_catalog.json, which is hashed above for drift detection.
    (GENERATED / "SOURCES.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    (GENERATED / "SOURCES.md").write_text(render_markdown(notes), encoding="utf-8")
    print("OK: wrote generated/SOURCES.json and generated/SOURCES.md")


if __name__ == "__main__":
    main()
