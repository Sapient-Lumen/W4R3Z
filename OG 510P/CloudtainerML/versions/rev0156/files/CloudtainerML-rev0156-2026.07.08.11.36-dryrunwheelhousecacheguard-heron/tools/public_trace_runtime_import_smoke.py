#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import importlib.metadata as md
import importlib.util
import inspect
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", "0"))).replace("rev", "")) if str(META.get("revision_number", "")).startswith("rev") else int(META.get("revision_number", REV.replace("rev", "0")))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

REQUIRED_IMPORTS = ["numpy", "torch", "transformers", "huggingface_hub", "safetensors", "hf_xet"]
PUBLIC_REQUIRED_EAGER_PARAMS = ["module", "query", "key", "value", "attention_mask", "scaling"]


def module_status(name: str, *, import_module: bool = True) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)  # type: ignore[attr-defined]
    rec: dict[str, Any] = {
        "name": name,
        "present": bool(spec is not None),
        "origin": str(getattr(spec, "origin", "")) if spec else "",
        "checked_without_network": True,
    }
    try:
        rec["version"] = md.version(name.replace("_", "-"))
    except Exception:
        try:
            rec["version"] = md.version(name)
        except Exception as exc:
            rec["version_error"] = type(exc).__name__ + ": " + repr(exc)
    if spec is None or not import_module:
        return rec
    try:
        mod = importlib.import_module(name)
        rec["import_ok"] = True
        rec["module_version_attr"] = str(getattr(mod, "__version__", rec.get("version", "unknown")))
    except Exception as exc:
        rec["import_ok"] = False
        rec["import_error"] = type(exc).__name__ + ": " + repr(exc)
    return rec


def sig_params(obj: Any) -> list[str]:
    try:
        return list(inspect.signature(obj).parameters)
    except Exception:
        return []


def venv_status() -> dict[str, Any]:
    expected = os.environ.get("PUBLIC_TRACE_VENV_DIR") or os.environ.get("VIRTUAL_ENV") or ""
    exe = Path(sys.executable).resolve()
    rec: dict[str, Any] = {
        "python_executable": str(exe),
        "sys_prefix": str(sys.prefix),
        "base_prefix": str(getattr(sys, "base_prefix", "")),
        "virtual_env": os.environ.get("VIRTUAL_ENV", ""),
        "public_trace_venv_dir": os.environ.get("PUBLIC_TRACE_VENV_DIR", ""),
        "expected_project_venv_dir": expected,
        "running_inside_virtualenv": bool(sys.prefix != getattr(sys, "base_prefix", sys.prefix) or os.environ.get("VIRTUAL_ENV")),
        "python_no_user_site": os.environ.get("PYTHONNOUSERSITE", ""),
    }
    if expected:
        try:
            exp = Path(expected).expanduser().resolve()
            rec["expected_project_venv_resolved"] = str(exp)
            rec["executable_inside_expected_project_venv"] = str(exe).startswith(str(exp) + os.sep)
        except Exception as exc:
            rec["expected_project_venv_resolve_error"] = type(exc).__name__ + ": " + repr(exc)
            rec["executable_inside_expected_project_venv"] = False
    else:
        rec["executable_inside_expected_project_venv"] = False
    return rec


