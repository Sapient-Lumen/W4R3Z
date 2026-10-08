#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
PROBE_OUT = ROOT / "artifacts" / "probe-results"
OUT.mkdir(parents=True, exist_ok=True)
PROBE_OUT.mkdir(parents=True, exist_ok=True)

# Reuse the mature public trace provenance and score-contract verifier. This
# tool adds a human/operator verdict layer plus a content-addressed receipt:
# selector entry is bound to exact file/tool digests, not the filesystem names
# that happened to exist during capture.
sys.path.insert(0, str(ROOT / "experiments" / "public_trace_gate_surrogate"))
try:
    from public_trace_gate_surrogate import validate_public_trace_provenance  # type: ignore
except Exception as exc:  # pragma: no cover - import failure is reported as audit failure
    validate_public_trace_provenance = None  # type: ignore[assignment]
    IMPORT_ERROR = repr(exc)
else:
    IMPORT_ERROR = None

RECEIPT_CONTRACT = "public_trace_evaluation_receipt_v2"
TRACE_IDENTITY_RECEIPT_CONTRACT = "public_trace_downstream_identity_receipt_v1"
EVALUATOR_REL = "tools/public_trace_evaluation_verdict_audit.py"
VERIFIER_REL = "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py"

TRACE_IDENTITY_FIELDS = [
    "trace_claim_version",
    "public_pretrained_trace",
    "model_id",
    "model_revision",
    "tokenizer_revision",
    "source_type",
    "schema",
    "trace_npz_sha256",
    "model_load_source",
    "model_load_source_is_local_path",
    "snapshot_digest_authenticity_contract",
    "snapshot_digest_authenticity_required",
    "snapshot_digest_authenticity_verified",
    "loader_snapshot_binding_contract",
    "loader_snapshot_binding_required",
    "loader_snapshot_binding_verified",
    "model_load_source_resolved_path",
    "verified_snapshot_path",
    "model_safetensors_sha256",
    "expected_model_safetensors_sha256",
    "model_safetensors_sha256_matches_expected",
    "prompt_manifest_contract",
    "prompt_manifest_sha256",
    "prompt_count",
    "tokenization_settings_sha256",
    "token_provenance_contract",
    "token_provenance_verified",
    "generation_config_sha256",
    "generation_determinism_contract",
    "generation_determinism_verified",
    "cache_implementation_contract",
    "generation_cache_implementation",
    "generation_cache_implementation_source",
    "generation_token_contract",
    "generation_token_provenance_verified",
    "generated_new_token_count_min",
    "generated_new_token_count_max",
    "capture_phase_contract",
    "prefill_phase_present",
    "decode_phase_present",
    "cache_decode_verified",
    "runtime_provenance_contract",
    "runtime_provenance_verified",
]


def _is_hex_sha256(value: object) -> bool:
    text = str(value or "").strip().lower()
    return len(text) == 64 and all(c in "0123456789abcdef" for c in text)


def _stable_identity_subset(record: dict[str, Any], keys: list[str] = TRACE_IDENTITY_FIELDS) -> dict[str, Any]:
    return {key: record.get(key) for key in keys if key in record}


