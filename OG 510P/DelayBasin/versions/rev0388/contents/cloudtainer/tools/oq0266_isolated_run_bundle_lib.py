"""Self-contained evidence-capsule contract for the OQ-0266 isolated pilot.

The final handoff must preserve more than the twelve dynamic response/custody/
score artifacts.  It also needs the exact prefreeze dispatch kit and exact
postfreeze validation kit that define what responders saw and how the run is
interpreted.  This module binds both source kits and every dynamic artifact in
one deterministic ZIP.  A trusted external verifier can therefore replay the
run without consulting mutable plan, policy, packet, template, or scorer files
outside the capsule.
"""
from __future__ import annotations

import hashlib
import io
import pathlib
import zipfile
from dataclasses import dataclass
from typing import Any

from priority_zero_external_run_artifact_lib import (
    ExternalRunArtifactError,
    non_placeholder_text,
    strict_json_bytes,
)

RUN_BUNDLE_CONTRACT_VERSION = "isolated-run-evidence-capsule-v2"
RUN_BUNDLE_RECORD_TYPE = "isolated-run-evidence-capsule-manifest"
RUN_BUNDLE_STATE = "source-kits-and-dynamic-artifacts-hash-frozen"
RUN_MANIFEST_MEMBER = "run-manifest.json"
PREFREEZE_KIT_MEMBER = "source-kits/prefreeze-dispatch-kit.zip"
POSTFREEZE_KIT_MEMBER = "source-kits/postfreeze-batch-kit.zip"
LOCK_MEMBER = "artifacts/response-set-lock.json"
POLICY_RECEIPT_MEMBER = "artifacts/postfreeze-policy-verification.json"

MAX_RUN_BUNDLE_BYTES = 64 * 1024 * 1024
MAX_SOURCE_KIT_BYTES = 32 * 1024 * 1024
MAX_SOURCE_KIT_MEMBERS = 512
MAX_SOURCE_KIT_UNCOMPRESSED_BYTES = 64 * 1024 * 1024
MAX_MEMBER_BYTES = 16 * 1024 * 1024

RUN_MANIFEST_FIELDS = {
    "project",
    "record_type",
    "run_bundle_contract_version",
    "run_bundle_state",
    "batch_id",
    "assignment_plan_sha256",
    "prefreeze_dispatch_kit_member",
    "prefreeze_dispatch_kit_sha256",
    "postfreeze_batch_kit_member",
    "postfreeze_batch_kit_sha256",
    "response_set_lock_member",
    "response_set_lock_sha256",
    "postfreeze_policy_verification_member",
    "postfreeze_policy_verification_sha256",
    "arms",
    "non_claim",
}
ARM_FIELDS = {
    "arm_code",
    "response_member",
    "response_file_sha256",
    "evidence_record_member",
    "evidence_record_file_sha256",
    "score_sheet_member",
    "score_sheet_file_sha256",
}


class RunBundleContractError(ValueError):
    """Raised when an isolated-run evidence capsule is malformed or unbound."""


def _text(value: Any, label: str) -> str:
    try:
        return non_placeholder_text(value, label)
    except ExternalRunArtifactError as exc:
        raise RunBundleContractError(str(exc)) from exc


def _sha256(value: Any, label: str) -> str:
    text = _text(value, label)
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise RunBundleContractError(f"{label} must be a lowercase SHA-256 digest")
    return text


def _safe_zip_name(name: str, label: str) -> str:
    if not isinstance(name, str) or not name or "\\" in name:
        raise RunBundleContractError(f"{label} contains a non-POSIX ZIP member name")
    pure = pathlib.PurePosixPath(name)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise RunBundleContractError(f"{label} contains unsafe ZIP member name: {name!r}")
    if pure.as_posix() != name or name.endswith("/"):
        raise RunBundleContractError(f"{label} contains non-canonical ZIP member name: {name!r}")
    return name


def _safe_zip_info(info: zipfile.ZipInfo, label: str) -> None:
    _safe_zip_name(info.filename, label)
    if info.is_dir():
        raise RunBundleContractError(f"{label} must contain files only: {info.filename}")
    if info.flag_bits & 0x1:
        raise RunBundleContractError(f"{label} contains encrypted member: {info.filename}")
    mode = (info.external_attr >> 16) & 0xFFFF
    if mode & 0o170000 == 0o120000:
        raise RunBundleContractError(f"{label} contains symlink member: {info.filename}")
    if info.file_size > MAX_MEMBER_BYTES:
        raise RunBundleContractError(
            f"{label} member exceeds {MAX_MEMBER_BYTES} bytes: {info.filename}"
        )


