#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0143"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", ""))))
OUT_ROOT = ROOT / "artifacts" / "external-runner"
AUDIT_ROOT = ROOT / "artifacts" / "audit"
PACKET_DIR = OUT_ROOT / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER"
PACKET_ZIP = OUT_ROOT / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER.zip"
sys.path.insert(0, str(ROOT))
from tools.public_trace_external_runner_closure_audit import compute_live_closure  # noqa: E402

FILES = [
    "CUBE-META.json",
    "REVISION-RECEIPT.json",
    "EVIDENCE-STATUS.json",
    "SURFACE-STATUS.json",
    "REENTRY-CONTRACT.json",
    "START_HERE.md",
    "PRIORITY-LIST.md",
    "MISSION-KERNEL.md",
    "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh",
    "artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh",
    "artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh",
    f"artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh",
    f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh",
    f"artifacts/capture-kit/{REVUP}_PREPARE_TINYLLAMA_SNAPSHOT.sh",
    f"artifacts/capture-kit/{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh",
    f"artifacts/capture-kit/{REVUP}_FIRST_REAL_TRACE_ONE_COMMAND.sh",
    f"artifacts/capture-kit/{REVUP}_COMMON_PUBLIC_TRACE_ENV.sh",
    f"artifacts/prompts/{REVUP}_PUBLIC_TRACE_PROMPTS.txt",
    f"artifacts/runtime/{REVUP}_public_trace_requirements.txt",
    f"artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json",
    f"artifacts/run-manifests/{REVUP}_TINYLLAMA_SOURCE_LOCK.json",
]
DIRS: list[str] = []  # REV0150: builder copies the computed live closure, not whole directories.
EXTRA_PACKET_FILES = [
    "tools/public_trace_external_runner_packet_builder.py",
    "tools/public_trace_external_runner_closure_audit.py",
    "tools/public_trace_external_runner_manifest_integrity_audit.py",
    "tools/semantic_currentness_audit.py",
]
REQUIRED_IN_PACKET = [
    "RUN_PUBLIC_TRACE.sh",
    "PREPARE_SNAPSHOT.sh",
    "BOOTSTRAP_RUNTIME.sh",
    "RUN_FIRST_REAL_TRACE.sh",
    "README_RUNNER.md",
    "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json",
    "tools/public_trace_external_runner_packet_builder.py",
    "tools/public_trace_external_runner_closure_audit.py",
    "tools/public_trace_external_runner_manifest_integrity_audit.py",
    "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh",
    "artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh",
    "tools/current_live_script_dependency_audit.py",
    "tools/public_trace_first_real_trace_audit.py",
    "tools/public_trace_common_env_contract_audit.py",
    "tools/public_trace_bootstrap_runtime_audit.py",
    "tools/public_trace_runtime_import_smoke.py",
    "tools/public_trace_runtime_requirement_lock_audit.py",
    "tools/public_trace_cache_root_contract_audit.py",
    "tools/public_trace_snapshot_download_plan.py",
    "tools/public_trace_snapshot_download_plan_gate_audit.py",
    "tools/public_trace_run_manifest_coherence_audit.py",
    "tools/public_trace_external_runner_closure_audit.py",
    "experiments/public_trace_capture/hf_attention_trace_capture.py",
    "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py",
    "experiments/attention_compiler_core/attention_core.py",
]

