#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from archive_meta import ROOT, archive_note_paths, current_revision, note_catalog, source_data, thesis_for, summary_for, first_section_text

REQUIRED_TOP = [
    "README.md",
    "CHANGELOG.md",
    "INDEX.md",
    "THREADS.md",
    "THREAD_SUMMARY.json",
    "SOURCES.md",
    "SOURCES.json",
    "ARCHIVE_INDEX.json",
    "CONTROL_SURFACES.json",
    "MANIFEST.json",
    "RELEASES.json",
    "VERSION",
    "Makefile",
]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

REQUIRED_SECTIONS = [
    "## One-line thesis",
    "## Why this matters",
    "## Pattern pack",
    "## Guardrails",
    "## Failure modes",
    "## Practical tests",
    "## Closing synthesis",
]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)

for name in REQUIRED_TOP:
    if not (ROOT / name).exists():
        fail(f"Missing required file: {name}")

catalog = note_catalog()
sources = source_data()["notes"]
seen = []
seen_theses = {}
for path in archive_note_paths():
    rel = str(path.relative_to(ROOT))
    seen.append(rel)
    text = path.read_text(encoding="utf-8")
    if rel not in catalog:
        fail(f"Missing catalog entry for {rel}")
    if rel not in sources:
        fail(f"Missing source entry for {rel}")
    cfg = catalog[rel]
    if cfg.get('status') != 'canon':
        fail(f"Unexpected status for {rel}: {cfg.get('status')!r}")
    thread = cfg.get('thread')
    if not isinstance(thread, str) or not SLUG_RE.match(thread):
        fail(f"Malformed thread slug for {rel}: {thread!r}")
    tags = cfg.get('tags')
    if not isinstance(tags, list) or not tags:
        fail(f"Missing tags for {rel}")
    if len(tags) != len(set(tags)):
        fail(f"Duplicate tags for {rel}")
    for tag in tags:
        if not isinstance(tag, str) or not SLUG_RE.match(tag):
            fail(f"Malformed tag slug for {rel}: {tag!r}")
    if not re.match(r"^# \d{3} — .+", text.splitlines()[0]):
        fail(f"Bad H1 format in {rel}")
    file_num = Path(rel).name.split('-', 1)[0]
    h1_num = text.splitlines()[0].split(' ', 2)[1]
    if h1_num != file_num:
        fail(f"H1 number/filename number mismatch in {rel}: H1={h1_num}, file={file_num}")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f"Missing section {section!r} in {rel}")
    practical_section = first_section_text(path, "Practical tests")
    practical_count = len(re.findall(r"^\d+\. ", practical_section, flags=re.M))
    if practical_count != 5:
        fail(f"Practical tests must contain exactly 5 numbered items in {rel}")
    thesis = thesis_for(path)
    if not thesis:
        fail(f"Empty thesis in {rel}")
    norm_thesis = thesis.casefold()
    other = seen_theses.get(norm_thesis)
    if other is not None:
        fail(f"Duplicate one-line thesis in {rel} and {other}")
    seen_theses[norm_thesis] = rel
    if len([ln for ln in text.splitlines() if ln.lstrip().startswith(">")]) > 6:
        fail(f"Too many quote lines in {rel}")
    if re.search(r"https?://\S+\.pdf(?:\?\S*)?", text, re.I):
        fail(f"Raw PDF link in note {rel}")

if len(seen) != len(set(seen)):
    fail("Duplicate archive files detected")

if sorted(catalog) != sorted(seen):
    extra = sorted(set(catalog) - set(seen))
    missing = sorted(set(seen) - set(catalog))
    fail(f"Catalog/archive mismatch; extra={extra}, missing={missing}")

if sorted(sources) != sorted(seen):
    extra = sorted(set(sources) - set(seen))
    missing = sorted(set(seen) - set(sources))
    fail(f"Source/archive mismatch; extra={extra}, missing={missing}")

if list(catalog.keys()) != seen:
    fail("tools/note_catalog.json key order must match canonical archive order")

if list(sources.keys()) != seen:
    fail("tools/source_data.json note key order must match canonical archive order")

nums = [int(Path(rel).name.split('-', 1)[0]) for rel in seen]
expected = list(range(nums[0], nums[0] + len(nums)))
if nums != expected:
    fail(f"Archive note numbering gap or disorder: got {nums}, expected {expected}")

archive_index = json.loads((ROOT / "ARCHIVE_INDEX.json").read_text(encoding="utf-8"))
if archive_index.get("revision") != current_revision():
    fail("ARCHIVE_INDEX.json revision mismatch")