def _trace_identity_summary(provenance_status: dict[str, Any]) -> dict[str, Any]:
    """Compact the accepted verifier result into receipt-level identity facts.

    The full provenance JSON and NPZ are still the source of truth, but the
    selector and handoff receipts should not hide the model/prompt/generation
    identity behind a single boolean. This summary is small enough to replay
    downstream and prevents a receipt from saying only "verifier accepted"
    while omitting which selected snapshot, prompt manifest, and cache/generation
    contract were accepted.
    """
    manifest = provenance_status.get("manifest") if isinstance(provenance_status, dict) else {}
    if not isinstance(manifest, dict):
        manifest = {}
    npz_status = provenance_status.get("npz_metadata_status") if isinstance(provenance_status, dict) else {}
    npz_meta = npz_status.get("metadata") if isinstance(npz_status, dict) else {}
    if not isinstance(npz_meta, dict):
        npz_meta = {}
    errors: list[str] = []
    warnings: list[str] = []
    loader_status = provenance_status.get("loader_snapshot_binding_status", {}) if isinstance(provenance_status, dict) else {}
    manifest_loader_errors = list(loader_status.get("manifest_errors", [])) if isinstance(loader_status, dict) else []
    npz_loader_errors = list(loader_status.get("npz_errors", [])) if isinstance(loader_status, dict) else []
    mismatches: dict[str, dict[str, Any]] = {}
    for key in TRACE_IDENTITY_FIELDS:
        if key in manifest and key in npz_meta and str(manifest.get(key)) != str(npz_meta.get(key)):
            mismatches[key] = {"manifest": manifest.get(key), "npz": npz_meta.get(key)}
    errors.extend("manifest loader binding: " + str(e) for e in manifest_loader_errors)
    errors.extend("NPZ loader binding: " + str(e) for e in npz_loader_errors)
    for key in [
        "model_id", "model_revision", "tokenizer_revision", "trace_npz_sha256",
        "model_load_source_resolved_path", "verified_snapshot_path", "model_safetensors_sha256",
        "expected_model_safetensors_sha256", "prompt_manifest_sha256",
        "generation_config_sha256", "tokenization_settings_sha256",
    ]:
        if not str(manifest.get(key, "")).strip():
            errors.append(f"manifest missing downstream identity field: {key}")
    for key in ["trace_npz_sha256", "model_safetensors_sha256", "expected_model_safetensors_sha256", "prompt_manifest_sha256", "generation_config_sha256", "tokenization_settings_sha256"]:
        if key in manifest and not _is_hex_sha256(manifest.get(key)):
            errors.append(f"manifest {key} must be SHA-256 hex")
    if manifest.get("snapshot_digest_authenticity_verified") is not True:
        errors.append("snapshot_digest_authenticity_verified must be true in downstream identity receipt")
    if manifest.get("loader_snapshot_binding_verified") is not True:
        errors.append("loader_snapshot_binding_verified must be true in downstream identity receipt")
    if manifest.get("model_safetensors_sha256_matches_expected") is not True:
        errors.append("model_safetensors_sha256_matches_expected must be true in downstream identity receipt")
    if str(manifest.get("model_load_source_resolved_path") or "").strip() != str(manifest.get("verified_snapshot_path") or "").strip():
        errors.append("model_load_source_resolved_path must equal verified_snapshot_path in downstream identity receipt")
    if manifest.get("token_provenance_verified") is not True:
        errors.append("token_provenance_verified must be true in downstream identity receipt")
    if manifest.get("generation_determinism_verified") is not True:
        errors.append("generation_determinism_verified must be true in downstream identity receipt")
    if manifest.get("generation_token_provenance_verified") is not True:
        errors.append("generation_token_provenance_verified must be true in downstream identity receipt")
    if manifest.get("runtime_provenance_verified") is not True:
        errors.append("runtime_provenance_verified must be true in downstream identity receipt")
    if manifest.get("cache_decode_verified") is not True:
        errors.append("cache_decode_verified must be true in downstream identity receipt")
    if mismatches:
        errors.append("manifest/NPZ identity field mismatch: " + ", ".join(sorted(mismatches)))
    if provenance_status.get("accepted") is not True:
        warnings.append("verifier did not accept provenance; downstream identity is diagnostic only")
    verified = bool(provenance_status.get("accepted") is True and not errors)
    identity = {
        "trace_identity_receipt_contract": TRACE_IDENTITY_RECEIPT_CONTRACT,
        "verified_for_downstream_selector_entry": verified,
        "verifier_accepted": provenance_status.get("accepted") is True,
        "provenance_verifier_status": provenance_status.get("status"),
        "loader_snapshot_binding_verified": manifest.get("loader_snapshot_binding_verified") is True and not manifest_loader_errors and not npz_loader_errors,
        "snapshot_digest_authenticity_verified": manifest.get("snapshot_digest_authenticity_verified") is True,
        "prompt_manifest_sha256": manifest.get("prompt_manifest_sha256"),
        "generation_config_sha256": manifest.get("generation_config_sha256"),
        "tokenization_settings_sha256": manifest.get("tokenization_settings_sha256"),
        "trace_npz_sha256": manifest.get("trace_npz_sha256"),
        "model_id": manifest.get("model_id"),
        "model_revision": manifest.get("model_revision"),
        "tokenizer_revision": manifest.get("tokenizer_revision"),
        "model_load_source_resolved_path": manifest.get("model_load_source_resolved_path"),
        "verified_snapshot_path": manifest.get("verified_snapshot_path"),
        "model_safetensors_sha256": manifest.get("model_safetensors_sha256"),
        "expected_model_safetensors_sha256": manifest.get("expected_model_safetensors_sha256"),
        "model_safetensors_sha256_matches_expected": manifest.get("model_safetensors_sha256_matches_expected"),
        "cache_implementation_contract": manifest.get("cache_implementation_contract"),
        "generation_cache_implementation": manifest.get("generation_cache_implementation"),
        "generation_determinism_contract": manifest.get("generation_determinism_contract"),
        "generation_token_contract": manifest.get("generation_token_contract"),
        "token_provenance_contract": manifest.get("token_provenance_contract"),
        "manifest_identity": _stable_identity_subset(manifest),
        "npz_identity": _stable_identity_subset(npz_meta),
        "manifest_npz_identity_mismatches": mismatches,
        "errors": errors,
        "warnings": warnings,
    }
    identity["trace_identity_sha256"] = _stable_sha256({
        "contract": TRACE_IDENTITY_RECEIPT_CONTRACT,
        "manifest_identity": identity["manifest_identity"],
        "npz_identity": identity["npz_identity"],
    })
    return identity


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _default_npz() -> Path:
    return ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz"


