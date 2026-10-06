#!/usr/bin/env python3
"""End-to-end canary for the blinded OQ-0266 isolated semantic pilot.

The checker proves the runnable package boundary rather than merely inspecting
metadata.  It opens only the prefreeze dispatch kit, freezes all four synthetic
responses into one response-set lock, opens the postfreeze kit afterward, and
then executes custody, scoring, and aggregation.  It also attacks the batch
barrier, artifact bindings, and responder-separation rules.  All synthetic
content stays in a temporary directory and is explicitly non-evidence.
"""
from __future__ import annotations

import argparse
import copy
from datetime import timedelta
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile
from typing import Any

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
PILOT = ROOT / "cloudtainer/oq0266-isolated-semantic-pilot"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "cloudtainer/tools"))

from oq0266_isolated_commitment_lib import (  # type: ignore  # noqa: E402
    CommitmentContractError,
    responder_packet_projection_sha256,
)
from oq0266_isolated_response_set_lib import (  # type: ignore  # noqa: E402
    RESPONSE_SET_CONTRACT_VERSION,
    ResponseSetContractError,
    validate_dispatch_manifest,
)
from oq0266_isolated_run_bundle_lib import (  # type: ignore  # noqa: E402
    RUN_BUNDLE_CONTRACT_VERSION,
    RUN_MANIFEST_MEMBER,
    load_run_bundle,
    score_sheet_member,
)
from oq0266_isolated_scoring_policy_lib import (  # type: ignore  # noqa: E402
    POLICY_VERIFICATION_CONTRACT_VERSION,
    SCORING_POLICY_CONTRACT_VERSION,
    ScoringPolicyContractError,
    validate_policy_commitment,
    validate_scorer_against_policy,
    validate_scoring_policy,
)
from priority_zero_external_run_artifact_lib import (  # type: ignore  # noqa: E402
    ExternalRunArtifactError,
    parse_timestamp,
    strict_json_bytes,
)

BATCH_SCORER_REL = "cloudtainer/tools/score_oq0266_isolated_semantic_pilot.py"
RESPONSE_SET_LOCK_TOOL = "cloudtainer/tools/lock_oq0266_isolated_response_set.py"
RESPONSE_SET_LIB = "cloudtainer/tools/oq0266_isolated_response_set_lib.py"
RESPONSE_TOOL = "tools/prepare_priority_zero_external_replay_response.py"
CUSTODY_TOOL = "tools/prepare_priority_zero_clean_response_custody_record.py"
SCORE_TOOL = "tools/prepare_priority_zero_external_replay_score_sheet.py"
RUN_MANIFEST_TOOL = "cloudtainer/tools/prepare_oq0266_isolated_run_manifest.py"
RUN_BUNDLE_LIB = "cloudtainer/tools/oq0266_isolated_run_bundle_lib.py"
CAUSAL_LIB = "tools/priority_zero_causal_artifact_lib.py"
DISPATCH_REL = "cloudtainer/oq0266-isolated-semantic-pilot/dispatch-manifest.json"
COMMITMENT_REL = "cloudtainer/oq0266-isolated-semantic-pilot/assignment-commitment.json"
PLAN_REL = "cloudtainer/oq0266-isolated-semantic-pilot/assignment-plan.json"
POLICY_REL = "cloudtainer/oq0266-isolated-semantic-pilot/scoring-policy.json"
PREFREEZE_README_REL = "cloudtainer/oq0266-isolated-semantic-pilot/PREFREEZE-README.md"
POLICY_VERIFY_TOOL = "cloudtainer/tools/verify_oq0266_isolated_postfreeze_policy.py"
SCORING_POLICY_LIB = "cloudtainer/tools/oq0266_isolated_scoring_policy_lib.py"
COMMITMENT_LIB = "cloudtainer/tools/oq0266_isolated_commitment_lib.py"
ARTIFACT_LIB = "tools/priority_zero_external_run_artifact_lib.py"
RESPONSE_LIB = "tools/priority_zero_external_replay_response_lib.py"
REQUIRED_ANSWER_FIELDS = [
    "mission_heart",
    "oq_routing",
    "compact_gate_posture",
    "waste_or_refactor_implicated",
    "next_safe_action",
    "abstentions",
    "uncertainty_or_conflicts",
]
FORBIDDEN_RESPONDER_FRAGMENTS = [
    '"answer_key"',
    '"true_variant"',
    '"expected_score"',
    '"source_packet_label"',
    '"analysis_variant"',
    "packet-alpha",
    "packet-bravo",
    "packet-charlie",
    "packet-delta",
    "/assignment-plan.json",
    "/scorer-intake.json",
    "/custody-template.json",
]
MAPPING_LABELS = ["packet-alpha", "packet-bravo", "packet-charlie", "packet-delta"]


class PilotCheckError(RuntimeError):
    pass