indexed = [entry["file"] for entry in archive_index["notes"]]
if indexed != seen:
    fail("ARCHIVE_INDEX.json note order mismatch")

for entry, rel in zip(archive_index["notes"], seen):
    path = ROOT / rel
    cfg = catalog[rel]
    if entry.get("title") != path.read_text(encoding="utf-8").splitlines()[0].split("—", 1)[1].strip():
        fail(f"ARCHIVE_INDEX.json title mismatch for {rel}")
    if entry.get("thesis") != thesis_for(path):
        fail(f"ARCHIVE_INDEX.json thesis mismatch for {rel}")
    if entry.get("summary") != summary_for(path):
        fail(f"ARCHIVE_INDEX.json summary mismatch for {rel}")
    if entry.get("tags") != cfg.get("tags"):
        fail(f"ARCHIVE_INDEX.json tags mismatch for {rel}")
    if entry.get("thread") != cfg.get("thread"):
        fail(f"ARCHIVE_INDEX.json thread mismatch for {rel}")
    if entry.get("status") != cfg.get("status"):
        fail(f"ARCHIVE_INDEX.json status mismatch for {rel}")

source_index = json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))
if source_index.get("revision") != current_revision():
    fail("SOURCES.json revision mismatch")
tool_source_data = source_data()
if tool_source_data.get("revision") != current_revision():
    fail("tools/source_data.json revision mismatch")
for rel in seen:
    groups = source_index["notes"].get(rel, {}).get("groups", [])
    if not groups:
        fail(f"No source groups for {rel}")
    urls = [g.get("url", "") for g in groups]
    if len(urls) != len(set(u.rstrip("/") for u in urls)):
        fail(f"Duplicate source URL for {rel}")
    source_ids = [(g.get("title", "").strip().casefold(), g.get("publisher", "").strip().casefold()) for g in groups]
    if len(source_ids) != len(set(source_ids)):
        fail(f"Duplicate source title/publisher pair for {rel}")
    for g in groups:
        for field in ["title", "publisher", "url", "load_bearing_use"]:
            if not isinstance(g.get(field), str) or not g[field].strip():
                fail(f"Malformed source field {field!r} for {rel}")
        if not g["url"].startswith("https://"):
            fail(f"Source URL must use https:// for {rel}: {g['url']}")

for md in ["README.md", "CHANGELOG.md", "INDEX.md", "THREADS.md", "SOURCES.md"]:
    text = (ROOT / md).read_text(encoding="utf-8")
    if len(re.findall(r"(?m)^# ", text)) != 1:
        fail(f"{md} should have exactly one H1")

sources_md_text = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
for rel in seen:
    file_name = Path(rel).name
    if file_name not in sources_md_text:
        fail(f"SOURCES.md does not mention archive note {file_name}")

changelog_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
changelog_revs = re.findall(r"(?m)^##\s+(rev\d{4})\b", changelog_text)
if not changelog_revs:
    fail("CHANGELOG.md has no revision sections")
if len(changelog_revs) != len(set(changelog_revs)):
    fail("CHANGELOG.md has duplicate revision sections")
if changelog_revs[0] != current_revision():
    fail("CHANGELOG.md latest revision is not first")

threads_md = (ROOT / "THREADS.md").read_text(encoding="utf-8")
for rel in seen:
    file_name = Path(rel).name
    if file_name not in threads_md:
        fail(f"THREADS.md does not mention archive note {file_name}")
for thread in sorted({cfg["thread"] for cfg in catalog.values()}):
    if f"## {thread}" not in threads_md:
        fail(f"THREADS.md missing thread section for {thread}")

thread_summary = json.loads((ROOT / "THREAD_SUMMARY.json").read_text(encoding="utf-8"))
if thread_summary.get("revision") != current_revision():
    fail("THREAD_SUMMARY.json revision mismatch")
summary_threads = thread_summary.get("threads", [])
summary_thread_names = [entry.get("thread") for entry in summary_threads]
expected_thread_names = sorted({cfg["thread"] for cfg in catalog.values()})
if sorted(summary_thread_names) != expected_thread_names:
    fail("THREAD_SUMMARY.json thread set mismatch")
summary_files = []
for entry in summary_threads:
    thread = entry.get("thread")
    files = entry.get("files", [])
    expected_files = [rel for rel in seen if catalog[rel]["thread"] == thread]
    if files != expected_files:
        fail(f"THREAD_SUMMARY.json files mismatch for thread {thread}")
    if entry.get("count") != len(files):
        fail(f"THREAD_SUMMARY.json count mismatch for thread {thread}")
    summary_files.extend(files)
