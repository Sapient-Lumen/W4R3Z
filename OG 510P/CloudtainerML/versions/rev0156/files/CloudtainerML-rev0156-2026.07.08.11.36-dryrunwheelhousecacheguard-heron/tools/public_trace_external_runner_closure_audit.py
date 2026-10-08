#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", "0"))))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

CONTRACT = "public_trace_external_runner_live_closure_v1"

ACTIVE_SHELL_SCRIPTS = [
    "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh",
    "artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh",
    "artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh",
    f"artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh",
    f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh",
    f"artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh",
    f"artifacts/capture-kit/{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh",
    f"artifacts/capture-kit/{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh",
    f"artifacts/capture-kit/{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh",
]

PACKET_BASE_FILES = [
    "CUBE-META.json",
    "REVISION-RECEIPT.json",
    "EVIDENCE-STATUS.json",
    "SURFACE-STATUS.json",
    "REENTRY-CONTRACT.json",
    "START_HERE.md",
    "PRIORITY-LIST.md",
    "MISSION-KERNEL.md",
    f"artifacts/prompts/{REVUP}_PUBLIC_TRACE_PROMPTS.txt",
    f"artifacts/runtime/{REVUP}_public_trace_requirements.txt",
    f"artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json",
    f"artifacts/run-manifests/{REVUP}_TINYLLAMA_SOURCE_LOCK.json",
]

ROOT_RUNNER_FILES = [
    "RUN_PUBLIC_TRACE.sh",
    "PREPARE_SNAPSHOT.sh",
    "BOOTSTRAP_RUNTIME.sh",
    "RUN_FIRST_REAL_TRACE.sh",
    "README_RUNNER.md",
    "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json",
]

PY_PATH_RE = re.compile(r"(?:python3|python|sys\.executable)\s+([A-Za-z0-9_./-]+\.py)")
STRING_PATH_RE = re.compile(r"[\"'](tools/[A-Za-z0-9_./-]+\.py|experiments/[A-Za-z0-9_./-]+\.py)[\"']")
BASH_REL_RE = re.compile(r"(?:bash|exec)\s+(?:\"\$HERE/)?([A-Za-z0-9_./$\{\}-]+\.sh)\"?")
SOURCE_REL_RE = re.compile(r"(?:source|\.)\s+(?:\"\$HERE/)?([A-Za-z0-9_./$\{\}-]+\.sh)\"?")
DYNAMIC_REV_SHELL_RE = re.compile(r"\$\{REVUP\}_([A-Z0-9_]+\.sh)")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(root: Path, rel: str) -> str:
    p = root / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def module_to_rel(module: str) -> str | None:
    if module.startswith("tools."):
        return module.replace(".", "/") + ".py"
    if module.startswith("experiments."):
        return module.replace(".", "/") + ".py"
    return None


def normalize_shell_ref(raw: str, *, script_dir: Path) -> str | None:
    text = raw.strip().strip('"').strip("'")
    if not text or text.startswith("-"):
        return None
    if "${REVUP}_" in text:
        m = DYNAMIC_REV_SHELL_RE.search(text)
        if not m:
            return None
        text = f"{REVUP}_{m.group(1)}"
    if text.startswith("$HERE/"):
        return (script_dir / text[len("$HERE/"):]).as_posix()
    if text.startswith("./"):
        return (script_dir / text[2:]).as_posix()
    if text.startswith(("artifacts/", "tools/", "experiments/")) or text == "VERIFY_HANDOFF.py":
        return text
    if text.startswith(f"{REVUP}_"):
        return (script_dir / text).as_posix()
    return None


def python_refs_from_shell(root: Path, rel: str) -> set[str]:
    text = read_text(root, rel)
    return {m.group(1) for m in PY_PATH_RE.finditer(text) if m.group(1).startswith(("tools/", "experiments/"))}


def shell_refs_from_shell(root: Path, rel: str) -> set[str]:
    text = read_text(root, rel)
    script_dir = Path(rel).parent
    refs: set[str] = set()
    for pattern in (BASH_REL_RE, SOURCE_REL_RE):
        for m in pattern.finditer(text):
            ref = normalize_shell_ref(m.group(1), script_dir=script_dir)
            if ref:
                refs.add(ref)
    for m in DYNAMIC_REV_SHELL_RE.finditer(text):
        refs.add((script_dir / f"{REVUP}_{m.group(1)}").as_posix())
    return refs