def transformers_surface() -> tuple[dict[str, Any], list[str], list[str]]:
    facts: dict[str, Any] = {}
    blockers: list[str] = []
    warnings: list[str] = []
    try:
        import transformers  # type: ignore
        facts["transformers_version"] = str(getattr(transformers, "__version__", "unknown"))
        facts["AutoTokenizer_present"] = hasattr(transformers, "AutoTokenizer")
        facts["AutoModelForCausalLM_present"] = hasattr(transformers, "AutoModelForCausalLM")
        if not facts["AutoTokenizer_present"]:
            blockers.append("transformers_autotokenizer_missing")
        if not facts["AutoModelForCausalLM_present"]:
            blockers.append("transformers_automodelforcausallm_missing")
    except Exception as exc:
        facts["transformers_import_error"] = type(exc).__name__ + ": " + repr(exc)
        blockers.append("transformers_import_failed")
        return facts, blockers, warnings

    try:
        ml = importlib.import_module("transformers.models.llama.modeling_llama")
        facts["modeling_llama_import_ok"] = True
        eager = getattr(ml, "eager_attention_forward", None)
        facts["eager_attention_forward_present"] = callable(eager)
        eager_params = sig_params(eager) if callable(eager) else []
        facts["eager_attention_forward_signature"] = eager_params
        missing = [p for p in PUBLIC_REQUIRED_EAGER_PARAMS if p not in eager_params]
        if not callable(eager):
            blockers.append("llama_eager_attention_forward_missing")
        elif missing:
            blockers.append("llama_eager_attention_forward_signature_incompatible:" + ",".join(missing))
        LlamaAttention = getattr(ml, "LlamaAttention", None)
        facts["LlamaAttention_present"] = LlamaAttention is not None
        fwd = getattr(LlamaAttention, "forward", None) if LlamaAttention is not None else None
        fwd_params = sig_params(fwd) if fwd is not None else []
        facts["LlamaAttention_forward_signature"] = fwd_params
        for p in ["hidden_states", "position_embeddings", "attention_mask"]:
            if p not in fwd_params:
                warnings.append("llama_attention_forward_missing_expected_param:" + p)
        if "cache_position" not in fwd_params:
            warnings.append("llama_attention_forward_cache_position_not_visible")
        if "past_key_value" not in fwd_params and "past_key_values" not in fwd_params:
            warnings.append("llama_attention_forward_past_key_value_not_visible")
    except Exception as exc:
        facts["modeling_llama_import_ok"] = False
        facts["modeling_llama_error"] = type(exc).__name__ + ": " + repr(exc)
        blockers.append("transformers_llama_modeling_import_failed")

    try:
        import transformers  # type: ignore
        facts["AttentionInterface_present"] = getattr(transformers, "AttentionInterface", None) is not None
        facts["AttentionMaskInterface_present"] = getattr(transformers, "AttentionMaskInterface", None) is not None
        if not facts["AttentionInterface_present"]:
            warnings.append("AttentionInterface_not_exported_from_transformers")
        if not facts["AttentionMaskInterface_present"]:
            warnings.append("AttentionMaskInterface_not_exported_from_transformers")
    except Exception as exc:
        warnings.append("attention_interface_probe_failed:" + repr(exc))
    return facts, blockers, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Import-only runtime smoke for the public TinyLlama trace lane.")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--require-project-venv", action="store_true", help="fail unless sys.executable is inside PUBLIC_TRACE_VENV_DIR/VIRTUAL_ENV")
    args = ap.parse_args()

    # Make the smoke a no-network check even if an operator has ambient HF settings.
    offline_exports = {
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
        "HF_HUB_DISABLE_UPDATE_CHECK": "1",
    }
    for key, value in offline_exports.items():
        os.environ.setdefault(key, value)

    blockers: list[str] = []
    warnings: list[str] = []

    # Fail fast before importing heavy libraries.  In the chat/container runner,
    # importing torch can be materially slower than simply discovering that the
    # capture stack is incomplete.  The first-real-trace command should not burn
    # CPU proving torch importability when transformers/huggingface_hub/etc. are
    # absent and the run is already blocked.  On a capable machine with every
    # required package present, the second pass below imports the full stack.
    modules = {name: module_status(name, import_module=False) for name in REQUIRED_IMPORTS}
    missing_required = [name for name, rec in modules.items() if not rec.get("present")]
    for name in missing_required:
        blockers.append(f"{name}_not_present_in_runtime_python")
    heavy_imports_skipped_due_to_missing = bool(missing_required)
    if not missing_required:
        modules = {name: module_status(name, import_module=True) for name in REQUIRED_IMPORTS}
        for name, rec in modules.items():
            if rec.get("import_ok") is False:
                blockers.append(f"{name}_import_failed")
    else:
        warnings.append("heavy_runtime_imports_skipped_until_required_modules_are_present")

    venv = venv_status()
    if args.require_project_venv:
        if not venv.get("expected_project_venv_dir"):
            blockers.append("project_venv_required_but_PUBLIC_TRACE_VENV_DIR_or_VIRTUAL_ENV_missing")
        elif not venv.get("executable_inside_expected_project_venv"):
            blockers.append("python_executable_not_inside_expected_project_venv")
        if not venv.get("running_inside_virtualenv"):
            blockers.append("project_venv_required_but_python_not_inside_virtualenv")
    else:
        if not venv.get("running_inside_virtualenv"):
            warnings.append("runtime_import_smoke_using_ambient_python_not_project_venv")

    if modules.get("transformers", {}).get("present") and not heavy_imports_skipped_due_to_missing:
        surface_facts, surface_blockers, surface_warnings = transformers_surface()
        blockers.extend(surface_blockers)
        warnings.extend(surface_warnings)
    else:
        surface_facts = {"transformers_surface_probe_skipped": True, "reason": "required_runtime_module_missing"}
    if str(modules.get("transformers", {}).get("version", "")).startswith("5."):
        blockers.append("transformers_major_5_detected_runtime_lock_requires_lt5")

    blockers = sorted(set(blockers))
    warnings = sorted(set(warnings))
    status = "pass" if not blockers else "blocked_here_runtime_import_smoke"
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Import-only runtime smoke for the first-real-trace lane. REV0149 makes this a two-stage smoke: first cheap module discovery, then heavy imports only after the full required stack is present. It fails before any 2.2GB snapshot materialization if the Python that will run capture cannot import torch/transformers/huggingface_hub/safetensors/hf_xet/numpy or if the current Transformers Llama eager-attention surface is incompatible with the capture adapter.",
        "strict": bool(args.strict),
        "require_project_venv": bool(args.require_project_venv),
        "offline_exports_for_smoke": offline_exports,
        "venv": venv,
        "python": {"version": platform.python_version(), "executable": sys.executable, "platform": platform.platform()},
        "modules": modules,
        "heavy_imports_skipped_due_to_missing_required_modules": heavy_imports_skipped_due_to_missing,
        "transformers_surface": surface_facts,
        "blockers": blockers,
        "warnings": warnings,
        "decision": "runtime_import_surface_ready_for_snapshot_then_capture" if not blockers else "repair_runtime_before_download_or_capture",
        "source_basis": [
            {"url": "https://huggingface.co/docs/hub/en/xet/using-xet-storage", "fact": "Hugging Face Xet docs state huggingface_hub 0.32+ installs hf_xet for Xet-backed large files; the runner still imports hf_xet explicitly so an older or broken install fails early."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/guides/download", "fact": "Hub download docs describe cache/snapshot_download for local materialization; the runtime smoke is intentionally before that expensive phase in the one-command path."},
            {"url": "https://huggingface.co/docs/hub/en/local-cache", "fact": "The Hub local cache has an explicit snapshot layout, which the later selected-snapshot gate binds to after this runtime smoke passes."},
            {"url": "https://huggingface.co/docs/transformers/model_doc/auto", "fact": "Transformers Auto classes load model/tokenizer implementations through from_pretrained; the smoke verifies those classes and the Llama attention surface are importable before capture."},
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_RUNTIME_IMPORT_SMOKE.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace runtime import smoke — {REVUP}",
        "",
        f"Status: `{status}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Blockers",
        "",
    ]
    md.extend([f"- `{b}`" for b in blockers] if blockers else ["- none"])
    md.extend(["", "## Warnings", ""])
    md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
    md.extend(["", "## Interpretation", "", "This is an operational waste guard: do not spend snapshot-download time on a first-real-trace attempt until the exact Python runtime can import the capture stack and its Llama hook surface."])
    (OUT / f"{REVUP}_PUBLIC_TRACE_RUNTIME_IMPORT_SMOKE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "blockers": blockers, "warnings": warnings}, indent=2))
    return 0 if (not blockers or not args.strict) else 1


if __name__ == "__main__":
    raise SystemExit(main())