if sorted(summary_files) != sorted(seen):
    fail("THREAD_SUMMARY.json flattened file set mismatch")
if len(summary_files) != len(set(summary_files)):
    fail("THREAD_SUMMARY.json duplicates files across threads")

control = json.loads((ROOT / "CONTROL_SURFACES.json").read_text(encoding="utf-8"))
if control.get("revision") != current_revision():
    fail("CONTROL_SURFACES.json revision mismatch")
if control.get("current_note_set") != seen:
    fail("CONTROL_SURFACES.json current_note_set mismatch")

latest_note = Path(seen[-1]).name
for md in ["README.md", "CHANGELOG.md", "INDEX.md"]:
    text = (ROOT / md).read_text(encoding="utf-8")
    if latest_note not in text:
        fail(f"{md} does not mention latest archive note {latest_note}")

index_text = (ROOT / "INDEX.md").read_text(encoding="utf-8")
for rel in seen:
    file_name = Path(rel).name
    if file_name not in index_text:
        fail(f"INDEX.md does not mention archive note {file_name}")

readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
readme_revs = re.findall(r"(?m)^##\s+(rev\d{4}) additions$", readme_text)
if not readme_revs:
    fail("README.md has no revision additions sections")
if len(readme_revs) != len(set(readme_revs)):
    fail("README.md has duplicate revision additions sections")
if readme_revs[0] != current_revision():
    fail("README.md latest revision additions heading is not first")
if f"## {current_revision()} additions" not in readme_text:
    fail("README.md missing current revision additions heading")

release_note_text = first_section_text(ROOT / "README.md", "Release note")
if not release_note_text:
    fail("README.md missing Release note section content")
if latest_note not in release_note_text:
    fail("README.md Release note must mention latest archive note filename")

version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if version != current_revision():
    fail("VERSION mismatch")

releases = json.loads((ROOT / "RELEASES.json").read_text(encoding="utf-8"))
if not isinstance(releases, list) or not releases:
    fail("RELEASES.json must be a nonempty list")
latest_release = releases[-1]
if latest_release.get("revision") != current_revision():
    fail("RELEASES.json latest entry must match current revision")
release_file = latest_release.get("release_file")
if not isinstance(release_file, str) or not release_file.startswith(f"Metaphysics-{current_revision()}-"):
    fail("RELEASES.json latest release_file must begin with current revision prefix")

manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
if manifest.get("revision") != current_revision():
    fail("MANIFEST.json revision mismatch")

releases = json.loads((ROOT / "RELEASES.json").read_text(encoding="utf-8"))
if not releases:
    fail("RELEASES.json is empty")
latest = releases[-1]
if latest.get("revision") != current_revision():
    fail("RELEASES.json latest revision mismatch")
latest_summary = latest.get("summary", "")
if not isinstance(latest_summary, str) or Path(seen[-1]).name not in latest_summary:
    fail("RELEASES.json latest summary must mention latest archive note filename")
release_files = [r.get("release_file", "") for r in releases]
if len(release_files) != len(set(release_files)):
    fail("Duplicate release_file entries in RELEASES.json")
release_codenames = [r.get("codename", "") for r in releases]
if len(release_codenames) != len(set(release_codenames)):
    fail("Duplicate codenames in RELEASES.json")
for r in releases:
    rev = r.get("revision", "")
    release_file = r.get("release_file", "")
    codename = r.get("codename", "")
    summary = r.get("summary", "")
    if not release_file.startswith(f"Metaphysics-{rev}-"):
        fail(f"release_file revision mismatch for {rev}: {release_file}")
    if not isinstance(codename, str) or not SLUG_RE.match(codename):
        fail(f"Malformed release codename for {rev}: {codename!r}")
    if not isinstance(summary, str) or not summary.strip():
        fail(f"Missing release summary for {rev}")

release_revs = [r.get("revision", "") for r in releases]
if set(changelog_revs) != set(release_revs):
    missing = sorted(set(release_revs) - set(changelog_revs))
    extra = sorted(set(changelog_revs) - set(release_revs))
    fail(f"CHANGELOG/RELEASES mismatch; missing={missing}, extra={extra}")
if changelog_revs != list(reversed(release_revs)):
    fail("CHANGELOG revision order must match RELEASES.json in reverse chronological order")

print("PASS: archive lint clean")