def python_refs_from_python(root: Path, rel: str) -> set[str]:
    path = root / rel
    refs: set[str] = set()
    if not path.is_file():
        return refs
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return refs
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                r = module_to_rel(alias.name)
                if r:
                    refs.add(r)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "tools":
                for alias in node.names:
                    refs.add("tools/" + alias.name + ".py")
            else:
                r = module_to_rel(module)
                if r:
                    refs.add(r)
    for m in STRING_PATH_RE.finditer(text):
        refs.add(m.group(1))
    # The surrogate evaluator prepends experiments/attention_compiler_core to sys.path
    # and imports attention_core as a bare module. Keep this explicit so the closure
    # remains cheap and deterministic instead of copying all experiments.
    if "from attention_core import" in text or "import attention_core" in text:
        refs.add("experiments/attention_compiler_core/attention_core.py")
    return refs


def compute_live_closure(root: Path = ROOT) -> dict[str, Any]:
    shell_scripts = set(ACTIVE_SHELL_SCRIPTS)
    changed = True
    while changed:
        changed = False
        for rel in list(shell_scripts):
            for ref in shell_refs_from_shell(root, rel):
                if ref.endswith(".sh") and ref not in shell_scripts:
                    shell_scripts.add(ref)
                    changed = True
    python_start: set[str] = {"tools/public_trace_external_runner_manifest_integrity_audit.py"}
    for rel in shell_scripts:
        python_start.update(python_refs_from_shell(root, rel))
    python_files = set(python_start)
    stack = list(python_start)
    while stack:
        rel = stack.pop()
        for ref in python_refs_from_python(root, rel):
            if ref.endswith(".py") and ref not in python_files:
                python_files.add(ref)
                stack.append(ref)
    base_files = set(PACKET_BASE_FILES)
    all_files = sorted(base_files | shell_scripts | python_files)
    return {
        "contract": CONTRACT,
        "revision": REV,
        "revision_number": REVNO,
        "base_files": sorted(base_files),
        "shell_scripts": sorted(shell_scripts),
        "python_files": sorted(python_files),
        "all_source_files": all_files,
        "root_runner_files": ROOT_RUNNER_FILES[:],
        "source_file_count": len(all_files),
        "python_file_count": len(python_files),
        "shell_script_count": len(shell_scripts),
    }


def file_set(root: Path, patterns: tuple[str, ...]) -> set[str]:
    out: set[str] = set()
    for pattern in patterns:
        base = root / pattern
        if base.is_file():
            out.add(pattern)
        elif base.is_dir():
            for p in base.rglob("*"):
                if p.is_file() and "__pycache__" not in p.parts and not p.name.endswith(".pyc"):
                    out.add(p.relative_to(root).as_posix())
    return out


