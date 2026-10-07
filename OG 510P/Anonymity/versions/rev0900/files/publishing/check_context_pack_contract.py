#!/usr/bin/env python3
"""Validate the compact reentry context pack against the shipped archive state."""

from __future__ import annotations

import argparse
import json
import pathlib
import shlex
import sys


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def record(checks: list[dict], name: str, ok: bool, details: str):
    checks.append({"name": name, "status": "pass" if ok else "fail", "details": details})


def check(root: pathlib.Path) -> dict:
    pack = load_json(root / "CONTEXT_PACK.json")
    release_manifest = load_json(root / "RELEASE_MANIFEST.json")
    queue_index = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    citation_heads = load_json(root / "published" / "citation_heads.json")
    checks: list[dict] = []

    required_top = {
        "format",
        "version",
        "project",
        "revision",
        "bundle",
        "must_read",
        "quick_checks",
        "current_posture",
        "control_surfaces",
        "operator_warnings",
    }
    missing_top = sorted(required_top - set(pack))
    record(
        checks,
        "required_top_level_keys_present",
        not missing_top,
        "missing=" + (", ".join(missing_top) if missing_top else "none"),
    )

    required_prefix = ["VERSION", "START_HERE.md", "CONTEXT_PACK.json"]
    starts_ok = pack.get("must_read", [])[:3] == required_prefix
    record(
        checks,
        "must_read_starts_with_reentry_triplet",
        starts_ok,
        f"must_read_prefix={pack.get('must_read', [])[:3]}",
    )

    missing_must_read = sorted(p for p in pack.get("must_read", []) if not (root / p).exists())
    record(
        checks,
        "must_read_paths_exist",
        not missing_must_read,
        "missing=" + (", ".join(missing_must_read) if missing_must_read else "none"),
    )

    malformed_commands = []
    missing_quick_check_scripts = []
    for name, cmd in pack.get("quick_checks", {}).items():
        parts = shlex.split(cmd)
        if len(parts) < 2 or parts[0] != "python3":
            malformed_commands.append(f"{name}:{cmd}")
            continue
        script_index = 1
        while script_index < len(parts) and parts[script_index].startswith("-"):
            script_index += 1
        if script_index >= len(parts):
            malformed_commands.append(f"{name}:{cmd}")
            continue
        script = root / parts[script_index]
        if not script.exists():
            missing_quick_check_scripts.append(parts[script_index])
    record(
        checks,
        "quick_check_commands_are_python3_scripts",
        not malformed_commands,
        "malformed=" + (", ".join(malformed_commands) if malformed_commands else "none"),
    )
    record(
        checks,
        "quick_check_scripts_exist",
        not missing_quick_check_scripts,
        "missing=" + (", ".join(missing_quick_check_scripts) if missing_quick_check_scripts else "none"),
    )

    missing_control_surfaces = sorted(
        path for path in pack.get("control_surfaces", {}).values() if not (root / path).exists()
    )
    record(
        checks,
        "control_surface_paths_exist",
        not missing_control_surfaces,
        "missing=" + (", ".join(missing_control_surfaces) if missing_control_surfaces else "none"),
    )

    queue_posture_ok = pack.get("current_posture", {}).get("queue") == {
        "candidate": queue_index["summary"]["candidate"],
        "published_ready": queue_index["summary"]["published_ready"],
        "hold": queue_index["summary"]["hold"],
        "published": queue_index["summary"].get("published", 0),
    }
    record(
        checks,
        "queue_posture_matches_queue_index",
        queue_posture_ok,
        f"context_queue={pack.get('current_posture', {}).get('queue')} queue_index_summary={queue_index['summary']}",
    )

    citation_ok = (
        pack.get("current_posture", {}).get("legacy_public_head_count")
        == citation_heads["summary"]["legacy_public_head_count"]
        and pack.get("current_posture", {}).get("new_post_policy_anonymity_head_count")
        == citation_heads["summary"]["new_post_policy_anonymity_head_count"]
        and pack.get("current_posture", {}).get("repo_frozen_noncanonical_entry_count")
        == citation_heads["summary"]["repo_frozen_noncanonical_entry_count"]
    )
    record(
        checks,
        "citation_posture_matches_citation_heads",
        citation_ok,
        f"context_posture={pack.get('current_posture', {})}",
    )

    identity_ok = pack.get("revision") == release_manifest.get("revision") and pack.get("bundle") == release_manifest.get("bundle")
    record(
        checks,
        "revision_and_bundle_match_release_manifest",
        identity_ok,
        f"context_revision={pack.get('revision')} context_bundle={pack.get('bundle')} release_manifest={release_manifest}",
    )

    failures = [c for c in checks if c["status"] == "fail"]
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release_manifest.get("revision"),
        "checked_revision": release_manifest.get("revision"),
        "checked_bundle": release_manifest.get("bundle"),
        "publication_authorized": False,
        "checks": checks,
        "summary": {
            "checks_passed": len(checks) - len(failures),
            "checks_failed": len(failures),
        },
        "fail_closed_rule": "If this report fails, default to no publication and repair CONTEXT_PACK.json before using it as a reentry packet.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = (root / args.write_report).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
