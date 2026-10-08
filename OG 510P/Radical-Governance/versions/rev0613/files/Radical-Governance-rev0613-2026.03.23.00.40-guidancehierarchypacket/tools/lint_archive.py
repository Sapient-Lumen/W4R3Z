#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive"

REQUIRED_TOP_LEVEL = ["README.md", "CHANGELOG.md", "INDEX.md", "THREADS.md", "THREAD_SUMMARY.json", "RELEASES.json", "MANIFEST.json", "SOURCES.md", "SOURCES.json", "ARCHIVE_INDEX.json", "CONTROL_SURFACES.json", "ASSURANCE_ARTIFACTS.json", "LIFECYCLE_GATES.json"]
REQUIRED_EXACT = [
    "## Pattern pack",
]
REQUIRED_ANY_OF = [
    ["## One-line thesis"],
    ["## Why this matters", "## Core claim", "## The problem"],
    ["## Failure modes", "## Anti-theater tests"],
]
from archive_meta import current_notes_from_index, current_revision

CURRENT_REV = current_revision()
CURRENT_NOTES = current_notes_from_index()




def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    for name in REQUIRED_TOP_LEVEL:
        if not (ROOT / name).exists():
            fail(f"missing required file: {name}")

    files = sorted(ARCHIVE.glob("[0-9][0-9][0-9]-*.md"))
    if not files:
        fail("no numbered archive files found")

    numbers = []
    for path in files:
        m = re.match(r"^(\d{3})-(.+)\.md$", path.name)
        if not m:
            fail(f"bad numbered filename: {path.name}")
        num = int(m.group(1))
        numbers.append(num)
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        heading = lines[0].strip() if lines else ""
        expected_heading_prefix = f"# {m.group(1)} — "
        if not heading.startswith(expected_heading_prefix):
            fail(f"heading mismatch in {path.name}: expected prefix '{expected_heading_prefix}'")
        for fragment in REQUIRED_EXACT:
            if fragment not in text:
                fail(f"missing section '{fragment}' in {path.name}")
        for group in REQUIRED_ANY_OF:
            if not any(fragment in text for fragment in group):
                fail(f"missing one of {group} in {path.name}")
        if re.search(r"(?i)https?://\S+\.pdf(?:\?\S*)?", text):
            fail(f"raw PDF link found in archive note: {path.name}")
        quote_lines = [line for line in lines if line.lstrip().startswith(">")]
        if len(quote_lines) > 8:
            fail(f"too many quoted lines in archive note: {path.name}")

    if len(numbers) != len(set(numbers)):
        fail("duplicate archive numbers detected")

    if numbers != sorted(numbers):
        fail("archive numbering is not sorted")

    titles = []
    theses = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        title = lines[0].strip() if lines else ""
        titles.append((path.name, title))
        capture = False
        thesis = ""
        for line in lines:
            if line.strip() == "## One-line thesis":
                capture = True
                continue
            if capture and line.startswith("## "):
                break
            if capture and line.strip():
                thesis = line.strip()
                break
        theses.append((path.name, thesis))

    title_map = {}
    for fname, title in titles:
        title_map.setdefault(title, []).append(fname)
    dup_titles = {title: names for title, names in title_map.items() if len(names) > 1}
    if dup_titles:
        fail(f"duplicate archive titles detected: {dup_titles}")

    thesis_map = {}
    for fname, thesis in theses:
        if thesis:
            thesis_map.setdefault(thesis, []).append(fname)
    dup_theses = {thesis: names for thesis, names in thesis_map.items() if len(names) > 1}
    if dup_theses:
        fail(f"duplicate one-line theses detected: {dup_theses}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    index = (ROOT / "INDEX.md").read_text(encoding="utf-8")
    sources = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
    if CURRENT_REV not in readme:
        fail(f"README does not mention current revision {CURRENT_REV}")
    if CURRENT_REV not in changelog:
        fail(f"CHANGELOG does not mention current revision {CURRENT_REV}")
    latest_num = max(numbers)
    latest_prefix = f"{latest_num:03d}-"
    if latest_prefix not in index:
        fail(f"INDEX does not include latest archive addition {latest_prefix}")
    if f"Sources used for {CURRENT_REV}" not in sources:
        fail("SOURCES.md does not mention the current revision")
    for required in CURRENT_NOTES:
        basename = Path(required).name
        if basename not in readme:
            fail(f"README does not list current note {basename}")
        if basename not in index:
            fail(f"INDEX does not list current note {basename}")
        if basename not in sources:
            fail(f"SOURCES.md does not list current note {basename}")

    for top in ["README.md", "CHANGELOG.md", "INDEX.md", "THREADS.md", "SOURCES.md"]:
        text = (ROOT / top).read_text(encoding="utf-8")
        h1s = re.findall(r"(?m)^# ", text)
        if len(h1s) != 1:
            fail(f"{top} should contain exactly one H1 heading")

    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("revision") != CURRENT_REV:
        fail(f"MANIFEST.json revision mismatch: expected {CURRENT_REV}")

    manifest_files = [entry["file"].split("/", 1)[-1] for entry in manifest.get("archive_notes", [])]
    if sorted(manifest_files) != [p.name for p in files]:
        fail("MANIFEST.json archive note list does not match archive directory")

    def check_entries(entries: list[dict], label: str) -> None:
        for entry in entries:
            if not isinstance(entry.get("bytes"), int) or entry["bytes"] < 0:
                fail(f"{label} entry missing valid bytes field: {entry}")
            sha = entry.get("sha256", "")
            if not re.fullmatch(r"[0-9a-f]{64}", sha):
                fail(f"{label} entry missing valid sha256: {entry}")

    check_entries(manifest.get("top_level_files", []), "top_level_files")
    check_entries(manifest.get("archive_notes", []), "archive_notes")
    check_entries(manifest.get("meta_notes", []), "meta_notes")
    check_entries(manifest.get("tool_scripts", []), "tool_scripts")

    source_index = json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))
    if source_index.get("revision") != CURRENT_REV:
        fail(f"SOURCES.json revision mismatch: expected {CURRENT_REV}")
    note_sources = source_index.get("notes", {})
    for required in CURRENT_NOTES:
        if required not in note_sources:
            fail(f"SOURCES.json missing current note entry: {required}")
        if not note_sources[required].get("groups"):
            fail(f"SOURCES.json note entry has no source groups: {required}")
        urls = set()
        for group in note_sources[required].get("groups", []):
            if not isinstance(group.get("title"), str) or not group["title"].strip():
                fail(f"SOURCES.json source group missing title: {required}")
            if not isinstance(group.get("publisher"), str) or not group["publisher"].strip():
                fail(f"SOURCES.json source group missing publisher: {required}")
            url = group.get("url", "")
            if not isinstance(url, str) or not url.startswith("http"):
                fail(f"SOURCES.json source group missing valid url: {required}")
            norm = url.rstrip("/")
            if norm in urls:
                fail(f"SOURCES.json current note has duplicate source url: {required}")
            urls.add(norm)

    archive_index = json.loads((ROOT / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
    if archive_index.get("revision") != CURRENT_REV:
        fail(f"ARCHIVE_INDEX.json revision mismatch: expected {CURRENT_REV}")
    indexed_files = [entry.get("file") for entry in archive_index.get("notes", [])]
    expected_files = [str(p.relative_to(ROOT)) for p in files]
    if indexed_files != expected_files:
        fail("ARCHIVE_INDEX.json note list does not match archive directory order")
    for required in CURRENT_NOTES:
        matched = [entry for entry in archive_index.get("notes", []) if entry.get("file") == required]
        if not matched:
            fail(f"ARCHIVE_INDEX.json missing current note entry: {required}")
        thesis = matched[0].get("thesis", "")
        if not isinstance(thesis, str) or not thesis.strip():
            fail(f"ARCHIVE_INDEX.json note entry missing thesis: {required}")
        tags = matched[0].get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(tag, str) and tag for tag in tags):
            fail(f"ARCHIVE_INDEX.json note entry missing valid tags: {required}")
        if not tags:
            fail(f"ARCHIVE_INDEX.json note entry has empty tag list: {required}")

    threads = (ROOT / "THREADS.md").read_text(encoding="utf-8")
    if "448-governance-state-honesty-request-review-approval-and-live-separation.md" not in threads or "450-contemporaneous-decision-witnesses-what-was-shown-and-dispute-reconstruction.md" not in threads:
        fail("THREADS.md does not include rev0418 additions")
    for required in CURRENT_NOTES:
        basename = Path(required).name
        if basename not in threads:
            fail(f"THREADS.md does not list current note {basename}")

    thread_summary = json.loads((ROOT / "THREAD_SUMMARY.json").read_text(encoding="utf-8"))
    if thread_summary.get("revision") != CURRENT_REV:
        fail(f"THREAD_SUMMARY.json revision mismatch: expected {CURRENT_REV}")
    for tag in ["operations", "monitoring", "data-governance", "regulatory-governance", "administrative-procedure-governance", "official-notice-governance", "base-registry-governance", "service-delivery-governance", "open-data-governance", "public-enterprise-governance", "budget-governance", "procurement-governance", "audit-governance", "legislature-governance", "civil-service-governance", "judiciary-governance", "prosecution-governance", "election-governance", "ombuds-governance", "human-rights-governance", "policing-governance", "corrections-governance", "public-defense-governance", "information-rights-governance", "statistics-governance", "districting-governance", "civil-registration-governance", "entity-registry-governance", "anti-corruption-governance", "land-administration-governance", "administrative-geography-governance", "public-records-governance", "quality-infrastructure-governance", "trust-services-governance"]:
        if tag not in thread_summary.get("tags", {}):
            fail(f"THREAD_SUMMARY.json missing expected tag: {tag}")
    for required in CURRENT_NOTES:
        note_entry = next((entry for entry in archive_index.get("notes", []) if entry.get("file") == required), None)
        if not note_entry:
            fail(f"ARCHIVE_INDEX.json missing current note entry for thread summary check: {required}")
        tags = note_entry.get("tags", [])
        if not any(thread_summary.get("tags", {}).get(tag, {}).get("latest_file") == required for tag in tags):
            fail(f"THREAD_SUMMARY.json does not expose current note as latest_file for any of its tags: {required}")

    control_surfaces = json.loads((ROOT / "CONTROL_SURFACES.json").read_text(encoding="utf-8"))
    if control_surfaces.get("revision") != CURRENT_REV:
        fail(f"CONTROL_SURFACES.json revision mismatch: expected {CURRENT_REV}")
    for surface in ["boundary-setting", "predeployment-evidence", "live-operations", "user-interaction", "evidence-and-redress", "supplier-and-ecosystem"]:
        if surface not in control_surfaces.get("surfaces", {}):
            fail(f"CONTROL_SURFACES.json missing expected surface: {surface}")

    assurance = json.loads((ROOT / "ASSURANCE_ARTIFACTS.json").read_text(encoding="utf-8"))
    if assurance.get("revision") != CURRENT_REV:
        fail(f"ASSURANCE_ARTIFACTS.json revision mismatch: expected {CURRENT_REV}")
    for artifact in ["register", "notice", "log", "schedule", "waiver"]:
        if artifact not in assurance.get("artifacts", {}):
            fail(f"ASSURANCE_ARTIFACTS.json missing expected artifact bucket: {artifact}")

    lifecycle = json.loads((ROOT / "LIFECYCLE_GATES.json").read_text(encoding="utf-8"))
    if lifecycle.get("revision") != CURRENT_REV:
        fail(f"LIFECYCLE_GATES.json revision mismatch: expected {CURRENT_REV}")
    for gate in ["scoping-and-authority", "prelaunch-and-approval", "live-operation", "change-and-release", "redress-and-review", "retirement-and-continuity"]:
        if gate not in lifecycle.get("gates", {}):
            fail(f"LIFECYCLE_GATES.json missing expected gate: {gate}")

    releases = json.loads((ROOT / "RELEASES.json").read_text(encoding="utf-8"))
    if releases.get("revision") != CURRENT_REV:
        fail(f"RELEASES.json revision mismatch: expected {CURRENT_REV}")
    rev_entry = None
    for item in releases.get("releases", []):
        if item.get("revision") == CURRENT_REV:
            rev_entry = item
            break
    if not rev_entry:
        fail("RELEASES.json missing current revision entry")
    if sorted(rev_entry.get("notes", [])) != sorted(CURRENT_NOTES):
        fail("RELEASES.json current revision note list mismatch")

    print("OK: archive lint passed")
    print(f"Checked {len(files)} numbered archive files in {ARCHIVE}")


if __name__ == "__main__":
    main()
