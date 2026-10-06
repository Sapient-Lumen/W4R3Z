import json
import pathlib
import re
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
REV_RE = re.compile(r"rev\d{4}")
BUNDLE_RE = re.compile(r"DelayBasin-rev\d{4}-[^\s`\"']+?\.zip")

LIVE_RECEIPT_KEYS = [
    "receipt_freshness_witness",
    "question_posture_witness",
    "status_witness",
    "reentry_cue_witness",
    "latest_revision_cue_witness",
    "currentness_cue_witness",
    "package_identity_witness",
    "lint_idempotence_witness",
    "schema_conformance_witness",
    "schema_coverage_witness",
    "basis_provenance_witness",
    "self_sufficiency_witness",
    "self_sufficiency_tail_witness",
    "release_hardening_witness",
    "canary_evidence_witness",
    "path_alias_witness",
    "alias_retention_witness",
    "archive_economy_witness",
    "current_witness_slot",
]


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def walk_scalars(obj: Any, path: str = ""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{path}.{key}" if path else str(key)
            yield from walk_scalars(value, child)
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from walk_scalars(value, f"{path}[{index}]")
    else:
        yield path, obj


def must_equal(problems: list[str], path: str, observed: Any, expected: Any) -> None:
    if observed != expected:
        problems.append(f"{path}: observed {observed!r}, expected {expected!r}")


def main() -> None:
    receipt = load("REVISION-RECEIPT.json")
    manifest = load("RELEASE-MANIFEST.json")
    status = load("SURFACE-STATUS.json")

    expected_revision = manifest.get("revision")
    expected_bundle = manifest.get("bundle")
    expected_stamp = manifest.get("timestamp")
    expected_slug = manifest.get("slug")
    expected_resolved = receipt.get("resolved_question")
    expected_next = receipt.get("next_open_question")
    problems: list[str] = []

    for name, value in {
        "manifest.revision": expected_revision,
        "manifest.bundle": expected_bundle,
        "manifest.timestamp": expected_stamp,
        "manifest.slug": expected_slug,
        "receipt.resolved_question": expected_resolved,
        "receipt.next_open_question": expected_next,
    }.items():
        if not isinstance(value, str) or not value:
            problems.append(f"{name} must be a non-empty string")

    if problems:
        raise SystemExit("currentness residue guard precondition failed: " + "; ".join(problems))

    current_status_keys = [
        "revision", "current_head", "latest_revision", "current_revision",
    ]
    for key in current_status_keys:
        must_equal(problems, f"SURFACE-STATUS.{key}", status.get(key), expected_revision)
    for key in [
        "bundle", "latest_bundle", "current_bundle", "latest_archive",
        "frozen_public_surface", "current_release_surface",
    ]:
        must_equal(problems, f"SURFACE-STATUS.{key}", status.get(key), expected_bundle)
    must_equal(problems, "SURFACE-STATUS.stamp", status.get("stamp"), expected_stamp)
    must_equal(problems, "SURFACE-STATUS.slug", status.get("slug"), expected_slug)
    must_equal(problems, "SURFACE-STATUS.resolved_question", status.get("resolved_question"), expected_resolved)
    must_equal(problems, "SURFACE-STATUS.next_open_question", status.get("next_open_question"), expected_next)
    if isinstance(status.get("current_surfaces"), list):
        must_equal(problems, "SURFACE-STATUS.current_surface_count", status.get("current_surface_count"), len(status["current_surfaces"]))
    previous_surface = (status.get("previous_citation_head") or {}).get("surface")
    if previous_surface:
        must_equal(problems, "SURFACE-STATUS.previous_bundle", status.get("previous_bundle"), previous_surface)

    # These receipt slots are live-current controls, not historical witness sediment.
    for key in LIVE_RECEIPT_KEYS:
        obj = receipt.get(key)
        if not isinstance(obj, dict):
            continue
        for path, value in walk_scalars(obj, key):
            if not isinstance(value, str):
                continue
            if path.endswith("revision") or path.endswith("current_revision") or path.endswith("latest_revision"):
                if REV_RE.fullmatch(value) and value != expected_revision:
                    problems.append(f"REVISION-RECEIPT.{path} stale revision token {value!r}; expected {expected_revision!r}")
            if path.endswith("bundle") or path.endswith("current_bundle") or path.endswith("latest_bundle") or path.endswith("packaged_bundle") or path.endswith("frozen_public_surface") or path.endswith("current_release_surface") or path.endswith("packaged_bundle_filename"):
                if BUNDLE_RE.fullmatch(value) and value != expected_bundle:
                    problems.append(f"REVISION-RECEIPT.{path} stale bundle token {value!r}; expected {expected_bundle!r}")
            if path.endswith("resolved_question") and value != expected_resolved:
                problems.append(f"REVISION-RECEIPT.{path} stale resolved question {value!r}; expected {expected_resolved!r}")
            if path.endswith("next_open_question") and value != expected_next:
                problems.append(f"REVISION-RECEIPT.{path} stale next question {value!r}; expected {expected_next!r}")

    change_summary = receipt.get("change_summary", "")
    if isinstance(change_summary, str):
        revs = REV_RE.findall(change_summary)
        if revs and expected_revision not in revs:
            problems.append("REVISION-RECEIPT.change_summary appears to describe a prior revision")

    if problems:
        raise SystemExit("currentness residue guard failed:\n- " + "\n- ".join(problems[:40]))
    print("check_currentness_residue_guard: OK")


if __name__ == "__main__":
    main()
