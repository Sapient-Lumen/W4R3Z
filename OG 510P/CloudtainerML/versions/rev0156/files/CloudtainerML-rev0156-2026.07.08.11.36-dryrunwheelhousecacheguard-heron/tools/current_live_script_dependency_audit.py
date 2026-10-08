#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

STABLE_RUN = Path("artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh")
STABLE_PREPARE = Path("artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh")
CURRENT_RUN = Path(f"artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh")
CURRENT_ONE_SHOT = Path(f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh")
CURRENT_PREPARE = Path(f"artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh")
CURRENT_BOOTSTRAP = Path(f"artifacts/capture-kit/{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh")
CURRENT_COMMON_ENV = Path(f"artifacts/capture-kit/{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh")
STABLE_FIRST_TRACE = Path("artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh")
CURRENT_FIRST_TRACE = Path(f"artifacts/capture-kit/{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh")
ACTIVE_SCRIPTS = [STABLE_RUN, STABLE_PREPARE, STABLE_FIRST_TRACE, CURRENT_RUN, CURRENT_ONE_SHOT, CURRENT_PREPARE, CURRENT_BOOTSTRAP, CURRENT_FIRST_TRACE, CURRENT_COMMON_ENV]

PYTHON_REL_RE = re.compile(r"(?:python3|python|sys\.executable)\s+([A-Za-z0-9_./-]+\.py)")
BASH_REL_RE = re.compile(r"(?:bash|exec)\s+(?:\"\$HERE/)?([A-Za-z0-9_./$\{\}-]+\.sh)\"?")
SOURCE_REL_RE = re.compile(r"(?:source|\.)\s+(?:\"\$HERE/)?([A-Za-z0-9_./$\{\}-]+\.sh)\"?")
DIRECT_EXEC_SHELL_RE = re.compile(r"^\s*exec\s+(?!bash\b)(?!/usr/bin/env\s+bash\b)(?:\"\$HERE/)?([A-Za-z0-9_./$\{\}-]+\.sh)\"?", re.M)
REQ_ASSIGN_RE = re.compile(r"^\s*([A-Z_][A-Z0-9_]*)=\"([^\"]+_public_trace_requirements\.txt)\"", re.M)
REQ_LITERAL_RE = re.compile(r"([A-Za-z0-9_./$\{\}-]+_public_trace_requirements\.txt)")
DYNAMIC_REV_SHELL_RE = re.compile(r"\$\{REVUP\}_([A-Z0-9_]+\.sh)")
STALE_REV_RE = re.compile(r"REV(\d{4})_[A-Z0-9_]+\.(?:sh|py)")
ASSIGNMENT_CONCAT_RE = re.compile(r"(?:\"|\'|\)|\])(?=[A-Z_][A-Z0-9_]*=)")


def read(rel: Path) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


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
        text = text[len("$HERE/"):]
        return (script_dir / text).as_posix()
    if text.startswith("./"):
        text = text[2:]
        return (script_dir / text).as_posix()
    if text.startswith("artifacts/") or text.startswith("tools/") or text.startswith("experiments/") or text == "VERIFY_HANDOFF.py":
        return text
    if text.startswith(f"{REVUP}_"):
        return (script_dir / text).as_posix()
    return None


def extract_python_refs(src: str) -> list[str]:
    refs: list[str] = []
    for match in PYTHON_REL_RE.finditer(src):
        rel = match.group(1).strip().strip('"').strip("'")
        if rel.startswith(("tools/", "experiments/")) or rel == "VERIFY_HANDOFF.py":
            refs.append(rel)
    return sorted(set(refs))


def extract_shell_refs(src: str, *, script_dir: Path) -> list[str]:
    refs: list[str] = []
    for pattern in (BASH_REL_RE, SOURCE_REL_RE):
        for match in pattern.finditer(src):
            rel = normalize_shell_ref(match.group(1), script_dir=script_dir)
            if rel:
                refs.append(rel)
    # Explicit dynamic exec pattern in stable/current wrappers.
    for match in DYNAMIC_REV_SHELL_RE.finditer(src):
        refs.append((script_dir / f"{REVUP}_{match.group(1)}").as_posix())
    return sorted(set(refs))



def extract_requirement_refs(src: str, *, script_dir: Path) -> list[str]:
    refs: set[str] = set()
    assignments = {m.group(1): m.group(2) for m in REQ_ASSIGN_RE.finditer(src)}
    for match in REQ_LITERAL_RE.finditer(src):
        raw = match.group(1).strip().strip('"').strip("'")
        if raw.startswith('$'):
            raw = assignments.get(raw[1:], raw)
        if raw.startswith('${') and raw.endswith('}'):
            raw = assignments.get(raw[2:-1], raw)
        if '${REVUP}' in raw:
            raw = raw.replace('${REVUP}', REVUP)
        if raw.startswith('$HERE/'):
            refs.add((script_dir / raw[len('$HERE/'):]).as_posix())
        elif raw.startswith('artifacts/'):
            refs.add(raw)
    # Also catch pip install -r "$REQ" with variable indirection.
    for var, value in assignments.items():
        if f'-r "${var}"' in src or f"-r '${var}'" in src or f'-r ${var}' in src:
            refs.add(value.replace('${REVUP}', REVUP))
    return sorted(refs)


def shell_syntax_check(rel: Path) -> dict[str, Any]:
    path = ROOT / rel
    if not path.is_file():
        return {"checked": False, "returncode": None, "stderr_tail": ""}
    try:
        proc = subprocess.run(["bash", "-n", str(path)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        return {"checked": True, "returncode": proc.returncode, "stderr_tail": proc.stderr[-1200:]}
    except Exception as exc:
        return {"checked": False, "returncode": 999, "stderr_tail": repr(exc)}


def assignment_concat_hazards(src: str) -> list[str]:
    out: list[str] = []
    for lineno, line in enumerate(src.splitlines(), start=1):
        if ASSIGNMENT_CONCAT_RE.search(line):
            out.append(f"line_{lineno}:{line.strip()[:160]}")
    return out

def script_report(rel: Path) -> dict[str, Any]:
    src = read(rel)
    script_dir = rel.parent
    python_refs = extract_python_refs(src)
    shell_refs = extract_shell_refs(src, script_dir=script_dir)
    stale = []
    syntax = shell_syntax_check(rel)
    assignment_hazards = assignment_concat_hazards(src)
    for match in STALE_REV_RE.finditer(src):
        old = "REV" + match.group(1)
        if old != REVUP:
            stale.append(match.group(0))
    requirement_refs = extract_requirement_refs(src, script_dir=script_dir)
    direct_exec_shell_refs = []
    for match in DIRECT_EXEC_SHELL_RE.finditer(src):
        rel_exec = normalize_shell_ref(match.group(1), script_dir=script_dir)
        if rel_exec:
            direct_exec_shell_refs.append(rel_exec)
    concatenation_hazards = sorted({h for h in ["pypython3", "thenif", "fifi", "donepython3", "thenpython3"] if h in src})
    missing_python = [r for r in python_refs if not (ROOT / r).is_file()]
    missing_shell = [r for r in shell_refs if not (ROOT / r).is_file()]
    missing_requirements = [r for r in requirement_refs if not (ROOT / r).is_file()]
    return {
        "script": rel.as_posix(),
        "exists": (ROOT / rel).is_file(),
        "python_refs": python_refs,
        "shell_refs": shell_refs,
        "requirement_refs": requirement_refs,
        "direct_exec_shell_refs": sorted(set(direct_exec_shell_refs)),
        "missing_python_refs": missing_python,
        "missing_shell_refs": missing_shell,
        "missing_requirement_refs": missing_requirements,
        "concatenation_hazards": concatenation_hazards,
        "assignment_concatenation_hazards": assignment_hazards,
        "shell_syntax": syntax,
        "stale_revision_refs": sorted(set(stale)),
    }


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    reports = [script_report(rel) for rel in ACTIVE_SCRIPTS]
    for rep in reports:
        if not rep["exists"]:
            errors.append("missing_active_script:" + rep["script"])
        for rel in rep["missing_python_refs"]:
            errors.append(f"{rep['script']} references missing python file: {rel}")
        for rel in rep["missing_shell_refs"]:
            errors.append(f"{rep['script']} references missing shell file: {rel}")
        for rel in rep.get("missing_requirement_refs", []):
            errors.append(f"{rep['script']} references missing requirement file: {rel}")
        for rel in rep.get("direct_exec_shell_refs", []):
            errors.append(f"{rep['script']} directly execs shell script without bash interpreter: {rel}")
        for hazard in rep.get("concatenation_hazards", []):
            errors.append(f"{rep['script']} shell concatenation hazard: {hazard}")
        if rep.get("shell_syntax", {}).get("returncode") not in (0, None):
            errors.append(f"{rep['script']} bash -n failed: {rep.get('shell_syntax', {}).get('stderr_tail')}")
        for hazard in rep.get("assignment_concatenation_hazards", []):
            errors.append(f"{rep['script']} assignment concatenation hazard: {hazard}")
        for rel in rep["stale_revision_refs"]:
            errors.append(f"{rep['script']} contains stale revision executable reference: {rel}")
    # Hard requirement: the live one-shot must call the closure audit itself before capture.
    one_shot_text = read(CURRENT_ONE_SHOT)
    run_text = read(CURRENT_RUN)
    first_trace_text = read(CURRENT_FIRST_TRACE)
    common_text = read(CURRENT_COMMON_ENV)
    if "tools/current_live_script_dependency_audit.py" not in one_shot_text:
        errors.append("current one-shot wrapper does not run current_live_script_dependency_audit")
    if "tools/current_live_script_dependency_audit.py" not in run_text:
        errors.append("current run wrapper does not run current_live_script_dependency_audit")

    if "PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE=1" not in run_text:
        errors.append("current run wrapper must export PUBLIC_TRACE_CAPTURE_PREFLIGHT_DONE=1 before one-shot handoff")
    if "capture_start_preflight_done_selected_snapshot_v1" not in run_text or "capture_start_preflight_done_selected_snapshot_v1" not in one_shot_text:
        errors.append("current live wrappers missing preflight handoff contract marker")
    if "tools/public_trace_capture_preflight_handoff_audit.py" not in run_text or "tools/public_trace_capture_preflight_handoff_audit.py" not in one_shot_text:
        errors.append("current live wrappers missing preflight handoff audit marker")
    if "tools/public_trace_common_env_contract_audit.py" not in first_trace_text + run_text + one_shot_text + common_text:
        errors.append("active wrappers missing common env contract audit marker")
    for marker in ["tools/public_trace_run_manifest_coherence_audit.py", "tools/public_trace_bootstrap_runtime_audit.py"]:
        if marker not in run_text:
            errors.append("current run wrapper missing active audit marker: " + marker)
    if "tools/current_live_script_dependency_audit.py" not in first_trace_text:
        errors.append("current first-real-trace wrapper does not run current_live_script_dependency_audit")
    if "ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1" not in first_trace_text:
        errors.append("current first-real-trace wrapper must force local-only capture phase")
    if "public_trace_first_real_trace_audit.py --mode status" not in first_trace_text:
        errors.append("current first-real-trace wrapper must write status audit receipt")
    if "tools/public_trace_run_manifest_coherence_audit.py" not in first_trace_text:
        errors.append("current first-real-trace wrapper must run run-manifest coherence audit")
    if "tools/public_trace_bootstrap_runtime_audit.py" not in first_trace_text:
        errors.append("current first-real-trace wrapper must run bootstrap runtime audit")
    if 'source "$BOOTSTRAP_ENV"' not in first_trace_text:
        errors.append("current first-real-trace wrapper must source bootstrap env so venv PATH persists after bootstrap")
    expected_prompt_default = 'PROMPT_MANIFEST:-artifacts/prompts/${REVUP}_PUBLIC_TRACE_PROMPTS.txt'
    for label, text in (("current_run", run_text), ("current_one_shot", one_shot_text)):
        if "PUBLIC_TRACE_PROMPTS.jsonl" in text:
            errors.append(label + " still defaults to missing .jsonl prompt manifest")
        if expected_prompt_default not in (text + common_text):
            errors.append(label + " prompt manifest default does not target the current .txt manifest or sourced common env")
    audit = {
        "revision": REV,
        "revision_number": int(META.get("revision_number") or REV.replace("rev", "") or 0),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "fail" if errors else "pass",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Static closure audit for the active live shell surface. It checks stable aliases plus current run/one-shot/prepare/bootstrap wrappers for missing Python, shell, and requirement-file targets; stale revision executable references; and non-portable direct exec of nested shell scripts before an operator spends time on a long capture attempt.",
        "active_scripts_checked": [p.as_posix() for p in ACTIVE_SCRIPTS],
        "reports": reports,
        "errors": errors,
        "warnings": warnings,
        "decision": "live_script_dependency_closure_ok" if not errors else "repair_missing_live_script_targets_before_capture",
    }
    (OUT / f"{REVUP}_CURRENT_LIVE_SCRIPT_DEPENDENCY_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Current live script dependency audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit["summary"],
        "",
        "## Active scripts checked",
        "",
    ]
    md.extend(f"- `{p.as_posix()}`" for p in ACTIVE_SCRIPTS)
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    md.extend(["", "## Warnings", ""])
    md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
    (OUT / f"{REVUP}_CURRENT_LIVE_SCRIPT_DEPENDENCY_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "warnings": warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
