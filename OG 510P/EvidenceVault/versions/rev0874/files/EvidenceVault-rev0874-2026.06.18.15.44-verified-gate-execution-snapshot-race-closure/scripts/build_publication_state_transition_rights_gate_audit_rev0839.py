#!/usr/bin/env python3
"""Build the rev0839 audit for direct publication-state transition gating.

rev0838 protected the main artifact-emitting publication entry points, but a
lower-level queue-state utility still had enough authority to move a queue item
into the published state.  This audit records and validates that the utility now
runs the shared rights gate before any lookup or mutation when --to-state
published is requested.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from publication_rights_gate import publication_rights_gate_status  # noqa: E402

JSON_OUT = ROOT / "AUDIT" / "PUBLICATION_STATE_TRANSITION_RIGHTS_GATE_REV0839.json"
MD_OUT = ROOT / "AUDIT" / "PUBLICATION_STATE_TRANSITION_RIGHTS_GATE_REV0839.md"
TRANSITION_REL = "scripts/transition_queue_item.py"
PROBE_ITEM = "EV-QUEUE-2026-03-20-full-archive-mirror-not-public"


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def transition_script_status() -> dict[str, Any]:
    path = ROOT / TRANSITION_REL
    text = read(path)
    guard = "assert_publication_rights_ready(ROOT, 'transition-queue-item')"
    conditional = "if args.to_state == 'published':"
    first_lookup = "\n    src_state, json_path = find_item(args.item)"
    first_write = "\n    dest_json.write_text("
    guard_index = text.find(guard)
    lookup_index = text.find(first_lookup)
    write_index = text.find(first_write)
    conditional_index = text.find(conditional)
    return {
        "path": TRANSITION_REL,
        "sha256": sha256_file(path),
        "imports_shared_helper": "from publication_rights_gate import assert_publication_rights_ready" in text,
        "conditional_published_state_guard_present": conditional_index >= 0,
        "expected_guard_call": guard,
        "guard_call_present": guard_index >= 0,
        "guard_call_index": guard_index,
        "published_state_conditional_index": conditional_index,
        "first_queue_lookup_marker": first_lookup,
        "first_queue_lookup_index": lookup_index,
        "first_mutation_marker": first_write,
        "first_mutation_index": write_index,
        "guard_precedes_queue_lookup": guard_index >= 0 and lookup_index >= 0 and guard_index < lookup_index,
        "guard_precedes_first_mutation": guard_index >= 0 and write_index >= 0 and guard_index < write_index,
    }


def snapshot(paths: list[Path]) -> dict[str, dict[str, Any] | None]:
    out: dict[str, dict[str, Any] | None] = {}
    for path in paths:
        key = path.relative_to(ROOT).as_posix()
        if not path.exists():
            out[key] = None
            continue
        stat = path.stat()
        out[key] = {
            "size_bytes": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "sha256": sha256_file(path) if path.is_file() else None,
        }
    return out


def probe_paths() -> list[Path]:
    return [
        ROOT / "release_queue" / "hold" / "2026-03-20-full-archive-mirror-not-public.json",
        ROOT / "release_queue" / "hold" / "2026-03-20-full-archive-mirror-not-public.md",
        ROOT / "release_queue" / "published" / "2026-03-20-full-archive-mirror-not-public.json",
        ROOT / "release_queue" / "published" / "2026-03-20-full-archive-mirror-not-public.md",
    ]


def run_block_probe() -> dict[str, Any]:
    before = snapshot(probe_paths())
    cmd = [
        sys.executable,
        str(ROOT / TRANSITION_REL),
        "--item",
        PROBE_ITEM,
        "--to-state",
        "published",
        "--decision-id",
        "EV-REL-REV0839-RIGHTS-GATE-PROBE",
        "--public-release-id",
        "EV-PUB-REV0839-RIGHTS-GATE-PROBE",
        "--next-action",
        "rev0839 publication-state rights-gate probe; should not be written",
    ]
    env = dict(**{k: v for k, v in __import__('os').environ.items()})
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(cmd, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    after = snapshot(probe_paths())
    changed = [key for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)]
    combined = (proc.stdout or "") + (proc.stderr or "")
    return {
        "command": ["python3", TRANSITION_REL, "--item", PROBE_ITEM, "--to-state", "published", "--decision-id", "EV-REL-REV0839-RIGHTS-GATE-PROBE", "--public-release-id", "EV-PUB-REV0839-RIGHTS-GATE-PROBE"],
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "combined_output_contains_rights_block": "publication rights gate blocked" in combined,
        "combined_output_contains_transition_ok": "transition-queue-item: OK" in combined,
        "publication_artifacts_or_queue_files_changed": bool(changed),
        "changed_paths": changed,
    }


def build(root: Path = ROOT, run_probe: bool = True) -> dict[str, Any]:
    rights = publication_rights_gate_status(root)
    script = transition_script_status()
    probe = run_block_probe() if run_probe and root == ROOT else None
    probe_ok = bool(probe) and probe["returncode"] != 0 and probe["combined_output_contains_rights_block"] and not probe["publication_artifacts_or_queue_files_changed"] and not probe["combined_output_contains_transition_ok"]
    static_ok = (
        script["imports_shared_helper"]
        and script["conditional_published_state_guard_present"]
        and script["guard_call_present"]
        and script["guard_precedes_queue_lookup"]
        and script["guard_precedes_first_mutation"]
    )
    current_tree_blocked = bool(rights.get("blocked"))
    return {
        "version": 1,
        "revision_context": "rev0839-session-patch-over-rev0838-over-rev0826",
        "status": "direct_published_state_transition_rights_gated" if static_ok and current_tree_blocked and (probe_ok or not run_probe) else "publication_state_transition_rights_gate_attention_required",
        "purpose": "Close the direct queue-state bypass by preventing scripts/transition_queue_item.py from moving any item to published while the publication rights ledger blocks release.",
        "current_rights_status": rights,
        "transition_script": script,
        "probe_item": PROBE_ITEM,
        "blocked_transition_probe": probe,
        "static_checks_pass": static_ok,
        "blocked_probe_pass": probe_ok if probe is not None else None,
        "builder": "scripts/build_publication_state_transition_rights_gate_audit_rev0839.py",
        "validator": "scripts/validate_publication_state_transition_rights_gate_rev0839.py",
    }


def render_markdown(data: dict[str, Any]) -> str:
    script = data["transition_script"]
    rights = data["current_rights_status"]
    probe = data.get("blocked_transition_probe") or {}
    lines = [
        "# Publication state transition rights gate audit — rev0839",
        "",
        "rev0838 guarded public/full release emitters. rev0839 closes the lower-level queue-state bypass: direct transitions into `published` must also refuse while rights are blocked.",
        "",
        f"- Status: `{data['status']}`",
        f"- Transition utility: `{script['path']}`",
        f"- Transition utility SHA-256: `{script['sha256']}`",
        f"- Rights ledger: `{rights.get('rights_ledger')}`",
        f"- Rights blocked: `{str(bool(rights.get('blocked'))).lower()}`",
        f"- Rights blocked reasons: `{', '.join(rights.get('blocked_reasons', []))}`",
        f"- Static checks pass: `{str(bool(data['static_checks_pass'])).lower()}`",
        f"- Blocked probe pass: `{str(bool(data['blocked_probe_pass'])).lower()}`",
        "",
        "## Static guard placement",
        "",
        f"- Imports shared helper: `{str(script['imports_shared_helper']).lower()}`",
        f"- Conditional `--to-state published` guard present: `{str(script['conditional_published_state_guard_present']).lower()}`",
        f"- Guard call present: `{str(script['guard_call_present']).lower()}`",
        f"- Guard precedes queue lookup: `{str(script['guard_precedes_queue_lookup']).lower()}`",
        f"- Guard precedes first mutation: `{str(script['guard_precedes_first_mutation']).lower()}`",
        "",
        "## Refusal probe",
        "",
        f"- Probe item: `{data['probe_item']}`",
        f"- Return code: `{probe.get('returncode')}`",
        f"- Output contains rights block: `{str(bool(probe.get('combined_output_contains_rights_block'))).lower()}`",
        f"- Output contains transition OK: `{str(bool(probe.get('combined_output_contains_transition_ok'))).lower()}`",
        f"- Queue/publication files changed: `{str(bool(probe.get('publication_artifacts_or_queue_files_changed'))).lower()}`",
        "",
        "## Why this matters",
        "",
        "A rights-blocked tree should remain development-testable, but no path should mark a release queue item as executed/public. This guard blocks the direct state mutation path separately from the higher-level `publish_queue_item.py` emitter.",
    ]
    changed = probe.get("changed_paths") or []
    if changed:
        lines.extend(["", "## Changed paths during probe", ""])
        lines.extend(f"- `{item}`" for item in changed)
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    data = build(ROOT, run_probe=True)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(f"publication-state-transition-rights-gate-audit-build: OK ({data['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