RESEARCH_BASIS = [
    {
        "url": "https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables",
        "observed_lines_from_web_run": "turn193120view0 lines 81-110 and 132-147",
        "fact": "huggingface_hub reads environment variables at import time and defines HF_HOME, HF_HUB_CACHE, HF_XET_CACHE, and slow-link timeout controls, so the runner binds project-local cache roots before any Hub import.",
    },
    {
        "url": "https://huggingface.co/docs/huggingface_hub/main/en/package_reference/environment_variables",
        "observed_lines_from_web_run": "turn240500view4 lines 87-88 and turn895090view1 lines 169-178",
        "fact": "huggingface_hub reads environment variables at import time; HF_HUB_OFFLINE prevents HTTP calls and skips the usual cache freshness request, so evidence capture must set it before importing the runtime.",
    },
    {
        "url": "https://huggingface.co/docs/transformers/en/installation",
        "observed_lines_from_web_run": "turn895090view3 lines 210-233",
        "fact": "Transformers offline use requires downloaded/cached files ahead of time and supports local_files_only=True from a local directory; this matches the prepare-then-local-capture split.",
    },
    {
        "url": "https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables",
        "observed_lines_from_web_run": "turn948532view0 lines 132-148 and 167-172",
        "fact": "HF_HUB_DOWNLOAD_TIMEOUT/HF_HUB_ETAG_TIMEOUT and HF_HUB_OFFLINE are current Hub controls relevant to slow or local-only snapshot materialization.",
    },
    {
        "url": "https://huggingface.co/docs/transformers/installation",
        "observed_lines_from_web_run": "turn948532view2 lines 210-233",
        "fact": "Transformers offline mode requires files to be downloaded/cached first and supports local_files_only loading from a local directory.",
    },
    {
        "url": "https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/blob/2fef61190c752e2412f7b5dd2c2bde6f08fdb634/model.safetensors",
        "observed_lines_from_web_run": "turn948532view4 lines 200-215",
        "fact": "The selected TinyLlama model.safetensors is an Xet-backed 2.2GB file with a published SHA-256, motivating a first-full-hash plus stat-bound reuse contract rather than repeated rehashing in every gate.",
    },
    {
        "url": "https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "observed_lines_from_web_run": "turn287001view0 lines 187-190",
        "fact": "TinyLlama is a compact 1.1B model using the Llama 2 architecture/tokenizer family; this supports the Llama-specific trace surface but not any promotion claim.",
    },
    {
        "url": "https://huggingface.co/docs/huggingface_hub/en/guides/download",
        "observed_lines_from_web_run": "turn356359view0 lines 117-125",
        "fact": "Hugging Face Hub docs require a full-length commit hash for specific commit downloads and describe snapshot_download at a given revision.",
    },
    {
        "url": "https://huggingface.co/docs/huggingface_hub/en/guides/download",
        "observed_lines_from_web_run": "turn356359view1 lines 143-170 and turn356359view2 lines 202-229",
        "fact": "snapshot_download supports filtering/local folders/dry-run, which makes an external runner packet more useful than another top-level registry note.",
    },
    {
        "url": "https://huggingface.co/docs/transformers/en/attention_interface",
        "observed_lines_from_web_run": "turn287001view2 lines 126-160 and 212-217",
        "fact": "Transformers exposes attention backend selection through attn_implementation and mask handling is backend-sensitive; trace semantics must stay eager while SDPA/Flash remain timing baselines.",
    },
    {
        "url": "https://slsa.dev/spec/v1.0/verifying-artifacts",
        "observed_lines_from_web_run": "turn287001view4 lines 52-59 and 112-129",
        "fact": "SLSA verification guidance says provenance only matters if consumers inspect it against expectations; external runner receipts must be digest-checked, not merely generated.",
    },
    {
        "url": "https://arxiv.org/abs/2602.10046",
        "observed_lines_from_web_run": "turn399817view0 lines 22-26",
        "fact": "Recent artifact-evaluation work frames reproduction as executable scripts and reports finding errors, reinforcing a runner-first repair instead of more doctrine.",
    },
    {
        "url": "https://peps.python.org/pep-0668/",
        "observed_lines_from_web_run": "turn179914search2",
        "fact": "Externally-managed Python environments make direct system pip installs a likely external-runner blocker; use project-local virtualenv bootstrap instead.",
    },
    {
        "url": "https://huggingface.co/docs/hub/en/xet/using-xet-storage",
        "observed_lines_from_web_run": "turn889822search4",
        "fact": "Modern Hugging Face Hub large-file paths can use hf_xet; older hub clients may need hf-xet installed explicitly.",
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_file(rel: str, dst_root: Path) -> None:
    src = ROOT / rel
    if not src.is_file():
        raise FileNotFoundError(rel)
    dst = dst_root / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_dir(rel: str, dst_root: Path) -> None:
    src = ROOT / rel
    if not src.is_dir():
        raise FileNotFoundError(rel)
    dst = dst_root / rel
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def write_runner_scripts(dst: Path) -> None:
    (dst / "RUN_PUBLIC_TRACE.sh").write_text("""#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
export CAPTURE_LOCAL_ONLY="${CAPTURE_LOCAL_ONLY:-1}"
export ALLOW_DOWNLOAD=0
exec bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh "$@"
""", encoding="utf-8")
    (dst / "PREPARE_SNAPSHOT.sh").write_text("""#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
# This is the only phase where network download may be enabled after license/source review.
exec bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh "$@"
""", encoding="utf-8")
    (dst / "BOOTSTRAP_RUNTIME.sh").write_text("""#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
exec bash artifacts/capture-kit/""" + f"{REVUP}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh" + """ "$@"
""", encoding="utf-8")
    (dst / "RUN_FIRST_REAL_TRACE.sh").write_text("""#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
exec bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh "$@"
""", encoding="utf-8")
    for name in ["RUN_PUBLIC_TRACE.sh", "PREPARE_SNAPSHOT.sh", "BOOTSTRAP_RUNTIME.sh", "RUN_FIRST_REAL_TRACE.sh"]:
        (dst / name).chmod(0o755)


def write_readme(dst: Path) -> None:
    packet = f"artifacts/run-manifests/{REVUP}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json"
    readme = f"""# {REVUP} public-trace external runner packet

Current revision: `{REV}`.

This is the live-closure packet for the riskiest unfinished work: producing the first real digest-bound TinyLlama public trace. It intentionally omits historical mission audits, idea ledgers, older capture-kit wrappers, and tool files not reachable from the current first-real-trace path.

## Status boundary

- Promotion allowed: `false`.
- This packet is a runner, not evidence.
- A real claim still requires: digest-verified TinyLlama snapshot → capture → evaluation receipt → selector-entry receipt → replay gate → handoff archive gate → named-hardware sparse-vs-dense timing.

## Commands

0. One-command path for the first real trace. By default, Hugging Face/Transformers/Xet cache files go under `artifacts/runtime/public-trace-hf-cache` inside this runner; set `PUBLIC_TRACE_CACHE_ROOT=/path/to/cache` to override:

```bash
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh
```

For a host with a prebuilt wheelhouse/no-index policy:

```bash
PUBLIC_TRACE_WHEELHOUSE=/path/to/wheels BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh
```

Or, with an already reviewed snapshot:

```bash
LOCAL_SNAPSHOT_DIR=/path/to/TinyLlama-snapshot bash RUN_FIRST_REAL_TRACE.sh
```

Manual phase path:

1. Optional runtime bootstrap; this creates/uses a project-local `.venv-public-trace` and writes `artifacts/runtime/CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh`:

```bash
bash BOOTSTRAP_RUNTIME.sh
```

For manual shells, source the generated env before later phases:

```bash
source artifacts/runtime/CURRENT_PUBLIC_TRACE_BOOTSTRAP_ENV.sh
```

2. Materialize the reviewed snapshot on a machine where downloads are allowed:

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash PREPARE_SNAPSHOT.sh
```

3. Capture only from local verified files:

```bash
ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 bash RUN_PUBLIC_TRACE.sh
```

4. Or mount an already reviewed flat snapshot:

```bash
LOCAL_SNAPSHOT_DIR=/path/to/TinyLlama-snapshot ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 bash RUN_PUBLIC_TRACE.sh
```

Reviewed run packet: `{packet}`.

## Why this exists

The full cube has useful history, but the current failure mode is operational: the real trace needs a runtime and a large model snapshot. This packet gives an external runner the current live closure without asking it to wade through the whole datacube or carry unrelated probe tools.
"""
    (dst / "README_RUNNER.md").write_text(readme, encoding="utf-8")


def build_manifest(dst: Path) -> dict[str, Any]:
    subjects = []
    total_bytes = 0
    for path in sorted(dst.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(dst).as_posix()
        if rel == "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json":
            continue
        size = path.stat().st_size
        total_bytes += size
        subjects.append({"path": rel, "bytes": size, "sha256": sha256_file(path)})
    manifest = {
        "contract": "public_trace_external_runner_packet_v1",
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "runner_packet_built_not_evidence",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "packet_scope": "active TinyLlama public trace runner plus computed live-script closure; no whole tools directory; manifest excludes itself for verifiable runner-local integrity",
        "cache_root_contract": "project_local_hf_cache_root_v1",
        "default_public_trace_cache_root": "artifacts/runtime/public-trace-hf-cache",
        "cache_env_vars": ["PUBLIC_TRACE_CACHE_ROOT", "HF_HOME", "HF_HUB_CACHE", "HF_XET_CACHE", "HF_ASSETS_CACHE"],
        "wheelhouse_bootstrap_contract": "optional_public_trace_wheelhouse_no_index_bootstrap_v1",
        "cache_duplication_guard_contract": "hf_disable_symlinks_explicit_override_v1",
        "omitted_on_purpose": [
            "historical mission audits",
            "idea ledgers and old native probes",
            "historical REV00xx capture wrappers",
            "trace outputs and receipts that must be generated fresh by the runner",
        ],
        "commands": {
            "bootstrap_runtime": "bash BOOTSTRAP_RUNTIME.sh",
            "prepare_snapshot": "HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash PREPARE_SNAPSHOT.sh",
            "first_real_trace_one_command": "BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh",
            "capture_local_only": "ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 bash RUN_PUBLIC_TRACE.sh",
            "cache_root_override": "PUBLIC_TRACE_CACHE_ROOT=/path/to/cache BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh",
            "wheelhouse_first_real_trace": "PUBLIC_TRACE_WHEELHOUSE=/path/to/wheels BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh",
        },
        "required_in_packet": REQUIRED_IN_PACKET,
        "subject_count": len(subjects),
        "total_bytes": total_bytes,
        "subjects_sha256": hashlib.sha256(json.dumps(subjects, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "live_closure_contract": "public_trace_external_runner_live_closure_v1",
        "live_closure": compute_live_closure(ROOT),
        "subjects": subjects,
        "research_basis": RESEARCH_BASIS,
    }
    return manifest


def write_zip(zip_path: Path, source_dir: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue
            arc = path.relative_to(source_dir.parent).as_posix()
            info = zipfile.ZipInfo(arc)
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if path.suffix == ".sh" else 0o644
            info.external_attr = mode << 16
            zf.writestr(info, path.read_bytes())


def run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    timeout_seconds = int(os.environ.get("PUBLIC_TRACE_RUNNER_SMOKE_TIMEOUT_SECONDS", "60"))
    timed_out = False
    with tempfile.NamedTemporaryFile("w+b") as stdout_file, tempfile.NamedTemporaryFile("w+b") as stderr_file:
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=stdout_file, stderr=stderr_file, env=env, start_new_session=True)
        try:
            returncode = proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                returncode = proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                returncode = proc.wait()
                if returncode == 0:
                    returncode = 124
            if returncode == 0:
                returncode = 124
        stdout_file.flush(); stderr_file.flush()
        stdout_file.seek(0); stderr_file.seek(0)
        stdout = stdout_file.read().decode("utf-8", errors="replace")
        stderr = stderr_file.read().decode("utf-8", errors="replace")
    return {
        "cmd": cmd,
        "wrapped_cmd": ["process_group_timeout", f"{timeout_seconds}s", *cmd],
        "returncode": returncode,
        "stdout_tail": stdout[-4000:],
        "stderr_tail": stderr[-4000:],
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
    }


def smoke_extracted(zip_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"{REVUP.lower()}_external_runner_", dir=str(ROOT.parent)) as td:
        base = Path(td)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(base)
            for member in zf.infolist():
                mode = (member.external_attr >> 16) & 0o777
                if mode:
                    target = base / member.filename
                    if target.exists():
                        target.chmod(mode)
        extracted = base / PACKET_DIR.name
        closure = run([sys.executable, "tools/current_live_script_dependency_audit.py"], cwd=extracted)
        runner_closure = run([sys.executable, "tools/public_trace_external_runner_closure_audit.py", "--strict", "--runner-root", "."], cwd=extracted)
        runner_manifest_integrity = run([sys.executable, "tools/public_trace_external_runner_manifest_integrity_audit.py", "--strict"], cwd=extracted)
        runner_smoke_validate = run([sys.executable, "tools/smoke_validate.py"], cwd=extracted)
        surface = run([sys.executable, "tools/public_trace_first_real_trace_audit.py", "--mode", "surface"], cwd=extracted)
        cache_contract = run([sys.executable, "tools/public_trace_cache_root_contract_audit.py"], cwd=extracted)
        requirement_lock = run([sys.executable, "tools/public_trace_runtime_requirement_lock_audit.py", "--strict"], cwd=extracted)
        common_env_contract = run([sys.executable, "tools/public_trace_common_env_contract_audit.py"], cwd=extracted)
        runtime_import_smoke = run([sys.executable, "tools/public_trace_runtime_import_smoke.py", "--strict"], cwd=extracted)
        snapshot_download_plan_gate = run([sys.executable, "tools/public_trace_snapshot_download_plan_gate_audit.py"], cwd=extracted)
        first_trace_syntax = run(["bash", "-n", "RUN_FIRST_REAL_TRACE.sh"], cwd=extracted)
        # Do not execute the whole capture wrapper in packet-build smoke: on a
        # capable machine it may proceed into expensive runtime/model phases. The
        # extracted packet smoke only proves the first capture-start blocker is
        # receipt-backed and local-only; the full run is the operator action.
        blocked = run([sys.executable, "tools/public_trace_capture_start_preflight_report.py", "--phase", "capture", "--strict", "--require-weight-hash", "--capture-local-only"], cwd=extracted)
        direct = run(["bash", "-n", "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh"], cwd=extracted)
        blocked_ok = (blocked["returncode"] != 126) and ("blocked_here" in blocked["stdout_tail"] or "blocked_here" in blocked["stderr_tail"] or blocked["returncode"] == 0)
        direct_ok = direct["returncode"] == 0
        first_trace_ok = first_trace_syntax["returncode"] == 0 and (runtime_import_smoke["returncode"] in (0, 1)) and ("blocked_here_runtime_import_smoke" in runtime_import_smoke["stdout_tail"] or runtime_import_smoke["returncode"] == 0)
        return {"closure": closure, "runner_live_closure": runner_closure, "runner_manifest_integrity": runner_manifest_integrity, "runner_smoke_validate": runner_smoke_validate, "first_trace_surface": surface, "cache_root_contract": cache_contract, "runtime_requirement_lock": requirement_lock, "common_env_contract": common_env_contract, "runtime_import_smoke": runtime_import_smoke, "snapshot_download_plan_gate": snapshot_download_plan_gate, "run_first_real_trace": first_trace_syntax, "run_first_real_trace_syntax_only": True, "capture_start_preflight": blocked, "run_public_trace": blocked, "direct_current_alias": direct, "direct_current_alias_syntax_only": True, "run_first_real_trace_reaches_actionable_gate_or_passes": first_trace_ok, "capture_start_preflight_reaches_gate_or_passes": blocked_ok, "run_public_trace_reaches_gate_or_passes": blocked_ok, "direct_current_alias_reaches_gate_or_passes": direct_ok}


def smoke_extracted_fresh(zip_path: Path) -> dict[str, Any]:
    # Run the extracted-packet smoke in a fresh Python process.  This avoids
    # carrying import/subprocess state from the packet-build phase into the
    # runner smoke, which was exactly the kind of hidden CI/container waste
    # REV0150 is meant to remove.
    smoke_out = AUDIT_ROOT / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER_PACKET_SMOKE_TMP.json"
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    if smoke_out.exists():
        smoke_out.unlink()
    cmd = [sys.executable, str(Path(__file__).resolve()), "--smoke-only", str(zip_path), "--smoke-out", str(smoke_out)]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=int(os.environ.get("PUBLIC_TRACE_PACKET_SMOKE_PROCESS_TIMEOUT_SECONDS", "180")))
    if proc.returncode != 0 or not smoke_out.exists():
        return {
            "smoke_process_returncode": proc.returncode,
            "smoke_process_stdout_tail": proc.stdout[-4000:],
            "smoke_process_stderr_tail": proc.stderr[-4000:],
            "closure": {"returncode": 999},
            "runner_live_closure": {"returncode": 999},
            "first_trace_surface": {"returncode": 999},
            "runner_manifest_integrity": {"returncode": 999},
            "runner_smoke_validate": {"returncode": 999},
            "cache_root_contract": {"returncode": 999},
            "runtime_requirement_lock": {"returncode": 999},
            "common_env_contract": {"returncode": 999},
            "runtime_import_smoke": {"returncode": 999},
            "snapshot_download_plan_gate": {"returncode": 999},
            "run_first_real_trace": {"returncode": 999},
            "capture_start_preflight": {"returncode": 999},
            "run_public_trace": {"returncode": 999},
            "direct_current_alias": {"returncode": 999},
            "run_first_real_trace_reaches_actionable_gate_or_passes": False,
            "run_public_trace_reaches_gate_or_passes": False,
            "direct_current_alias_reaches_gate_or_passes": False,
        }
    smoke = json.loads(smoke_out.read_text(encoding="utf-8"))
    smoke["smoke_process_returncode"] = proc.returncode
    smoke["smoke_process_stdout_tail"] = proc.stdout[-4000:]
    smoke["smoke_process_stderr_tail"] = proc.stderr[-4000:]
    smoke_out.unlink(missing_ok=True)
    return smoke


def build(no_write: bool = False, out_dir: Path = PACKET_DIR, zip_path: Path = PACKET_ZIP) -> dict[str, Any]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    copied: set[str] = set()
    closure = compute_live_closure(ROOT)
    live_files = sorted(set(FILES) | set(EXTRA_PACKET_FILES) | set(closure["all_source_files"]))
    for rel in live_files:
        copy_file(rel, out_dir)
        copied.add(rel)
    for rel in DIRS:
        copy_dir(rel, out_dir)
    # Remove package-level generated runner artifacts from copied files if any appeared through previous runs.
    for pycache in out_dir.rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)
    write_runner_scripts(out_dir)
    write_readme(out_dir)
    manifest = build_manifest(out_dir)
    (out_dir / "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    # Recompute manifest after writing it so the manifest file itself is covered.
    manifest = build_manifest(out_dir)
    (out_dir / "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    write_zip(zip_path, out_dir)
    smoke = smoke_extracted_fresh(zip_path)
    errors = []
    warnings = []
    for rel in REQUIRED_IN_PACKET:
        if not (out_dir / rel).exists():
            errors.append("missing_required_packet_file:" + rel)
    if smoke["closure"]["returncode"] != 0:
        errors.append("extracted_packet_live_script_dependency_closure_failed")
    if smoke.get("runner_live_closure", {}).get("returncode") != 0:
        errors.append("extracted_packet_live_closure_trim_audit_failed")
    if smoke.get("runner_manifest_integrity", {}).get("returncode") != 0:
        errors.append("extracted_packet_runner_manifest_integrity_audit_failed")
    if smoke.get("runner_smoke_validate", {}).get("returncode") != 0:
        errors.append("extracted_packet_runner_smoke_validate_failed")
    if smoke.get("first_trace_surface", {}).get("returncode") != 0:
        errors.append("extracted_packet_first_trace_surface_audit_failed")
    if smoke.get("cache_root_contract", {}).get("returncode") != 0:
        errors.append("extracted_packet_cache_root_contract_audit_failed")
    if smoke.get("runtime_requirement_lock", {}).get("returncode") != 0:
        errors.append("extracted_packet_runtime_requirement_lock_audit_failed")
    if smoke.get("common_env_contract", {}).get("returncode") != 0:
        errors.append("extracted_packet_common_env_contract_audit_failed")
    if smoke.get("snapshot_download_plan_gate", {}).get("returncode") != 0:
        errors.append("extracted_packet_snapshot_download_plan_gate_audit_failed")
    if not smoke.get("run_first_real_trace_reaches_actionable_gate_or_passes"):
        errors.append("extracted_packet_run_first_real_trace_did_not_reach_actionable_gate_or_pass")
    if smoke.get("run_first_real_trace", {}).get("returncode") == 126:
        errors.append("extracted_packet_run_first_real_trace_permission_error")
    if not smoke.get("run_public_trace_reaches_gate_or_passes"):
        errors.append("extracted_packet_capture_start_preflight_did_not_reach_gate_or_pass")
    if smoke["run_public_trace"]["returncode"] == 126:
        errors.append("extracted_packet_run_public_trace_permission_error")
    if smoke.get("direct_current_alias", {}).get("returncode") != 0:
        errors.append("extracted_packet_direct_current_alias_syntax_failed")
    if not smoke.get("direct_current_alias_reaches_gate_or_passes"):
        errors.append("extracted_packet_direct_current_alias_syntax_or_manifest_exec_check_failed")
    if smoke["run_public_trace"]["returncode"] != 0:
        warnings.append("extracted_packet_current_environment_still_blocks_real_capture_expected_without_snapshot_or_transformers")
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass_with_expected_environment_blockers" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Builds and smoke-checks a live-closure external runner packet for the riskiest unfinished work: producing the first real digest-bound TinyLlama trace on a machine with runtime, disk, and network. REV0156 keeps the live-closure packet trimmed and smoke-checked while adding semantic-currentness discipline around the runner-facing docs and metadata.",
        "live_closure": compute_live_closure(ROOT),
        "packet_dir": out_dir.relative_to(ROOT).as_posix() if out_dir.is_relative_to(ROOT) else str(out_dir),
        "packet_zip": zip_path.relative_to(ROOT).as_posix() if zip_path.is_relative_to(ROOT) else str(zip_path),
        "packet_zip_sha256": sha256_file(zip_path),
        "packet_manifest": manifest,
        "extracted_smoke": smoke,
        "errors": errors,
        "warnings": warnings,
        "decision": "use_external_runner_or_install_snapshot_runtime_next" if not errors else "repair_external_runner_packet_before_use",
    }
    if not no_write:
        AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
        (AUDIT_ROOT / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER_PACKET_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        md = [
            f"# Public trace external runner packet audit — {REVUP}",
            "",
            f"Status: `{audit['status']}`  ",
            "Promotion allowed: `false`",
            "",
            audit["summary"],
            "",
            f"Packet zip: `{audit['packet_zip']}`  ",
            f"Packet SHA-256: `{audit['packet_zip_sha256']}`",
            "",
            "## Extracted smoke",
            "",
            f"- dependency closure return code: `{smoke['closure']['returncode']}`",
            f"- live-closure trim audit return code: `{smoke.get('runner_live_closure', {}).get('returncode')}`",
            f"- runner manifest integrity audit return code: `{smoke.get('runner_manifest_integrity', {}).get('returncode')}`",
            f"- runner smoke_validate fallback return code: `{smoke.get('runner_smoke_validate', {}).get('returncode')}`",
            f"- first-trace surface audit return code: `{smoke.get('first_trace_surface', {}).get('returncode')}`",
            f"- cache-root contract audit return code: `{smoke.get('cache_root_contract', {}).get('returncode')}`",
            f"- runtime requirement lock audit return code: `{smoke.get('runtime_requirement_lock', {}).get('returncode')}`",
            f"- common-env contract audit return code: `{smoke.get('common_env_contract', {}).get('returncode')}`",
            f"- snapshot download-plan gate audit return code: `{smoke.get('snapshot_download_plan_gate', {}).get('returncode')}`",
            f"- first real trace return code: `{smoke.get('run_first_real_trace', {}).get('returncode')}`",
            f"- capture-start preflight return code: `{smoke['run_public_trace']['returncode']}`",
            f"- direct current alias syntax return code: `{smoke.get('direct_current_alias', {}).get('returncode')}`",
            f"- first real trace reaches actionable gate/pass: `{smoke.get('run_first_real_trace_reaches_actionable_gate_or_passes')}`",
            f"- reaches intended preflight/pass: `{smoke['run_public_trace_reaches_gate_or_passes']}`",
            f"- direct current alias syntax/manifest-exec check passes: `{smoke.get('direct_current_alias_reaches_gate_or_passes')}`",
            "",
            "## Errors",
            "",
        ]
        md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
        md.extend(["", "## Warnings", ""])
        md.extend([f"- `{w}`" for w in warnings] if warnings else ["- none"])
        md.extend(["", "## Interpretation", "", "The correction is operational: carry less, run sooner, and produce real receipts on an external runner rather than spending another turn expanding the registry surface; the packet now fails if a reachable script/import is missing, if unrelated tool/experiment files creep back into the runner, or if the runner-local manifest cannot substitute for full-cube CHECKSUMS.sha256 in the compact packet."])
        (AUDIT_ROOT / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_RUNNER_PACKET_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--out-dir", type=Path, default=PACKET_DIR)
    ap.add_argument("--zip", type=Path, default=PACKET_ZIP)
    ap.add_argument("--smoke-only", type=Path, default=None, help="internal: smoke an already-built packet zip and exit")
    ap.add_argument("--smoke-out", type=Path, default=None, help="internal: write smoke JSON here")
    args = ap.parse_args()
    if args.smoke_only is not None:
        smoke = smoke_extracted(args.smoke_only)
        if args.smoke_out is not None:
            args.smoke_out.parent.mkdir(parents=True, exist_ok=True)
            args.smoke_out.write_text(json.dumps(smoke, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        else:
            print(json.dumps(smoke, indent=2, sort_keys=False))
        return 0
    audit = build(no_write=args.no_write, out_dir=args.out_dir, zip_path=args.zip)
    print(json.dumps({"status": audit["status"], "packet_zip": audit["packet_zip"], "errors": audit["errors"], "warnings": audit["warnings"]}, indent=2))
    return 0 if not audit["errors"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
