#!/usr/bin/env python3
"""Require the isolated pilot's response-lock and preanswer-policy barrier."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[1]
CHECKER = ROOT / "cloudtainer/tools/check_oq0266_isolated_semantic_pilot.py"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "cloudtainer/tools"))

from oq0266_isolated_response_set_lib import (  # type: ignore  # noqa: E402
    RESPONSE_SET_CONTRACT_VERSION,
)
from oq0266_isolated_run_bundle_lib import (  # type: ignore  # noqa: E402
    RUN_BUNDLE_CONTRACT_VERSION,
)
from oq0266_isolated_scoring_policy_lib import (  # type: ignore  # noqa: E402
    POLICY_VERIFICATION_CONTRACT_VERSION,
    SCORING_POLICY_CONTRACT_VERSION,
)

EXPECTED_POSITIVE_CANARIES = {
    "cross-machine-clock-skew-accepted",
    "self-contained-capsule-replay-without-ambient-pilot-files",
    "postassembly-source-score-mutation-isolated",
    "separately-pinned-outer-digest-accepted",
}

EXPECTED_CANARIES = {
    "responder-bundle-mapping-leak",
    "prefreeze-dispatch-postfreeze-leak",
    "incomplete-response-set-lock",
    "missing-custody-prerequisite-receipt",
    "substituted-custody-prerequisite-receipt",
    "response-set-lock-substitution",
    "postresponse-plan-commitment-substitution",
    "postresponse-scorer-policy-substitution-self-score",
    "responder-stimulus-and-runtime-hash-substitution",
    "duplicate-responder-batch",
    "strict-json-exponent-overflow",
    "postassembly-score-member-replacement",
    "whole-capsule-replacement-against-preserved-digest",
    "unsafe-nested-zip-member",
}


def fail(message: str) -> int:
    print(f"check_oq0266_isolated_batch_barrier_contract: FAIL: {message}")
    return 1


def main() -> int:
    if not CHECKER.exists():
        return fail(f"missing executable pilot checker: {CHECKER.relative_to(ROOT)}")
    result = subprocess.run(
        [sys.executable, "-S", str(CHECKER), "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode:
        return fail(
            f"pilot checker returned {result.returncode}; stdout={result.stdout!r}; stderr={result.stderr!r}"
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return fail(f"pilot checker did not emit JSON: {exc}")
    if payload.get("ok") is not True:
        return fail(f"pilot checker did not report ok: {payload}")
    if payload.get("response_set_contract_version") != RESPONSE_SET_CONTRACT_VERSION:
        return fail("response-set contract version drifted")
    if payload.get("scoring_policy_contract_version") != SCORING_POLICY_CONTRACT_VERSION:
        return fail("preanswer scoring-policy contract version drifted")
    if payload.get("policy_verification_contract_version") != POLICY_VERIFICATION_CONTRACT_VERSION:
        return fail("postfreeze policy-verification contract version drifted")
    if payload.get("run_bundle_contract_version") != RUN_BUNDLE_CONTRACT_VERSION:
        return fail("final evidence-capsule contract version drifted")
    if payload.get("batch_barrier_state") != (
        "all-four-responses-hash-locked-policy-receipt-bound-source-kits-and-final-triplets-content-bundled"
    ):
        return fail("batch barrier state drifted")
    observed_positive = set(payload.get("positive_canaries", []))
    missing_positive = sorted(EXPECTED_POSITIVE_CANARIES - observed_positive)
    if missing_positive:
        return fail(f"pilot checker omitted required positive canaries: {missing_positive}")
    observed = set(payload.get("negative_canaries", []))
    missing = sorted(EXPECTED_CANARIES - observed)
    if missing:
        return fail(f"pilot checker omitted required negative canaries: {missing}")
    if payload.get("global_compact_gate_confirmed") is not False:
        return fail("synthetic pilot improperly claimed global compact-gate confirmation")
    print(
        "check_oq0266_isolated_batch_barrier_contract: OK "
        f"({payload.get('arm_count')} arms; {len(observed)} negative canaries)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