def read_safe_zip_members(
    raw: bytes,
    label: str,
    *,
    max_archive_bytes: int = MAX_SOURCE_KIT_BYTES,
    max_members: int = MAX_SOURCE_KIT_MEMBERS,
    max_uncompressed_bytes: int = MAX_SOURCE_KIT_UNCOMPRESSED_BYTES,
) -> dict[str, bytes]:
    """Return exact ZIP member bytes after bounded topology and path checks."""
    if not isinstance(raw, bytes):
        raise RunBundleContractError(f"{label} must be supplied as bytes")
    if len(raw) > max_archive_bytes:
        raise RunBundleContractError(
            f"{label} exceeds archive byte limit {max_archive_bytes}: {len(raw)}"
        )
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            if archive.comment:
                raise RunBundleContractError(f"{label} must not carry a ZIP comment")
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if not infos:
                raise RunBundleContractError(f"{label} is empty")
            if len(infos) > max_members:
                raise RunBundleContractError(
                    f"{label} exceeds member-count limit {max_members}: {len(infos)}"
                )
            if len(names) != len(set(names)):
                raise RunBundleContractError(f"{label} contains duplicate ZIP names")
            total = 0
            for info in infos:
                _safe_zip_info(info, label)
                total += info.file_size
                if total > max_uncompressed_bytes:
                    raise RunBundleContractError(
                        f"{label} exceeds uncompressed byte limit {max_uncompressed_bytes}"
                    )
            bad = archive.testzip()
            if bad is not None:
                raise RunBundleContractError(f"{label} failed ZIP integrity at member {bad}")
            return {info.filename: archive.read(info.filename) for info in infos}
    except zipfile.BadZipFile as exc:
        raise RunBundleContractError(f"{label} is not a valid ZIP: {exc}") from exc


def _validate_deterministic_run_zip(infos: list[zipfile.ZipInfo]) -> None:
    for info in infos:
        _safe_zip_info(info, "isolated run evidence capsule")
        mode = (info.external_attr >> 16) & 0xFFFF
        if info.compress_type != zipfile.ZIP_STORED:
            raise RunBundleContractError(
                f"run capsule member must use stored compression: {info.filename}"
            )
        if info.date_time != (1980, 1, 1, 0, 0, 0):
            raise RunBundleContractError(
                f"run capsule member has non-deterministic timestamp: {info.filename}"
            )
        if info.create_system != 3 or mode != 0o100444:
            raise RunBundleContractError(
                f"run capsule member has non-canonical file metadata: {info.filename}"
            )


def response_member(arm: str) -> str:
    return f"artifacts/{arm}/response.json"


def evidence_record_member(arm: str) -> str:
    return f"artifacts/{arm}/custody.json"


def score_sheet_member(arm: str) -> str:
    return f"artifacts/{arm}/score-sheet.json"


def expected_member_order(arm_order: list[str]) -> list[str]:
    names = [
        RUN_MANIFEST_MEMBER,
        PREFREEZE_KIT_MEMBER,
        POSTFREEZE_KIT_MEMBER,
        LOCK_MEMBER,
        POLICY_RECEIPT_MEMBER,
    ]
    for arm in arm_order:
        names.extend(
            [
                response_member(arm),
                evidence_record_member(arm),
                score_sheet_member(arm),
            ]
        )
    return names


