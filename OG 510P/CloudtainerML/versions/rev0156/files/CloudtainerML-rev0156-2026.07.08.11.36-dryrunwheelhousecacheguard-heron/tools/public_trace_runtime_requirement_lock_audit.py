#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.metadata as md
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", "0"))))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
REQ = ROOT / "artifacts" / "runtime" / f"{REVUP}_public_trace_requirements.txt"
CORE = {"numpy", "torch", "transformers", "huggingface-hub", "safetensors", "hf-xet"}


def clean_line(line: str) -> str:
    return line.split("#", 1)[0].strip()


def normalize_name(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def parse_requirement(line: str) -> dict[str, Any]:
    raw = line
    line = clean_line(line)
    if not line:
        return {"raw": raw, "empty": True}
    if line.startswith(("-", "git+", "http://", "https://")):
        return {"raw": raw, "line": line, "name": "", "spec": line, "direct_or_option": True}
    m = re.match(r"^([A-Za-z0-9_.-]+)(\[[^\]]+\])?\s*(.*)$", line)
    if not m:
        return {"raw": raw, "line": line, "name": "", "spec": line, "parse_error": True}
    return {
        "raw": raw,
        "line": line,
        "name": normalize_name(m.group(1)),
        "extras": m.group(2) or "",
        "spec": (m.group(3) or "").strip(),
    }


def has_op(spec: str, op: str, version_prefix: str | None = None) -> bool:
    for part in [p.strip() for p in spec.split(",") if p.strip()]:
        if not part.startswith(op):
            continue
        if version_prefix is None:
            return True
        return part[len(op):].strip().startswith(version_prefix)
    return False


def has_any_upper(spec: str) -> bool:
    return any(part.strip().startswith(("<", "<=", "~=", "===")) for part in spec.split(","))


def installed_version(name: str) -> dict[str, Any]:
    candidates = [name, name.replace("-", "_")]
    for cand in candidates:
        try:
            return {"present": True, "version": md.version(cand)}
        except Exception:
            pass
    return {"present": False}


def check_scripts() -> dict[str, Any]:
    checks: dict[str, Any] = {}
    scripts = {
        "bootstrap": ROOT / "artifacts" / "capture-kit" / f"{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh",
        "first_real_trace": ROOT / "artifacts" / "capture-kit" / f"{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh",
        "snapshot_prepare": ROOT / "artifacts" / "capture-kit" / f"{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh",
        "capture_wrapper": ROOT / "artifacts" / "capture-kit" / f"{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh",
        "one_shot_capture": ROOT / "artifacts" / "capture-kit" / f"{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh",
    }
    for name, path in scripts.items():
        rec: dict[str, Any] = {"path": path.relative_to(ROOT).as_posix(), "exists": path.exists()}
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            audit_pos = text.find("tools/public_trace_runtime_requirement_lock_audit.py")
            pip_pos = text.find("pip install -r")
            smoke_pos = text.find("public_trace_runtime_import_smoke.py")
            materializer_pos = text.find("hf_snapshot_materializer.py")
            rec.update({
                "audit_call_present": audit_pos >= 0,
                "audit_call_before_pip_install": bool(audit_pos >= 0 and (pip_pos < 0 or audit_pos < pip_pos)),
                "audit_call_before_runtime_smoke": bool(audit_pos >= 0 and (smoke_pos < 0 or audit_pos < smoke_pos)),
                "audit_call_before_snapshot_materializer": bool(audit_pos >= 0 and (materializer_pos < 0 or audit_pos < materializer_pos)),
            })
        checks[name] = rec
    return checks


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit bounded runtime requirements for the public TinyLlama trace runner.")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    parsed: list[dict[str, Any]] = []
    by_name: dict[str, list[dict[str, Any]]] = {}
    if not REQ.exists():
        errors.append("missing_current_runtime_requirements_file")
    else:
        for line in REQ.read_text(encoding="utf-8").splitlines():
            rec = parse_requirement(line)
            parsed.append(rec)
            name = rec.get("name")
            if name:
                by_name.setdefault(str(name), []).append(rec)

    for name in CORE:
        if name not in by_name:
            errors.append(f"missing_core_runtime_requirement:{name}")
        elif len(by_name[name]) > 1:
            errors.append(f"duplicate_runtime_requirement:{name}")

    def spec(name: str) -> str:
        return str((by_name.get(name) or [{}])[0].get("spec", ""))

    tf_spec = spec("transformers")
    if not tf_spec:
        errors.append("transformers_requirement_unbounded")
    else:
        if not has_op(tf_spec, ">=", "4.56") and not has_op(tf_spec, "==", "4."):
            errors.append("transformers_requirement_missing_reviewed_lower_bound_4_56")
        if not has_op(tf_spec, "<", "5"):
            errors.append("transformers_requirement_missing_major_upper_bound_lt5")

    torch_spec = spec("torch")
    if not torch_spec:
        errors.append("torch_requirement_unbounded")
    else:
        if not has_op(torch_spec, ">=", "2.4") and not has_op(torch_spec, "==", "2."):
            errors.append("torch_requirement_missing_docs_lower_bound_2_4")
        if not has_op(torch_spec, "<", "3"):
            errors.append("torch_requirement_missing_major_upper_bound_lt3")

    hub_spec = spec("huggingface-hub")
    if not hub_spec:
        errors.append("huggingface_hub_requirement_unbounded")
    else:
        if not has_op(hub_spec, ">=", "0.32") and not has_op(hub_spec, "==", "0.") and not has_op(hub_spec, "==", "1."):
            errors.append("huggingface_hub_requirement_missing_hf_xet_lower_bound_0_32")
        if not has_op(hub_spec, "<", "2"):
            errors.append("huggingface_hub_requirement_missing_major_upper_bound_lt2")

    np_spec = spec("numpy")
    if np_spec and not has_any_upper(np_spec):
        warnings.append("numpy_requirement_has_no_upper_bound")
    safetensors_spec = spec("safetensors")
    if safetensors_spec and not has_any_upper(safetensors_spec):
        warnings.append("safetensors_requirement_has_no_upper_bound")
    if spec("hf-xet") == "":
        errors.append("hf_xet_requirement_unbounded_or_missing")

    direct_or_options = [r for r in parsed if r.get("direct_or_option") or r.get("parse_error")]
    for r in direct_or_options:
        errors.append("runtime_requirements_contains_unreviewed_direct_or_option_line:" + str(r.get("line") or r.get("raw")))

    script_checks = check_scripts()
    for name, rec in script_checks.items():
        if not rec.get("exists"):
            errors.append(f"missing_active_script_for_requirement_audit:{name}")
        elif not rec.get("audit_call_present"):
            errors.append(f"active_script_missing_runtime_requirement_lock_audit:{name}")
    if script_checks.get("bootstrap", {}).get("exists") and not script_checks["bootstrap"].get("audit_call_before_pip_install"):
        errors.append("bootstrap_does_not_audit_requirements_before_pip_install")
    for name in ["first_real_trace", "capture_wrapper", "one_shot_capture"]:
        if script_checks.get(name, {}).get("exists") and not script_checks[name].get("audit_call_before_runtime_smoke"):
            warnings.append(f"{name}_audit_not_before_runtime_smoke_or_no_smoke_reference")
    if script_checks.get("snapshot_prepare", {}).get("exists") and not script_checks["snapshot_prepare"].get("audit_call_before_snapshot_materializer"):
        errors.append("snapshot_prepare_does_not_audit_requirements_before_snapshot_materializer")

    runtime_smoke = (ROOT / "tools" / "public_trace_runtime_import_smoke.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools" / "public_trace_runtime_import_smoke.py").exists() else ""
    if 'blockers.append("transformers_major_5_detected' not in runtime_smoke:
        errors.append("runtime_import_smoke_does_not_block_transformers_major_5")

    installed = {name: installed_version(name) for name in sorted(CORE)}
    status = "pass" if not errors else "fail"
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Fail-fast audit for the bounded public-trace runtime requirements. The runner depends on the Llama eager-attention capture seam, so unbounded major-version upgrades are treated as execution risk, not harmless freshness.",
        "requirements_file": REQ.relative_to(ROOT).as_posix(),
        "parsed_requirements": parsed,
        "normalized_requirement_names": sorted(by_name),
        "installed_runtime_versions_observed_here": installed,
        "script_checks": script_checks,
        "contract": "bounded_public_trace_runtime_requirements_v1",
        "required_constraints": {
            "transformers": ">=4.56,<5",
            "torch": ">=2.4,<3",
            "huggingface_hub": ">=0.32,<2",
            "hf_xet": "present_bounded_or_lower_bounded",
        },
        "online_source_basis": [
            {"url": "https://huggingface.co/docs/transformers/main/installation", "fact": "Current Transformers docs show a new major stable line and state Python 3.10+ / PyTorch 2.4+ support; runtime constraints should not silently float across a private attention-surface dependency."},
            {"url": "https://huggingface.co/docs/transformers/attention_interface", "fact": "AttentionInterface and attention-mask handling are backend-specific; custom attention functions require a matching mask function or mask semantics can be dropped."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/guides/download", "fact": "snapshot_download supports revision and allow_patterns, so the runtime lock should be checked before expensive snapshot materialization."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables", "fact": "Hugging Face cache/offline environment variables are part of the runtime contract and must be bound before Hub imports."},
        ],
        "errors": errors,
        "warnings": warnings,
        "decision": "runtime_requirements_safe_to_bootstrap_then_smoke" if not errors else "repair_runtime_requirement_lock_before_bootstrap_or_snapshot",
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_RUNTIME_REQUIREMENT_LOCK_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace runtime requirement lock audit — {REVUP}",
        "",
        f"Status: `{status}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Requirements file",
        "",
        f"- `{audit['requirements_file']}`",
        "",
        "## Errors",
        "",
    ]
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Warnings", ""])
    md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
    md.extend(["", "## Interpretation", "", "This is a substance-first guard: fail before package install, snapshot download, or capture if the runtime contract has drifted into an unreviewed dependency surface."])
    (OUT / f"{REVUP}_PUBLIC_TRACE_RUNTIME_REQUIREMENT_LOCK_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "errors": errors, "warnings": warnings}, indent=2))
    return 0 if (not errors or not args.strict) else 1


if __name__ == "__main__":
    raise SystemExit(main())
