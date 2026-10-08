#!/usr/bin/env python3
"""Run semantic audits with shared caches and bounded process memory.

Structural checks run in the coordinator. Answer/runtime, replay, promotion,
and output checks run one script per isolated process while sharing one answer
cache and one strict-schema evidence cache. This avoids both duplicated graph
builds and long-lived workers that retain every intermediate graph.
"""
from __future__ import annotations

import gc
import os
import pathlib
import runpy
import subprocess
import sys
import tempfile
from typing import Iterable, Optional

sys.dont_write_bytecode = True

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
worker_group = sys.argv[2] if len(sys.argv) > 2 else None

PRE_AUDITS = [
    "tools/audit_cube.py",
    "tools/audit_axis_hygiene.py",
    "tools/audit_prose_bloat.py",
    "tools/audit_waste_signals.py",
    "tools/audit_source_currentness.py",
    "tools/audit_external_attestation_verifier.py",
    "tools/audit_procurement_risk.py",
    "tools/audit_remedy_profiles.py",
    "tools/audit_case_contracts.py",
    "tools/audit_route_profile_index.py",
]
ANSWER_AUDITS = [
    "tools/audit_answer_skeletons.py",
    "tools/audit_claim_provenance.py",
    "tools/audit_precedence_resolution.py",
    "tools/audit_disposition_synthesis.py",
    "tools/audit_decision_adapters.py",
    "tools/audit_adapter_execution.py",
    "tools/audit_evidence_producer_contracts.py",
    "tools/audit_evidence_producer_execution.py",
    "tools/audit_model_input_bundles.py",
    "tools/audit_model_input_source_manifests.py",
    "tools/audit_authority_evidence_bundles.py",
]
TRUTH_BOUNDARY_AUDITS = [
    "tools/audit_evidence_replay_ledger.py",
    "tools/audit_decision_promotion_gate.py",
    "tools/audit_positive_external_evidence_path.py",
    "tools/audit_decision_review_bundle.py",
    "tools/audit_decision_output_packets.py",
]
POST_AUDITS = [
    "tools/audit_release_lineage.py",
    "tools/audit_policy_action_profiles.py",
    "tools/audit_actor_accountability_profiles.py",
]

answer_cache_path: Optional[pathlib.Path] = None
strict_evidence_cache_path: Optional[pathlib.Path] = None


def run_in_process(rel_paths: Iterable[str]) -> None:
    for rel in rel_paths:
        script = root / rel
        if not script.exists():
            raise SystemExit(f"missing semantic audit script: {rel}")
        old_argv = sys.argv[:]
        try:
            sys.argv = [str(script), str(root)]
            runpy.run_path(str(script), run_name="__main__")
        except SystemExit as exc:
            if exc.code not in (0, None):
                raise
        finally:
            sys.argv = old_argv
            gc.collect()


def run_isolated(rel_paths: Iterable[str]) -> None:
    """Run expensive audits one process at a time while preserving shared caches.

    Rev0340 keeps the answer-packet and strict-evidence caches, but avoids the
    previous long-lived worker retaining every intermediate graph across
    authority, replay, promotion, and output audits. This makes `make audit`
    more cloud-container friendly without dropping any audit.
    """
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    if answer_cache_path is not None:
        env["MT_ANSWER_PACKET_CACHE"] = str(answer_cache_path)
    if strict_evidence_cache_path is not None:
        env["MT_STRICT_SCHEMA_TEST_EVIDENCE_CACHE"] = str(strict_evidence_cache_path)
    for rel in rel_paths:
        script = root / rel
        if not script.exists():
            raise SystemExit(f"missing semantic audit script: {rel}")
        print(f"semantic audit running {rel}", flush=True)
        try:
            subprocess.run([sys.executable, str(script), str(root)], check=True, env=env, timeout=300)
        except subprocess.TimeoutExpired as exc:
            raise SystemExit(f"semantic audit timed out after {exc.timeout}s: {rel}") from exc


def ensure_shared_caches() -> None:
    global answer_cache_path, strict_evidence_cache_path
    if answer_cache_path is not None:
        return

    fd, answer_name = tempfile.mkstemp(prefix="mt-answer-packets-", suffix=".json")
    os.close(fd)
    answer_cache_path = pathlib.Path(answer_name)
    with answer_cache_path.open("w", encoding="utf-8") as output:
        subprocess.run(
            [
                sys.executable,
                str(root / "tools/answer_case.py"),
                str(root),
                "--all",
                "--route-limit",
                "5",
                "--facts-only-candidate-limit",
                "8",
                "--json",
            ],
            check=True,
            text=True,
            stdout=output,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    fd, evidence_name = tempfile.mkstemp(prefix="mt-strict-evidence-", suffix=".json")
    os.close(fd)
    strict_evidence_cache_path = pathlib.Path(evidence_name)
    strict_evidence_cache_path.unlink()
    os.environ["MT_ANSWER_PACKET_CACHE"] = str(answer_cache_path)
    os.environ["MT_STRICT_SCHEMA_TEST_EVIDENCE_CACHE"] = str(strict_evidence_cache_path)


def cleanup_shared_caches() -> None:
    for path in (answer_cache_path, strict_evidence_cache_path):
        if path is not None:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
    os.environ.pop("MT_ANSWER_PACKET_CACHE", None)
    os.environ.pop("MT_STRICT_SCHEMA_TEST_EVIDENCE_CACHE", None)


if worker_group:
    groups = {
        "--pre-worker": PRE_AUDITS,
        "--answer-worker": ANSWER_AUDITS,
        "--truth-worker": TRUTH_BOUNDARY_AUDITS,
        "--post-worker": POST_AUDITS,
    }
    if worker_group not in groups:
        raise SystemExit(f"unknown semantic audit worker group: {worker_group}")
    try:
        if worker_group in {"--answer-worker", "--truth-worker"}:
            ensure_shared_caches()
            run_isolated(groups[worker_group])
        else:
            run_in_process(groups[worker_group])
    finally:
        cleanup_shared_caches()
    print(f"semantic audit worker {worker_group[2:]} ok")
    raise SystemExit(0)

try:
    run_in_process(PRE_AUDITS)
    ensure_shared_caches()
    run_isolated(ANSWER_AUDITS)
    run_isolated(TRUTH_BOUNDARY_AUDITS)
    run_in_process(POST_AUDITS)
finally:
    cleanup_shared_caches()

print("semantic audit suite ok")
