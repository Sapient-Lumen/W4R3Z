#!/usr/bin/env python3
"""scripts/release_gate.py

One-command release gate runner.

This is intentionally simple: it runs the required checks in docs/162 in a stable order.
It avoids git dependencies by using scripts/build_manifest.py --check.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], quiet: bool) -> bool:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    ok = proc.returncode == 0
    if quiet and ok:
        return True

    label = "PASS" if ok else "FAIL"
    print(label, " ".join(cmd[1:]) if cmd and cmd[0] == sys.executable else " ".join(cmd))
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip())
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the archive release gate")
    ap.add_argument("--quiet", action="store_true", help="only emit failures")
    ap.add_argument(
        "--write-manifest",
        action="store_true",
        help="regenerate MANIFEST.sha256 instead of checking it",
    )
    args = ap.parse_args()

    py = sys.executable

    steps: list[list[str]] = [
        [py, str(ROOT / "scripts" / "check_index.py")],
        [py, str(ROOT / "scripts" / "check_doc_number_collisions.py")],
        [py, str(ROOT / "scripts" / "check_tracks.py")],
        [py, str(ROOT / "scripts" / "check_adr_index.py")],
        [py, str(ROOT / "scripts" / "gen_track_bundles.py")],
        [py, str(ROOT / "scripts" / "gen_tombstone_index.py")],
        [py, str(ROOT / "scripts" / "check_no_tombstone_refs.py")],
        [py, str(ROOT / "scripts" / "gen_example_packets_index.py")],
        [py, str(ROOT / "scripts" / "gen_external_sources_index.py")],
        [py, str(ROOT / "scripts" / "check_doc_links.py")],
        [py, str(ROOT / "scripts" / "check_doc_backtick_refs.py")],
        [py, str(ROOT / "scripts" / "check_no_raw_urls_modern_docs.py")],
        [py, str(ROOT / "scripts" / "check_no_forbidden_example_tlds.py")],
        [py, str(ROOT / "scripts" / "check_no_cache_artifacts.py")],
        [py, str(ROOT / "scripts" / "check_no_symlinks.py")],
        [py, str(ROOT / "scripts" / "check_tool_maturity_registry.py")],
        [py, str(ROOT / "scripts" / "check_registries_readme.py")],
        [py, str(ROOT / "scripts" / "check_envelope_kinds.py")],
        [py, str(ROOT / "scripts" / "check_doc_envelope_kind_references.py")],
        [py, str(ROOT / "scripts" / "check_envelope_payload_schemas.py")],
        [py, str(ROOT / "scripts" / "check_attachment_requirements.py")],
        [py, str(ROOT / "scripts" / "check_attachment_registry_integrity.py")],
        [py, str(ROOT / "scripts" / "check_example_packets.py")],
        [py, str(ROOT / "scripts" / "check_example_packets_public_artifact_lint.py")],
        [py, str(ROOT / "scripts" / "check_no_hedging_in_public_templates.py")],
        [py, str(ROOT / "scripts" / "check_example_packet_readmes.py")],
        [py, str(ROOT / "scripts" / "check_example_payloads_against_schemas.py")],
        [py, str(ROOT / "scripts" / "check_example_ordering_conventions.py")],
        [py, str(ROOT / "scripts" / "check_example_report_pins.py")],
        [py, str(ROOT / "scripts" / "check_operator_smoke_coverage.py")],
        [py, str(ROOT / "scripts" / "check_operator_tools_smoke.py")],
        [py, str(ROOT / "scripts" / "check_public_surface_pins_coverage.py")],
        [py, str(ROOT / "scripts" / "check_packet_paths.py")],
        [py, str(ROOT / "scripts" / "check_object_uri_alignment.py")],
        [py, str(ROOT / "scripts" / "check_receipt_profiles.py")],
        [py, str(ROOT / "scripts" / "check_publication_triggers.py")],
        [py, str(ROOT / "scripts" / "check_election_milestones_registry.py")],
        [py, str(ROOT / "scripts" / "check_drill_scenarios.py")],
        [py, str(ROOT / "scripts" / "check_known_issues_registry.py")],
        [py, str(ROOT / "scripts" / "check_catastrophe_classes_registry.py")],
        [py, str(ROOT / "scripts" / "check_hazard_catastrophe_classes.py")],
        [py, str(ROOT / 'scripts' / 'check_official_channels_registry.py')],
        [py, str(ROOT / "scripts" / "check_discovery_pointer_coherence.py")],
        [py, str(ROOT / "scripts" / "check_public_notice_type_coherence.py")],
        [py, str(ROOT / "scripts" / "check_proof_obligations.py")],
        [py, str(ROOT / "scripts" / "check_tombstones.py")],
        [py, str(ROOT / "scripts" / "check_no_private_keys.py")],
        [py, str(ROOT / "scripts" / "check_jcs_vectors.py")],
        [py, str(ROOT / "scripts" / "check_observer_kit_jcs_mirror.py")],
        [py, str(ROOT / "scripts" / "check_results_hash_vectors.py")],
        [py, str(ROOT / "scripts" / "check_compact_context_vectors.py")],
        [py, str(ROOT / "scripts" / "check_envelope_vectors.py")],
        [py, str(ROOT / "scripts" / "check_version_consistency.py")],
        [py, str(ROOT / "scripts" / "gen_evidence_object_catalog.py")],
        [py, str(ROOT / "scripts" / "check_verifier_problem_codes_registry.py")],
        [py, str(ROOT / "scripts" / "check_surface_anomaly_codes_registry.py")],
        [py, str(ROOT / "scripts" / "check_verifier_profiles_registry.py")],
        [py, str(ROOT / "scripts" / "gen_verifier_profiles.py")],
        [py, str(ROOT / "scripts" / "gen_verifier_problem_codes.py")],
        [py, str(ROOT / "scripts" / "gen_surface_anomaly_codes.py")],
        [py, str(ROOT / "scripts" / "check_packet_verification_report_linkage.py")],
        [py, str(ROOT / "scripts" / "check_packet_verification_report_emit_packet.py")],
        [py, str(ROOT / "scripts" / "check_size_budget.py")],
        [py, str(ROOT / "scripts" / "validate_schemas.py")],
        [py, str(ROOT / "scripts" / "gen_schema_catalog.py")],
        [py, str(ROOT / "scripts" / "gen_public_surface_index.py")],
        [py, str(ROOT / "scripts" / "check_external_sources_lockfile.py")],
        [py, str(ROOT / "scripts" / "check_track_a_pinned_sources.py")],
        [py, str(ROOT / "scripts" / "check_unused_sources.py")],
        [py, str(ROOT / "scripts" / "verify_external_sources_lock.py")],
        [py, str(ROOT / "scripts" / "validate_artifact_refs.py")],
    ]

    if args.write_manifest:
        steps.append([py, str(ROOT / "scripts" / "build_manifest.py")])
    else:
        steps.append([py, str(ROOT / "scripts" / "build_manifest.py"), "--check"])

    ok_all = True
    for s in steps:
        ok = run(s, quiet=args.quiet)
        ok_all = ok_all and ok

    return 0 if ok_all else 2


if __name__ == "__main__":
    raise SystemExit(main())