def audit(root: Path, *, runner_root: Path | None = None) -> dict[str, Any]:
    closure = compute_live_closure(root)
    expected = set(closure["all_source_files"])
    errors: list[str] = []
    warnings: list[str] = []
    missing_source = [rel for rel in sorted(expected) if not (root / rel).is_file()]
    errors.extend("missing_source_closure_file:" + rel for rel in missing_source)
    source_hashes = {rel: sha256_file(root / rel) for rel in sorted(expected) if (root / rel).is_file()}

    runner_report: dict[str, Any] | None = None
    if runner_root is not None:
        rr = runner_root
        present_tools = file_set(rr, ("tools",))
        present_exps = file_set(rr, ("experiments",))
        present_sources = {rel for rel in (present_tools | present_exps | {r for r in expected if (rr / r).is_file()}) if (rr / rel).is_file()}
        missing_runner = [rel for rel in sorted(expected) if not (rr / rel).is_file()]
        # Only enforce surplus for tool/experiment files; README/manifest/root scripts are generated by the builder.
        expected_tool_exp = {rel for rel in expected if rel.startswith(("tools/", "experiments/"))}
        surplus_runner = sorted((present_tools | present_exps) - expected_tool_exp)
        runner_report = {
            "runner_root": str(rr),
            "present_tool_files": sorted(present_tools),
            "present_experiment_files": sorted(present_exps),
            "present_tool_count": sum(1 for rel in present_tools if rel.endswith(".py")),
            "present_experiment_file_count": len(present_exps),
            "missing_runner_closure_files": missing_runner,
            "surplus_runner_tool_or_experiment_files": surplus_runner,
        }
        errors.extend("missing_runner_closure_file:" + rel for rel in missing_runner)
        errors.extend("surplus_runner_tool_or_experiment_file:" + rel for rel in surplus_runner)
    else:
        # In a source cube, warn if the active external runner still appears to carry the entire tools tree.
        candidate = root / "artifacts" / "external-runner" / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER"
        if candidate.exists():
            rr_report = audit(root, runner_root=candidate)
            runner_report = rr_report.get("runner_report")
            for e in rr_report.get("errors", []):
                if e.startswith("missing_runner_closure_file") or e.startswith("surplus_runner_tool_or_experiment_file"):
                    errors.append(e)

    audit_doc: dict[str, Any] = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Computes the live-script closure for the first-real-trace external runner. REV0150 uses this to stop copying the entire tools directory into the runner packet while preserving every reachable script/import needed by the active public-trace path.",
        "contract": CONTRACT,
        "closure": closure,
        "source_hashes": source_hashes,
        "runner_report": runner_report,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "decision": "runner_packet_matches_live_closure" if not errors else "repair_external_runner_closure_before_shipping_packet",
        "research_basis": [
            {
                "url": "https://huggingface.co/docs/huggingface_hub/en/guides/download",
                "observed": "Current Hub docs describe snapshot_download dry_run returning file size/cache/download flags and hf_xet as the modern large-file path.",
            },
            {
                "url": "https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables",
                "observed": "Hub env vars are read at import time and include HF_HOME/HF_HUB_CACHE/HF_XET_CACHE plus offline controls, so runner scripts must carry env-binding tools but not unrelated probes.",
            },
            {
                "url": "https://huggingface.co/docs/transformers/en/attention_interface",
                "observed": "Attention backend and mask handling are backend-sensitive, so the live closure keeps the eager trace-surface probes and leaves unrelated historical probes out of the packet.",
            },
        ],
    }
    return audit_doc


def write_outputs(audit_doc: dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER_CLOSURE_AUDIT.json").write_text(json.dumps(audit_doc, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    closure = audit_doc.get("closure", {})
    rr = audit_doc.get("runner_report") or {}
    md = [
        f"# Public trace external runner closure audit — {REVUP}",
        "",
        f"Status: `{audit_doc['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit_doc.get("summary", ""),
        "",
        "## Closure counts",
        "",
        f"- source files: `{closure.get('source_file_count')}`",
        f"- Python files: `{closure.get('python_file_count')}`",
        f"- shell scripts: `{closure.get('shell_script_count')}`",
        f"- runner tool files present: `{rr.get('present_tool_count', 'not checked')}`",
        "",
        "## Errors",
        "",
    ]
    md.extend([f"- `{e}`" for e in audit_doc.get("errors", [])] if audit_doc.get("errors") else ["- none"])
    md.extend(["", "## Decision", "", audit_doc.get("decision", "")])
    (OUT / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER_CLOSURE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit the live closure copied into the public-trace external runner.")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--runner-root", type=Path, default=None, help="Check a built/extracted runner root against the live closure.")
    ap.add_argument("--source-root", type=Path, default=ROOT)
    args = ap.parse_args()
    source_root = args.source_root.resolve()
    runner_root = args.runner_root.resolve() if args.runner_root else None
    audit_doc = audit(source_root, runner_root=runner_root)
    write_outputs(audit_doc)
    print(json.dumps({
        "status": audit_doc["status"],
        "source_file_count": audit_doc["closure"]["source_file_count"],
        "python_file_count": audit_doc["closure"]["python_file_count"],
        "errors": audit_doc["errors"],
    }, indent=2))
    if args.strict and audit_doc["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