def _default_prov() -> Path:
    return ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json"


def _default_receipt() -> Path:
    return PROBE_OUT / f"{REVUP}_PUBLIC_TRACE_EVALUATION_RECEIPT.json"


def _stable_sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _subjects(*, trace_sha: str | None, prov_sha: str | None, evaluator_sha: str | None, verifier_sha: str | None, reported_trace_sha: str | None) -> list[dict[str, Any]]:
    # Names are semantic role names, not filesystem paths; this keeps the
    # subject-set digest stable if the bundle is copied to another directory.
    return [
        {"name": "public_trace_npz", "digest": {"sha256": trace_sha}, "reported_by_verifier_sha256": reported_trace_sha},
        {"name": "public_trace_provenance_json", "digest": {"sha256": prov_sha}},
        {"name": "public_trace_verifier_tool", "digest": {"sha256": verifier_sha}},
        {"name": "public_trace_evaluator_tool", "digest": {"sha256": evaluator_sha}},
    ]


def _subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    normalized = []
    for item in subjects:
        normalized.append({
            "name": item.get("name"),
            "digest": item.get("digest", {}),
            "reported_by_verifier_sha256": item.get("reported_by_verifier_sha256"),
        })
    return _stable_sha256({"receipt_contract": RECEIPT_CONTRACT, "subjects": normalized})


