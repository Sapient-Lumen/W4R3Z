#!/usr/bin/env python3
"""Release-critical executable check for the Derive runtime golden thread.

This is deliberately not another schema expansion.  It proves the smallest
current product path really runs: Spec -> Lock -> Plan -> Artifact -> Activate ->
Explain -> Rollback, with explicit dry-run truth and no FreeBSD mutation claim.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from cube_digest_lib import load_json_strict_text
import derive_runtime as runtime
from derive_runtime import (
    DEFAULT_FREEBSD_REAL_BACKEND_COMMANDS,
    HOST_PROOF_TARGET_MATRIX_ID,
    PRIMARY_FREEBSD_MIN_OSRELDATE,
    PRIMARY_FREEBSD_RELEASE,
    RUNTIME_IDENTITY_PROFILE,
    STATE_JOURNAL_NAME,
    STATE_LOCK_NAME,
    STATE_COMMIT_OBSERVATION,
    ARTIFACT_STORE_POLICY,
    MATERIAL_SOURCE_POLICY,
    PACKAGE_CLOSURE_POLICY,
    PACKAGE_PAYLOAD_METADATA_POLICY,
    PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
    runtime_digest,
    package_catalog_digest,
    package_repository_snapshot_digest,
)

ROOT = Path(__file__).resolve().parents[1]
DERIVE = ROOT / "tools" / "derive_runtime.py"
STAMP = "2026-06-18T00:00:00Z"
VERSION = "2026-06-18r630"
FREEBSD_TOOLS = ROOT / "tools" / "freebsd"
if str(FREEBSD_TOOLS) not in sys.path:
    sys.path.insert(0, str(FREEBSD_TOOLS))

import host_proof_contract as host_contract  # noqa: E402
import import_removable_media_local_fallback_host_proof_handoff as host_importer  # noqa: E402
from check_removable_media_local_fallback_freebsd_host_proof_sealed_importer import build_synthetic_real_handoff  # noqa: E402


def load(path: Path) -> Any:
    return load_json_strict_text(path.read_text(encoding="utf-8"))


def current_generation(state_dir: Path) -> dict[str, Any] | None:
    path = state_dir / "current-generation.json"
    if not path.exists():
        return None
    value = load(path)
    if not isinstance(value, dict):
        raise AssertionError(f"{path} did not contain a generation object")
    return value


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-S", str(DERIVE), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def write_digest_bound_preflight(path: Path, receipt: dict[str, Any]) -> None:
    clone = dict(receipt)
    clone.pop("host_preflight_digest", None)
    receipt["host_preflight_digest"] = runtime_digest(clone)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def command_rows(found: bool = True) -> list[dict[str, Any]]:
    return [{"name": name, "found": found} for name in sorted(DEFAULT_FREEBSD_REAL_BACKEND_COMMANDS)]


def make_artifact_file_writable(path: Path) -> None:
    path.parent.chmod(0o755)
    path.chmod(0o644)


def reseal_artifact_file(path: Path) -> None:
    path.chmod(0o444)
    path.parent.chmod(0o555)


def write_payload_variant(stem: str, base_rel: str, mutate) -> tuple[str, Path]:
    """Write a temporary repo-relative fixture payload for negative resolver tests."""

    base = ROOT / base_rel
    obj = load(base)
    mutate(obj)
    rel = f"validation/runtime-materials/current/packages/.golden-thread-{stem}-{os.getpid()}.pkg"
    path = ROOT / rel
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel, path


def write_snapshot_variant(stem: str, mutate) -> tuple[str, Path, dict[str, Any]]:
    """Write a temporary repo-relative repository snapshot for negative resolver tests."""

    obj = load(ROOT / "validation" / "runtime-package-repository" / "current" / "snapshot.json")
    mutate(obj)
    obj["snapshot_digest"] = package_repository_snapshot_digest(obj)
    rel = f"validation/runtime-package-repository/current/.golden-thread-{stem}-{os.getpid()}.json"
    path = ROOT / rel
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel, path, obj


def main() -> int:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="derivebsd-golden-thread-") as td:
        workspace = Path(td) / "run"
        summary_path = Path(td) / "summary.json"
        proc = run([
            "run-golden-thread",
            "--spec", "spec/examples/microvm.spec.json",
            "--workspace", str(workspace),
            "--out", str(summary_path),
            "--stamp", STAMP,
        ])
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            print("runtime golden thread check FAILED")
            return 1
        summary = load(summary_path)
        checked_summary_path = ROOT / "validation/runtime-golden-thread/current/run.summary.json"
        if checked_summary_path.exists():
            checked_summary = load(checked_summary_path)
            require(errors, checked_summary.get("generated_for_version") == VERSION, "checked-in golden-thread evidence must bind current cube cut")
            require(errors, checked_summary.get("steps_completed") == ["lock", "plan", "build", "activate", "explain", "rollback"], "checked-in golden-thread evidence must retain the full step sequence")
            require(errors, checked_summary.get("system_effect") == "no-freebsd-system-mutation", "checked-in golden-thread evidence must preserve the dry-run truth claim")
        else:
            errors.append("missing validation/runtime-golden-thread/current/run.summary.json")
        require(errors, summary.get("generated_for_version") == VERSION, "run summary must bind current cube cut")
        require(errors, summary.get("steps_completed") == ["lock", "plan", "build", "activate", "explain", "rollback"], "all golden-thread steps must complete in order")
        require(errors, summary.get("system_effect") == "no-freebsd-system-mutation", "cloudtainer run must not claim host mutation")
        require(errors, summary.get("rollback_restored_previous_generation") is True, "rollback must restore the prior local state pointer")
        require(errors, summary.get("runtime_identity_profile") == RUNTIME_IDENTITY_PROFILE, "run summary must name the runtime identity profile")
        require(errors, summary.get("state_commit_policy") == "exclusive-lock-plus-precommit-journal", "run summary must name the journaled state commit policy")
        require(errors, summary.get("state_commit_observation") == STATE_COMMIT_OBSERVATION, "run summary must prove current-generation readback before journal cleanup")
        require(errors, summary.get("state_journal_removed_after_commit") is True, "activation and rollback journals must be removed after successful commits")

        paths = summary.get("paths", {}) if isinstance(summary.get("paths"), dict) else {}
        lock = load(Path(paths["lock"]))
        plan = load(Path(paths["plan"]))
        artifact = load(Path(paths["artifact"]))
        activation = load(Path(paths["activation_receipt"]))
        explanation = load(Path(paths["explanation"]))
        rollback = load(Path(paths["rollback_receipt"]))

        for label, obj, field in [
            ("lock", lock, "lock_digest"),
            ("plan", plan, "plan_digest"),
            ("artifact", artifact, "artifact_digest"),
            ("activation", activation, "activation_receipt_digest"),
            ("explanation", explanation, "explanation_digest"),
            ("rollback", rollback, "rollback_receipt_digest"),
        ]:
            require(errors, obj.get("runtime_identity_profile") == RUNTIME_IDENTITY_PROFILE, f"{label} must name the path-independent runtime identity profile")
            clone = dict(obj)
            clone.pop(field, None)
            require(errors, obj.get(field) == runtime_digest(clone), f"{label} stored digest must match runtime identity view")

        require(errors, lock.get("resolver", {}).get("network_used") is False, "lock must prove no network resolution")
        require(errors, lock.get("resolver", {}).get("mode") == "offline-fixture-catalog-no-network", "lock must use the finite offline fixture catalog resolver")
        require(errors, lock.get("resolver", {}).get("truth_claim") == "finite-offline-fixture-repository-snapshot-plus-catalog-projection-plus-payload-verified-closure-and-bytes-not-a-package-index-resolution", "lock must not overclaim package/material/dependency resolution")
        require(errors, lock.get("resolver", {}).get("material_source_policy") == MATERIAL_SOURCE_POLICY, "lock must bind the material source policy")
        require(errors, lock.get("resolver", {}).get("package_closure_policy") == PACKAGE_CLOSURE_POLICY, "lock must bind the package closure policy")
        require(errors, lock.get("resolver", {}).get("package_payload_metadata_policy") == PACKAGE_PAYLOAD_METADATA_POLICY, "lock must bind the package payload metadata policy")
        require(errors, lock.get("resolver", {}).get("package_repository_snapshot_policy") == PACKAGE_REPOSITORY_SNAPSHOT_POLICY, "lock must bind the package repository snapshot policy")
        require(errors, isinstance(lock.get("resolver", {}).get("package_repository_snapshot_digest"), str), "lock must bind the admitted repository snapshot digest")
        require(errors, isinstance(lock.get("resolver", {}).get("package_repository_snapshot_sha256"), str), "lock must bind the repository snapshot file sha256")
        require(errors, isinstance(lock.get("resolver", {}).get("package_catalog_digest"), str), "lock must bind the package catalog digest")
        packages = lock.get("packages", []) if isinstance(lock.get("packages"), list) else []
        package_by_id = {row.get("id"): row for row in packages if isinstance(row, dict)}
        closure = lock.get("package_closure", {}) if isinstance(lock.get("package_closure"), dict) else {}
        require(errors, closure.get("policy") == PACKAGE_CLOSURE_POLICY, "lock must expose the package closure policy")
        require(errors, closure.get("package_payload_metadata_policy") == PACKAGE_PAYLOAD_METADATA_POLICY, "lock closure must bind the package payload metadata policy")
        require(errors, closure.get("package_repository_snapshot_policy") == PACKAGE_REPOSITORY_SNAPSHOT_POLICY, "lock closure must bind the repository snapshot policy")
        require(errors, closure.get("package_repository_snapshot_digest") == lock.get("resolver", {}).get("package_repository_snapshot_digest"), "lock closure must carry the admitted snapshot digest")
        require(errors, closure.get("requested_package_ids") == ["nginx"], "lock closure must preserve the requested package list")
        require(errors, closure.get("resolved_package_ids") == ["openssl", "pcre2", "nginx"], "lock closure must include transitive dependencies before the requested package")
        require(errors, closure.get("dependency_package_ids") == ["openssl", "pcre2"], "lock closure must distinguish dependency packages from requested packages")
        require(errors, isinstance(closure.get("closure_digest"), str), "lock closure must bind a closure digest")
        require(errors, set(package_by_id) == {"nginx", "openssl", "pcre2"}, "lock package rows must be the closed fixture dependency set")
        require(errors, package_by_id.get("nginx", {}).get("requested") is True, "requested nginx package must be marked requested")
        require(errors, package_by_id.get("nginx", {}).get("dependency_depth") == 0, "requested nginx package must have depth zero")
        require(errors, package_by_id.get("nginx", {}).get("dependencies") == ["openssl", "pcre2"], "nginx fixture must bind its transitive dependency edge list")
        for dep_id in ["openssl", "pcre2"]:
            row = package_by_id.get(dep_id, {})
            require(errors, row.get("requested") is False, f"{dep_id} must be marked as a dependency, not a direct request")
            require(errors, row.get("dependency_depth") == 1, f"{dep_id} must be one edge from nginx")
            require(errors, row.get("requested_by") == ["nginx"], f"{dep_id} must be bound to its requesting root")
            require(errors, row.get("package_closure_policy") == PACKAGE_CLOSURE_POLICY, f"{dep_id} must bind the package closure policy")
            require(errors, row.get("package_payload_metadata_policy") == PACKAGE_PAYLOAD_METADATA_POLICY, f"{dep_id} must bind the package payload metadata policy")
            require(errors, row.get("package_repository_snapshot_policy") == PACKAGE_REPOSITORY_SNAPSHOT_POLICY, f"{dep_id} must bind the package repository snapshot policy")
        require(errors, all(isinstance(row, dict) and isinstance(row.get("catalog_entry_digest"), str) for row in packages), "lock package rows must bind catalog entry digests")
        require(errors, all(isinstance(row, dict) and isinstance(row.get("package_repository_snapshot_digest"), str) for row in packages), "lock package rows must bind repository snapshot digests")
        require(errors, all(isinstance(row, dict) and isinstance(row.get("package_repository_snapshot_row_digest"), str) for row in packages), "lock package rows must bind repository snapshot row digests")
        require(errors, all(isinstance(row, dict) and row.get("consumable_bytes_verified") is True for row in packages), "lock package rows must verify consumable fixture bytes")
        require(errors, all(isinstance(row, dict) and row.get("payload_metadata_verified") is True for row in packages), "lock package rows must verify fixture payload metadata projection")
        require(errors, all(isinstance(row, dict) and isinstance(row.get("fixture_payload_digest"), str) for row in packages), "lock package rows must bind fixture payload digests")
        require(errors, all(isinstance(row, dict) and isinstance((row.get("material") or {}).get("sha256"), str) for row in packages), "lock package rows must bind material sha256")
        require(errors, all(isinstance(row, dict) and isinstance((row.get("material") or {}).get("fixture_payload_digest"), str) for row in packages), "lock material rows must bind fixture payload digests")
        require(errors, plan.get("execution_surface", {}).get("package_closure_policy") == PACKAGE_CLOSURE_POLICY, "plan execution surface must bind the package closure policy")
        require(errors, plan.get("execution_surface", {}).get("package_payload_metadata_policy") == PACKAGE_PAYLOAD_METADATA_POLICY, "plan execution surface must bind the package payload metadata policy")
        require(errors, plan.get("execution_surface", {}).get("package_repository_snapshot_policy") == PACKAGE_REPOSITORY_SNAPSHOT_POLICY, "plan execution surface must bind the package repository snapshot policy")
        require(errors, plan.get("package_closure", {}).get("closure_digest") == closure.get("closure_digest"), "plan must carry the lock package closure digest")
        require(errors, plan.get("execution_surface", {}).get("bhyve_execution") is False, "plan must not claim bhyve execution in cloudtainer")
        require(errors, plan.get("blast_radius", {}).get("host_files_changed") == [], "dry-run plan must have empty host mutation blast radius")
        require(errors, activation.get("state_journal", {}).get("policy") == "exclusive-lock-plus-precommit-journal", "activation receipt must bind the journaled state commit policy")
        require(errors, isinstance(activation.get("state_journal", {}).get("precommit_journal_digest"), str), "activation receipt must bind a precommit journal digest")
        require(errors, activation.get("state_journal", {}).get("commit_observation") == STATE_COMMIT_OBSERVATION, "activation receipt must prove exact readback before journal clear")
        require(errors, activation.get("state_journal", {}).get("commit_readback_digest") == runtime_digest(activation.get("state_after", {}).get("current_generation")), "activation readback digest must bind state_after")
        require(errors, rollback.get("state_journal", {}).get("policy") == "exclusive-lock-plus-precommit-journal", "rollback receipt must bind the journaled state commit policy")
        require(errors, isinstance(rollback.get("state_journal", {}).get("precommit_journal_digest"), str), "rollback receipt must bind a precommit journal digest")
        require(errors, rollback.get("state_journal", {}).get("commit_observation") == STATE_COMMIT_OBSERVATION, "rollback receipt must prove exact readback before journal clear")
        require(errors, rollback.get("state_journal", {}).get("commit_readback_digest") is None or isinstance(rollback.get("state_journal", {}).get("commit_readback_digest"), str), "rollback readback digest must be null or a digest")
        require(errors, artifact.get("activation_surface", {}).get("freebsd_backend_executed") is False, "artifact must not claim FreeBSD backend execution")
        require(errors, artifact.get("activation_surface", {}).get("artifact_tree_policy") == "sealed-readonly-no-symlink-no-hardlink-aliases", "artifact must record the sealed tree policy")
        require(errors, artifact.get("activation_surface", {}).get("artifact_store_policy") == ARTIFACT_STORE_POLICY, "artifact must record the no-clobber CAS store policy")
        require(errors, artifact.get("activation_surface", {}).get("material_source_policy") == MATERIAL_SOURCE_POLICY, "artifact must record the material source policy")
        require(errors, artifact.get("activation_surface", {}).get("package_closure_policy") == PACKAGE_CLOSURE_POLICY, "artifact must record the package closure policy")
        require(errors, artifact.get("activation_surface", {}).get("package_payload_metadata_policy") == PACKAGE_PAYLOAD_METADATA_POLICY, "artifact must record the package payload metadata policy")
        require(errors, artifact.get("activation_surface", {}).get("package_repository_snapshot_policy") == PACKAGE_REPOSITORY_SNAPSHOT_POLICY, "artifact must record the repository snapshot policy")
        require(errors, artifact.get("activation_surface", {}).get("package_repository_snapshot_digest") == lock.get("resolver", {}).get("package_repository_snapshot_digest"), "artifact must carry the admitted repository snapshot digest")
        require(errors, artifact.get("activation_surface", {}).get("state_commit_policy") == "exclusive-lock-plus-precommit-journal", "artifact must record the journaled state commit policy")
        require(errors, artifact.get("activation_surface", {}).get("state_commit_observation") == STATE_COMMIT_OBSERVATION, "artifact must record current-generation readback policy")
        rows = artifact.get("tree_manifest", []) if isinstance(artifact.get("tree_manifest"), list) else []
        file_rows = [row for row in rows if isinstance(row, dict) and row.get("type") == "file"]
        dir_rows = [row for row in rows if isinstance(row, dict) and row.get("type") == "directory"]
        require(errors, file_rows and all(row.get("mode") == "0o444" for row in file_rows), "artifact file rows must be sealed read-only in the tree manifest")
        require(errors, dir_rows and all(row.get("mode") == "0o555" for row in dir_rows), "artifact directory rows must be sealed read-only in the tree manifest")
        artifact_root = Path(artifact["artifact_path"])
        material_manifest_path = artifact_root / "inputs" / "package-materials.json"
        require(errors, material_manifest_path.is_file(), "artifact tree must carry copied package material manifest")
        if material_manifest_path.is_file():
            material_manifest = load(material_manifest_path)
            material_rows = material_manifest.get("packages", []) if isinstance(material_manifest.get("packages"), list) else []
            lock_material = {row.get("id"): (row.get("material") or {}) for row in lock.get("packages", []) if isinstance(row, dict)}
            require(errors, material_manifest.get("material_source_policy") == MATERIAL_SOURCE_POLICY, "package material manifest must bind the material source policy")
            require(errors, material_manifest.get("package_closure_policy") == PACKAGE_CLOSURE_POLICY, "package material manifest must bind the package closure policy")
            require(errors, material_manifest.get("package_payload_metadata_policy") == PACKAGE_PAYLOAD_METADATA_POLICY, "package material manifest must bind the package payload metadata policy")
            require(errors, material_manifest.get("package_repository_snapshot_policy") == PACKAGE_REPOSITORY_SNAPSHOT_POLICY, "package material manifest must bind the repository snapshot policy")
            require(errors, material_manifest.get("package_repository_snapshot_digest") == lock.get("resolver", {}).get("package_repository_snapshot_digest"), "package material manifest must bind the admitted repository snapshot digest")
            require(errors, len(material_rows) == len(packages), "package material manifest must carry every closed package input")
            require(errors, material_manifest.get("package_materials_digest") == runtime_digest(material_rows), "package material manifest digest must bind copied material rows")
            for row in material_rows:
                if not isinstance(row, dict):
                    errors.append("package material row must be an object")
                    continue
                pkg_id = row.get("package_id")
                member = row.get("artifact_member_path")
                require(errors, isinstance(member, str) and member.startswith("inputs/packages/"), "package material row must point inside inputs/packages")
                if isinstance(member, str):
                    member_path = artifact_root / member
                    require(errors, member_path.is_file(), f"copied package material {member} must exist")
                    if member_path.is_file():
                        require(errors, runtime.sha256_bytes(member_path.read_bytes()) == row.get("sha256"), f"copied package material {member} sha256 must match manifest")
                if isinstance(pkg_id, str) and isinstance(lock_material.get(pkg_id), dict):
                    require(errors, row.get("sha256") == lock_material[pkg_id].get("sha256"), f"copied package material for {pkg_id} must match lock material sha256")
                require(errors, row.get("package_closure_policy") == PACKAGE_CLOSURE_POLICY, "copied package material row must bind closure policy")
                require(errors, row.get("package_payload_metadata_policy") == PACKAGE_PAYLOAD_METADATA_POLICY, "copied package material row must bind payload metadata policy")
                require(errors, row.get("package_repository_snapshot_policy") == PACKAGE_REPOSITORY_SNAPSHOT_POLICY, "copied package material row must bind repository snapshot policy")
                require(errors, row.get("package_repository_snapshot_digest") == lock.get("resolver", {}).get("package_repository_snapshot_digest"), "copied package material row must bind admitted snapshot digest")
                require(errors, row.get("payload_metadata_verified") is True, "copied package material row must preserve payload metadata verification")
                require(errors, isinstance(row.get("fixture_payload_digest"), str), "copied package material row must bind fixture payload digest")
                require(errors, isinstance(row.get("dependencies"), list), "copied package material row must carry dependency metadata")

        host_preflight_path = Path(td) / "host-preflight-denial.receipt.json"
        host_preflight = run([
            "host-preflight",
            "--out", str(host_preflight_path),
            "--stamp", STAMP,
            "--require-command", "__derivebsd_missing_real_backend_command__",
        ])
        require(errors, host_preflight.returncode != 0, "host preflight must emit a denial when a required real-backend command is missing")
        preflight = load(host_preflight_path)
        require(errors, preflight.get("kind") == "derive.runtime.host_preflight.receipt", "host preflight must write a typed receipt")
        require(errors, preflight.get("generated_for_version") == VERSION, "host preflight receipt must bind current cube cut")
        require(errors, preflight.get("system_effect") == "no-freebsd-system-mutation", "host preflight must be observation-only")
        require(errors, preflight.get("admissible_for_real_backend") is False, "denied host preflight must not be real-backend admissible")
        require(errors, "missing-required-command:__derivebsd_missing_real_backend_command__" in preflight.get("denial_reasons", []), "forced host preflight denial must name the missing command")
        clone = dict(preflight)
        clone.pop("host_preflight_digest", None)
        require(errors, preflight.get("host_preflight_digest") == runtime_digest(clone), "host preflight stored digest must match runtime identity view")

        host_proof_status_path = Path(td) / "host-proof-status.json"
        host_proof_status = run([
            "host-proof-status",
            "--import-root", "validation/freebsd-host-proof-imports",
            "--out", str(host_proof_status_path),
            "--fail-if-incomplete",
        ])
        require(errors, host_proof_status.returncode != 0, "host-proof-status --fail-if-incomplete must fail while no primary proof is imported")
        status_report = load(host_proof_status_path)
        require(errors, status_report.get("generated_for_version") == VERSION, "host proof status must bind current cube cut")
        require(errors, status_report.get("proof_complete") is False, "empty checked import root must remain explicitly incomplete")
        require(errors, status_report.get("status") == "blocked-no-real-host-proof-import", "empty checked import root must report the blocked status")

        no_preflight_state = Path(td) / "no-preflight-real-state"
        no_preflight_real = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(no_preflight_state),
            "--mode", "freebsd-real",
            "--out", str(Path(td) / "no-preflight-real.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, no_preflight_real.returncode != 0, "freebsd-real activation must require host preflight")
        require(errors, "requires --host-preflight" in no_preflight_real.stderr, "missing preflight failure should name the required preflight")
        require(errors, current_generation(no_preflight_state) is None, "missing-preflight real activation must fail before state mutation")

        denied_preflight_state = Path(td) / "denied-preflight-real-state"
        denied_preflight_real = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(denied_preflight_state),
            "--mode", "freebsd-real",
            "--host-preflight", str(host_preflight_path),
            "--out", str(Path(td) / "denied-preflight-real.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, denied_preflight_real.returncode != 0, "freebsd-real activation must reject a denied host preflight")
        require(errors, "host preflight denied real backend admission" in denied_preflight_real.stderr, "denied preflight failure should name admission denial")
        require(errors, current_generation(denied_preflight_state) is None, "denied-preflight real activation must fail before state mutation")

        tampered_preflight_path = Path(td) / "tampered-host-preflight.receipt.json"
        tampered_preflight = dict(preflight)
        tampered_preflight["result"] = "passed"
        tampered_preflight["admissible_for_real_backend"] = True
        tampered_preflight_path.write_text(json.dumps(tampered_preflight, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tampered_preflight_real = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(Path(td) / "tampered-preflight-real-state"),
            "--mode", "freebsd-real",
            "--host-preflight", str(tampered_preflight_path),
            "--out", str(Path(td) / "tampered-preflight-real.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, tampered_preflight_real.returncode != 0, "freebsd-real activation must reject tampered host preflight receipts")
        require(errors, "host_preflight_digest mismatch" in tampered_preflight_real.stderr, "tampered preflight failure should name the preflight digest mismatch")

        digest_valid_but_semantically_forged_path = Path(td) / "digest-valid-but-linux-forged-host-preflight.json"
        digest_valid_but_semantically_forged = dict(preflight)
        digest_valid_but_semantically_forged.update({
            "result": "passed",
            "admissible_for_real_backend": True,
            "denial_reasons": [],
            "required_commands": command_rows(found=True),
            "host": {
                "system": "Linux",
                "release": PRIMARY_FREEBSD_RELEASE,
                "machine": "amd64",
                "python_implementation": "CPython",
                "python_version": "3.11.0",
                "effective_uid": 0,
                "kern_osreldate": PRIMARY_FREEBSD_MIN_OSRELDATE,
                "primary_freebsd_release": PRIMARY_FREEBSD_RELEASE,
                "minimum_freebsd_osreldate": PRIMARY_FREEBSD_MIN_OSRELDATE,
                "host_target_tier": "primary-production",
                "host_target_matrix_id": HOST_PROOF_TARGET_MATRIX_ID,
            },
        })
        write_digest_bound_preflight(digest_valid_but_semantically_forged_path, digest_valid_but_semantically_forged)
        semantically_forged_real = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(Path(td) / "semantically-forged-preflight-state"),
            "--mode", "freebsd-real",
            "--host-preflight", str(digest_valid_but_semantically_forged_path),
            "--out", str(Path(td) / "semantically-forged-preflight.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, semantically_forged_real.returncode != 0, "freebsd-real activation must reject digest-valid but semantically forged preflight")
        require(errors, "unsupported-host-os" in semantically_forged_real.stderr, "semantic preflight failure must name unsupported-host-os")
        require(errors, current_generation(Path(td) / "semantically-forged-preflight-state") is None, "semantic preflight rejection must fail before state mutation")

        synthetic_primary_preflight_path = Path(td) / "synthetic-primary-freebsd-preflight.json"
        synthetic_primary_preflight = dict(preflight)
        synthetic_primary_preflight.update({
            "result": "passed",
            "admissible_for_real_backend": True,
            "denial_reasons": [],
            "required_commands": command_rows(found=True),
            "host": {
                "system": "FreeBSD",
                "release": PRIMARY_FREEBSD_RELEASE,
                "machine": "amd64",
                "python_implementation": "CPython",
                "python_version": "3.11.0",
                "effective_uid": 0,
                "kern_osreldate": PRIMARY_FREEBSD_MIN_OSRELDATE,
                "primary_freebsd_release": PRIMARY_FREEBSD_RELEASE,
                "minimum_freebsd_osreldate": PRIMARY_FREEBSD_MIN_OSRELDATE,
                "host_target_tier": "primary-production",
                "host_target_matrix_id": HOST_PROOF_TARGET_MATRIX_ID,
            },
        })
        write_digest_bound_preflight(synthetic_primary_preflight_path, synthetic_primary_preflight)
        no_imported_proof_state = Path(td) / "no-imported-proof-real-state"
        no_imported_proof_real = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(no_imported_proof_state),
            "--mode", "freebsd-real",
            "--host-preflight", str(synthetic_primary_preflight_path),
            "--host-proof-import-root", "validation/freebsd-host-proof-imports",
            "--out", str(Path(td) / "no-imported-proof-real.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, no_imported_proof_real.returncode != 0, "freebsd-real activation must require imported primary-production real-host proof after preflight")
        require(errors, "requires imported primary-production real FreeBSD host proof" in no_imported_proof_real.stderr, "missing imported proof failure should name the proof import requirement")
        require(errors, current_generation(no_imported_proof_state) is None, "missing imported proof must fail before state mutation")

        synthetic_real_handoff = Path(td) / "synthetic-primary-real-handoff"
        build_synthetic_real_handoff(
            synthetic_real_handoff,
            uname_release=PRIMARY_FREEBSD_RELEASE,
            osreldate=str(PRIMARY_FREEBSD_MIN_OSRELDATE),
            host_target_tier=host_contract.HOST_TARGET_PRIMARY_TIER,
        )
        synthetic_import_root = Path(td) / "synthetic-primary-import-root"
        imported_dir = host_importer.import_handoff(synthetic_real_handoff, import_root=synthetic_import_root)
        imported_status_path = Path(td) / "synthetic-host-proof-status.json"
        imported_status = run([
            "host-proof-status",
            "--import-root", str(synthetic_import_root),
            "--out", str(imported_status_path),
            "--fail-if-incomplete",
        ])
        require(errors, imported_status.returncode == 0, f"synthetic primary real-like import should satisfy status gate: {imported_status.stdout} {imported_status.stderr}")
        imported_report = load(imported_status_path)
        require(errors, imported_report.get("proof_complete") is True, "synthetic primary import root should report complete proof")
        items = imported_report.get("items", []) if isinstance(imported_report.get("items"), list) else []
        first_item = items[0] if items and isinstance(items[0], dict) else {}
        require(errors, first_item.get("host_probe_uname_release") == PRIMARY_FREEBSD_RELEASE, "host-proof status item must expose imported proof release")
        require(errors, first_item.get("host_probe_uname_machine") == "amd64", "host-proof status item must expose imported proof machine")
        require(errors, first_item.get("host_probe_osreldate") == str(PRIMARY_FREEBSD_MIN_OSRELDATE), "host-proof status item must expose imported proof osreldate")
        require(errors, first_item.get("host_target_matrix_id") == HOST_PROOF_TARGET_MATRIX_ID, "host-proof status item must expose current target matrix id")

        matching_import_real_state = Path(td) / "matching-import-real-state"
        matching_import_real = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(matching_import_real_state),
            "--mode", "freebsd-real",
            "--host-preflight", str(synthetic_primary_preflight_path),
            "--host-proof-import-root", str(synthetic_import_root),
            "--out", str(Path(td) / "matching-import-real.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, matching_import_real.returncode != 0, "freebsd-real activation remains unimplemented after matched preflight/proof")
        require(errors, "freebsd-real activation backend is not implemented" in matching_import_real.stderr, "matched preflight/proof should reach the explicit backend refusal")
        require(errors, current_generation(matching_import_real_state) is None, "unimplemented real backend refusal must fail before state mutation")

        stale_release_preflight_path = Path(td) / "stale-release-primary-freebsd-preflight.json"
        stale_release_preflight = json.loads(json.dumps(synthetic_primary_preflight))
        stale_release_preflight["host"]["release"] = PRIMARY_FREEBSD_RELEASE + "-stale"
        write_digest_bound_preflight(stale_release_preflight_path, stale_release_preflight)
        stale_release_state = Path(td) / "stale-release-real-state"
        stale_release_real = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(stale_release_state),
            "--mode", "freebsd-real",
            "--host-preflight", str(stale_release_preflight_path),
            "--host-proof-import-root", str(synthetic_import_root),
            "--out", str(Path(td) / "stale-release-real.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, stale_release_real.returncode != 0, "freebsd-real activation must reject imported proof that does not match the admitted preflight release")
        require(errors, "host-proof-preflight-release-mismatch" in stale_release_real.stderr, "stale-release rejection should name the release mismatch")
        require(errors, current_generation(stale_release_state) is None, "mismatched proof/preflight must fail before state mutation")

        require(errors, activation.get("truth_claim", "").startswith("local pointer mutation only"), "activation receipt must state dry-run truth")
        require(errors, rollback.get("state_after", {}).get("current_generation") == activation.get("state_before", {}).get("current_generation"), "rollback receipt must restore pre-activation state")
        precondition = rollback.get("precondition", {}) if isinstance(rollback.get("precondition"), dict) else {}
        require(errors, precondition.get("result") == "passed-before-state-mutation", "rollback receipt must prove its precondition passed before mutation")
        require(errors, precondition.get("current_generation_must_match_activation_state_after") is True, "rollback must be stale-activation guarded")

        chain = explanation.get("digest_chain", {}) if isinstance(explanation.get("digest_chain"), dict) else {}
        require(errors, chain.get("spec_digest") == lock.get("spec", {}).get("digest"), "explain must bind spec digest")
        require(errors, chain.get("lock_digest") == runtime_digest({k: v for k, v in lock.items() if k != "lock_digest"}), "explain must bind live lock digest")
        require(errors, chain.get("plan_digest") == runtime_digest({k: v for k, v in plan.items() if k != "plan_digest"}), "explain must bind live plan digest")
        require(errors, chain.get("artifact_digest") == runtime_digest({k: v for k, v in artifact.items() if k != "artifact_digest"}), "explain must bind live artifact digest")
        require(errors, chain.get("activation_receipt_digest") == runtime_digest({k: v for k, v in activation.items() if k != "activation_receipt_digest"}), "explain must bind live activation digest")
        require(errors, "nginx" in explanation.get("packages", []), "microvm fixture package should survive into explanation")
        require(errors, explanation.get("dependency_packages") == ["openssl", "pcre2"], "explanation must expose transitive dependency packages")
        require(errors, explanation.get("package_closure_policy") == PACKAGE_CLOSURE_POLICY, "explanation must bind the package closure policy")
        require(errors, explanation.get("package_payload_metadata_policy") == PACKAGE_PAYLOAD_METADATA_POLICY, "explanation must bind the package payload metadata policy")
        require(errors, explanation.get("package_repository_snapshot_policy") == PACKAGE_REPOSITORY_SNAPSHOT_POLICY, "explanation must bind the repository snapshot policy")
        require(errors, explanation.get("package_repository_snapshot_digest") == lock.get("resolver", {}).get("package_repository_snapshot_digest"), "explanation must carry the admitted repository snapshot digest")
        require(errors, explanation.get("microvm_instances_planned_not_launched") == ["edge-nginx"], "microvm target should be planned but not launched")

        tampered_lock = Path(td) / "tampered-lock.json"
        tampered_lock_obj = dict(lock)
        tampered_lock_obj["packages"] = [dict(lock["packages"][0], id="tampered-nginx")]
        tampered_lock.write_text(json.dumps(tampered_lock_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tampered_lock_plan = run(["plan", "--lock", str(tampered_lock), "--out", str(Path(td) / "tampered-plan.json"), "--stamp", STAMP])
        require(errors, tampered_lock_plan.returncode != 0, "plan must reject a lock whose content changed without a lock_digest update")
        require(errors, "lock_digest mismatch" in tampered_lock_plan.stderr, "tampered lock failure should name the digest mismatch")

        tampered_plan = Path(td) / "tampered-plan-input.json"
        tampered_plan_obj = dict(plan)
        tampered_plan_obj["blast_radius"] = dict(plan["blast_radius"], host_files_changed=["/etc/rc.conf"])
        tampered_plan.write_text(json.dumps(tampered_plan_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tampered_plan_build = run(["build", "--plan", str(tampered_plan), "--store", str(Path(td) / "tampered-store"), "--out", str(Path(td) / "tampered-artifact.json"), "--stamp", STAMP])
        require(errors, tampered_plan_build.returncode != 0, "build must reject a plan whose blast radius changed without a plan_digest update")
        require(errors, "plan_digest mismatch" in tampered_plan_build.stderr, "tampered plan failure should name the digest mismatch")

        state_dir = Path(paths["state"])
        require(errors, current_generation(state_dir) is None, "golden-thread rollback should leave no current generation after restoring an empty previous state")

        tampered_activation = Path(td) / "tampered-activation.receipt.json"
        tampered_activation_obj = dict(activation)
        tampered_activation_obj["state_before"] = {
            "current_generation": {
                "generation_id": "forged-preactivation-generation",
                "mode": "malicious-local-state",
            }
        }
        tampered_activation.write_text(json.dumps(tampered_activation_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tampered_rollback = run(["rollback", "--receipt", str(tampered_activation), "--state", str(state_dir), "--out", str(Path(td) / "tampered-rollback.receipt.json"), "--stamp", STAMP])
        require(errors, tampered_rollback.returncode != 0, "rollback must reject a tampered activation receipt")
        require(errors, "activation_receipt_digest mismatch" in tampered_rollback.stderr, "tampered rollback failure should name the activation receipt digest mismatch")
        require(errors, current_generation(state_dir) is None, "tampered rollback must fail before mutating the current generation pointer")

        stale_rollback = run(["rollback", "--receipt", paths["activation_receipt"], "--state", str(state_dir), "--out", str(Path(td) / "stale-rollback.receipt.json"), "--stamp", STAMP])
        require(errors, stale_rollback.returncode != 0, "rollback must reject a stale activation receipt when current state has already moved")
        require(errors, "rollback precondition failed" in stale_rollback.stderr, "stale rollback failure should name the precondition")
        require(errors, current_generation(state_dir) is None, "stale rollback must not mutate the current generation pointer")

        bad_artifact = Path(td) / "bad-artifact.json"
        bad_artifact_obj = dict(artifact)
        bad_artifact_obj["spec_digest"] = "sha256:" + "0" * 64
        bad_artifact.write_text(json.dumps(bad_artifact_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        retargeted_activation = Path(td) / "retargeted-activation.receipt.json"
        retargeted_activation_obj = dict(activation)
        retargeted_activation_obj["artifact_path"] = bad_artifact.as_posix()
        retargeted_activation.write_text(json.dumps(retargeted_activation_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        retargeted_explain = run(["explain", "--receipt", str(retargeted_activation), "--out", str(Path(td) / "retargeted-explain.json"), "--stamp", STAMP])
        require(errors, retargeted_explain.returncode != 0, "explain must reject locator retargeting to a digest-mismatched artifact")
        require(errors, "artifact_digest mismatch" in retargeted_explain.stderr, "retargeted explain failure should name the artifact digest mismatch")

        artifact_tree_file = Path(artifact["artifact_path"]) / "activation" / "rc.conf.d" / "derivebsd.conf"
        original_artifact_text = artifact_tree_file.read_text(encoding="utf-8")
        make_artifact_file_writable(artifact_tree_file)
        artifact_tree_file.write_text(original_artifact_text + "# tampered-after-build\n", encoding="utf-8")
        reseal_artifact_file(artifact_tree_file)
        tampered_tree_activate = run(["activate", "--artifact", paths["artifact"], "--state", str(Path(td) / "tampered-tree-state"), "--out", str(Path(td) / "tampered-tree-activation.receipt.json"), "--stamp", STAMP])
        require(errors, tampered_tree_activate.returncode != 0, "activate must reject an artifact whose on-disk tree changed after build")
        require(errors, "artifact tree_manifest mismatch" in tampered_tree_activate.stderr, "tampered artifact tree failure should name the tree manifest mismatch")
        require(errors, current_generation(Path(td) / "tampered-tree-state") is None, "tampered artifact tree activation must fail before writing state")
        make_artifact_file_writable(artifact_tree_file)
        artifact_tree_file.write_text(original_artifact_text, encoding="utf-8")
        reseal_artifact_file(artifact_tree_file)

        symlink_store_target = Path(td) / "symlink-store-target"
        symlink_store_target.mkdir()
        symlink_store = Path(td) / "symlink-store"
        symlink_store.symlink_to(symlink_store_target, target_is_directory=True)
        symlink_store_build = run([
            "build",
            "--plan", paths["plan"],
            "--store", str(symlink_store),
            "--out", str(Path(td) / "symlink-store-artifact.json"),
            "--stamp", STAMP,
        ])
        require(errors, symlink_store_build.returncode != 0, "build must reject symlinked artifact store paths")
        require(errors, "artifact store must not contain existing symlink components" in symlink_store_build.stderr, "symlinked store rejection should name the store symlink guard")
        require(errors, list(symlink_store_target.iterdir()) == [], "symlinked store rejection must fail before writing through the link")

        symlink_state_target = Path(td) / "symlink-state-target"
        symlink_state_target.mkdir()
        symlink_state = Path(td) / "symlink-state"
        symlink_state.symlink_to(symlink_state_target, target_is_directory=True)
        symlink_state_activate = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(symlink_state),
            "--out", str(Path(td) / "symlink-state-activation.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, symlink_state_activate.returncode != 0, "activate must reject symlinked state directories")
        require(errors, "state directory must not contain existing symlink components" in symlink_state_activate.stderr, "symlinked state rejection should name the state symlink guard")
        require(errors, list(symlink_state_target.iterdir()) == [], "symlinked state rejection must fail before writing through the link")

        state_with_symlink_generations = Path(td) / "state-with-symlink-generations"
        state_with_symlink_generations.mkdir()
        symlink_generations_target = Path(td) / "symlink-generations-target"
        symlink_generations_target.mkdir()
        (state_with_symlink_generations / "generations").symlink_to(symlink_generations_target, target_is_directory=True)
        symlink_generations_activate = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(state_with_symlink_generations),
            "--out", str(Path(td) / "symlink-generations-activation.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, symlink_generations_activate.returncode != 0, "activate must reject symlinked generation stores inside the state directory")
        require(errors, "generations directory must not contain existing symlink components" in symlink_generations_activate.stderr, "symlink generations rejection should name the generations symlink guard")
        require(errors, list(symlink_generations_target.iterdir()) == [], "symlinked generations rejection must fail before writing through the link")

        state_with_symlink_pointer = Path(td) / "state-with-symlink-pointer"
        state_with_symlink_pointer.mkdir()
        symlink_pointer_target = Path(td) / "symlink-current-generation-target.json"
        symlink_pointer_target.write_text("{\"forged\":true}\n", encoding="utf-8")
        (state_with_symlink_pointer / "current-generation.json").symlink_to(symlink_pointer_target)
        symlink_pointer_activate = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(state_with_symlink_pointer),
            "--out", str(Path(td) / "symlink-pointer-activation.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, symlink_pointer_activate.returncode != 0, "activate must reject symlinked current-generation pointers")
        require(errors, "current generation pointer must not contain existing symlink components" in symlink_pointer_activate.stderr, "symlink pointer rejection should name the pointer symlink guard")
        require(errors, not (state_with_symlink_pointer / "generations").exists(), "symlinked pointer rejection must fail before creating a generation store")
        require(errors, symlink_pointer_target.read_text(encoding="utf-8") == "{\"forged\":true}\n", "symlinked pointer rejection must not overwrite the linked target")

        symlink_artifact_target = Path(td) / "symlink-artifact-target.txt"
        symlink_artifact_target.write_text(original_artifact_text, encoding="utf-8")
        make_artifact_file_writable(artifact_tree_file)
        artifact_tree_file.unlink()
        artifact_tree_file.symlink_to(symlink_artifact_target)
        artifact_tree_file.parent.chmod(0o555)
        symlink_artifact_activate = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(Path(td) / "symlink-artifact-state"),
            "--out", str(Path(td) / "symlink-artifact-activation.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, symlink_artifact_activate.returncode != 0, "activate must reject symlink members inside artifact trees")
        require(errors, "artifact tree must not contain symlink entries" in symlink_artifact_activate.stderr, "symlink artifact rejection should name the artifact symlink guard")
        require(errors, current_generation(Path(td) / "symlink-artifact-state") is None, "symlink artifact activation must fail before writing state")
        artifact_tree_file.parent.chmod(0o755)
        artifact_tree_file.unlink()
        artifact_tree_file.write_text(original_artifact_text, encoding="utf-8")
        reseal_artifact_file(artifact_tree_file)

        artifact_tree_dir = artifact_tree_file.parent
        artifact_tree_dir.chmod(0o755)
        writable_dir_activate = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(Path(td) / "writable-artifact-dir-state"),
            "--out", str(Path(td) / "writable-artifact-dir-activation.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, writable_dir_activate.returncode != 0, "activate must reject writable directories inside sealed artifact trees")
        require(errors, "artifact directory must be sealed read-only" in writable_dir_activate.stderr, "writable artifact directory rejection should name the sealed directory guard")
        require(errors, current_generation(Path(td) / "writable-artifact-dir-state") is None, "writable artifact directory activation must fail before writing state")
        artifact_tree_dir.chmod(0o555)

        make_artifact_file_writable(artifact_tree_file)
        reseal_artifact_file(artifact_tree_file)
        artifact_tree_file.chmod(0o644)
        writable_file_activate = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(Path(td) / "writable-artifact-file-state"),
            "--out", str(Path(td) / "writable-artifact-file-activation.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, writable_file_activate.returncode != 0, "activate must reject writable files inside sealed artifact trees")
        require(errors, "artifact file must be sealed read-only" in writable_file_activate.stderr, "writable artifact file rejection should name the sealed file guard")
        require(errors, current_generation(Path(td) / "writable-artifact-file-state") is None, "writable artifact file activation must fail before writing state")
        artifact_tree_file.chmod(0o444)

        artifact_hardlink = Path(td) / "derivebsd-artifact-hardlink-alias.conf"
        os.link(artifact_tree_file, artifact_hardlink)
        hardlink_alias_activate = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(Path(td) / "hardlink-alias-state"),
            "--out", str(Path(td) / "hardlink-alias-activation.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, hardlink_alias_activate.returncode != 0, "activate must reject hardlink-aliased files inside sealed artifact trees")
        require(errors, "artifact file must not have hardlink aliases" in hardlink_alias_activate.stderr, "hardlink alias rejection should name the hardlink guard")
        require(errors, current_generation(Path(td) / "hardlink-alias-state") is None, "hardlink alias activation must fail before writing state")
        artifact_hardlink.unlink()

        lock_guard_state = Path(td) / "lock-guard-state"
        lock_guard_activation_path = Path(td) / "lock-guard-activation.receipt.json"
        lock_guard_first = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(lock_guard_state),
            "--out", str(lock_guard_activation_path),
            "--stamp", STAMP,
        ])
        require(errors, lock_guard_first.returncode == 0, "lock guard setup activation should succeed")
        lock_guard_generation = current_generation(lock_guard_state)
        require(errors, lock_guard_generation is not None, "lock guard setup should create a current generation")
        require(errors, not (lock_guard_state / STATE_LOCK_NAME).exists(), "successful activation must release the state mutation lock")
        require(errors, not (lock_guard_state / STATE_JOURNAL_NAME).exists(), "successful activation must remove the state mutation journal")
        (lock_guard_state / STATE_LOCK_NAME).write_text("stale writer lock fixture\n", encoding="utf-8")
        locked_activate_state_before = current_generation(lock_guard_state)
        locked_activate = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(lock_guard_state),
            "--out", str(Path(td) / "locked-activation.receipt.json"),
            "--stamp", "2026-06-18T00:00:01Z",
        ])
        require(errors, locked_activate.returncode != 0, "activate must fail closed when another state mutation lock exists")
        require(errors, "state mutation lock already exists" in locked_activate.stderr, "locked activation failure should name the state mutation lock")
        require(errors, current_generation(lock_guard_state) == locked_activate_state_before, "locked activation must not change current generation")
        (lock_guard_state / STATE_LOCK_NAME).unlink()

        duplicate_generation = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(lock_guard_state),
            "--out", str(Path(td) / "duplicate-generation-activation.receipt.json"),
            "--stamp", STAMP,
        ])
        require(errors, duplicate_generation.returncode != 0, "same artifact/stamp activation must not clobber an existing generation receipt")
        require(errors, "exclusive output path already exists" in duplicate_generation.stderr, "duplicate generation failure should name the exclusive receipt path")
        require(errors, current_generation(lock_guard_state) == locked_activate_state_before, "duplicate generation refusal must leave current generation unchanged")
        require(errors, not (lock_guard_state / STATE_LOCK_NAME).exists(), "duplicate generation refusal must release the state mutation lock")
        require(errors, not (lock_guard_state / STATE_JOURNAL_NAME).exists(), "duplicate generation refusal must not leave a state mutation journal")

        artifact_root = Path(artifact["artifact_path"])
        artifact_inode_before = artifact_root.stat().st_ino
        rebuild_artifact_path = Path(td) / "rebuilt-same-artifact.json"
        rebuilt = run([
            "build",
            "--plan", paths["plan"],
            "--store", paths["store"],
            "--out", str(rebuild_artifact_path),
            "--stamp", STAMP,
        ])
        require(errors, rebuilt.returncode == 0, "same artifact rebuild should reuse the content-addressed object")
        if rebuilt.returncode == 0:
            rebuilt_artifact = load(rebuild_artifact_path)
            require(errors, rebuilt_artifact.get("artifact_path") == artifact.get("artifact_path"), "same artifact rebuild must keep the same CAS path")
            require(errors, rebuilt_artifact.get("artifact_digest") == artifact.get("artifact_digest"), "same artifact rebuild must keep the same artifact digest")
            require(errors, artifact_root.stat().st_ino == artifact_inode_before, "same artifact rebuild must not delete and republish the existing CAS tree")
            require(errors, rebuilt_artifact.get("activation_surface", {}).get("artifact_publish_result", "").startswith("reused-existing"), "same artifact rebuild should report exact existing CAS reuse")

        state_readback_probe = Path(td) / "state-readback-probe"
        state_readback_probe.mkdir()
        original_write_current_generation = runtime.write_current_generation
        try:
            runtime.write_current_generation = lambda state_dir, generation: None  # type: ignore[assignment]
            try:
                runtime.commit_current_generation(state_readback_probe, {"generation_id": "fault-injected"}, operation="fault-probe")
            except runtime.DeriveRuntimeError as exc:
                require(errors, "commit readback mismatch" in str(exc), "commit helper must reject missing or mismatched current-generation readback")
            else:
                require(errors, False, "commit helper must not report success when current-generation was not written")
        finally:
            runtime.write_current_generation = original_write_current_generation  # type: ignore[assignment]

        replacement_lock_state = Path(td) / "replacement-lock-state"
        replacement_lock_state.mkdir()
        try:
            with runtime.acquire_state_mutation_lock(replacement_lock_state, operation="fault-probe", stamp=STAMP):
                replacement_lock_path = replacement_lock_state / STATE_LOCK_NAME
                replacement_lock_path.unlink()
                replacement_lock_path.write_text("replacement lock from another owner\n", encoding="utf-8")
        except runtime.DeriveRuntimeError as exc:
            require(errors, "lock ownership changed" in str(exc), "lock release must detect ownership changes")
        else:
            require(errors, False, "lock release must fail if the lock pathname was replaced")
        require(errors, (replacement_lock_state / STATE_LOCK_NAME).exists(), "lock release must not delete a replacement lock")
        (replacement_lock_state / STATE_LOCK_NAME).unlink()

        malformed_status_state = Path(td) / "malformed-journal-state"
        malformed_status_state.mkdir()
        (malformed_status_state / STATE_JOURNAL_NAME).write_text("malformed journal fixture\n", encoding="utf-8")
        malformed_status_path = Path(td) / "malformed-journal-status.json"
        malformed_status = run([
            "state-status",
            "--state", str(malformed_status_state),
            "--out", str(malformed_status_path),
            "--stamp", STAMP,
        ])
        require(errors, malformed_status.returncode == 0, "state-status must inspect malformed pending journals without mutating state")
        if malformed_status.returncode == 0:
            malformed_status_report = load(malformed_status_path)
            require(errors, malformed_status_report.get("pending_journal") is True, "state-status must report a pending journal")
            require(errors, malformed_status_report.get("status") == "journal-pending-malformed", "state-status must classify malformed journals")
            require(errors, malformed_status_report.get("recovery_action") == "quarantine-state-dir-and-review-malformed-journal", "state-status must name quarantine for malformed journals")

        journal_guard_state = Path(td) / "journal-guard-state"
        journal_guard_state.mkdir()
        (journal_guard_state / STATE_JOURNAL_NAME).write_text("interrupted precommit journal fixture\n", encoding="utf-8")
        stale_journal_activate = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(journal_guard_state),
            "--out", str(Path(td) / "stale-journal-activation.receipt.json"),
            "--stamp", "2026-06-18T00:00:05Z",
        ])
        require(errors, stale_journal_activate.returncode != 0, "activate must fail closed when a pending state mutation journal exists")
        require(errors, "state mutation journal already exists" in stale_journal_activate.stderr, "stale journal activation failure should name the pending journal")
        require(errors, current_generation(journal_guard_state) is None, "stale journal activation must not create a current generation")
        require(errors, (journal_guard_state / STATE_JOURNAL_NAME).exists(), "stale journal activation must not delete the pending journal")
        require(errors, not (journal_guard_state / STATE_LOCK_NAME).exists(), "stale journal activation must not leave a state lock")

        rollback_lock_state = Path(td) / "rollback-lock-state"
        rollback_lock_activation_path = Path(td) / "rollback-lock-activation.receipt.json"
        rollback_setup = run([
            "activate",
            "--artifact", paths["artifact"],
            "--state", str(rollback_lock_state),
            "--out", str(rollback_lock_activation_path),
            "--stamp", "2026-06-18T00:00:02Z",
        ])
        require(errors, rollback_setup.returncode == 0, "rollback lock setup activation should succeed")
        rollback_state_before_lock = current_generation(rollback_lock_state)
        (rollback_lock_state / STATE_LOCK_NAME).write_text("stale rollback lock fixture\n", encoding="utf-8")
        locked_rollback = run([
            "rollback",
            "--receipt", str(rollback_lock_activation_path),
            "--state", str(rollback_lock_state),
            "--out", str(Path(td) / "locked-rollback.receipt.json"),
            "--stamp", "2026-06-18T00:00:03Z",
        ])
        require(errors, locked_rollback.returncode != 0, "rollback must fail closed when another state mutation lock exists")
        require(errors, "state mutation lock already exists" in locked_rollback.stderr, "locked rollback failure should name the state mutation lock")
        require(errors, current_generation(rollback_lock_state) == rollback_state_before_lock, "locked rollback must not change current generation")
        (rollback_lock_state / STATE_LOCK_NAME).unlink()
        (rollback_lock_state / STATE_JOURNAL_NAME).write_text("interrupted rollback journal fixture\n", encoding="utf-8")
        rollback_before_stale_journal = current_generation(rollback_lock_state)
        stale_journal_rollback = run([
            "rollback",
            "--receipt", str(rollback_lock_activation_path),
            "--state", str(rollback_lock_state),
            "--out", str(Path(td) / "stale-journal-rollback.receipt.json"),
            "--stamp", "2026-06-18T00:00:04Z",
        ])
        require(errors, stale_journal_rollback.returncode != 0, "rollback must fail closed when a pending state mutation journal exists")
        require(errors, "state mutation journal already exists" in stale_journal_rollback.stderr, "stale journal rollback failure should name the pending journal")
        require(errors, current_generation(rollback_lock_state) == rollback_before_stale_journal, "stale journal rollback must not change current generation")
        require(errors, (rollback_lock_state / STATE_JOURNAL_NAME).exists(), "stale journal rollback must not delete the pending journal")
        (rollback_lock_state / STATE_JOURNAL_NAME).unlink()
        rollback_after_unlock = run([
            "rollback",
            "--receipt", str(rollback_lock_activation_path),
            "--state", str(rollback_lock_state),
            "--out", str(Path(td) / "rollback-after-unlock.receipt.json"),
            "--stamp", "2026-06-18T00:00:06Z",
        ])
        require(errors, rollback_after_unlock.returncode == 0, "rollback should succeed after the exclusive state lock is removed")
        require(errors, not (rollback_lock_state / STATE_LOCK_NAME).exists(), "successful rollback must release the state mutation lock")
        require(errors, not (rollback_lock_state / STATE_JOURNAL_NAME).exists(), "successful rollback must remove the state mutation journal")

        second_workspace = Path(td) / "same-spec-second-workspace"
        second_summary_path = Path(td) / "same-spec-second-summary.json"
        second = run([
            "run-golden-thread",
            "--spec", "spec/examples/microvm.spec.json",
            "--workspace", str(second_workspace),
            "--out", str(second_summary_path),
            "--stamp", STAMP,
        ])
        if second.returncode != 0:
            errors.append(f"same-spec second workspace run should succeed, stderr={second.stderr!r}")
        else:
            second_summary = load(second_summary_path)
            require(errors, second_summary.get("digests") == summary.get("digests"), "same spec and stamp must produce identical runtime digests in different workspaces")
            require(errors, second_summary.get("run_digest") == summary.get("run_digest"), "run digest must ignore local workspace paths")
            require(errors, second_summary.get("paths") != summary.get("paths"), "test fixture should actually use distinct local paths")

        copied_catalog = Path(td) / "copied-runtime-package-catalog.json"
        copied_catalog.write_text((ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json").read_text(encoding="utf-8"), encoding="utf-8")
        copied_catalog_summary_path = Path(td) / "copied-catalog-summary.json"
        copied_catalog_workspace = Path(td) / "copied-catalog-workspace"
        copied_catalog_run = run([
            "run-golden-thread",
            "--spec", "spec/examples/microvm.spec.json",
            "--package-catalog", str(copied_catalog),
            "--workspace", str(copied_catalog_workspace),
            "--out", str(copied_catalog_summary_path),
            "--stamp", STAMP,
        ])
        if copied_catalog_run.returncode != 0:
            errors.append(f"same catalog content at a different path should succeed, stderr={copied_catalog_run.stderr!r}")
        else:
            copied_catalog_summary = load(copied_catalog_summary_path)
            require(errors, copied_catalog_summary.get("digests") == summary.get("digests"), "same catalog content at another path must not change runtime digests")

        # Negative guard: package id changes must change the spec/lock side of the chain.
        mutated_spec = Path(td) / "mutated.spec.json"
        data = load(ROOT / "spec/examples/microvm.spec.json")
        data["packages"][0]["id"] = "lighttpd"
        mutated_spec.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        mutated_workspace = Path(td) / "mutated"
        mutated_summary_path = Path(td) / "mutated-summary.json"
        mutated = run([
            "run-golden-thread",
            "--spec", str(mutated_spec),
            "--workspace", str(mutated_workspace),
            "--out", str(mutated_summary_path),
            "--stamp", STAMP,
        ])
        if mutated.returncode != 0:
            errors.append(f"mutated spec run should still succeed, stderr={mutated.stderr!r}")
        else:
            mutated_summary = load(mutated_summary_path)
            require(errors, mutated_summary.get("digests", {}).get("spec") != summary.get("digests", {}).get("spec"), "spec digest must change after package mutation")
            require(errors, mutated_summary.get("digests", {}).get("lock") != summary.get("digests", {}).get("lock"), "lock digest must change after package mutation")

        unknown_spec = Path(td) / "unknown-package.spec.json"
        unknown_data = load(ROOT / "spec/examples/microvm.spec.json")
        unknown_data["packages"] = [{"id": "definitely-not-in-runtime-catalog"}]
        unknown_spec.write_text(json.dumps(unknown_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        unknown_lock = run([
            "lock",
            "--spec", str(unknown_spec),
            "--out", str(Path(td) / "unknown-lock.json"),
            "--stamp", STAMP,
        ])
        require(errors, unknown_lock.returncode != 0, "lock must reject packages absent from the finite offline fixture catalog")
        require(errors, "not present in the offline package catalog" in unknown_lock.stderr, "unknown package rejection must name the finite catalog miss")

        bad_catalog = Path(td) / "bad-runtime-package-catalog.json"
        bad_catalog_obj = load(ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json")
        bad_catalog_obj["platforms"]["freebsd-15.1-amd64"]["packages"]["nginx"]["version"] = "tampered-after-digest"
        bad_catalog.write_text(json.dumps(bad_catalog_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        bad_catalog_lock = run([
            "lock",
            "--spec", "spec/examples/microvm.spec.json",
            "--package-catalog", str(bad_catalog),
            "--out", str(Path(td) / "bad-catalog-lock.json"),
            "--stamp", STAMP,
        ])
        require(errors, bad_catalog_lock.returncode != 0, "lock must reject a package catalog changed without catalog_digest refresh")
        require(errors, "package catalog_digest mismatch" in bad_catalog_lock.stderr, "tampered catalog rejection must name catalog_digest mismatch")

        bad_material_catalog = Path(td) / "bad-material-runtime-package-catalog.json"
        bad_material_obj = load(ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json")
        bad_material_obj["platforms"]["freebsd-15.1-amd64"]["packages"]["nginx"]["material"]["sha256"] = "sha256:" + "0" * 64
        bad_material_obj["catalog_digest"] = package_catalog_digest(bad_material_obj)
        bad_material_catalog.write_text(json.dumps(bad_material_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        bad_material_lock = run([
            "lock",
            "--spec", "spec/examples/microvm.spec.json",
            "--package-catalog", str(bad_material_catalog),
            "--out", str(Path(td) / "bad-material-lock.json"),
            "--stamp", STAMP,
        ])
        require(errors, bad_material_lock.returncode != 0, "lock must reject catalog material whose bound sha256 does not match the checked-in bytes")
        require(errors, "material sha256 mismatch" in bad_material_lock.stderr, "bad material failure must name the sha256 mismatch")

        stale_snapshot_catalog = Path(td) / "stale-snapshot-runtime-package-catalog.json"
        stale_snapshot_obj = load(ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json")
        stale_snapshot_rel, stale_snapshot_path, stale_snapshot_data = write_snapshot_variant(
            "stale-snapshot",
            lambda obj: obj.__setitem__("truth_claim", obj.get("truth_claim", "") + " stale-sha-negative-test"),
        )
        try:
            stale_snapshot_obj["repository_snapshot"] = {
                "path": stale_snapshot_rel,
                "sha256": runtime.sha256_bytes(stale_snapshot_path.read_bytes()),
                "snapshot_digest": stale_snapshot_data["snapshot_digest"],
                "policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
            }
            stale_snapshot_obj["catalog_digest"] = package_catalog_digest(stale_snapshot_obj)
            stale_snapshot_catalog.write_text(json.dumps(stale_snapshot_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            stale_snapshot_data["truth_claim"] = stale_snapshot_data.get("truth_claim", "") + " changed-after-catalog-digest"
            stale_snapshot_data["snapshot_digest"] = package_repository_snapshot_digest(stale_snapshot_data)
            stale_snapshot_path.write_text(json.dumps(stale_snapshot_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            stale_snapshot_lock = run([
                "lock",
                "--spec", "spec/examples/microvm.spec.json",
                "--package-catalog", str(stale_snapshot_catalog),
                "--out", str(Path(td) / "stale-snapshot-lock.json"),
                "--stamp", STAMP,
            ])
        finally:
            stale_snapshot_path.unlink(missing_ok=True)
        require(errors, stale_snapshot_lock.returncode != 0, "lock must reject repository snapshots changed after catalog admission metadata was written")
        require(errors, "package repository snapshot sha256 mismatch" in stale_snapshot_lock.stderr, "stale snapshot failure must name the snapshot sha256 mismatch")

        snapshot_projection_catalog = Path(td) / "snapshot-projection-runtime-package-catalog.json"
        snapshot_projection_obj = load(ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json")
        snapshot_projection_rel, snapshot_projection_path, snapshot_projection_data = write_snapshot_variant(
            "projection-mismatch",
            lambda obj: obj["platforms"]["freebsd-15.1-amd64"]["packages"]["nginx"].__setitem__("runtime_dependencies", []),
        )
        try:
            snapshot_projection_obj["repository_snapshot"] = {
                "path": snapshot_projection_rel,
                "sha256": runtime.sha256_bytes(snapshot_projection_path.read_bytes()),
                "snapshot_digest": snapshot_projection_data["snapshot_digest"],
                "policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
            }
            snapshot_projection_obj["catalog_digest"] = package_catalog_digest(snapshot_projection_obj)
            snapshot_projection_catalog.write_text(json.dumps(snapshot_projection_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            snapshot_projection_lock = run([
                "lock",
                "--spec", "spec/examples/microvm.spec.json",
                "--package-catalog", str(snapshot_projection_catalog),
                "--out", str(Path(td) / "snapshot-projection-lock.json"),
                "--stamp", STAMP,
            ])
        finally:
            snapshot_projection_path.unlink(missing_ok=True)
        require(errors, snapshot_projection_lock.returncode != 0, "lock must reject repository snapshot rows that drift from consumed package payload metadata")
        require(errors, "fixture payload dependencies do not match repository snapshot" in snapshot_projection_lock.stderr, "snapshot projection failure must name payload/snapshot dependency drift")

        projection_mismatch_catalog = Path(td) / "projection-mismatch-runtime-package-catalog.json"
        projection_mismatch_obj = load(ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json")
        projection_mismatch_obj["platforms"]["freebsd-15.1-amd64"]["packages"]["nginx"]["dependencies"] = []
        projection_mismatch_obj["catalog_digest"] = package_catalog_digest(projection_mismatch_obj)
        projection_mismatch_catalog.write_text(json.dumps(projection_mismatch_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        projection_mismatch_lock = run([
            "lock",
            "--spec", "spec/examples/microvm.spec.json",
            "--package-catalog", str(projection_mismatch_catalog),
            "--out", str(Path(td) / "projection-mismatch-lock.json"),
            "--stamp", STAMP,
        ])
        require(errors, projection_mismatch_lock.returncode != 0, "lock must reject catalog rows that drift from fixture payload dependency metadata")
        require(errors, "catalog dependencies do not match fixture payload runtime_dependencies" in projection_mismatch_lock.stderr, "projection mismatch failure must name catalog/payload dependency drift")

        missing_dep_catalog = Path(td) / "missing-dependency-runtime-package-catalog.json"
        missing_dep_obj = load(ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json")
        missing_dep_rel, missing_dep_payload = write_payload_variant(
            "nginx-missing-dep",
            "validation/runtime-materials/current/packages/nginx-1.26.3_1-fixture.pkg",
            lambda obj: obj["runtime_dependencies"].append("definitely-not-in-runtime-catalog"),
        )
        try:
            missing_dep_payload_obj = load(missing_dep_payload)
            entry = missing_dep_obj["platforms"]["freebsd-15.1-amd64"]["packages"]["nginx"]
            entry["dependencies"] = ["openssl", "pcre2", "definitely-not-in-runtime-catalog"]
            entry["material"]["path"] = missing_dep_rel
            entry["material"]["sha256"] = runtime.sha256_bytes(missing_dep_payload.read_bytes())
            entry["material"]["size_bytes"] = missing_dep_payload.stat().st_size
            missing_dep_snapshot_rel, missing_dep_snapshot_path, missing_dep_snapshot = write_snapshot_variant(
                "missing-dep-snapshot",
                lambda obj: obj["platforms"]["freebsd-15.1-amd64"]["packages"]["nginx"].update({
                    "fixture_payload_digest": runtime.canonical_digest(missing_dep_payload_obj),
                    "material": dict(entry["material"]),
                    "runtime_dependencies": ["openssl", "pcre2", "definitely-not-in-runtime-catalog"],
                }),
            )
            missing_dep_obj["repository_snapshot"] = {
                "path": missing_dep_snapshot_rel,
                "sha256": runtime.sha256_bytes(missing_dep_snapshot_path.read_bytes()),
                "snapshot_digest": missing_dep_snapshot["snapshot_digest"],
                "policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
            }
            missing_dep_obj["catalog_digest"] = package_catalog_digest(missing_dep_obj)
            missing_dep_catalog.write_text(json.dumps(missing_dep_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            missing_dep_lock = run([
                "lock",
                "--spec", "spec/examples/microvm.spec.json",
                "--package-catalog", str(missing_dep_catalog),
                "--out", str(Path(td) / "missing-dependency-lock.json"),
                "--stamp", STAMP,
            ])
        finally:
            missing_dep_payload.unlink(missing_ok=True)
            if "missing_dep_snapshot_path" in locals():
                missing_dep_snapshot_path.unlink(missing_ok=True)
        require(errors, missing_dep_lock.returncode != 0, "lock must reject payload dependency edges whose target package is absent")
        require(errors, "dependency package" in missing_dep_lock.stderr and "not present in the offline package catalog" in missing_dep_lock.stderr, "missing dependency failure must name the absent dependency")

        cycle_catalog = Path(td) / "cycle-runtime-package-catalog.json"
        cycle_obj = load(ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json")
        cycle_rel, cycle_payload = write_payload_variant(
            "pcre2-cycle",
            "validation/runtime-materials/current/packages/pcre2-10.43-fixture.pkg",
            lambda obj: obj.__setitem__("runtime_dependencies", ["nginx"]),
        )
        try:
            cycle_payload_obj = load(cycle_payload)
            entry = cycle_obj["platforms"]["freebsd-15.1-amd64"]["packages"]["pcre2"]
            entry["dependencies"] = ["nginx"]
            entry["material"]["path"] = cycle_rel
            entry["material"]["sha256"] = runtime.sha256_bytes(cycle_payload.read_bytes())
            entry["material"]["size_bytes"] = cycle_payload.stat().st_size
            cycle_snapshot_rel, cycle_snapshot_path, cycle_snapshot = write_snapshot_variant(
                "cycle-snapshot",
                lambda obj: obj["platforms"]["freebsd-15.1-amd64"]["packages"]["pcre2"].update({
                    "fixture_payload_digest": runtime.canonical_digest(cycle_payload_obj),
                    "material": dict(entry["material"]),
                    "runtime_dependencies": ["nginx"],
                }),
            )
            cycle_obj["repository_snapshot"] = {
                "path": cycle_snapshot_rel,
                "sha256": runtime.sha256_bytes(cycle_snapshot_path.read_bytes()),
                "snapshot_digest": cycle_snapshot["snapshot_digest"],
                "policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
            }
            cycle_obj["catalog_digest"] = package_catalog_digest(cycle_obj)
            cycle_catalog.write_text(json.dumps(cycle_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            cycle_lock = run([
                "lock",
                "--spec", "spec/examples/microvm.spec.json",
                "--package-catalog", str(cycle_catalog),
                "--out", str(Path(td) / "cycle-lock.json"),
                "--stamp", STAMP,
            ])
        finally:
            cycle_payload.unlink(missing_ok=True)
            if "cycle_snapshot_path" in locals():
                cycle_snapshot_path.unlink(missing_ok=True)
        require(errors, cycle_lock.returncode != 0, "lock must reject dependency cycles in the fixture payload closure")
        require(errors, "package dependency cycle detected" in cycle_lock.stderr, "cycle failure must name dependency cycle detection")

        latest_spec = Path(td) / "latest-microvm.spec.json"
        latest_spec_obj = load(ROOT / "spec/examples/microvm.spec.json")
        latest_spec_obj["targets"]["microvms"][0]["image"]["closure"] = "services/nginx:latest"
        latest_spec.write_text(json.dumps(latest_spec_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        latest_lock = run([
            "lock",
            "--spec", str(latest_spec),
            "--out", str(Path(td) / "latest-lock.json"),
            "--stamp", STAMP,
        ])
        require(errors, latest_lock.returncode != 0, "lock must reject microvm closures that use latest tags")
        require(errors, "must not use a latest tag" in latest_lock.stderr, "latest closure rejection must name the mutable latest tag")

    if errors:
        print("runtime golden thread check FAILED")
        for error in errors:
            print("-", error)
        return 1
    print("runtime golden thread check passed")
    print("Spec -> Lock -> Plan -> Artifact -> Activate -> Explain -> Rollback ran in dry-run mode with no FreeBSD mutation claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
