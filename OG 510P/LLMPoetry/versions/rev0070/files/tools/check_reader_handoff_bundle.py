#!/usr/bin/env python3
"""Validate the portable reader-only P0002-D010 handoff ZIP.

The check verifies that a future operator can hand over a small bundle without
leaking evaluator rubric language, source-packet machinery, tools, registries, or
cube paths before the first reader response. It is a transfer/readiness gate, not
reader evidence and not poem-quality validation.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from html import escape
from pathlib import Path

CANDIDATE_HEAD = "P0002-D010"
def is_candidate_successor_head(head: str | None) -> bool:
    if not isinstance(head, str) or not head.startswith("P0002-D"):
        return False
    try:
        return int(head.split("-D", 1)[1]) >= 11
    except ValueError:
        return False
HANDOFF_DIR = Path("anthology/candidates/P0002-D010_reader_handoff")
HANDOFF_MANIFEST = HANDOFF_DIR / "HANDOFF_MANIFEST.json"
BUNDLE = Path("anthology/candidates/P0002-D010_reader_handoff_bundle.zip")
SIDECAR = Path("anthology/candidates/P0002-D010_reader_handoff_bundle.zip.sha256")
PAYLOAD_FILES = {
    "HANDOFF_MANIFEST.json",
    "README.md",
    "reader_one_sheet.md",
    "reader_one_sheet.html",
    "reader_response_form.html",
    "response_intake_template.json",
}
READER_FACE_FORBIDDEN = [
    "anthology/", "poems/", "sources/", "registries/", "reports/", "tools/",
    "evaluator rubric", "hostile", "hard-fail", "graceful receipt object"
]
BUNDLE_FORBIDDEN_NAMES = ["evaluator", "rubric", "source_material", "registry", "report", "tool"]
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")


def add(checks: list[dict], name: str, ok: bool, detail: str = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def poem_body(raw: str) -> str:
    if "## Poem" not in raw or "## Disclosure" not in raw:
        return ""
    return raw.split("## Poem", 1)[1].split("## Disclosure", 1)[0].strip("\n")


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    packet = load_json(root / "anthology/candidates/P0002-D010_disclosed_reader_packet.json")
    rev = state.get("revision")
    current_head = surface.get("current_head")
    candidate_is_current = current_head == CANDIDATE_HEAD
    pilot_queue = load_json(root / "registries/pilot_queue.json")
    recommended = [p for p in pilot_queue.get("pilots", []) if isinstance(p, dict) and p.get("status") == "recommended_next"]
    candidate_is_active_target = bool(
        candidate_is_current
        or (
            len(recommended) == 1
            and recommended[0].get("target_draft") == CANDIDATE_HEAD
            and recommended[0].get("target_is_not_global_head") is True
            and recommended[0].get("current_head") == current_head
        )
    )
    draft_body = poem_body(text(root / "poems/P0002/draft_010.md"))

    add(checks, "reader_handoff_bundle_evaluation_target_active", candidate_is_active_target, f"global={current_head} target={recommended[0].get('target_draft') if recommended else None}")
    for rel in (HANDOFF_MANIFEST, BUNDLE, SIDECAR):
        add(checks, f"reader_handoff_bundle_path_exists:{rel.as_posix()}", (root / rel).exists(), rel.as_posix())
    if not (root / BUNDLE).exists():
        return checks

    side = text(root / SIDECAR).strip().split()
    add(checks, "reader_handoff_bundle_sidecar_format", len(side) >= 2, text(root / SIDECAR).strip())
    if len(side) >= 2:
        add(checks, "reader_handoff_bundle_sidecar_hash", side[0] == sha256_file(root / BUNDLE), side[0])
        add(checks, "reader_handoff_bundle_sidecar_name", side[1] == BUNDLE.name, side[1])

    paths = packet.get("paths", {})
    add(checks, "reader_handoff_bundle_declared_in_packet", paths.get("reader_handoff_bundle") == BUNDLE.as_posix(), str(paths.get("reader_handoff_bundle")))
    add(checks, "reader_handoff_bundle_sidecar_declared_in_packet", paths.get("reader_handoff_bundle_sidecar") == SIDECAR.as_posix(), str(paths.get("reader_handoff_bundle_sidecar")))
    policy = packet.get("reader_handoff_bundle_policy", {})
    add(checks, "reader_handoff_bundle_policy_mode", policy.get("mode") == "reader_only_zip_no_rubric_no_source_packet", str(policy.get("mode")))
    add(checks, "reader_handoff_bundle_policy_nonclaim", policy.get("not_reader_evidence") is True and policy.get("not_admission") is True, str(policy))

    with zipfile.ZipFile(root / BUNDLE) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        add(checks, "reader_handoff_bundle_exact_payload", set(names) == PAYLOAD_FILES and len(names) == len(PAYLOAD_FILES), names)
        add(checks, "reader_handoff_bundle_no_dirs_or_paths", all("/" not in n and ".." not in n for n in names), names)
        bad_names = [n for n in names for bad in BUNDLE_FORBIDDEN_NAMES if bad in n.lower()]
        add(checks, "reader_handoff_bundle_no_forbidden_entry_names", not bad_names, bad_names)
        add(checks, "reader_handoff_bundle_fixed_timestamps", all(i.date_time == (1980, 1, 1, 0, 0, 0) for i in infos), [i.date_time for i in infos])
        data = {n: z.read(n) for n in names}

    manifest = json.loads(data.get("HANDOFF_MANIFEST.json", b"{}").decode("utf-8"))
    add(checks, "reader_handoff_bundle_manifest_revision", manifest.get("revision") == rev or not candidate_is_current, manifest.get("revision"))
    add(checks, "reader_handoff_bundle_manifest_current_head", manifest.get("draft_id") == CANDIDATE_HEAD, manifest.get("draft_id"))
    add(checks, "reader_handoff_bundle_manifest_exclusion_flags", manifest.get("bundle_includes_evaluator_rubric") is False and manifest.get("bundle_includes_source_packet") is False and manifest.get("bundle_includes_tools_or_registries") is False, str(manifest))
    file_entries = {entry.get("path"): entry for entry in manifest.get("files", []) if isinstance(entry, dict)}
    add(checks, "reader_handoff_bundle_manifest_lists_payload_files", set(file_entries) == (PAYLOAD_FILES - {"HANDOFF_MANIFEST.json"}), sorted(file_entries))
    for rel, entry in file_entries.items():
        blob = data.get(rel)
        add(checks, f"reader_handoff_bundle_manifest_entry_present:{rel}", blob is not None, rel)
        if blob is not None:
            add(checks, f"reader_handoff_bundle_manifest_hash:{rel}", entry.get("sha256") == sha256_bytes(blob), rel)
            add(checks, f"reader_handoff_bundle_manifest_size:{rel}", entry.get("size") == len(blob), rel)
            disk = root / HANDOFF_DIR / rel
            add(checks, f"reader_handoff_bundle_matches_disk:{rel}", disk.exists() and disk.read_bytes() == blob, rel)

    for rel in ["README.md", "reader_one_sheet.md", "reader_one_sheet.html", "reader_response_form.html"]:
        raw = data.get(rel, b"").decode("utf-8", errors="replace")
        low = raw.lower()
        bad = [s for s in READER_FACE_FORBIDDEN if s in low]
        add(checks, f"reader_handoff_bundle_no_cube_or_rubric_leak:{rel}", not bad, bad)
        add(checks, f"reader_handoff_bundle_mentions_revision_or_historical:{rel}", rev in raw or not candidate_is_current, rel)
        add(checks, f"reader_handoff_bundle_mentions_current_head:{rel}", CANDIDATE_HEAD in raw, rel)
    one_md = data.get("reader_one_sheet.md", b"").decode("utf-8", errors="replace")
    one_html = data.get("reader_one_sheet.html", b"").decode("utf-8", errors="replace")
    add(checks, "reader_handoff_bundle_one_sheet_exact_poem_md", bool(draft_body and draft_body in one_md), "md")
    add(checks, "reader_handoff_bundle_one_sheet_exact_poem_html", bool(draft_body and escape(draft_body.splitlines()[0]) in one_html and escape(draft_body.splitlines()[-1]) in one_html), "html")
    before_poem = one_md.split("## Poem", 1)[0]
    add(checks, "reader_handoff_bundle_prepoem_word_cap", len(WORD_RE.findall(before_poem)) <= 120, f"words={len(WORD_RE.findall(before_poem))}")
    return checks


def main(root: str = ".") -> int:
    checks = run(Path(root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