def load(path: pathlib.Path) -> dict[str, Any]:
    value = strict_json_bytes(path.read_bytes(), str(path))
    if not isinstance(value, dict):
        raise PilotCheckError(f"{path} must contain a JSON object")
    return value


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rewrite_zip_members(path: pathlib.Path, replacements: dict[str, bytes]) -> None:
    """Rewrite selected members while preserving the original member order."""
    with zipfile.ZipFile(path) as source:
        infos = source.infolist()
        observed = [info.filename for info in infos]
        missing = sorted(set(replacements) - set(observed))
        if missing:
            raise PilotCheckError(f"ZIP rewrite targets were absent from {path}: {missing}")
        payloads = {
            info.filename: replacements.get(info.filename, source.read(info.filename))
            for info in infos
        }
        archive_comment = source.comment
    temporary = path.with_name(path.name + ".rewrite-tmp")
    try:
        with zipfile.ZipFile(temporary, "w") as target:
            target.comment = archive_comment
            for info in infos:
                target.writestr(info, payloads[info.filename])
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def run_expect_failure(
    command: list[str],
    *,
    cwd: pathlib.Path,
    expected_fragment: str,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode == 0:
        raise PilotCheckError(
            f"negative canary unexpectedly passed in {cwd}: {' '.join(command)}"
        )
    combined = result.stdout + "\n" + result.stderr
    if expected_fragment not in combined:
        raise PilotCheckError(
            f"negative canary failed for the wrong reason; expected {expected_fragment!r}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result



def copy_zip_with_extra_member(
    source: pathlib.Path,
    destination: pathlib.Path,
    member_name: str,
    payload: bytes,
) -> None:
    """Copy a ZIP byte-for-byte by member and append one adversarial entry."""
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        members = [(info, archive.read(info.filename)) for info in infos]
    with zipfile.ZipFile(destination, "w") as archive:
        for info, raw in members:
            clone = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            clone.compress_type = info.compress_type
            clone.create_system = info.create_system
            clone.external_attr = info.external_attr
            archive.writestr(clone, raw)
        attack = zipfile.ZipInfo(member_name, date_time=(1980, 1, 1, 0, 0, 0))
        attack.compress_type = zipfile.ZIP_STORED
        attack.create_system = 3
        attack.external_attr = (0o100444 << 16)
        archive.writestr(attack, payload)

def run(command: list[str], *, cwd: pathlib.Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**__import__("os").environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode:
        raise PilotCheckError(
            f"command failed ({result.returncode}) in {cwd}: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def fill_response_draft(path: pathlib.Path, *, arm: str, cost: float) -> None:
    data = load(path)
    rows = data["responder_stage"]["packet_answers"]
    if len(rows) != 1 or rows[0].get("label") != arm:
        raise PilotCheckError(f"{arm} response draft did not contain exactly its opaque row")
    row = rows[0]
    row["operator_cost_minutes"] = cost
    for field in REQUIRED_ANSWER_FIELDS:
        row[field] = f"synthetic non-evidence checker answer for {arm}: {field}"
    data["responder_stage"]["operator_cost_minutes"] = cost
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fill_score_draft(path: pathlib.Path, *, arm: str, target: int) -> None:
    data = load(path)
    rows = data["manual_metric_scores"]
    if len(rows) != 1 or rows[0].get("label") != arm:
        raise PilotCheckError(f"{arm} score draft did not contain exactly its opaque row")
    row = rows[0]
    remaining = target
    for metric in row["metric_scores"]:
        value = min(2, remaining)
        row["metric_scores"][metric] = value
        remaining -= value
        row["metric_rationales"][metric] = f"synthetic non-evidence rationale for {metric}"
    if remaining:
        raise PilotCheckError(f"cannot distribute target score {target} across metric maxima")
    row["notes"] = "synthetic package canary only; not external scoring"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _expected_prefreeze_members(dispatch: dict[str, Any]) -> list[str]:
    return [
        DISPATCH_REL,
        COMMITMENT_REL,
        PREFREEZE_README_REL,
        RESPONSE_SET_LOCK_TOOL,
        RESPONSE_SET_LIB,
        POLICY_VERIFY_TOOL,
        SCORING_POLICY_LIB,
        COMMITMENT_LIB,
        CAUSAL_LIB,
        ARTIFACT_LIB,
        RESPONSE_LIB,
        *[row["responder_bundle_surface"] for row in dispatch["arms"]],
    ]


def verify_static() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    assignment_path = PILOT / "assignment-plan.json"
    commitment_path = PILOT / "assignment-commitment.json"
    dispatch_path = PILOT / "dispatch-manifest.json"
    receipt_path = PILOT / "build-receipt.json"
    batch_manifest_path = PILOT / "batch-manifest.json"
    policy_path = PILOT / "scoring-policy.json"
    assignment = load(assignment_path)
    commitment = load(commitment_path)
    dispatch = load(dispatch_path)
    receipt = load(receipt_path)
    batch_manifest = load(batch_manifest_path)
    policy = load(policy_path)

    assignment_sha = sha256(assignment_path)
    commitment_sha = sha256(commitment_path)
    dispatch_sha = sha256(dispatch_path)
    policy_sha = sha256(policy_path)
    if commitment.get("assignment_plan_sha256") != assignment_sha:
        raise PilotCheckError("assignment plan no longer matches its responder-visible commitment")
    try:
        committed_packet_projections = validate_policy_commitment(
            commitment,
            assignment_plan_sha256=assignment_sha,
            scoring_policy_sha256=policy_sha,
        )
        policy_by_arm, _ = validate_scoring_policy(
            policy,
            assignment,
            assignment_plan_sha256=assignment_sha,
            root=ROOT,
        )
    except ScoringPolicyContractError as exc:
        raise PilotCheckError(f"preanswer scoring policy failed strict validation: {exc}") from exc
    if receipt.get("assignment_plan_sha256") != assignment_sha:
        raise PilotCheckError("build receipt assignment plan hash drifted")
    if receipt.get("scoring_policy_sha256") != policy_sha:
        raise PilotCheckError("build receipt scoring policy hash drifted")
    if receipt.get("assignment_commitment_sha256") != commitment_sha:
        raise PilotCheckError("build receipt assignment commitment hash drifted")
    if receipt.get("dispatch_manifest_sha256") != dispatch_sha:
        raise PilotCheckError("build receipt dispatch manifest hash drifted")
    if batch_manifest.get("assignment_plan_sha256") != assignment_sha:
        raise PilotCheckError("batch manifest assignment plan hash drifted")
    if batch_manifest.get("scoring_policy_sha256") != policy_sha:
        raise PilotCheckError("batch manifest scoring policy hash drifted")
    if batch_manifest.get("scoring_policy_contract_version") != SCORING_POLICY_CONTRACT_VERSION:
        raise PilotCheckError("batch manifest scoring policy contract version drifted")
    if batch_manifest.get("policy_verification_contract_version") != POLICY_VERIFICATION_CONTRACT_VERSION:
        raise PilotCheckError("batch manifest policy verification contract version drifted")
    if batch_manifest.get("assignment_commitment_sha256") != commitment_sha:
        raise PilotCheckError("batch manifest assignment commitment hash drifted")
    if batch_manifest.get("dispatch_manifest_sha256") != dispatch_sha:
        raise PilotCheckError("batch manifest dispatch manifest hash drifted")
    if receipt.get("response_set_contract_version") != RESPONSE_SET_CONTRACT_VERSION:
        raise PilotCheckError("build receipt response-set contract version drifted")
    if batch_manifest.get("response_set_contract_version") != RESPONSE_SET_CONTRACT_VERSION:
        raise PilotCheckError("batch manifest response-set contract version drifted")

    if receipt.get("run_bundle_contract_version") != RUN_BUNDLE_CONTRACT_VERSION:
        raise PilotCheckError("build receipt run-bundle contract version drifted")
    if batch_manifest.get("run_bundle_contract_version") != RUN_BUNDLE_CONTRACT_VERSION:
        raise PilotCheckError("batch manifest run-bundle contract version drifted")

    try:
        dispatch_by_arm = validate_dispatch_manifest(
            dispatch,
            assignment_commitment_sha256=commitment_sha,
            responder_packet_projection_sha256_by_arm=committed_packet_projections,
        )
    except ResponseSetContractError as exc:
        raise PilotCheckError(f"dispatch manifest failed strict validation: {exc}") from exc
    assignment_by_arm = {row["arm_code"]: row for row in assignment.get("arms", [])}
    batch_by_arm = {row["arm_code"]: row for row in batch_manifest.get("arms", [])}
    if len(assignment_by_arm) != 4 or len(batch_by_arm) != 4:
        raise PilotCheckError("isolated pilot must contain exactly four unique arms")
    if set(dispatch_by_arm) != set(assignment_by_arm) or set(dispatch_by_arm) != set(batch_by_arm):
        raise PilotCheckError("dispatch, assignment, and batch arm sets disagree")

    receipt_bundles = receipt.get("responder_bundle_sha256_by_arm", {})
    for arm, row in batch_by_arm.items():
        dispatch_row = dispatch_by_arm[arm]
        bundle = ROOT / row["responder_bundle_surface"]
        digest = sha256(bundle)
        if (
            digest != row["responder_bundle_sha256"]
            or digest != dispatch_row["responder_bundle_sha256"]
            or digest != receipt_bundles.get(arm)
        ):
            raise PilotCheckError(f"{arm} responder bundle hash drifted")
        with zipfile.ZipFile(bundle) as archive:
            if archive.testzip() is not None:
                raise PilotCheckError(f"{arm} responder bundle failed ZIP integrity")
            members = archive.namelist()
            if members != row["responder_bundle_members"] or members != dispatch_row["responder_bundle_members"]:
                raise PilotCheckError(f"{arm} responder bundle topology drifted")
            visible = b"\n".join(archive.read(name) for name in members).decode("utf-8")
        for fragment in FORBIDDEN_RESPONDER_FRAGMENTS:
            if fragment in visible:
                raise PilotCheckError(
                    f"{arm} responder bundle leaked post-freeze mapping/scorer fragment: {fragment}"
                )
        if visible.count(arm) == 0:
            raise PilotCheckError(f"{arm} responder bundle does not identify its own opaque arm")
        with zipfile.ZipFile(bundle) as archive:
            packet_raw = archive.read(row["responder_packet_surface"])
        packet = strict_json_bytes(packet_raw, f"{arm} responder packet")
        packet_projection_sha = responder_packet_projection_sha256(packet)
        if packet_projection_sha != committed_packet_projections[arm]:
            raise PilotCheckError(
                f"{arm} responder-visible packet projection drifted from preanswer commitment"
            )
        if dispatch_row.get("responder_packet_projection_sha256") != packet_projection_sha:
            raise PilotCheckError(f"{arm} dispatch packet projection hash drifted")
        scorer_path = ROOT / row["scorer_intake_surface"]
        scorer = load(scorer_path)
        if sha256(scorer_path) != row.get("scorer_intake_sha256"):
            raise PilotCheckError(f"{arm} scorer intake hash drifted from batch manifest")
        try:
            validate_scorer_against_policy(
                scorer,
                expected_policy=policy_by_arm[arm],
                arm=arm,
                scoring_policy_surface=POLICY_REL,
                scoring_policy_sha256=policy_sha,
            )
        except ScoringPolicyContractError as exc:
            raise PilotCheckError(f"{arm} scorer drifted from preanswer policy: {exc}") from exc

    prefreeze = PILOT / "prefreeze-dispatch-kit.zip"
    prefreeze_digest = sha256(prefreeze)
    if receipt.get("prefreeze_dispatch_kit_sha256") != prefreeze_digest:
        raise PilotCheckError("prefreeze dispatch kit hash drifted from build receipt")
    if batch_manifest.get("prefreeze_dispatch_kit_sha256") != prefreeze_digest:
        raise PilotCheckError("prefreeze dispatch kit hash drifted from batch manifest")
    with zipfile.ZipFile(prefreeze) as archive:
        if archive.testzip() is not None:
            raise PilotCheckError("prefreeze dispatch kit failed ZIP integrity")
        names = archive.namelist()
        expected_names = _expected_prefreeze_members(dispatch)
        if names != expected_names:
            raise PilotCheckError(
                f"prefreeze dispatch topology drifted: observed={names} expected={expected_names}"
            )
        if archive.read(DISPATCH_REL) != dispatch_path.read_bytes():
            raise PilotCheckError("prefreeze dispatch kit contains different dispatch bytes")
        if archive.read(COMMITMENT_REL) != commitment_path.read_bytes():
            raise PilotCheckError("prefreeze dispatch kit contains different commitment bytes")
        for arm, row in dispatch_by_arm.items():
            outer_bundle = ROOT / row["responder_bundle_surface"]
            if archive.read(row["responder_bundle_surface"]) != outer_bundle.read_bytes():
                raise PilotCheckError(f"prefreeze kit nested {arm} responder ZIP differs from outer ZIP")
        prefreeze_readme = archive.read(PREFREEZE_README_REL).decode("utf-8")
        lock_tool_source = archive.read(RESPONSE_SET_LOCK_TOOL).decode("utf-8")
        response_set_source = archive.read(RESPONSE_SET_LIB).decode("utf-8")
        policy_verify_source = archive.read(POLICY_VERIFY_TOOL).decode("utf-8")
        policy_lib_source = archive.read(SCORING_POLICY_LIB).decode("utf-8")
        commitment_lib_source = archive.read(COMMITMENT_LIB).decode("utf-8")
        if POLICY_REL in names:
            raise PilotCheckError("prefreeze dispatch kit exposed scoring-policy content")
    for label in MAPPING_LABELS:
        if any(
            label in surface
            for surface in [
                prefreeze_readme,
                lock_tool_source,
                response_set_source,
                policy_verify_source,
                policy_lib_source,
                commitment_lib_source,
            ]
        ):
            raise PilotCheckError(f"prefreeze dispatch kit leaked concrete assignment label {label}")
    lowered_readme = prefreeze_readme.lower()
    if (
        PLAN_REL in prefreeze_readme
        or "assignment plan" not in lowered_readme
        or "postfreeze kit" not in lowered_readme
        or "after all four" not in lowered_readme
    ):
        raise PilotCheckError("prefreeze README does not state the assignment/postfreeze visibility boundary")
    if "score_oq0266_isolated_semantic_pilot" in lock_tool_source:
        raise PilotCheckError("prefreeze lock tool imports or names the postfreeze batch scorer")
    if "prepare_priority_zero_clean_response_custody_record" in lock_tool_source:
        raise PilotCheckError("prefreeze lock tool imports or names the custody helper")
    if "DEFAULT_PLAN" in lock_tool_source or "assignment-plan.json" in lock_tool_source:
        raise PilotCheckError("prefreeze lock tool contains an assignment-plan default or path")

    postfreeze = PILOT / "postfreeze-batch-kit.zip"
    postfreeze_digest = sha256(postfreeze)
    if receipt.get("postfreeze_batch_kit_sha256") != postfreeze_digest:
        raise PilotCheckError("postfreeze batch kit hash drifted")
    with zipfile.ZipFile(postfreeze) as archive:
        if archive.testzip() is not None:
            raise PilotCheckError("postfreeze batch kit failed ZIP integrity")
        names = set(archive.namelist())
        if archive.read(DISPATCH_REL) != dispatch_path.read_bytes():
            raise PilotCheckError("postfreeze kit contains different dispatch bytes")
    required = {
        PLAN_REL,
        COMMITMENT_REL,
        DISPATCH_REL,
        "cloudtainer/oq0266-isolated-semantic-pilot/batch-manifest.json",
        BATCH_SCORER_REL,
        RESPONSE_SET_LIB,
        POLICY_REL,
        POLICY_VERIFY_TOOL,
        SCORING_POLICY_LIB,
        COMMITMENT_LIB,
        CAUSAL_LIB,
        RUN_MANIFEST_TOOL,
        RUN_BUNDLE_LIB,
        "cloudtainer/oq0266-isolated-semantic-pilot/run-manifest-template.json",
        CUSTODY_TOOL,
        SCORE_TOOL,
        "tools/score_priority_zero_external_replay_response.py",
        "tools/priority_zero_external_replay_custody_lib.py",
    }
    if not required.issubset(names):
        raise PilotCheckError(f"postfreeze kit missing required members: {sorted(required - names)}")
    return assignment, batch_manifest, dispatch


def _response_command_args(response_paths: dict[str, pathlib.Path]) -> list[str]:
    values: list[str] = []
    for arm in sorted(response_paths):
        values.extend(["--response", f"{arm}={response_paths[arm]}"])
    return values


def _batch_command(
    *,
    run_bundle: pathlib.Path,
    expected_digest: str | None = None,
) -> list[str]:
    return [
        sys.executable,
        "-S",
        BATCH_SCORER_REL,
        "--run-bundle",
        str(run_bundle),
        "--expected-run-bundle-sha256",
        expected_digest or sha256(run_bundle),
    ]


def _run_manifest_command(
    *,
    prefreeze_kit: pathlib.Path,
    postfreeze_kit: pathlib.Path,
    response_set_lock: pathlib.Path,
    policy_verification: pathlib.Path,
    rows: list[dict[str, str]],
    out: pathlib.Path,
) -> list[str]:
    command = [
        sys.executable,
        "-S",
        RUN_MANIFEST_TOOL,
        "--prefreeze-dispatch-kit",
        str(prefreeze_kit),
        "--postfreeze-batch-kit",
        str(postfreeze_kit),
        "--response-set-lock",
        str(response_set_lock),
        "--policy-verification",
        str(policy_verification),
    ]
    for row in rows:
        command.extend(["--response", f"{row['arm_code']}={row['response_file']}"])
    for row in rows:
        command.extend(
            ["--evidence-record", f"{row['arm_code']}={row['evidence_record_file']}"]
        )
    for row in rows:
        command.extend(["--score-sheet", f"{row['arm_code']}={row['score_sheet_file']}"])
    command.extend(["--out", str(out)])
    return command


def run_end_to_end(
    assignment: dict[str, Any],
    batch_manifest: dict[str, Any],
    dispatch: dict[str, Any],
) -> dict[str, Any]:
    try:
        strict_json_bytes(b'{"overflow":1e999}', "strict JSON overflow canary")
    except ExternalRunArtifactError:
        pass
    else:
        raise PilotCheckError("strict JSON parser accepted exponent overflow as infinity")

    temp = pathlib.Path(tempfile.mkdtemp(prefix="delaybasin-oq0266-isolated-canary-"))
    try:
        prefreeze_source_kit = temp / "original-prefreeze-dispatch-kit.zip"
        postfreeze_source_kit = temp / "original-postfreeze-batch-kit.zip"
        shutil.copyfile(PILOT / "prefreeze-dispatch-kit.zip", prefreeze_source_kit)
        shutil.copyfile(PILOT / "postfreeze-batch-kit.zip", postfreeze_source_kit)

        pref = temp / "prefreeze"
        with zipfile.ZipFile(prefreeze_source_kit) as archive:
            archive.extractall(pref)

        manifest_by_arm = {row["arm_code"]: row for row in batch_manifest["arms"]}
        response_paths: dict[str, pathlib.Path] = {}
        for index, plan_row in enumerate(assignment["arms"], start=1):
            arm = plan_row["arm_code"]
            manifest_row = manifest_by_arm[arm]
            nested_bundle = pref / manifest_row["responder_bundle_surface"]
            responder_root = temp / f"responder-{arm}"
            with zipfile.ZipFile(nested_bundle) as archive:
                archive.extractall(responder_root)
            base = f"cloudtainer/oq0266-isolated-semantic-pilot/arms/{arm}"
            packet = f"{base}/responder-packet.json"
            response_template = f"{base}/response-template.json"
            draft = temp / f"{arm}-response-draft.json"
            response = temp / f"{arm}-response-final.json"
            run(
                [
                    sys.executable,
                    "-S",
                    RESPONSE_TOOL,
                    "init",
                    "--bundle-file",
                    str(nested_bundle),
                    "--responder-id",
                    f"synthetic-responder-{index}",
                    "--template",
                    response_template,
                    "--packet",
                    packet,
                    "--out",
                    str(draft),
                ],
                cwd=responder_root,
            )
            fill_response_draft(draft, arm=arm, cost=float(index))
            run(
                [
                    sys.executable,
                    "-S",
                    RESPONSE_TOOL,
                    "finalize",
                    "--draft",
                    str(draft),
                    "--bundle-file",
                    str(nested_bundle),
                    "--template",
                    response_template,
                    "--packet",
                    packet,
                    "--exposure-notes",
                    "synthetic canary: only the named one-arm responder bundle was visible",
                    "--attest-clean-preanswer",
                    "--out",
                    str(response),
                ],
                cwd=responder_root,
            )
            response_paths[arm] = response

        # Positive skew canary: one responder machine reports a finalization
        # time fifteen minutes ahead of the collector.  The exact response bytes
        # must remain admissible because cross-machine wall clocks are not a
        # trustworthy causal ordering mechanism.
        skewed_arm = assignment["arms"][0]["arm_code"]
        skewed_path = response_paths[skewed_arm]
        skewed_response = load(skewed_path)
        finalized_text = skewed_response["response_artifact"]["finalized_at"]
        _, finalized_at = parse_timestamp(finalized_text, "clock-skew canary finalized_at")
        skewed_finalized_text = (finalized_at + timedelta(minutes=15)).isoformat()
        skewed_response["response_artifact"]["finalized_at"] = skewed_finalized_text
        skewed_response["responder_stage"]["run_completed_at"] = skewed_finalized_text
        skewed_path.chmod(0o644)
        skewed_path.write_text(
            json.dumps(skewed_response, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        skewed_path.chmod(0o444)

        lock_base_command = [
            sys.executable,
            "-S",
            RESPONSE_SET_LOCK_TOOL,
            "--collector-id",
            "synthetic-collector",
            "--exposure-notes",
            "synthetic canary: only prefreeze dispatch materials and four finalized responses were visible",
            "--attest-clean-batch-barrier",
            "--dispatch-manifest",
            DISPATCH_REL,
            "--commitment",
            COMMITMENT_REL,
        ]

        # Reproduce the rev0384 stimulus-substitution bypass with a fully
        # matching responder artifact.  The attacker changes one responder's
        # visible packet, updates its template, bundle, and dispatch hashes,
        # and finalizes a response from that altered bundle.  Before the v2
        # commitment this could survive the complete pipeline because those
        # runtime hashes were not bound preanswer.  Current locking must reject
        # the changed packet projection before publishing a response-set lock.
        tampered_pref = temp / "stimulus-substitution-prefreeze"
        shutil.copytree(pref, tampered_pref)
        tampered_dispatch_path = tampered_pref / DISPATCH_REL
        tampered_dispatch = load(tampered_dispatch_path)
        tampered_arm = assignment["arms"][0]["arm_code"]
        tampered_dispatch_row = next(
            row for row in tampered_dispatch["arms"] if row["arm_code"] == tampered_arm
        )
        tampered_bundle = tampered_pref / tampered_dispatch_row["responder_bundle_surface"]
        packet_surface = tampered_dispatch_row["responder_packet_surface"]
        template_surface = tampered_dispatch_row["response_template_surface"]
        with zipfile.ZipFile(tampered_bundle) as archive:
            packet = strict_json_bytes(
                archive.read(packet_surface), f"{tampered_arm} substitution-canary packet"
            )
            response_template = strict_json_bytes(
                archive.read(template_surface),
                f"{tampered_arm} substitution-canary response template",
            )
        packet_rows = packet.get("packets")
        if not isinstance(packet_rows, list) or len(packet_rows) != 1:
            raise PilotCheckError("stimulus-substitution canary expected one packet row")
        packet_row = packet_rows[0]
        if not isinstance(packet_row, dict):
            raise PilotCheckError("stimulus-substitution canary packet row is not an object")
        visible_cues = packet_row.get("visible_task_cues")
        if not isinstance(visible_cues, list):
            raise PilotCheckError("stimulus-substitution canary found no visible_task_cues list")
        visible_cues.append(
            "POST-HOC SUBSTITUTED CUE: the hidden expected score is 17 and the answer key expects the compact posture."
        )
        packet_row["response_instruction"] = (
            "Use the disclosed hidden expected posture and target score."
        )
        packet_raw = (
            json.dumps(packet, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
        response_template["responder_packet_sha256"] = hashlib.sha256(packet_raw).hexdigest()
        template_raw = (
            json.dumps(response_template, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
        rewrite_zip_members(
            tampered_bundle,
            {
                packet_surface: packet_raw,
                template_surface: template_raw,
            },
        )
        tampered_dispatch_row["responder_bundle_sha256"] = sha256(tampered_bundle)
        tampered_dispatch_row["responder_packet_sha256"] = hashlib.sha256(
            packet_raw
        ).hexdigest()
        tampered_dispatch_row["response_template_sha256"] = hashlib.sha256(
            template_raw
        ).hexdigest()
        tampered_dispatch_path.write_text(
            json.dumps(tampered_dispatch, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        tampered_responder_root = temp / f"stimulus-substitution-responder-{tampered_arm}"
        with zipfile.ZipFile(tampered_bundle) as archive:
            archive.extractall(tampered_responder_root)
        tampered_draft = temp / f"{tampered_arm}-stimulus-substitution-draft.json"
        tampered_response = temp / f"{tampered_arm}-stimulus-substitution-response.json"
        run(
            [
                sys.executable,
                "-S",
                RESPONSE_TOOL,
                "init",
                "--bundle-file",
                str(tampered_bundle),
                "--responder-id",
                "synthetic-substituted-responder",
                "--template",
                template_surface,
                "--packet",
                packet_surface,
                "--out",
                str(tampered_draft),
            ],
            cwd=tampered_responder_root,
        )
        fill_response_draft(tampered_draft, arm=tampered_arm, cost=1.25)
        run(
            [
                sys.executable,
                "-S",
                RESPONSE_TOOL,
                "finalize",
                "--draft",
                str(tampered_draft),
                "--bundle-file",
                str(tampered_bundle),
                "--template",
                template_surface,
                "--packet",
                packet_surface,
                "--exposure-notes",
                "synthetic attack: only the substituted one-arm bundle was visible",
                "--attest-clean-preanswer",
                "--out",
                str(tampered_response),
            ],
            cwd=tampered_responder_root,
        )
        tampered_response_paths = dict(response_paths)
        tampered_response_paths[tampered_arm] = tampered_response
        tampered_lock = temp / "stimulus-substitution-response-set-lock.json"
        run_expect_failure(
            lock_base_command
            + _response_command_args(tampered_response_paths)
            + ["--out", str(tampered_lock)],
            cwd=tampered_pref,
            expected_fragment=(
                f"{tampered_arm} responder packet projection disagrees with the preanswer commitment"
            ),
        )
        if tampered_lock.exists():
            raise PilotCheckError("stimulus-substitution canary published a lock")

        incomplete_lock = temp / "incomplete-response-set-lock.json"
        incomplete_args: list[str] = []
        for arm in sorted(response_paths)[:3]:
            incomplete_args.extend(["--response", f"{arm}={response_paths[arm]}"])
        run_expect_failure(
            lock_base_command + incomplete_args + ["--out", str(incomplete_lock)],
            cwd=pref,
            expected_fragment="exactly 4 --response ARM=PATH values are required",
        )
        if incomplete_lock.exists():
            raise PilotCheckError("incomplete response-set canary published an output artifact")

        response_set_lock = temp / "response-set-lock.json"
        run(
            lock_base_command
            + _response_command_args(response_paths)
            + ["--out", str(response_set_lock)],
            cwd=pref,
        )
        lock_sha = sha256(response_set_lock)
        lock_data = load(response_set_lock)
        skewed_lock_row = next(
            row for row in lock_data["responses"] if row["arm_code"] == skewed_arm
        )
        _, remote_finalized = parse_timestamp(
            skewed_lock_row["response_finalized_at"],
            "clock-skew canary response_finalized_at",
        )
        _, collector_locked = parse_timestamp(
            lock_data["collector_attestation"]["response_set_locked_at"],
            "clock-skew canary response_set_locked_at",
        )
        if remote_finalized <= collector_locked:
            raise PilotCheckError(
                "clock-skew canary did not actually place responder time after collector lock"
            )

        # Only now may the postfreeze surface open.
        post = temp / "postfreeze"
        with zipfile.ZipFile(postfreeze_source_kit) as archive:
            archive.extractall(post)

        policy_verification = temp / "postfreeze-policy-verification.json"
        run(
            [
                sys.executable,
                "-S",
                POLICY_VERIFY_TOOL,
                "--response-set-lock",
                str(response_set_lock),
                "--postfreeze-root",
                str(post),
                "--verifier-id",
                "synthetic-policy-verifier",
                "--attest-postfreeze-opened-after-lock",
                "--out",
                str(policy_verification),
            ],
            cwd=pref,
        )
        policy_verification_sha = sha256(policy_verification)

        first_arm = assignment["arms"][0]["arm_code"]
        first_base = f"cloudtainer/oq0266-isolated-semantic-pilot/arms/{first_arm}"
        missing_prerequisite_out = temp / "missing-prerequisite-custody.json"
        run_expect_failure(
            [
                sys.executable,
                "-S",
                CUSTODY_TOOL,
                str(response_paths[first_arm]),
                "--custodian-id",
                "synthetic-missing-prerequisite-custodian",
                "--pre-response-exposure-notes",
                "synthetic canary: one named responder bundle only",
                "--attest-clean-preanswer",
                "--template",
                f"{first_base}/custody-template.json",
                "--response-template",
                f"{first_base}/response-template.json",
                "--out",
                str(missing_prerequisite_out),
            ],
            cwd=post,
            expected_fragment="required prerequisite labels/order drifted",
        )
        if missing_prerequisite_out.exists():
            raise PilotCheckError("missing-prerequisite custody canary published an artifact")

        run_rows: list[dict[str, str]] = []
        for plan_row in assignment["arms"]:
            arm = plan_row["arm_code"]
            target = int(plan_row["reference_expected_score"])
            base = f"cloudtainer/oq0266-isolated-semantic-pilot/arms/{arm}"
            response_template = f"{base}/response-template.json"
            custody_template = f"{base}/custody-template.json"
            score_template = f"{base}/score-sheet-template.json"
            scorer = f"{base}/scorer-intake.json"
            response = response_paths[arm]
            custody = temp / f"{arm}-custody-final.json"
            score_draft = temp / f"{arm}-score-draft.json"
            score = temp / f"{arm}-score-final.json"
            run(
                [
                    sys.executable,
                    "-S",
                    CUSTODY_TOOL,
                    str(response),
                    "--custodian-id",
                    "synthetic-custodian-scorer",
                    "--pre-response-exposure-notes",
                    "synthetic canary: one named responder bundle only",
                    "--prerequisite",
                    f"response-set-lock={response_set_lock}",
                    "--prerequisite",
                    f"postfreeze-policy-verification={policy_verification}",
                    "--attest-clean-preanswer",
                    "--template",
                    custody_template,
                    "--response-template",
                    response_template,
                    "--out",
                    str(custody),
                ],
                cwd=post,
            )
            run(
                [
                    sys.executable,
                    "-S",
                    SCORE_TOOL,
                    "init",
                    str(response),
                    str(custody),
                    "--scorer-id",
                    "synthetic-custodian-scorer",
                    "--scorer-intake",
                    scorer,
                    "--template",
                    score_template,
                    "--response-template",
                    response_template,
                    "--out",
                    str(score_draft),
                ],
                cwd=post,
            )
            fill_score_draft(score_draft, arm=arm, target=target)
            run(
                [
                    sys.executable,
                    "-S",
                    SCORE_TOOL,
                    "finalize",
                    str(response),
                    str(custody),
                    "--scorer-id",
                    "synthetic-custodian-scorer",
                    "--scorer-intake",
                    scorer,
                    "--template",
                    score_template,
                    "--response-template",
                    response_template,
                    "--draft",
                    str(score_draft),
                    "--scorer-notes",
                    "synthetic package canary only; not external evidence",
                    "--attest-separated-scoring",
                    "--out",
                    str(score),
                ],
                cwd=post,
            )
            run_rows.append(
                {
                    "arm_code": arm,
                    "response_file": str(response),
                    "evidence_record_file": str(custody),
                    "score_sheet_file": str(score),
                }
            )

        run_bundle_path = temp / "oq0266-isolated-run-bundle.zip"
        run(
            _run_manifest_command(
                prefreeze_kit=prefreeze_source_kit,
                postfreeze_kit=postfreeze_source_kit,
                response_set_lock=response_set_lock,
                policy_verification=policy_verification,
                rows=run_rows,
                out=run_bundle_path,
            ),
            cwd=post,
        )
        run_bundle_digest = sha256(run_bundle_path)
        loaded_bundle = load_run_bundle(
            run_bundle_path,
            expected_bundle_sha256=run_bundle_digest,
            expected_batch_id=assignment["batch_id"],
            expected_assignment_plan_sha256=sha256(post / PLAN_REL),
            expected_arm_codes={row["arm_code"] for row in assignment["arms"]},
        )
        scorer_command = _batch_command(
            run_bundle=run_bundle_path,
            expected_digest=run_bundle_digest,
        )
        result = run(scorer_command, cwd=post)
        summary = json.loads(result.stdout)
        if summary.get("distinct_responder_count") != 4:
            raise PilotCheckError("batch aggregator did not require four distinct responders")
        if summary.get("batch_barrier_state") != (
            "all-four-responses-hash-locked-policy-receipt-bound-source-kits-and-final-triplets-content-bundled"
        ):
            raise PilotCheckError("batch aggregator did not report the complete content-bundled barrier")
        if summary.get("run_bundle_sha256") != sha256(run_bundle_path):
            raise PilotCheckError("batch aggregator did not report the exact evidence-capsule hash")
        if summary.get("run_bundle_manifest_sha256") != loaded_bundle.manifest_sha256:
            raise PilotCheckError("batch aggregator did not report the internal run-manifest hash")
        if summary.get("outer_digest_binding_state") != (
            "matched-separately-supplied-sha256-before-capsule-interpretation"
        ):
            raise PilotCheckError("batch aggregator did not enforce the separately preserved outer digest")
        if summary.get("source_kit_replay_state") != (
            "exact-prefreeze-and-postfreeze-kits-validated-from-capsule"
        ):
            raise PilotCheckError("batch aggregator did not replay exact source kits from the capsule")
        if summary.get("postfreeze_policy_verification", {}).get("verification_state") != (
            "postfreeze-policy-matches-preanswer-commitment"
        ):
            raise PilotCheckError("batch aggregator did not report verified preanswer scoring policy")
        lock_summary = summary.get("response_set_lock", {})
        if lock_summary.get("response_count") != 4 or lock_summary.get("distinct_responder_count") != 4:
            raise PilotCheckError("batch aggregator did not bind all four response-set rows")
        decision = summary.get("decision", {})
        if decision.get("decision_state") != "support-isolated-semantic-recovery-pilot":
            raise PilotCheckError(f"positive synthetic batch reached unexpected decision: {decision}")
        if decision.get("global_compact_gate_confirmed") is not False:
            raise PilotCheckError("isolated pilot improperly claimed global compact-gate confirmation")
        if not str(decision.get("operator_cost_inference_state", "")).startswith("descriptive-only"):
            raise PilotCheckError(
                "isolated pilot improperly treated between-responder cost as causal burden evidence"
            )

        # The run bundle is the final freeze boundary.  Mutating a source score
        # after assembly must not alter the accepted result because the scorer
        # reads only the exact member bytes captured inside the bundle.
        compact_arm = next(
            row["arm_code"] for row in assignment["arms"] if row["analysis_variant"] == "compact"
        )
        compact_source_row = next(row for row in run_rows if row["arm_code"] == compact_arm)
        compact_source_score = pathlib.Path(compact_source_row["score_sheet_file"])
        original_compact_score = compact_source_score.read_bytes()
        compact_score_data = strict_json_bytes(
            original_compact_score, "postassembly source-score mutation canary"
        )
        for metric in compact_score_data["manual_metric_scores"][0]["metric_scores"]:
            compact_score_data["manual_metric_scores"][0]["metric_scores"][metric] = 0
        compact_source_score.chmod(0o644)
        compact_source_score.write_text(
            json.dumps(compact_score_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        isolated_result = run(scorer_command, cwd=post)
        isolated_summary = json.loads(isolated_result.stdout)
        if isolated_summary["decision"] != summary["decision"]:
            raise PilotCheckError(
                "postassembly source score mutation changed the content-bundled decision"
            )
        if isolated_summary.get("run_bundle_sha256") != summary.get("run_bundle_sha256"):
            raise PilotCheckError("postassembly source mutation changed the reported run-bundle identity")
        compact_source_score.write_bytes(original_compact_score)
        compact_source_score.chmod(0o444)

        # Changing a score member inside a copied bundle without updating the
        # internal checksum manifest must fail before any score is interpreted.
        tampered_bundle_path = temp / "tampered-score-member-run-bundle.zip"
        shutil.copyfile(run_bundle_path, tampered_bundle_path)
        compact_member = score_sheet_member(compact_arm)
        with zipfile.ZipFile(run_bundle_path) as archive:
            compact_member_data = strict_json_bytes(
                archive.read(compact_member), "tampered run-bundle score member"
            )
        for metric in compact_member_data["manual_metric_scores"][0]["metric_scores"]:
            compact_member_data["manual_metric_scores"][0]["metric_scores"][metric] = 0
        rewrite_zip_members(
            tampered_bundle_path,
            {
                compact_member: (
                    json.dumps(compact_member_data, indent=2, ensure_ascii=False) + "\n"
                ).encode("utf-8")
            },
        )
        run_expect_failure(
            _batch_command(run_bundle=tampered_bundle_path),
            cwd=post,
            expected_fragment="score sheet member hash disagrees with manifest",
        )

        # A wholly replaced but internally valid capsule can carry a different
        # decision.  The separately preserved outer digest must reject it before
        # any of its internally consistent content is interpreted as the run.
        alternate_score_path = temp / f"{compact_arm}-alternate-score-final.json"
        alternate_score_data = strict_json_bytes(
            original_compact_score,
            "alternate internally valid score sheet",
        )
        for metric in alternate_score_data["manual_metric_scores"][0]["metric_scores"]:
            alternate_score_data["manual_metric_scores"][0]["metric_scores"][metric] = 0
        alternate_score_path.write_text(
            json.dumps(alternate_score_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        alternate_rows = [dict(row) for row in run_rows]
        next(
            row for row in alternate_rows if row["arm_code"] == compact_arm
        )["score_sheet_file"] = str(alternate_score_path)
        alternate_bundle_path = temp / "alternate-valid-run-capsule.zip"
        run(
            _run_manifest_command(
                prefreeze_kit=prefreeze_source_kit,
                postfreeze_kit=postfreeze_source_kit,
                response_set_lock=response_set_lock,
                policy_verification=policy_verification,
                rows=alternate_rows,
                out=alternate_bundle_path,
            ),
            cwd=post,
        )
        alternate_digest = sha256(alternate_bundle_path)
        alternate_result = run(
            _batch_command(
                run_bundle=alternate_bundle_path,
                expected_digest=alternate_digest,
            ),
            cwd=post,
        )
        alternate_summary = json.loads(alternate_result.stdout)
        if alternate_summary["decision"] == summary["decision"]:
            raise PilotCheckError(
                "alternate internally valid capsule did not demonstrate a result-changing wholesale replacement"
            )
        run_expect_failure(
            _batch_command(
                run_bundle=alternate_bundle_path,
                expected_digest=run_bundle_digest,
            ),
            cwd=post,
            expected_fragment="disagrees with the separately preserved expected digest",
        )

        # Nested source kits are parsed as bounded data, not extracted with
        # archive-controlled paths.  A traversal entry must fail before capsule
        # publication and must not create anything outside the intended root.
        unsafe_prefreeze_kit = temp / "unsafe-prefreeze-dispatch-kit.zip"
        copy_zip_with_extra_member(
            prefreeze_source_kit,
            unsafe_prefreeze_kit,
            "../escape.json",
            b"{}\n",
        )
        unsafe_bundle_path = temp / "unsafe-source-kit-run-capsule.zip"
        run_expect_failure(
            _run_manifest_command(
                prefreeze_kit=unsafe_prefreeze_kit,
                postfreeze_kit=postfreeze_source_kit,
                response_set_lock=response_set_lock,
                policy_verification=policy_verification,
                rows=run_rows,
                out=unsafe_bundle_path,
            ),
            cwd=post,
            expected_fragment="contains unsafe ZIP member name",
        )
        if unsafe_bundle_path.exists() or (temp / "escape.json").exists():
            raise PilotCheckError(
                "unsafe nested-ZIP canary published a capsule or escaped its extraction boundary"
            )

        # A custody helper may record any supplied prerequisite bytes under the
        # required labels, but the bundle assembler must reject a policy
        # substitution before publishing the final freeze artifact.
        wrong_prerequisite_custody = temp / "wrong-prerequisite-custody.json"
        run(
            [
                sys.executable,
                "-S",
                CUSTODY_TOOL,
                str(response_paths[first_arm]),
                "--custodian-id",
                "synthetic-wrong-prerequisite-custodian",
                "--pre-response-exposure-notes",
                "synthetic canary: one named responder bundle only",
                "--prerequisite",
                f"response-set-lock={response_set_lock}",
                "--prerequisite",
                f"postfreeze-policy-verification={post / POLICY_REL}",
                "--attest-clean-preanswer",
                "--template",
                f"{first_base}/custody-template.json",
                "--response-template",
                f"{first_base}/response-template.json",
                "--out",
                str(wrong_prerequisite_custody),
            ],
            cwd=post,
        )
        wrong_rows = [dict(row) for row in run_rows]
        wrong_rows[0]["evidence_record_file"] = str(wrong_prerequisite_custody)
        wrong_bundle_path = temp / "wrong-prerequisite-run-bundle.zip"
        run_expect_failure(
            _run_manifest_command(
                prefreeze_kit=prefreeze_source_kit,
                postfreeze_kit=postfreeze_source_kit,
                response_set_lock=response_set_lock,
                policy_verification=policy_verification,
                rows=wrong_rows,
                out=wrong_bundle_path,
            ),
            cwd=post,
            expected_fragment=f"{first_arm} custody prerequisites drifted",
        )
        if wrong_bundle_path.exists():
            raise PilotCheckError("substituted-prerequisite canary published a run bundle")

        substituted_lock = copy.deepcopy(load(response_set_lock))
        substituted_lock["responses"][0]["response_file_sha256"] = "0" * 64
        substituted_lock_path = temp / "substituted-response-set-lock.json"
        substituted_lock_path.write_text(
            json.dumps(substituted_lock, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        substituted_receipt = copy.deepcopy(load(policy_verification))
        substituted_receipt["response_set_lock_sha256"] = sha256(substituted_lock_path)
        substituted_receipt_path = temp / "substituted-postfreeze-policy-verification.json"
        substituted_receipt_path.write_text(
            json.dumps(substituted_receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        substituted_bundle_path = temp / "substituted-response-set-run-bundle.zip"
        run_expect_failure(
            _run_manifest_command(
                prefreeze_kit=prefreeze_source_kit,
                postfreeze_kit=postfreeze_source_kit,
                response_set_lock=substituted_lock_path,
                policy_verification=substituted_receipt_path,
                rows=run_rows,
                out=substituted_bundle_path,
            ),
            cwd=post,
            expected_fragment="response bytes disagree with the response-set lock",
        )
        if substituted_bundle_path.exists():
            raise PilotCheckError("response-set substitution canary published a run bundle")

        # Final replay must not consult mutable ambient pilot data.  Remove the
        # entire pilot data directory from a verifier-only extraction while
        # retaining the trusted verifier implementation and its dependencies.
        verifier_only = temp / "verifier-only"
        with zipfile.ZipFile(postfreeze_source_kit) as archive:
            archive.extractall(verifier_only)
        shutil.rmtree(
            verifier_only / "cloudtainer/oq0266-isolated-semantic-pilot",
            ignore_errors=True,
        )
        replay_result = run(scorer_command, cwd=verifier_only)
        replay_summary = json.loads(replay_result.stdout)
        if replay_summary["decision"] != summary["decision"]:
            raise PilotCheckError(
                "capsule replay without ambient pilot files changed the accepted decision"
            )
        if replay_summary.get("run_bundle_sha256") != run_bundle_digest:
            raise PilotCheckError(
                "capsule replay without ambient pilot files changed the evidence identity"
            )

        # Directly exercise the distinct-responder guard with otherwise valid
        # validated-row summaries without manufacturing falsely labeled
        # external artifacts.
        sys.path.insert(0, str(post / "cloudtainer/tools"))
        import score_oq0266_isolated_semantic_pilot as batch_module  # type: ignore

        duplicate_rows = [dict(row) for row in summary["arms"]]
        duplicate_rows[1]["responder_id"] = duplicate_rows[0]["responder_id"]
        try:
            batch_module.ensure_distinct_responder_ids(duplicate_rows)
        except batch_module.IsolatedBatchError:
            pass
        else:
            raise PilotCheckError("duplicate-responder negative canary was accepted")
        return summary
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        assignment, batch_manifest, dispatch = verify_static()
        summary = run_end_to_end(assignment, batch_manifest, dispatch)
    except (
        OSError,
        KeyError,
        ValueError,
        zipfile.BadZipFile,
        PilotCheckError,
        ResponseSetContractError,
        ScoringPolicyContractError,
    ) as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"check_oq0266_isolated_semantic_pilot: FAIL: {exc}")
        return 1
    result = {
        "ok": True,
        "arm_count": summary["arm_count"],
        "distinct_responder_count": summary["distinct_responder_count"],
        "response_set_contract_version": RESPONSE_SET_CONTRACT_VERSION,
        "scoring_policy_contract_version": SCORING_POLICY_CONTRACT_VERSION,
        "policy_verification_contract_version": POLICY_VERIFICATION_CONTRACT_VERSION,
        "run_bundle_contract_version": RUN_BUNDLE_CONTRACT_VERSION,
        "batch_barrier_state": summary["batch_barrier_state"],
        "synthetic_decision_state": summary["decision"]["decision_state"],
        "global_compact_gate_confirmed": summary["decision"]["global_compact_gate_confirmed"],
        "operator_cost_inference_state": summary["decision"]["operator_cost_inference_state"],
        "positive_canaries": [
            "cross-machine-clock-skew-accepted",
            "self-contained-capsule-replay-without-ambient-pilot-files",
            "postassembly-source-score-mutation-isolated",
            "separately-pinned-outer-digest-accepted",
        ],
        "negative_canaries": [
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
        ],
        "non_claim": "synthetic execution canary only; not an external OQ-0266 result",
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("check_oq0266_isolated_semantic_pilot: OK")
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