def _make_receipt(*, trace_npz: Path, provenance_json: Path, status: str, verdict: str, errors: list[str], blockers: list[str], provenance_status: dict[str, Any], strict_require_trace: bool) -> dict[str, Any]:
    trace_sha = sha256_file(trace_npz)
    prov_sha = sha256_file(provenance_json)
    evaluator_sha = sha256_file(ROOT / EVALUATOR_REL)
    verifier_sha = sha256_file(ROOT / VERIFIER_REL)
    reported_trace_sha = provenance_status.get("trace_npz_sha256_actual")
    trace_identity = _trace_identity_summary(provenance_status)
    receipt_identity_errors: list[str] = []
    if reported_trace_sha and trace_sha and reported_trace_sha != trace_sha:
        receipt_identity_errors.append("verifier_reported_trace_hash_does_not_match_actual_trace_hash")
    if provenance_status.get("accepted") is True and not trace_sha:
        receipt_identity_errors.append("accepted_verifier_status_without_actual_trace_hash")
    if provenance_status.get("accepted") is True and not prov_sha:
        receipt_identity_errors.append("accepted_verifier_status_without_actual_provenance_hash")
    if provenance_status.get("accepted") is True and trace_identity.get("verified_for_downstream_selector_entry") is not True:
        receipt_identity_errors.append("accepted_verifier_status_without_downstream_trace_identity_receipt")
    subjects = _subjects(
        trace_sha=trace_sha,
        prov_sha=prov_sha,
        evaluator_sha=evaluator_sha,
        verifier_sha=verifier_sha,
        reported_trace_sha=reported_trace_sha,
    )
    subject_set = _subject_set_sha256(subjects)
    accepted_for_evaluation = bool(
        verdict == "accepted_for_selector_evaluation_not_promotion"
        and not errors
        and not receipt_identity_errors
        and provenance_status.get("accepted") is True
        and trace_sha
        and prov_sha
        and evaluator_sha
        and verifier_sha
        and trace_identity.get("verified_for_downstream_selector_entry") is True
        and (not reported_trace_sha or reported_trace_sha == trace_sha)
    )
    return {
        "receipt_contract": RECEIPT_CONTRACT,
        "revision": REV,
        "revision_number": int(REV.replace("rev", "")),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "verdict": verdict,
        "accepted_for_selector_evaluation": accepted_for_evaluation,
        "promotion_allowed": False,
        "strict_require_trace": bool(strict_require_trace),
        "path_relocation_policy": "selector entry is permitted only when the receipt subject digests match the actual files supplied at evaluation time; original paths are advisory labels, not identity",
        "trace_npz": _rel(trace_npz),
        "trace_npz_exists": trace_npz.exists(),
        "trace_npz_sha256": trace_sha,
        "provenance_json": _rel(provenance_json),
        "provenance_json_exists": provenance_json.exists(),
        "provenance_json_sha256": prov_sha,
        "evaluator_tool": EVALUATOR_REL,
        "evaluator_tool_sha256": evaluator_sha,
        "gate_verifier": VERIFIER_REL,
        "gate_verifier_sha256": verifier_sha,
        "trace_npz_sha256_reported_by_verifier": reported_trace_sha,
        "provenance_verifier_status": provenance_status.get("status"),
        "provenance_verifier_accepted": provenance_status.get("accepted") is True,
        "trace_identity_receipt_contract": TRACE_IDENTITY_RECEIPT_CONTRACT,
        "trace_identity_verified_for_downstream": trace_identity.get("verified_for_downstream_selector_entry") is True,
        "trace_identity_sha256": trace_identity.get("trace_identity_sha256"),
        "trace_identity": trace_identity,
        "evidence_subjects": subjects,
        "evidence_subject_set_sha256": subject_set,
        "receipt_identity_errors": receipt_identity_errors,
        "errors_sha256": hashlib.sha256(json.dumps(errors, sort_keys=True).encode("utf-8")).hexdigest(),
        "blockers_sha256": hashlib.sha256(json.dumps(blockers, sort_keys=True).encode("utf-8")).hexdigest(),
        "selector_evaluation_entry_allowed": accepted_for_evaluation,
        "named_hardware_timing_still_required_for_promotion": True,
    }


