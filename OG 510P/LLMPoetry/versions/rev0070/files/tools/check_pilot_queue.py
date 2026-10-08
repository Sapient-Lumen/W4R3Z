#!/usr/bin/env python3
"""Validate pilot queue semantics, including pilots aimed at preserved candidates.

A pilot's global ``current_head`` records cube state; ``target_draft`` records the
object actually being tested. Those fields are deliberately allowed to differ.
This prevents a long successor chain from making its strongest preserved draft
operationally unreachable.
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

FIELD_KIT_DIR = Path("anthology/candidates/P0002-D010_field_kit")
FIELD_KIT_ZIP = Path("anthology/candidates/P0002-D010_field_kit.zip")
FIELD_KIT_SIDE = Path("anthology/candidates/P0002-D010_field_kit.zip.sha256")
FIELD_KIT_FILES = {
    "P0002-D010_field_test.html",
    "README.md",
    "FIELD_KIT_MANIFEST.json",
}


def add(checks: list[dict], name: str, ok: bool, detail: str = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_field_kit(root: Path, checks: list[dict], target: str) -> None:
    manifest_path = root / FIELD_KIT_DIR / "FIELD_KIT_MANIFEST.json"
    html_path = root / FIELD_KIT_DIR / "P0002-D010_field_test.html"
    readme_path = root / FIELD_KIT_DIR / "README.md"
    for rel in (manifest_path, html_path, readme_path, root / FIELD_KIT_ZIP, root / FIELD_KIT_SIDE):
        add(checks, f"reader_field_kit_exists:{rel.relative_to(root).as_posix()}", rel.exists(), rel)
    if not all(p.exists() for p in (manifest_path, html_path, readme_path, root / FIELD_KIT_ZIP, root / FIELD_KIT_SIDE)):
        return

    manifest = load_json(manifest_path)
    add(checks, "reader_field_kit_target", manifest.get("target_draft") == target == "P0002-D010", manifest.get("target_draft"))
    add(checks, "reader_field_kit_offline", manifest.get("network_requests") is False and manifest.get("remote_assets") is False, str(manifest.get("network_requests")))
    add(checks, "reader_field_kit_no_identity", manifest.get("collects_identity") is False, str(manifest.get("collects_identity")))
    add(checks, "reader_field_kit_excludes_source_and_rubric", manifest.get("contains_source_packet") is False and manifest.get("contains_evaluator_rubric") is False, "field kit exclusions")
    source_path = root / str(manifest.get("target_draft_path", ""))
    add(checks, "reader_field_kit_target_hash_current", source_path.exists() and manifest.get("target_draft_sha256") == sha256_file(source_path), manifest.get("target_draft_sha256"))

    html_raw = html_path.read_text(encoding="utf-8", errors="replace")
    add(checks, "reader_field_kit_html_has_exact_candidate_edges", "Behind the Marine Inspection Office," in html_raw and "Height does not." in html_raw, "candidate body edges")
    add(checks, "reader_field_kit_html_has_download_action", "P0002-D010-reader-response.json" in html_raw and "new Blob" in html_raw, "offline JSON download")
    add(checks, "reader_field_kit_html_no_network_calls", not any(token in html_raw for token in ("fetch(", "XMLHttpRequest", "sendBeacon", "https://", "http://")), "network-token scan")
    required_fields = {
        "disclosure_seen_before_poem", "source_packet_opened_before_first_response",
        "boundary_acknowledged", "keep_reject_uncertain", "strongest_line_or_phrase",
        "weakest_line_or_phrase", "disclosure_delta", "body_works_without_source_packet",
        "documentation_doing_poem_work", "revision_instruction", "quality_claims",
    }
    missing_fields = sorted(field for field in required_fields if field not in html_raw)
    add(checks, "reader_field_kit_intake_fields_complete", not missing_fields, missing_fields)

    side = (root / FIELD_KIT_SIDE).read_text(encoding="utf-8").split()
    add(checks, "reader_field_kit_sidecar_format", len(side) >= 2, side)
    if len(side) >= 2:
        add(checks, "reader_field_kit_sidecar_hash", side[0] == sha256_file(root / FIELD_KIT_ZIP), side[0])
        add(checks, "reader_field_kit_sidecar_name", side[1] == FIELD_KIT_ZIP.name, side[1])

    with zipfile.ZipFile(root / FIELD_KIT_ZIP) as zf:
        names = [i.filename for i in zf.infolist()]
        add(checks, "reader_field_kit_zip_exact_payload", set(names) == FIELD_KIT_FILES and len(names) == len(FIELD_KIT_FILES), names)
        add(checks, "reader_field_kit_zip_fixed_timestamps", all(i.date_time == (1980, 1, 1, 0, 0, 0) for i in zf.infolist()), [i.date_time for i in zf.infolist()])
        for name in names:
            disk = root / FIELD_KIT_DIR / name
            add(checks, f"reader_field_kit_zip_matches_disk:{name}", disk.exists() and zf.read(name) == disk.read_bytes(), name)


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    obj = load_json(root / "registries/pilot_queue.json")
    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    pilots = obj.get("pilots", [])
    recommended = [p for p in pilots if p.get("status") == "recommended_next"]

    add(checks, "pilot_queue_parse", isinstance(pilots, list) and bool(pilots), f"count={len(pilots)}")
    add(checks, "pilot_queue_revision_matches_state", obj.get("revision") == state.get("revision"), obj.get("revision"))
    add(checks, "pilot_queue_current_head_matches_surface", obj.get("current_head") == surface.get("current_head"), obj.get("current_head"))
    add(checks, "exactly_one_recommended_next", len(recommended) == 1, f"count={len(recommended)}")
    add(checks, "pilots_have_verification_path", all(p.get("verification_path") for p in pilots), "verification_path")

    forms = load_json(root / "registries/form_registry.json").get("forms", [])
    form_ids = {f.get("form_id") for f in forms}
    missing = [p.get("form_id") for p in pilots if p.get("form_id") not in form_ids]
    add(checks, "pilot_form_ids_registered", not missing, missing)

    if not recommended:
        return checks

    rec = recommended[0]
    paths = rec.get("verification_path") or []
    kind = rec.get("pilot_kind") or "legacy_current_head"
    target = rec.get("target_draft")
    add(checks, "recommended_pilot_global_head_current", rec.get("current_head") == surface.get("current_head"), rec.get("current_head"))
    add(checks, "recommended_pilot_kind_declared", kind in {"cold_review", "reader_evidence_launch", "legacy_current_head"}, kind)
    add(checks, "recommended_pilot_target_declared", isinstance(target, str) and bool(target), target)
    add(checks, "recommended_pilot_verification_paths_unique", len(paths) == len(set(paths)), f"count={len(paths)}")
    add(checks, "recommended_pilot_top_aliases", obj.get("current_pilot") == rec.get("pilot_id") and obj.get("recommended_pilot") == rec.get("pilot_id") and obj.get("current_recommended_pilot") == rec.get("pilot_id"), str(rec.get("pilot_id")))

    if kind == "reader_evidence_launch":
        required = {
            "anthology/candidates/P0002-D010_field_kit/P0002-D010_field_test.html",
            "anthology/candidates/P0002-D010_field_kit/README.md",
            "anthology/candidates/P0002-D010_field_kit/FIELD_KIT_MANIFEST.json",
            FIELD_KIT_ZIP.as_posix(),
            FIELD_KIT_SIDE.as_posix(),
            "anthology/candidates/P0002-D010_reader_responses.json",
            "tools/build_reader_field_kit.py",
            "tools/record_reader_response.py",
            "tools/check_reader_response_intake.py",
            "tools/check_pilot_queue.py",
        }
        add(checks, "recommended_reader_launch_targets_preserved_candidate", target == "P0002-D010", target)
        add(checks, "recommended_reader_launch_may_differ_from_global_head", target != rec.get("current_head") and rec.get("target_is_not_global_head") is True, f"target={target} head={rec.get('current_head')}")
        add(checks, "recommended_reader_launch_paths", required <= set(paths), sorted(required - set(paths)))
        response_log = load_json(root / "anthology/candidates/P0002-D010_reader_responses.json")
        add(checks, "recommended_reader_launch_log_still_empty", response_log.get("response_count") == 0 and response_log.get("responses") == [], f"count={response_log.get('response_count')}")
        validate_field_kit(root, checks, target)
    elif kind == "cold_review":
        add(checks, "recommended_cold_review_targets_current_head", target == rec.get("current_head") == surface.get("current_head"), f"target={target}")
        if isinstance(target, str) and target.startswith("P0002-D"):
            n = int(target.split("-D", 1)[1])
            d, prev = f"{n:03d}", f"{n-1:03d}"
            required = {
                f"poems/P0002/draft_{d}.md",
                f"poems/P0002/material/source_material_packet_{d}.json",
                f"poems/P0002/verification/metrics_draft_{d}.json",
                f"poems/P0002/judgments/cold_review_{prev}_on_D{prev}.json",
                "tools/check_external_material_pressure.py",
                "tools/check_release_surfaces.py",
            }
            add(checks, "recommended_cold_review_current_successor_paths", required <= set(paths), sorted(required - set(paths)))
    else:
        add(checks, "recommended_legacy_target_matches_head", target == rec.get("current_head"), f"target={target}")

    declared_files = []
    for rel in paths:
        if isinstance(rel, str) and rel.startswith(("anthology/", "tools/", "reports/", "poems/", "docs/")):
            declared_files.append((rel, (root / rel).exists()))
    add(checks, "recommended_pilot_declared_file_paths_exist", all(ok for _, ok in declared_files), [rel for rel, ok in declared_files if not ok])
    return checks


def main(root: str = ".") -> int:
    try:
        checks = run(Path(root))
    except Exception as exc:
        checks = [{"name": "pilot_queue_parse", "ok": False, "detail": repr(exc)}]
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
