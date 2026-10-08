#!/usr/bin/env python3
"""Build the rev0840 audit for publication preflight and dry-run safety."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "AUDIT" / "PUBLICATION_PREFLIGHT_DRY_RUN_SAFETY_REV0840.json"
MD_OUT = ROOT / "AUDIT" / "PUBLICATION_PREFLIGHT_DRY_RUN_SAFETY_REV0840.md"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read(rel: str) -> str:
    path = ROOT / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def load_json(rel: str) -> dict[str, Any]:
    try:
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def index_or_none(text: str, needle: str) -> int | None:
    idx = text.find(needle)
    return idx if idx >= 0 else None


def helper_cli_status() -> dict[str, Any]:
    rel = "scripts/publication_rights_gate.py"
    text = read(rel)
    required = [
        "def main() -> int",
        "argparse.ArgumentParser",
        "--context",
        "--root",
        "--json",
        "publication_rights_gate_status(root)",
        "format_publication_rights_block(args.context, status)",
    ]
    return {
        "path": rel,
        "sha256": sha256_file(ROOT / rel) if (ROOT / rel).is_file() else None,
        "required_cli_snippets": required,
        "missing_required_cli_snippets": [snippet for snippet in required if snippet not in text],
    }


def preflight_shell_status() -> dict[str, Any]:
    rel = "scripts/publish_preflight.sh"
    text = read(rel)
    guard = "python3 scripts/publication_rights_gate.py --context publish-preflight"
    root_check = '[[ "$(basename "$ROOT_DIR")" =~ ^EvidenceVault-rev[0-9]{4}$ ]]'
    gate_run = "python3 scripts/gate.py"
    guard_index = index_or_none(text, guard)
    root_index = index_or_none(text, root_check)
    gate_index = index_or_none(text, gate_run)
    return {
        "path": rel,
        "sha256": sha256_file(ROOT / rel) if (ROOT / rel).is_file() else None,
        "expected_guard_line": guard,
        "guard_index": guard_index,
        "root_name_check_index": root_index,
        "development_gate_run_index": gate_index,
        "guard_present": guard_index is not None,
        "guard_precedes_root_name_check": guard_index is not None and root_index is not None and guard_index < root_index,
        "guard_precedes_development_gate_run": guard_index is not None and gate_index is not None and guard_index < gate_index,
    }


def makefile_release_ledgers_status() -> dict[str, Any]:
    rel = "Makefile"
    text = read(rel)
    target = text.split("\nrelease-ledgers:\n", 1)[1].split("\npreflight:", 1)[0] if "\nrelease-ledgers:\n" in text and "\npreflight:" in text else ""
    guard = "$(PYTHON) scripts/publication_rights_gate.py --context release-ledgers"
    builders = [
        "$(PYTHON) scripts/build_release_queue_index.py",
        "$(PYTHON) scripts/build_release_ledger.py",
        "$(PYTHON) scripts/materialize_public_release.py",
    ]
    guard_index = index_or_none(target, guard)
    builder_indexes = {item: index_or_none(target, item) for item in builders}
    return {
        "path": rel,
        "sha256": sha256_file(ROOT / rel) if (ROOT / rel).is_file() else None,
        "target": "release-ledgers",
        "expected_guard_recipe": guard,
        "guard_index_in_target": guard_index,
        "builder_indexes_in_target": builder_indexes,
        "guard_present": guard_index is not None,
        "guard_precedes_all_builders": guard_index is not None and all(idx is not None and guard_index < idx for idx in builder_indexes.values()),
    }


def publish_queue_dry_run_status() -> dict[str, Any]:
    rel = "scripts/publish_queue_item.py"
    text = read(rel)
    dry_run = "\n    if args.dry_run:\n"
    snapshot_write = "\n        write_public_surface_snapshot(snapshot_rel, snapshot_payload)"
    record_write = "\n        atomic_write_text(record_json,"
    snapshot_builder = "def build_public_surface_snapshot"
    snapshot_bytes = "def public_surface_snapshot_bytes"
    writer = "def write_public_surface_snapshot"
    dry_idx = index_or_none(text, dry_run)
    snapshot_write_idx = index_or_none(text, snapshot_write)
    record_write_idx = index_or_none(text, record_write)
    return {
        "path": rel,
        "sha256": sha256_file(ROOT / rel) if (ROOT / rel).is_file() else None,
        "snapshot_builder_present": snapshot_builder in text,
        "snapshot_bytes_function_present": snapshot_bytes in text,
        "snapshot_writer_present": writer in text,
        "dry_run_branch_index": dry_idx,
        "snapshot_write_index": snapshot_write_idx,
        "record_write_index": record_write_idx,
        "dry_run_precedes_snapshot_write": dry_idx is not None and snapshot_write_idx is not None and dry_idx < snapshot_write_idx,
        "dry_run_precedes_record_write": dry_idx is not None and record_write_idx is not None and dry_idx < record_write_idx,
    }


def rights_status() -> dict[str, Any]:
    ledger = load_json("RIGHTS/component_license_ledger.json")
    blockers = ledger.get("blocking_findings", []) if isinstance(ledger.get("blocking_findings"), list) else []
    return {
        "rights_ledger": "RIGHTS/component_license_ledger.json",
        "rights_ledger_sha256": sha256_file(ROOT / "RIGHTS" / "component_license_ledger.json") if (ROOT / "RIGHTS" / "component_license_ledger.json").is_file() else None,
        "ledger_status": str(ledger.get("status", "missing")),
        "decision_required_before_publication": bool(ledger.get("decision_required_before_publication")),
        "root_license_or_notice_file_present": bool(ledger.get("root_license_or_notice_file_present")),
        "blocking_finding_ids": [str(item.get("id")) for item in blockers if isinstance(item, dict) and item.get("id")],
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    global ROOT, JSON_OUT, MD_OUT
    old_root, old_json, old_md = ROOT, JSON_OUT, MD_OUT
    ROOT = root
    JSON_OUT = ROOT / "AUDIT" / "PUBLICATION_PREFLIGHT_DRY_RUN_SAFETY_REV0840.json"
    MD_OUT = ROOT / "AUDIT" / "PUBLICATION_PREFLIGHT_DRY_RUN_SAFETY_REV0840.md"
    try:
        helper = helper_cli_status()
        preflight = preflight_shell_status()
        make_ledgers = makefile_release_ledgers_status()
        queue = publish_queue_dry_run_status()
        rights = rights_status()
        static_ok = (
            not helper["missing_required_cli_snippets"]
            and preflight["guard_precedes_root_name_check"]
            and preflight["guard_precedes_development_gate_run"]
            and make_ledgers["guard_precedes_all_builders"]
            and queue["snapshot_builder_present"]
            and queue["snapshot_bytes_function_present"]
            and queue["snapshot_writer_present"]
            and queue["dry_run_precedes_snapshot_write"]
            and queue["dry_run_precedes_record_write"]
        )
        current_tree_blocked = (
            rights["decision_required_before_publication"]
            or rights["ledger_status"].startswith("publication_blocked")
            or bool(rights["blocking_finding_ids"])
            or not rights["root_license_or_notice_file_present"]
        )
        return {
            "version": 1,
            "revision_context": "rev0840-session-patch-over-rev0839-over-rev0826",
            "status": "publication_preflight_and_dry_run_safety_hooks_present" if static_ok and current_tree_blocked else "publication_preflight_or_dry_run_safety_attention_required",
            "purpose": "Fail publication preflight/ledger entrypoints before they run long or mutating steps while rights are blocked, and make publish_queue_item.py --dry-run a true no-write preview even after rights are resolved.",
            "current_rights_status": rights,
            "current_tree_expected_to_refuse_publication_entrypoints": current_tree_blocked,
            "shared_helper_cli": helper,
            "publish_preflight_shell": preflight,
            "makefile_release_ledgers_target": make_ledgers,
            "publish_queue_item_dry_run": queue,
            "dynamic_validator": "scripts/validate_publication_preflight_dry_run_safety_rev0840.py",
            "builder": "scripts/build_publication_preflight_dry_run_safety_audit_rev0840.py",
        }
    finally:
        ROOT, JSON_OUT, MD_OUT = old_root, old_json, old_md


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Publication preflight and dry-run safety audit — rev0840",
        "",
        "This audit covers two practical operator-safety issues: publication preflight should fail fast while rights are blocked, and queue-publisher dry-runs must not create public-release snapshots or records.",
        "",
        f"- Status: `{data['status']}`",
        f"- Current rights status: `{data['current_rights_status']['ledger_status']}`",
        f"- Current tree expected to refuse publication entrypoints: `{str(data['current_tree_expected_to_refuse_publication_entrypoints']).lower()}`",
        "",
        "## Static checks",
        "",
        f"- Shared helper CLI present: `{str(not data['shared_helper_cli']['missing_required_cli_snippets']).lower()}`",
        f"- `publish_preflight.sh` guard precedes root-name check: `{str(data['publish_preflight_shell']['guard_precedes_root_name_check']).lower()}`",
        f"- `publish_preflight.sh` guard precedes development gate run: `{str(data['publish_preflight_shell']['guard_precedes_development_gate_run']).lower()}`",
        f"- `make release-ledgers` guard precedes ledger/materializer builders: `{str(data['makefile_release_ledgers_target']['guard_precedes_all_builders']).lower()}`",
        f"- `publish_queue_item.py --dry-run` branch precedes snapshot write: `{str(data['publish_queue_item_dry_run']['dry_run_precedes_snapshot_write']).lower()}`",
        f"- `publish_queue_item.py --dry-run` branch precedes record write: `{str(data['publish_queue_item_dry_run']['dry_run_precedes_record_write']).lower()}`",
        "",
        "## Protected operator paths",
        "",
        "| Path | Protection |",
        "| --- | --- |",
        f"| `{data['publish_preflight_shell']['path']}` | `{data['publish_preflight_shell']['expected_guard_line']}` |",
        f"| `Makefile` target `{data['makefile_release_ledgers_target']['target']}` | `{data['makefile_release_ledgers_target']['expected_guard_recipe']}` |",
        f"| `{data['publish_queue_item_dry_run']['path']}` | dry-run returns before `write_public_surface_snapshot()` and atomic release-record writes |",
        "",
        "## Validator behavior",
        "",
        "`scripts/validate_publication_preflight_dry_run_safety_rev0840.py` regenerates this audit, probes rights-blocked `publish_preflight.sh` and `make release-ledgers` for fail-fast non-mutation, and runs `publish_queue_item.py --dry-run` in a minimal rights-ready temporary tree to prove the preview path writes no public snapshot, release record, or queue transition.",
    ]
    blockers = data["current_rights_status"].get("blocking_finding_ids", [])
    lines.extend(["", "## Current blocking finding IDs", ""])
    if blockers:
        lines.extend(f"- `{item}`" for item in blockers)
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    data = build(ROOT)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(f"publication-preflight-dry-run-safety-audit-build: OK ({data['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