def _write(audit: dict[str, Any], receipt: dict[str, Any], receipt_path: Path) -> None:
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    receipt_bytes_sha = sha256_file(receipt_path)
    audit["evaluation_receipt_sha256"] = receipt_bytes_sha
    (OUT / f"{REVUP}_PUBLIC_TRACE_EVALUATION_VERDICT_AUDIT.json").write_text(
        json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    md = [
        f"# Public trace evaluation verdict audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        f"Verdict: `{audit['verdict']}`  ",
        f"Receipt: `{audit['evaluation_receipt_path']}`  ",
        f"Promotion allowed: `{str(audit['promotion_allowed']).lower()}`",
        "",
        audit.get("summary", ""),
        "",
        "## Receipt binding",
        "",
        f"- receipt contract: `{receipt.get('receipt_contract')}`",
        f"- subject-set SHA-256: `{receipt.get('evidence_subject_set_sha256') or 'missing'}`",
        f"- receipt file SHA-256: `{receipt_bytes_sha or 'missing'}`",
        f"- trace NPZ SHA-256: `{receipt.get('trace_npz_sha256') or 'missing'}`",
        f"- provenance JSON SHA-256: `{receipt.get('provenance_json_sha256') or 'missing'}`",
        f"- trace identity SHA-256: `{receipt.get('trace_identity_sha256') or 'missing'}`",
        f"- verifier SHA-256: `{receipt.get('gate_verifier_sha256') or 'missing'}`",
        f"- evaluator SHA-256: `{receipt.get('evaluator_tool_sha256') or 'missing'}`",
        "",
        "## Blockers",
    ]
    md.extend([f"- `{b}`" for b in audit.get("blockers", [])] or ["- none"])
    md.extend(["", "## Errors"])
    md.extend([f"- `{e}`" for e in audit.get("errors", [])] or ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_EVALUATION_VERDICT_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Emit an operator verdict and content-addressed receipt for the current public trace bundle: missing, rejected, or accepted-for-evaluation.")
    ap.add_argument("--trace-npz", type=Path, default=None)
    ap.add_argument("--provenance-json", type=Path, default=None)
    ap.add_argument("--receipt-json", type=Path, default=None, help="where to write the exact bundle/verifier/evaluator receipt")
    ap.add_argument("--strict-require-trace", action="store_true", help="exit nonzero when the trace/provenance pair is absent")
    args = ap.parse_args()

    trace_npz = args.trace_npz or _default_npz()
    provenance_json = args.provenance_json or _default_prov()
    receipt_path = args.receipt_json or _default_receipt()
    errors: list[str] = []
    blockers: list[str] = []
    warnings: list[str] = []
    provenance_status: dict[str, Any] = {}

    if IMPORT_ERROR:
        errors.append("could not import public trace gate verifier: " + IMPORT_ERROR)
        status = "fail"
        verdict = "verifier_unavailable"
    elif not trace_npz.exists() or not provenance_json.exists():
        status = "pass_with_blockers"
        verdict = "blocked_no_trace_bundle"
        blockers.extend([
            "real_public_trace_npz_missing" if not trace_npz.exists() else "real_public_trace_npz_present",
            "real_public_trace_provenance_missing" if not provenance_json.exists() else "real_public_trace_provenance_present",
            "capture_must_complete_before_selector_evaluation",
            "evaluation_receipt_emitted_but_not_accepted",
        ])
        if args.strict_require_trace:
            errors.append("strict verdict requested but trace/provenance pair is absent")
            status = "fail"
    else:
        provenance_status = validate_public_trace_provenance(provenance_json, trace_npz)  # type: ignore[misc]
        if provenance_status.get("accepted") is True:
            status = "pass_with_blockers"
            verdict = "accepted_for_selector_evaluation_not_promotion"
            blockers.append("named_hardware_timing_still_required_for_promotion")
        else:
            status = "fail"
            verdict = "trace_bundle_rejected_before_evaluation"
            errors.extend(str(e) for e in provenance_status.get("errors", []))
            blockers.append("fix_trace_or_provenance_before_selector_evaluation")

    receipt = _make_receipt(
        trace_npz=trace_npz,
        provenance_json=provenance_json,
        status=status,
        verdict=verdict,
        errors=errors,
        blockers=blockers,
        provenance_status=provenance_status,
        strict_require_trace=args.strict_require_trace,
    )
    audit = {
        "revision": REV,
        "revision_number": int(REV.replace("rev", "")),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "verdict": verdict,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": bool(receipt["accepted_for_selector_evaluation"]),
        "gpu_fused_kernel_measured": False,
        "trace_npz": _rel(trace_npz),
        "provenance_json": _rel(provenance_json),
        "evaluation_receipt_path": _rel(receipt_path),
        "evaluation_receipt": receipt,
        "summary": "Prevents a partial or merely captured trace bundle from entering selector/cost evaluation until the NPZ and provenance manifest pass the public trace verifier. rev0108 upgrades the receipt from path-bound bookkeeping to a content-addressed subject set: the selector gate verifies actual file hashes at evaluation time, so moving/renaming a bundle does not break valid evidence and copying a receipt without matching files does not open evaluation.",
        "provenance_status": provenance_status,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "online_research_basis": [
            {"url": "https://slsa.dev/spec/v1.0/provenance", "note": "SLSA treats provenance as an attestation about artifacts produced by a build definition; digest-bound subjects are the relevant model for evidence handoff."},
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/README.md", "note": "in-toto statements bind predicate metadata to subject artifacts, which motivates content-addressed trace/evaluator receipts."},
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md", "note": "link materials/subjects use ResourceDescriptors with names and digests; rev0108 mirrors that with semantic subject names plus SHA-256 digests."},
            {"url": "https://docs.pytorch.org/docs/stable/notes/randomness.html", "note": "PyTorch warns that reproducibility may vary across releases/platforms/devices; evaluation receipts must bind exact evidence/tool digests rather than prose lineage."},
            {"url": "https://huggingface.co/docs/transformers/en/kv_cache", "note": "Transformers exposes multiple cache implementations; the accepted trace identity must stay tied to the dynamic-cache evidence bundle already gated in earlier revisions."},
        ],
    }
    _write(audit, receipt, receipt_path)
    print(json.dumps({"status": status, "verdict": verdict, "receipt": _rel(receipt_path), "errors": errors, "blockers": blockers}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