def validate_run_manifest(
    manifest: dict[str, Any],
    *,
    expected_batch_id: str | None = None,
    expected_assignment_plan_sha256: str | None = None,
    expected_arm_codes: set[str] | None = None,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    if not isinstance(manifest, dict) or set(manifest) != RUN_MANIFEST_FIELDS:
        observed = sorted(manifest) if isinstance(manifest, dict) else type(manifest).__name__
        raise RunBundleContractError(
            f"run-capsule manifest fields drifted: observed={observed} expected={sorted(RUN_MANIFEST_FIELDS)}"
        )
    if manifest.get("project") != "DelayBasin":
        raise RunBundleContractError("run-capsule manifest project must be DelayBasin")
    if manifest.get("record_type") != RUN_BUNDLE_RECORD_TYPE:
        raise RunBundleContractError(
            f"run-capsule manifest record_type must be {RUN_BUNDLE_RECORD_TYPE}"
        )
    if manifest.get("run_bundle_contract_version") != RUN_BUNDLE_CONTRACT_VERSION:
        raise RunBundleContractError(
            f"run-capsule contract must be {RUN_BUNDLE_CONTRACT_VERSION}"
        )
    if manifest.get("run_bundle_state") != RUN_BUNDLE_STATE:
        raise RunBundleContractError(f"run-capsule state must be {RUN_BUNDLE_STATE}")
    batch_id = _text(manifest.get("batch_id"), "run-capsule manifest batch_id")
    if expected_batch_id is not None and batch_id != expected_batch_id:
        raise RunBundleContractError("run-capsule batch_id disagrees with assignment plan")
    plan_sha = _sha256(
        manifest.get("assignment_plan_sha256"),
        "run-capsule manifest assignment_plan_sha256",
    )
    if expected_assignment_plan_sha256 is not None and plan_sha != expected_assignment_plan_sha256:
        raise RunBundleContractError(
            "run-capsule assignment_plan_sha256 disagrees with the committed plan"
        )
    expected_fixed_members = {
        "prefreeze_dispatch_kit_member": PREFREEZE_KIT_MEMBER,
        "postfreeze_batch_kit_member": POSTFREEZE_KIT_MEMBER,
        "response_set_lock_member": LOCK_MEMBER,
        "postfreeze_policy_verification_member": POLICY_RECEIPT_MEMBER,
    }
    for field, expected in expected_fixed_members.items():
        if manifest.get(field) != expected:
            raise RunBundleContractError(f"run-capsule {field} must be {expected}")
    for field in [
        "prefreeze_dispatch_kit_sha256",
        "postfreeze_batch_kit_sha256",
        "response_set_lock_sha256",
        "postfreeze_policy_verification_sha256",
    ]:
        _sha256(manifest.get(field), f"run-capsule manifest {field}")
    _text(manifest.get("non_claim"), "run-capsule manifest non_claim")

    rows = manifest.get("arms")
    if not isinstance(rows, list) or len(rows) != 4:
        raise RunBundleContractError("run-capsule manifest must contain exactly four arm rows")
    arm_order: list[str] = []
    by_arm: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != ARM_FIELDS:
            observed = sorted(row) if isinstance(row, dict) else type(row).__name__
            raise RunBundleContractError(
                f"run-capsule manifest arms[{index}] fields drifted: "
                f"observed={observed} expected={sorted(ARM_FIELDS)}"
            )
        arm = _text(row.get("arm_code"), f"run-capsule manifest arms[{index}].arm_code")
        if arm in by_arm:
            raise RunBundleContractError(f"run-capsule manifest duplicates arm {arm}")
        expected_members = {
            "response_member": response_member(arm),
            "evidence_record_member": evidence_record_member(arm),
            "score_sheet_member": score_sheet_member(arm),
        }
        for field, expected in expected_members.items():
            if row.get(field) != expected:
                raise RunBundleContractError(
                    f"run-capsule manifest {arm}.{field} must be {expected}"
                )
        for field in [
            "response_file_sha256",
            "evidence_record_file_sha256",
            "score_sheet_file_sha256",
        ]:
            _sha256(row.get(field), f"run-capsule manifest {arm}.{field}")
        arm_order.append(arm)
        by_arm[arm] = row
    if expected_arm_codes is not None and set(arm_order) != expected_arm_codes:
        raise RunBundleContractError(
            f"run-capsule arm set drifted: observed={sorted(arm_order)} "
            f"expected={sorted(expected_arm_codes)}"
        )
    return arm_order, by_arm


@dataclass(frozen=True)
class LoadedRunBundle:
    path: pathlib.Path
    bundle_sha256: str
    manifest: dict[str, Any]
    manifest_raw: bytes
    manifest_sha256: str
    prefreeze_dispatch_kit_raw: bytes
    postfreeze_batch_kit_raw: bytes
    response_set_lock: dict[str, Any]
    response_set_lock_raw: bytes
    postfreeze_policy_verification: dict[str, Any]
    postfreeze_policy_verification_raw: bytes
    artifacts_by_arm: dict[str, dict[str, bytes]]
    arm_order: tuple[str, ...]


def load_run_bundle(
    path: pathlib.Path,
    *,
    expected_bundle_sha256: str | None = None,
    expected_batch_id: str | None = None,
    expected_assignment_plan_sha256: str | None = None,
    expected_arm_codes: set[str] | None = None,
) -> LoadedRunBundle:
    path = pathlib.Path(path)
    if not path.exists() or not path.is_file():
        raise RunBundleContractError(f"missing isolated run evidence capsule: {path}")
    bundle_raw = path.read_bytes()
    if len(bundle_raw) > MAX_RUN_BUNDLE_BYTES:
        raise RunBundleContractError(
            f"isolated run evidence capsule exceeds {MAX_RUN_BUNDLE_BYTES} bytes"
        )
    bundle_sha = hashlib.sha256(bundle_raw).hexdigest()
    if expected_bundle_sha256 is not None:
        expected = _sha256(expected_bundle_sha256, "expected run-capsule SHA-256")
        if bundle_sha != expected:
            raise RunBundleContractError(
                "isolated run evidence capsule SHA-256 disagrees with the separately preserved expected digest"
            )
    try:
        with zipfile.ZipFile(io.BytesIO(bundle_raw)) as archive:
            if archive.comment:
                raise RunBundleContractError("isolated run evidence capsule must not carry a ZIP comment")
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise RunBundleContractError(
                    "isolated run evidence capsule contains duplicate ZIP names"
                )
            _validate_deterministic_run_zip(infos)
            bad = archive.testzip()
            if bad is not None:
                raise RunBundleContractError(
                    f"isolated run evidence capsule failed ZIP integrity at member {bad}"
                )
            if not names or names[0] != RUN_MANIFEST_MEMBER:
                raise RunBundleContractError(
                    f"isolated run evidence capsule first member must be {RUN_MANIFEST_MEMBER}"
                )
            manifest_raw = archive.read(RUN_MANIFEST_MEMBER)
            manifest = strict_json_bytes(manifest_raw, "isolated run-capsule manifest")
            arm_order, by_arm = validate_run_manifest(
                manifest,
                expected_batch_id=expected_batch_id,
                expected_assignment_plan_sha256=expected_assignment_plan_sha256,
                expected_arm_codes=expected_arm_codes,
            )
            expected_names = expected_member_order(arm_order)
            if names != expected_names:
                raise RunBundleContractError(
                    "isolated run evidence capsule member order/topology drifted: "
                    f"observed={names} expected={expected_names}"
                )

            prefreeze_raw = archive.read(PREFREEZE_KIT_MEMBER)
            postfreeze_raw = archive.read(POSTFREEZE_KIT_MEMBER)
            lock_raw = archive.read(LOCK_MEMBER)
            policy_raw = archive.read(POLICY_RECEIPT_MEMBER)
            fixed_hashes = {
                "prefreeze_dispatch_kit_sha256": hashlib.sha256(prefreeze_raw).hexdigest(),
                "postfreeze_batch_kit_sha256": hashlib.sha256(postfreeze_raw).hexdigest(),
                "response_set_lock_sha256": hashlib.sha256(lock_raw).hexdigest(),
                "postfreeze_policy_verification_sha256": hashlib.sha256(policy_raw).hexdigest(),
            }
            for field, observed in fixed_hashes.items():
                if observed != manifest[field]:
                    raise RunBundleContractError(
                        f"run-capsule {field.removesuffix('_sha256').replace('_', ' ')} member hash disagrees with manifest"
                    )
            # Validate the nested source kits now, before any caller materializes
            # them, so malformed paths, symlinks, oversized members, and duplicate
            # names cannot reach the filesystem.
            read_safe_zip_members(prefreeze_raw, "run-capsule prefreeze dispatch kit")
            read_safe_zip_members(postfreeze_raw, "run-capsule postfreeze batch kit")

            lock = strict_json_bytes(lock_raw, "run-capsule response-set lock")
            policy = strict_json_bytes(
                policy_raw,
                "run-capsule postfreeze policy verification",
            )
            artifacts_by_arm: dict[str, dict[str, bytes]] = {}
            for arm in arm_order:
                row = by_arm[arm]
                response_raw = archive.read(row["response_member"])
                custody_raw = archive.read(row["evidence_record_member"])
                score_raw = archive.read(row["score_sheet_member"])
                observed = {
                    "response_file_sha256": hashlib.sha256(response_raw).hexdigest(),
                    "evidence_record_file_sha256": hashlib.sha256(custody_raw).hexdigest(),
                    "score_sheet_file_sha256": hashlib.sha256(score_raw).hexdigest(),
                }
                for field, digest in observed.items():
                    if digest != row[field]:
                        label = field.removesuffix("_file_sha256").replace("_", " ")
                        raise RunBundleContractError(
                            f"run-capsule {arm} {label} member hash disagrees with manifest"
                        )
                strict_json_bytes(response_raw, f"run-capsule {arm} response")
                strict_json_bytes(custody_raw, f"run-capsule {arm} custody record")
                strict_json_bytes(score_raw, f"run-capsule {arm} score sheet")
                artifacts_by_arm[arm] = {
                    "response": response_raw,
                    "custody": custody_raw,
                    "score_sheet": score_raw,
                }
    except zipfile.BadZipFile as exc:
        raise RunBundleContractError(
            f"isolated run evidence capsule is not a valid ZIP: {exc}"
        ) from exc
    except ExternalRunArtifactError as exc:
        raise RunBundleContractError(str(exc)) from exc

    return LoadedRunBundle(
        path=path,
        bundle_sha256=bundle_sha,
        manifest=manifest,
        manifest_raw=manifest_raw,
        manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
        prefreeze_dispatch_kit_raw=prefreeze_raw,
        postfreeze_batch_kit_raw=postfreeze_raw,
        response_set_lock=lock,
        response_set_lock_raw=lock_raw,
        postfreeze_policy_verification=policy,
        postfreeze_policy_verification_raw=policy_raw,
        artifacts_by_arm=artifacts_by_arm,
        arm_order=tuple(arm_order),
    )
