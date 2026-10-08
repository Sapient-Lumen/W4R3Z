#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def maybe_load(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    return load(rel) if path.exists() else {}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_external_runner_manifest(errors: list[str], warnings: list[str]) -> bool:
    """Validate compact external-runner subjects when full-cube checksums are absent.

    REV0150: external runners intentionally omit most historical cube files. A
    successful capable-machine capture must not die at final smoke because
    CHECKSUMS.sha256 refers to a full source cube that the runner never claimed
    to carry. In runner mode, validate PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json
    instead. The manifest deliberately excludes itself to avoid an impossible
    self-hash.
    """
    manifest_path = ROOT / "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json"
    if not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append("external runner manifest unreadable: " + repr(exc))
        return True
    if manifest.get("contract") != "public_trace_external_runner_packet_v1":
        errors.append("external runner manifest unexpected contract: " + str(manifest.get("contract")))
    subjects = manifest.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        errors.append("external runner manifest has no subjects")
        return True
    clean_subjects = []
    seen: set[str] = set()
    for item in subjects:
        if not isinstance(item, dict):
            errors.append("external runner manifest malformed subject")
            continue
        rel = str(item.get("path", ""))
        if rel == "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json":
            errors.append("external runner manifest self-hash subject is not allowed")
            continue
        if not rel or rel.startswith("/") or ".." in Path(rel).parts:
            errors.append("external runner manifest unsafe subject: " + rel)
            continue
        if rel in seen:
            errors.append("external runner manifest duplicate subject: " + rel)
            continue
        seen.add(rel)
        target = ROOT / rel
        if not target.exists() or not target.is_file():
            errors.append("external runner manifest subject missing: " + rel)
            continue
        size = target.stat().st_size
        actual = sha256_file(target)
        if item.get("bytes") != size:
            errors.append("external runner manifest size mismatch: " + rel)
        if item.get("sha256") != actual:
            errors.append("external runner manifest sha256 mismatch: " + rel)
        clean_subjects.append({"path": rel, "bytes": size, "sha256": actual})
    if manifest.get("subject_count") != len(clean_subjects):
        errors.append("external runner manifest subject_count mismatch")
    total_bytes = sum(int(x["bytes"]) for x in clean_subjects)
    if manifest.get("total_bytes") != total_bytes:
        errors.append("external runner manifest total_bytes mismatch")
    expected_subjects_sha = hashlib.sha256(json.dumps(clean_subjects, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if manifest.get("subjects_sha256") != expected_subjects_sha:
        errors.append("external runner manifest subjects_sha256 mismatch")
    warnings.append("using external runner manifest integrity fallback instead of full-cube CHECKSUMS.sha256")
    return True




def validate_run_manifest_identity_live(errors: list[str], warnings: list[str], rev: str, revup: str, package_name: str, archive_name: str) -> None:
    """Reject stale current run-packet/source-lock identity even if their dedicated audit was not run."""
    revno = int(rev.replace("rev", ""))
    for rel in [f"artifacts/run-manifests/{revup}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json", f"artifacts/run-manifests/{revup}_TINYLLAMA_SOURCE_LOCK.json"]:
        path = ROOT / rel
        if not path.exists():
            errors.append("run_manifest_identity: missing " + rel)
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append("run_manifest_identity: unreadable " + rel + ":" + repr(exc))
            continue
        expected = {
            "revision": rev,
            "revision_number": revno,
            "revision_int": revno,
            "current_revision": rev,
            "current_revision_int": revno,
            "package_name": package_name,
            "archive_name": archive_name,
        }
        for key, val in expected.items():
            if data.get(key) != val:
                errors.append(f"run_manifest_identity: {rel} {key} expected={val!r} actual={data.get(key)!r}")
        blob = json.dumps(data, sort_keys=True)
        for stale in ["REV0153_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET", "REV0153_TINYLLAMA_SOURCE_LOCK", "rev0153_public_trace_prompt_set"]:
            if stale in blob and revup != "REV0153":
                errors.append(f"run_manifest_identity: {rel} stale token {stale}")

def validate_semantic_currentness_live(errors: list[str], warnings: list[str], rev: str, revup: str, package_name: str, archive_name: str) -> None:
    """Reject stale current surfaces that ordinary revision/checksum smoke can miss."""
    top_docs = ["README.md", "START_HERE.md", "START_HERE_SLIM.md", "NEXT-TURN-PROMPT.md", "PRIORITY-LIST.md", "MISSION-KERNEL.md", "PROJECT-CHARTER.md"]
    stale_terms = ["downloadplangate", "runnerclosuretrim", "runnermanifestfallback", "missionwastesemanticdrift", "value-norm", "value_norm", "REV0148_PUBLIC_TRACE_EXTERNAL_RUNNER", "REV0149_PUBLIC_TRACE_EXTERNAL_RUNNER", "REV0150_PUBLIC_TRACE_EXTERNAL_RUNNER", "REV0151_PUBLIC_TRACE_EXTERNAL_RUNNER"]
    def stale_refs(s: str) -> list[str]:
        return sorted({m.group(0) for m in re.finditer(r"(?i)rev\d{4}", s) if m.group(0).lower() != rev})
    for rel in top_docs:
        p = ROOT / rel
        if not p.exists():
            continue
        head = p.read_text(encoding="utf-8", errors="replace")[:5000]
        bad_refs = stale_refs(head)
        bad_terms = [x for x in stale_terms if x in head]
        if bad_refs:
            errors.append(f"semantic_currentness: {rel} stale revision refs near top: {bad_refs}")
        if bad_terms:
            errors.append(f"semantic_currentness: {rel} stale current terms near top: {bad_terms}")
    expected_current = {
        "current_external_runner_packet": f"artifacts/external-runner/{revup}_PUBLIC_TRACE_EXTERNAL_RUNNER.zip",
        "current_scientific_artifact": f"artifacts/run-manifests/{revup}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json",
        "current_lineage_artifact": f"MISSION-AUDIT-{revup}.md",
        "primary_lineage_artifact": f"MISSION-AUDIT-{revup}.md",
    }
    for rel in ["CUBE-META.json", "REVISION-RECEIPT.json", "EVIDENCE-STATUS.json", "SURFACE-STATUS.json", "REENTRY-CONTRACT.json", "BABY-DATACUBE-CANDIDATE.json"]:
        path = ROOT / rel
        if not path.exists():
            continue
        data = load(rel)
        for key, expected in expected_current.items():
            if key in data and data.get(key) != expected:
                errors.append(f"semantic_currentness: {rel} {key} {data.get(key)!r} != {expected!r}")
        for key in ["current_focus", "fresh_focus", "current_primary_change", "current_risk_focus", "summary", "revision_summary", "one_line_summary", "current_center", "current_best_next_step", "highlight"]:
            if key in data:
                value = str(data.get(key))
                bad_refs = stale_refs(value)
                bad_terms = [x for x in stale_terms if x in value]
                if bad_refs:
                    errors.append(f"semantic_currentness: {rel} {key} stale revision refs: {bad_refs}")
                if bad_terms:
                    errors.append(f"semantic_currentness: {rel} {key} stale terms: {bad_terms}")
    bytecode = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.pyc")]
    pycache = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("__pycache__") if p.is_dir()]
    if bytecode or pycache:
        errors.append("semantic_currentness: generated Python bytecode/cache present")
    ext = ROOT / "artifacts" / "external-runner"
    if ext.exists():
        stale = [p.relative_to(ROOT).as_posix() for p in ext.glob("REV*_PUBLIC_TRACE_EXTERNAL_RUNNER*") if not p.name.startswith(f"{revup}_")]
        if stale:
            errors.append("semantic_currentness: stale derived external runner packets present: " + ", ".join(stale))

def validate_semantic_pointer_consistency_live(errors: list[str], warnings: list[str], rev: str, revup: str) -> None:
    """Catch stale latest/current/active/primary metadata fields that can misdirect a session."""
    key_re = re.compile(r'^(current|latest|active|primary|fresh|next|operator)_|^(external_runner_packet|primary_artifact|primary_scientific_artifact|primary_audit|summary|revision_summary|one_line_summary|highlight|codename|revision|revision_kind|revision_name|package_name|archive_name)$|(_entrypoint|_lineage_artifact|_scientific_artifact|_external_runner)$')
    historical_key_re = re.compile(r'^(rev\d{4}|evidence_summary_rev\d{4}).*', re.I)
    stale_re = re.compile(r'(?i)rev\d{4}|REV\d{4}')
    expected = {
        'current_external_runner_packet': f'artifacts/external-runner/{revup}_PUBLIC_TRACE_EXTERNAL_RUNNER.zip',
        'latest_external_runner': f'artifacts/external-runner/{revup}_PUBLIC_TRACE_EXTERNAL_RUNNER.zip',
        'external_runner_packet': f'artifacts/external-runner/{revup}_PUBLIC_TRACE_EXTERNAL_RUNNER.zip',
        'current_scientific_artifact': f'artifacts/run-manifests/{revup}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json',
        'primary_scientific_artifact': f'artifacts/run-manifests/{revup}_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json',
        'current_lineage_artifact': f'MISSION-AUDIT-{revup}.md',
        'primary_lineage_artifact': f'MISSION-AUDIT-{revup}.md',
        'latest_online_research_note': f'artifacts/research/{revup}_ONLINE_RESEARCH_NOTES.md',
    }
    def refs(text: str) -> list[str]:
        return [r for r in sorted(set(m.group(0) for m in stale_re.finditer(text))) if r.lower() != rev]
    def walk(obj: Any, prefix: str = ''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                path = f'{prefix}.{k}' if prefix else k
                if key_re.search(k) and not historical_key_re.match(k):
                    yield path, k, v
                if isinstance(v, (dict, list)):
                    yield from walk(v, path)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                if isinstance(v, (dict, list)):
                    yield from walk(v, f'{prefix}[{i}]')
    for rel in ['CUBE-META.json','REVISION-RECEIPT.json','EVIDENCE-STATUS.json','SURFACE-STATUS.json','REENTRY-CONTRACT.json','BABY-DATACUBE-CANDIDATE.json']:
        p = ROOT / rel
        if not p.exists():
            continue
        data = load(rel)
        for key, expected_val in expected.items():
            if key in data and data.get(key) != expected_val:
                errors.append(f'semantic_pointer_consistency: {rel} {key} {data.get(key)!r} != {expected_val!r}')
        for dotted, key, value in walk(data):
            if key in {'previous_revision','source_revision','previous_revision_int','source_revision_int'} or dotted.endswith('.previous_revision') or dotted.endswith('.source_revision'):
                continue
            if isinstance(value, (str, int, float, bool)):
                bad = refs(str(value))
                if bad:
                    errors.append(f'semantic_pointer_consistency: {rel} {dotted} stale refs: {bad}')
            elif isinstance(value, list):
                bad = refs(json.dumps(value, sort_keys=True))
                if bad:
                    errors.append(f'semantic_pointer_consistency: {rel} {dotted} stale refs: {bad}')


def validate_active_capture_kit_pruned(errors: list[str], warnings: list[str], revup: str) -> None:
    kit = ROOT / 'artifacts' / 'capture-kit'
    if not kit.exists():
        errors.append('active_capture_kit_prune: missing capture-kit directory')
        return
    allowed = {
        'RUN_CURRENT_PUBLIC_TRACE.sh',
        'RUN_CURRENT_FIRST_REAL_TRACE.sh',
        'PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh',
        f'{revup}_RUN_TINYLLAMA_PUBLIC_TRACE.sh',
        f'{revup}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh',
        f'{revup}_PREPARE_TINYLLAMA_SNAPSHOT.sh',
        f'{revup}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh',
        f'{revup}_FIRST_REAL_TRACE_ONE_COMMAND.sh',
        f'{revup}_COMMON_PUBLIC_TRACE_ENV.sh',
    }
    stale_scripts = [p.name for p in kit.glob('REV*.sh') if p.name not in allowed]
    stale_runbooks = [p.name for p in kit.glob('REV*') if p.is_file() and p.name not in allowed and p.suffix.lower() in {'.md','.json'}]
    if stale_scripts:
        errors.append('active_capture_kit_prune: stale historical revision shell wrappers retained: ' + ', '.join(stale_scripts[:20]))
    if stale_runbooks:
        errors.append('active_capture_kit_prune: stale historical capture runbooks retained: ' + ', '.join(stale_runbooks[:20]))


def validate_checksums(errors: list[str], warnings: list[str]) -> None:
    path = ROOT / "CHECKSUMS.sha256"
    if not path.exists():
        if validate_external_runner_manifest(errors, warnings):
            return
        errors.append("missing required file: CHECKSUMS.sha256")
        return
    entries = 0
    seen: set[str] = set()
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append(f"CHECKSUMS.sha256 malformed line {lineno}")
            continue
        expected, rel = parts[0], parts[1].strip()
        if rel in seen:
            errors.append("CHECKSUMS.sha256 duplicate target: " + rel)
            continue
        seen.add(rel)
        entries += 1
        target = ROOT / rel
        if not target.exists():
            errors.append("CHECKSUMS.sha256 target missing: " + rel)
            continue
        actual = sha256_file(target)
        if actual != expected:
            errors.append("CHECKSUMS.sha256 mismatch: " + rel)
    if entries == 0:
        errors.append("CHECKSUMS.sha256 has no entries")


def validate_live_script_dependency_closure(errors: list[str], revup: str) -> None:
    """Fast static smoke check for the live shell surface.

    This intentionally avoids importing torch/transformers or running capture.
    It catches the wasteful failure mode where a long live wrapper references a
    missing in-cube tool and smoke still passes.
    """
    active_scripts = [
        "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh",
        "artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh",
        f"artifacts/capture-kit/{revup}_RUN_TINYLLAMA_PUBLIC_TRACE.sh",
        f"artifacts/capture-kit/{revup}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh",
        f"artifacts/capture-kit/{revup}_PREPARE_TINYLLAMA_SNAPSHOT.sh",
        f"artifacts/capture-kit/{revup}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh",
        "artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh",
        f"artifacts/capture-kit/{revup}_FIRST_REAL_TRACE_ONE_COMMAND.sh",
        f"artifacts/capture-kit/{revup}_COMMON_PUBLIC_TRACE_ENV.sh",
    ]
    py_re = re.compile(r"(?:python3|python|sys\.executable)\s+([A-Za-z0-9_./-]+\.py)")
    dyn_sh_re = re.compile(r"\$\{REVUP\}_([A-Z0-9_]+\.sh)")
    stale_re = re.compile(r"REV(\d{4})_[A-Z0-9_]+\.(?:sh|py)")
    assignment_concat_re = re.compile(r"(?:\"|\'|\)|\])(?=[A-Z_][A-Z0-9_]*=)")
    for rel in active_scripts:
        script = ROOT / rel
        if not script.exists():
            errors.append("missing live script dependency closure target: " + rel)
            continue
        src = script.read_text(encoding="utf-8", errors="replace")
        try:
            proc = subprocess.run(["bash", "-n", str(script)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
            if proc.returncode != 0:
                errors.append(f"{rel} bash_syntax_failed:{proc.stderr[-800:]}")
        except Exception as exc:
            errors.append(f"{rel} bash_syntax_check_error:{exc!r}")
        for lineno, line in enumerate(src.splitlines(), start=1):
            if assignment_concat_re.search(line):
                errors.append(f"{rel} assignment_concatenation_hazard:line_{lineno}:{line.strip()[:120]}")
        for hazard in ["pypython3", "thenif", "fifi", "donepython3", "thenpython3"]:
            if hazard in src:
                errors.append(f"{rel} shell_concatenation_hazard:{hazard}")
        for match in py_re.finditer(src):
            target = match.group(1).strip().strip('"').strip("'")
            if target.startswith(("tools/", "experiments/")) or target == "VERIFY_HANDOFF.py":
                if not (ROOT / target).is_file():
                    errors.append(f"{rel} references missing python file: {target}")
        for match in dyn_sh_re.finditer(src):
            target = f"artifacts/capture-kit/{revup}_{match.group(1)}"
            if not (ROOT / target).is_file():
                errors.append(f"{rel} references missing dynamic shell file: {target}")
        for match in stale_re.finditer(src):
            old = "REV" + match.group(1)
            if old != revup:
                errors.append(f"{rel} contains stale executable reference: {match.group(0)}")
    run = ROOT / f"artifacts/capture-kit/{revup}_RUN_TINYLLAMA_PUBLIC_TRACE.sh"
    one_shot = ROOT / f"artifacts/capture-kit/{revup}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh"
    common_env = ROOT / f"artifacts/capture-kit/{revup}_COMMON_PUBLIC_TRACE_ENV.sh"
    common_src = common_env.read_text(encoding="utf-8", errors="replace") if common_env.exists() else ""
    for rel, path in [(run.as_posix(), run), (one_shot.as_posix(), one_shot)]:
        if path.exists() and "tools/current_live_script_dependency_audit.py" not in path.read_text(encoding="utf-8", errors="replace"):
            errors.append(rel + " does not run current_live_script_dependency_audit.py")

    # Rev0118 anti-waste contract: the broad readiness gate must be strict/fail-fast
    # from the stable run wrapper, and one-shot capture must not continue past an
    # environment preflight that already knows the runtime/snapshot is blocked.
    first_trace = ROOT / f"artifacts/capture-kit/{revup}_FIRST_REAL_TRACE_ONE_COMMAND.sh"
    if first_trace.exists():
        first_src = first_trace.read_text(encoding="utf-8", errors="replace")
        if "bootstrap_runtime_dry_run" not in first_src or "PUBLIC_TRACE_BOOTSTRAP_DRY_RUN" not in first_src:
            errors.append("bootstrap_dry_run: first-real-trace wrapper must exit cleanly after bootstrap dry run")
        for marker in ["BOOTSTRAP_RUNTIME", "PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh", "ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1", "public_trace_first_real_trace_audit.py --mode status"]:
            if marker not in first_src:
                errors.append("first_real_trace_one_command: missing marker " + marker)
        if "REV0139" in first_src or "rev0139" in first_src:
            errors.append("first_real_trace_one_command: contains stale rev0139 reference")
    else:
        errors.append("first_real_trace_one_command: missing current one-command first trace wrapper")
    if not (ROOT / "artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh").is_file():
        errors.append("first_real_trace_one_command: missing stable first trace alias")
    if not (ROOT / "tools/public_trace_first_real_trace_audit.py").is_file():
        errors.append("first_real_trace_one_command: missing first trace audit/status tool")

    if run.exists():
        run_src = run.read_text(encoding="utf-8", errors="replace")
        if "PUBLIC_TRACE_PROMPTS.jsonl" in run_src:
            errors.append("prompt_manifest: current run wrapper still defaults to missing .jsonl prompt manifest")
        if 'PROMPT_MANIFEST:-artifacts/prompts/${REVUP}_PUBLIC_TRACE_PROMPTS.txt' not in (run_src + common_src):
            errors.append("prompt_manifest: current run wrapper default must match current .txt prompt manifest")
        if "public_trace_fast_prereq_gate.py --phase capture --local-only --strict" not in run_src:
            errors.append("fast_prereq: current run wrapper lacks strict local-only fast prerequisite gate")
        if "public_trace_fast_prereq_gate.py --phase capture --download --strict" in run_src:
            errors.append("fast_prereq: current run wrapper must not use download mode for capture")
        if "public_trace_readiness_gate.py --local-only --strict" not in run_src:
            errors.append("readiness_failfast: current run wrapper lacks strict local-only readiness gate")
        if "public_trace_readiness_gate.py --download --strict" in run_src:
            errors.append("readiness_failfast: current run wrapper must not use download readiness for capture")
        if "public_trace_readiness_gate.py --local-only || true" in run_src or "public_trace_readiness_gate.py --download || true" in run_src:
            errors.append("readiness_failfast: current run wrapper still ignores readiness gate")
    if common_env.exists():
        if "HF_HUB_DISABLE_SYMLINKS" not in common_src or "PUBLIC_TRACE_ALLOW_CACHE_DUPLICATION" not in common_src or "can duplicate large Hub files" not in common_src:
            errors.append("cache_duplication_guard: common env must guard HF_HUB_DISABLE_SYMLINKS duplication footgun")
    boot = ROOT / f"artifacts/capture-kit/{revup}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh"
    boot_src = boot.read_text(encoding="utf-8", errors="replace") if boot.exists() else ""
    for marker in ["PUBLIC_TRACE_WHEELHOUSE", "--no-index", "PIP_FIND_LINKS", "PUBLIC_TRACE_SKIP_PIP_UPGRADE"]:
        if marker not in boot_src:
            errors.append("wheelhouse_bootstrap: bootstrap missing " + marker)
    if one_shot.exists() and "public_trace_env_preflight.py --strict trace" not in one_shot.read_text(encoding="utf-8", errors="replace"):
        errors.append("readiness_failfast: one-shot capture does not strictly enforce env preflight")
    if one_shot.exists() and "--require-model-safetensors-sha256" not in one_shot.read_text(encoding="utf-8", errors="replace"):
        errors.append("digest_acceptance: one-shot public trace capture does not require model.safetensors SHA-256")
    if one_shot.exists():
        one_shot_src = one_shot.read_text(encoding="utf-8", errors="replace")
        if "PUBLIC_TRACE_PROMPTS.jsonl" in one_shot_src:
            errors.append("prompt_manifest: one-shot wrapper still defaults to missing .jsonl prompt manifest")
        if 'PROMPT_MANIFEST:-artifacts/prompts/${REVUP}_PUBLIC_TRACE_PROMPTS.txt' not in (one_shot_src + common_src):
            errors.append("prompt_manifest: one-shot wrapper default must match current .txt prompt manifest")
        if "--allow-download" in one_shot_src:
            errors.append("evidence_capture: one-shot public trace capture must not pass --allow-download")
        if "capture itself must not depend on network state" not in one_shot_src:
            errors.append("evidence_capture: one-shot public trace capture lacks local-only evidence-capture comment")
        if '--prompts-file "$PROMPT_MANIFEST"' not in one_shot_src:
            errors.append("prompt_manifest: one-shot public trace capture must load prompts from PROMPT_MANIFEST")
        if '--prompt "' in one_shot_src:
            errors.append("prompt_manifest: one-shot public trace capture still contains inline prompt arguments")
        prompt_manifest = ROOT / "artifacts" / "prompts" / f"{revup}_PUBLIC_TRACE_PROMPTS.txt"
        if not prompt_manifest.is_file():
            errors.append("prompt_manifest: missing current prompt manifest file")
        elif len([line for line in prompt_manifest.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip() and not line.lstrip().startswith("#")]) < 2:
            errors.append("prompt_manifest: current prompt manifest must contain at least two prompts")
    digest_audit = ROOT / "tools/public_trace_digest_acceptance_audit.py"
    if not digest_audit.is_file():
        errors.append("digest_acceptance: missing public trace digest acceptance audit tool")
    prep = ROOT / f"artifacts/capture-kit/{revup}_PREPARE_TINYLLAMA_SNAPSHOT.sh"
    if prep.exists() and "public_trace_env_preflight.py --strict trace" not in prep.read_text(encoding="utf-8", errors="replace"):
        errors.append("readiness_failfast: snapshot prepare does not strictly enforce env preflight")
    gate = ROOT / "tools/public_trace_readiness_gate.py"
    if gate.exists():
        gate_src = gate.read_text(encoding="utf-8", errors="replace")
        for marker in ["blocked_here_fail_fast", "fail_fast_prerequisite_blockers", "--continue-after-prereq-blockers", "EXPENSIVE_OR_POSTTRACE_STEPS"]:
            if marker not in gate_src:
                errors.append("readiness_failfast: readiness gate missing marker " + marker)

    # Rev0120 snapshot-prepare contract: missing capture-only packages must not
    # block the model snapshot materializer from running in download mode.
    if prep.exists():
        prep_src = prep.read_text(encoding="utf-8", errors="replace")
        if "hf_snapshot_materializer.py --download --strict" not in prep_src:
            errors.append("snapshot_prepare: download materializer is not strict")
        if "hf_snapshot_materializer.py --local-only --strict" not in prep_src:
            errors.append("snapshot_prepare: local materializer is not strict")
        m_idx = prep_src.find("hf_snapshot_materializer.py")
        d_idx = prep_src.find("public_trace_dependency_lock_audit.py")
        e_idx = prep_src.find("public_trace_env_preflight.py --strict trace")
        if m_idx < 0 or d_idx < 0 or e_idx < 0 or d_idx < m_idx or e_idx < m_idx:
            errors.append("snapshot_prepare: runtime dependency/env probes must run after snapshot materializer")
        if "public_trace_dependency_lock_audit.py || true" not in prep_src:
            errors.append("snapshot_prepare: dependency lock must be nonfatal for snapshot preparation")
        if "public_trace_fast_prereq_gate.py --phase snapshot --local-only --strict" not in prep_src:
            errors.append("snapshot_prepare: local fast gate must use snapshot phase")
        if "public_trace_fast_prereq_gate.py --phase snapshot --download --strict" not in prep_src:
            errors.append("snapshot_prepare: download fast gate must use snapshot phase")
        if "snapshot_integrity_contract_audit.py" not in prep_src:
            errors.append("snapshot_prepare: snapshot integrity audit must run before materializer")
        if "tinyllama_snapshot_threshold_audit.py" not in prep_src:
            errors.append("snapshot_prepare: threshold audit must run before materializer")
        if "tools/public_trace_env_snapshot_integrity_audit.py" not in prep_src:
            errors.append("env_snapshot_integrity: snapshot prepare must run env snapshot integrity audit")
        phase_audit = ROOT / "tools/snapshot_prepare_phase_order_audit.py"
        if not phase_audit.is_file():
            errors.append("snapshot_prepare: missing phase-order audit tool")
        threshold_audit = ROOT / "tools/tinyllama_snapshot_threshold_audit.py"
        if not threshold_audit.is_file():
            errors.append("snapshot_prepare: missing threshold audit tool")
        integrity_src = (ROOT / "tools/hf_snapshot_integrity.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/hf_snapshot_integrity.py").exists() else ""
        if "'config.json': 1000" in integrity_src:
            errors.append("snapshot_threshold: config.json min bytes would reject pinned TinyLlama config")
        if "PUBLISHED_SIZE_BYTES" not in integrity_src:
            errors.append("snapshot_threshold: hf_snapshot_integrity lacks published size hints")
        env_src = (ROOT / "tools/public_trace_env_preflight.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_env_preflight.py").exists() else ""
        preflight_src = (ROOT / "tools/public_trace_capture_start_preflight_report.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_capture_start_preflight_report.py").exists() else ""
        for marker in ["def integrity_snapshot_status", "inspect_snapshot", "snapshot_candidate_paths", "found_complete_integrity_snapshot", "no_integrity_valid_local_hf_snapshot_and_download_not_allowed"]:
            if marker not in env_src:
                errors.append("env_snapshot_integrity: public_trace_env_preflight missing marker " + marker)
        if "def cache_snapshot_status" in env_src:
            errors.append("env_preflight_still_defines_weak_cache_snapshot_status")
        env_snapshot_audit = ROOT / "tools/public_trace_env_snapshot_integrity_audit.py"
        if not env_snapshot_audit.is_file():
            errors.append("env_snapshot_integrity: missing env snapshot integrity audit tool")
        run_src_current = (ROOT / f"artifacts/capture-kit/{revup}_RUN_TINYLLAMA_PUBLIC_TRACE.sh").read_text(encoding="utf-8", errors="replace") if (ROOT / f"artifacts/capture-kit/{revup}_RUN_TINYLLAMA_PUBLIC_TRACE.sh").exists() else ""
        if "tools/public_trace_env_snapshot_integrity_audit.py" not in run_src_current:
            errors.append("env_snapshot_integrity: run wrapper must run env snapshot integrity audit")

        # Rev0129 local-only snapshot contract: a runner may mount a complete
        # snapshot and verify it without the Hub client; only download mode needs
        # huggingface_hub. This protects the external-runner path from an
        # avoidable prereq deadlock.
        fast_src = (ROOT / "tools/public_trace_fast_prereq_gate.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_fast_prereq_gate.py").exists() else ""
        if "if download_mode:\n        for name in SNAPSHOT_REQUIRED_MODULES" not in fast_src:
            errors.append("snapshot_local_only_gate: snapshot modules must be required only in download mode")
        if "for name in SNAPSHOT_REQUIRED_MODULES:\n        if not modules[name]['present']:\n            hard_blockers.append(f'{name}_not_importable_for_snapshot_materialization')\n    if download_mode:" in fast_src:
            errors.append("snapshot_local_only_gate: fast gate still has unconditional snapshot module blocker")
        local_only_audit = ROOT / "tools/public_trace_snapshot_local_only_gate_audit.py"
        if not local_only_audit.is_file():
            errors.append("snapshot_local_only_gate: missing local-only gate audit tool")
        if prep.exists() and "public_trace_snapshot_local_only_gate_audit.py" not in prep_src:
            errors.append("snapshot_local_only_gate: snapshot prepare must run local-only gate audit")
        if "public_trace_snapshot_local_only_gate_audit.py" not in run_src_current:
            errors.append("snapshot_local_only_gate: run wrapper must run local-only gate audit")

        # Rev0130 hash-preflight contract: structural safetensors/header checks are not enough for
        # public trace readiness. The live path must require the pinned 2.2GB
        # model.safetensors SHA-256 before capture, and long snapshot/hash work
        # must not inherit the short generic probe timeout.
        hash_contract_audit = ROOT / "tools/public_trace_hash_preflight_contract_audit.py"
        if not hash_contract_audit.is_file():
            errors.append("hash_preflight_contract: missing hash preflight contract audit tool")
        if "--phase capture --local-only --strict --require-weight-hash" not in run_src_current:
            errors.append("hash_preflight_contract: run wrapper must hash-gate local-only capture")
        if "--phase capture --download --strict" in run_src_current:
            errors.append("hash_preflight_contract: run wrapper must not download-gate capture; downloads belong to snapshot preparation")
        if prep.exists() and 'export HASH_WEIGHTS="${HASH_WEIGHTS:-1}"' not in (prep_src + common_src):
            errors.append("hash_preflight_contract: snapshot prepare must hash weights by default")
        if prep.exists() and 'hf_snapshot_materializer.py --download --strict "${HASH_ARG[@]}"' not in prep_src:
            errors.append("hash_preflight_contract: download materializer must receive hash args")
        if one_shot.exists() and "public_trace_env_preflight.py --strict trace --require-weight-hash --capture-local-only" not in one_shot_src:
            errors.append("hash_preflight_contract: one-shot env preflight must require weight hash and capture-local-only")
        if "--require-weight-hash" not in fast_src or "hash_verified_snapshot_available" not in fast_src:
            errors.append("hash_preflight_contract: fast gate lacks digest-aware local snapshot readiness")
        ready_src = (ROOT / "tools/public_trace_readiness_gate.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_readiness_gate.py").exists() else ""
        if "SNAPSHOT_GATE_STEP_TIMEOUT" not in ready_src or "--include-hashes" not in ready_src:
            errors.append("hash_preflight_contract: readiness gate must use snapshot-specific timeout and include hashes")
        if "public_trace_hash_preflight_contract_audit.py" not in run_src_current or (prep.exists() and "public_trace_hash_preflight_contract_audit.py" not in prep_src):
            errors.append("hash_preflight_contract: live wrappers must run hash preflight contract audit")

        # Rev0131 local-only capture contract: download is a snapshot-preparation
        # permission, not a public evidence capture permission. The capture helper
        # is local-files-only unless --allow-download is passed, and wrappers must
        # continue to forbid that option.
        capture_local_audit = ROOT / "tools/public_trace_capture_local_only_contract_audit.py"
        if not capture_local_audit.is_file():
            errors.append("capture_local_only_contract: missing capture local-only contract audit")
        if "public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only" not in run_src_current:
            errors.append("capture_local_only_contract: run wrapper must write strict capture-start preflight report")
        if "export ALLOW_DOWNLOAD=0" not in (run_src_current + common_src):
            errors.append("capture_local_only_contract: run wrapper must force ALLOW_DOWNLOAD=0 before capture")
        if "--capture-local-only" not in env_src or "allow_download_for_snapshot_preflight" not in env_src:
            errors.append("capture_local_only_contract: env preflight lacks capture-local-only semantics")
        if one_shot.exists() and "public_trace_capture_start_preflight_report.py --phase capture --strict --require-weight-hash --capture-local-only" not in one_shot_src:
            errors.append("capture_local_only_contract: one-shot must write capture-start preflight report before loading model")

        # Rev0132 selected-snapshot contract: the hash proof must bind to the
        # same local snapshot path the loader will consume, not just prove that
        # some cache candidate exists somewhere.
        selected_snapshot_audit = ROOT / "tools/public_trace_selected_snapshot_contract_audit.py"
        if not selected_snapshot_audit.is_file():
            errors.append("selected_snapshot_contract: missing selected snapshot contract audit")
        if "CURRENT_PUBLIC_TRACE_CAPTURE_ENV.sh" not in preflight_src or "selected_snapshot_path" not in preflight_src:
            errors.append("selected_snapshot_contract: capture-start preflight must write selected snapshot env and JSON fields")
        if 'source "$CAPTURE_ENV"' not in run_src_current:
            errors.append("selected_snapshot_contract: run wrapper must source capture env from preflight")
        if one_shot.exists() and 'source "$CAPTURE_ENV"' not in one_shot_src:
            errors.append("selected_snapshot_contract: one-shot must source capture env from preflight")
        if one_shot.exists() and "selected digest-verified LOCAL_SNAPSHOT_DIR was not exported by preflight" not in one_shot_src:
            errors.append("selected_snapshot_contract: one-shot must require selected LOCAL_SNAPSHOT_DIR")
        if one_shot.exists() and 'CAPTURE_MODEL="${CAPTURE_MODEL:-$LOCAL_SNAPSHOT_DIR}"' not in one_shot_src:
            errors.append("selected_snapshot_contract: one-shot must prefer preflight-selected CAPTURE_MODEL")
        if "public_trace_selected_snapshot_contract_audit.py" not in run_src_current or (one_shot.exists() and "public_trace_selected_snapshot_contract_audit.py" not in one_shot_src):
            errors.append("selected_snapshot_contract: live wrappers must run selected snapshot contract audit")
        loader_binding_audit = ROOT / "tools/public_trace_loader_snapshot_binding_audit.py"
        helper_src = (ROOT / "experiments/public_trace_capture/hf_attention_trace_capture.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "experiments/public_trace_capture/hf_attention_trace_capture.py").exists() else ""
        if not loader_binding_audit.is_file():
            errors.append("loader_snapshot_binding: missing loader snapshot binding audit")
        if "--require-loader-snapshot-bind" not in helper_src or "loader_snapshot_binding_verified" not in helper_src:
            errors.append("loader_snapshot_binding: capture helper must enforce loader/source digest binding")
        if one_shot.exists() and "--require-loader-snapshot-bind" not in one_shot_src:
            errors.append("loader_snapshot_binding: one-shot capture must pass --require-loader-snapshot-bind")
        if "public_trace_loader_snapshot_binding_audit.py" not in run_src_current or (one_shot.exists() and "public_trace_loader_snapshot_binding_audit.py" not in one_shot_src):
            errors.append("loader_snapshot_binding: live wrappers must run loader binding audit")

        # Rev0134 acceptance-loader-binding contract: downstream public-trace
        # acceptance must require the same digest and selected loader path that
        # capture startup now enforces, or selector/evaluation receipts could
        # accept evidence about unknown bytes.
        acceptance_binding_audit = ROOT / "tools/public_trace_acceptance_loader_binding_audit.py"
        verifier_src = (ROOT / "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py").exists() else ""
        if not acceptance_binding_audit.is_file():
            errors.append("acceptance_loader_binding: missing acceptance loader binding audit")
        if "PUBLIC_LOADER_BINDING_FIELDS" not in verifier_src or "_loader_binding_field_errors" not in verifier_src:
            errors.append("acceptance_loader_binding: public trace verifier must require loader binding fields")
        if "model_load_source_resolved_path must equal verified_snapshot_path" not in verifier_src:
            errors.append("acceptance_loader_binding: verifier must require loader path to equal verified snapshot path")
        if "expected_model_safetensors_sha256 must equal the pinned TinyLlama digest" not in verifier_src:
            errors.append("acceptance_loader_binding: verifier must require pinned model.safetensors digest")
        if "public_trace_acceptance_loader_binding_audit.py" not in run_src_current or (one_shot.exists() and "public_trace_acceptance_loader_binding_audit.py" not in one_shot_src):
            errors.append("acceptance_loader_binding: live wrappers must run acceptance loader binding audit")

        # Rev0136 downstream-identity receipt contract: selector-entry and handoff
        # receipts must carry a compact selected-snapshot/prompt/generation hash
        # once the verifier accepts, rather than hiding all identity behind a
        # single accepted boolean.
        downstream_identity_audit = ROOT / "tools/public_trace_downstream_identity_receipt_audit.py"
        evaluator_src = (ROOT / "tools/public_trace_evaluation_verdict_audit.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_evaluation_verdict_audit.py").exists() else ""
        selector_src = (ROOT / "tools/public_trace_selector_entry_gate.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_selector_entry_gate.py").exists() else ""
        replay_src = (ROOT / "tools/public_trace_selector_receipt_replay_gate.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_selector_receipt_replay_gate.py").exists() else ""
        handoff_builder_src = (ROOT / "tools/public_trace_handoff_builder.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_handoff_builder.py").exists() else ""
        handoff_gate_src = (ROOT / "tools/public_trace_handoff_archive_gate.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_handoff_archive_gate.py").exists() else ""
        if not downstream_identity_audit.is_file():
            errors.append("downstream_identity_receipt: missing downstream identity receipt audit")
        if "public_trace_downstream_identity_receipt_v1" not in evaluator_src or "_trace_identity_summary" not in evaluator_src:
            errors.append("downstream_identity_receipt: evaluator must emit compact trace identity receipt")
        if 'trace_identity.get("verified_for_downstream_selector_entry") is True' not in evaluator_src:
            errors.append("downstream_identity_receipt: evaluator must require verified trace identity before selector entry")
        if "_trace_identity_receipt_errors" not in selector_src or "trace_identity_sha256" not in selector_src:
            errors.append("downstream_identity_receipt: selector entry must require trace identity receipt")
        if "trace_identity_chain_errors" not in replay_src or "selector-entry trace_identity_sha256 does not match input evaluation receipt" not in replay_src:
            errors.append("downstream_identity_receipt: replay must cross-check selector/evaluation trace identity hashes")
        if "trace_identity_chain_bound" not in handoff_builder_src or "trace_identity_sha256" not in handoff_gate_src:
            errors.append("downstream_identity_receipt: handoff builder/gate must carry and replay trace identity hash")
        if "public_trace_downstream_identity_receipt_audit.py" not in run_src_current or (one_shot.exists() and "public_trace_downstream_identity_receipt_audit.py" not in one_shot_src):
            errors.append("downstream_identity_receipt: live wrappers must run downstream identity receipt audit")

        # Rev0136 selector-entry chain-binding contract: a selector-entry receipt
        # must not be reusable with a different accepted evaluation receipt, trace
        # identity, or replay bundle. The non-circular chain digest binds the
        # evaluation receipt hash, evaluation subject-set hash, downstream
        # trace-identity hash, actual replay subject-set hash, and selector tool
        # hash, and the handoff manifest must carry/replay the same chain hash.
        chain_audit = ROOT / "tools/public_trace_selector_receipt_chain_binding_audit.py"
        if not chain_audit.is_file():
            errors.append("selector_receipt_chain_binding: missing selector receipt chain binding audit")
        selector_src = (ROOT / "tools/public_trace_selector_entry_gate.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_selector_entry_gate.py").exists() else ""
        replay_src = (ROOT / "tools/public_trace_selector_receipt_replay_gate.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_selector_receipt_replay_gate.py").exists() else ""
        handoff_builder_src = (ROOT / "tools/public_trace_handoff_builder.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_handoff_builder.py").exists() else ""
        handoff_gate_src = (ROOT / "tools/public_trace_handoff_archive_gate.py").read_text(encoding="utf-8", errors="replace") if (ROOT / "tools/public_trace_handoff_archive_gate.py").exists() else ""
        if "public_trace_selector_entry_chain_v1" not in selector_src or "_selector_entry_chain_sha256" not in selector_src:
            errors.append("selector_receipt_chain_binding: selector gate must emit selector-entry chain digest")
        if "selector_entry_chain_errors" not in replay_src or "selector-entry receipt selector_entry_chain_sha256 does not match recomputed evaluation/identity/bundle chain" not in replay_src:
            errors.append("selector_receipt_chain_binding: replay gate must recompute selector-entry chain digest")
        if "selector_entry_chain_sha256" not in handoff_builder_src or "selector_entry_chain_sha256" not in handoff_gate_src:
            errors.append("selector_receipt_chain_binding: handoff builder/gate must carry selector-entry chain hash")
        if "public_trace_selector_receipt_chain_binding_audit.py" not in run_src_current or (one_shot.exists() and "public_trace_selector_receipt_chain_binding_audit.py" not in one_shot_src):
            errors.append("selector_receipt_chain_binding: live wrappers must run selector receipt chain binding audit")

        # Rev0137 replay-enforcement harness: the receipt chain must not be only
        # static strings. A synthetic good path plus trace/evaluation/selector
        # tamper failures must be available before expensive live capture.
        replay_harness = ROOT / "tools/public_trace_selector_receipt_replay_enforcement_harness.py"
        replay_harness_src = replay_harness.read_text(encoding="utf-8", errors="replace") if replay_harness.exists() else ""
        if not replay_harness.is_file():
            errors.append("selector_receipt_replay_harness: missing executable replay tamper harness")
        for token in ["selector_receipt_replay_tamper_enforcement_v1", "tampered_trace_rejected", "tampered_evaluation_receipt_rejected", "tampered_selector_chain_rejected"]:
            if token not in replay_harness_src:
                errors.append("selector_receipt_replay_harness: missing " + token)
        if "selector_receipt_replay_enforcement_harness.py" not in run_src_current or (one_shot.exists() and "selector_receipt_replay_enforcement_harness.py" not in one_shot_src):
            errors.append("selector_receipt_replay_harness: live wrappers must run the replay enforcement harness")
        if "selector_receipt_replay_tamper_harness_contract" not in (ROOT / "tools/trace_run_packet_audit.py").read_text(encoding="utf-8", errors="replace"):
            errors.append("selector_receipt_replay_harness: run packet audit must require the harness contract")
        # The presence of this block is itself the smoke guard for the capture-local-only contract.

def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    meta = load("CUBE-META.json")
    rev = meta["revision"]
    revup = rev.upper()
    package_name = meta.get("package_name")
    archive_name = meta.get("archive_name")
    runner_mode = (ROOT / "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json").exists() and not (ROOT / "CHECKSUMS.sha256").exists()
    runner_manifest = maybe_load("PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json") if runner_mode else {}

    if runner_mode:
        # Compact external runners are intentionally not full source cubes. Their
        # terminal smoke validates the runner manifest plus the live execution
        # surface instead of demanding historical docs/checksums that were never
        # copied into the packet.
        core_required = [
            "CUBE-META.json", "REVISION-RECEIPT.json", "EVIDENCE-STATUS.json",
            "SURFACE-STATUS.json", "REENTRY-CONTRACT.json", "START_HERE.md",
            "PRIORITY-LIST.md", "MISSION-KERNEL.md", "README_RUNNER.md",
            "PUBLIC_TRACE_EXTERNAL_RUNNER_MANIFEST.json", "RUN_PUBLIC_TRACE.sh",
            "PREPARE_SNAPSHOT.sh", "BOOTSTRAP_RUNTIME.sh", "RUN_FIRST_REAL_TRACE.sh",
        ]
        dynamic_required = [str(rel) for rel in runner_manifest.get("required_in_packet", [])]
        warnings.append("external_runner_subset_mode: validating runner manifest instead of full source cube docs")
    else:
        core_required = [
            "README.md", "START_HERE.md", "START_HERE_SLIM.md", "NEXT-TURN-PROMPT.md",
            f"MISSION-AUDIT-{revup}.md", "CUBE-META.json", "REVISION-RECEIPT.json",
            "EVIDENCE-STATUS.json", "SURFACE-STATUS.json", "REENTRY-CONTRACT.json",
            "SLIM-RETENTION-REPORT.json", "PRUNED-ARTIFACTS.jsonl",
        ]
        dynamic_required = list(meta.get("current_revision_artifacts", [])) + list(meta.get("new_code", []))
    for rel in core_required + dynamic_required:
        if rel and not (ROOT / rel).exists():
            errors.append("missing required file: " + rel)

    for rel in ["CUBE-META.json", "REVISION-RECEIPT.json", "EVIDENCE-STATUS.json", "SURFACE-STATUS.json", "REENTRY-CONTRACT.json"]:
        if (ROOT / rel).exists():
            data = load(rel)
            if data.get("revision") != rev:
                errors.append(rel + " revision mismatch")
            if data.get("revision_number") is not None and int(data.get("revision_number")) != int(meta.get("revision_number")):
                errors.append(rel + " revision_number mismatch")
            for int_key in ["revision_int", "current_revision_int"]:
                if data.get(int_key) is not None and int(data.get(int_key)) != int(meta.get("revision_number")):
                    errors.append(rel + " " + int_key + " mismatch")

            counts = data.get("counts")
            if isinstance(counts, dict) and counts.get("revision_number") is not None and int(counts.get("revision_number")) != int(meta.get("revision_number")):
                errors.append(rel + " counts.revision_number mismatch")
            if data.get("revision_name") and data.get("package_name") and data.get("revision_name") != data.get("package_name"):
                errors.append(rel + " revision_name/package_name mismatch")
            if data.get("package_name") and data.get("package_name") != package_name:
                errors.append(rel + " package mismatch")
            if data.get("archive_name") and data.get("archive_name") != archive_name:
                errors.append(rel + " archive mismatch")

    docs_to_check = ["README_RUNNER.md", "START_HERE.md", "PRIORITY-LIST.md"] if runner_mode else ["README.md", "START_HERE.md", "START_HERE_SLIM.md", "NEXT-TURN-PROMPT.md", "PRIORITY-LIST.md"]
    for rel in docs_to_check:
        path = ROOT / rel
        if path.exists() and rev not in path.read_text(encoding="utf-8", errors="replace")[:3000]:
            errors.append(rel + " does not mention current revision near top")

    # Current live execution surface must be directly runnable from stable aliases.
    # REV0115 exposed a real risk: the package could smoke-pass while
    # RUN_CURRENT/PREPARE_CURRENT still reopened stale historical wrappers.
    current_surface_required = [
        "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh",
        "artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh",
        f"artifacts/capture-kit/{revup}_RUN_TINYLLAMA_PUBLIC_TRACE.sh",
        f"artifacts/capture-kit/{revup}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh",
        f"artifacts/capture-kit/{revup}_PREPARE_TINYLLAMA_SNAPSHOT.sh",
        f"artifacts/capture-kit/{revup}_BOOTSTRAP_PUBLIC_TRACE_ENV.sh",
        "artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh",
        f"artifacts/capture-kit/{revup}_FIRST_REAL_TRACE_ONE_COMMAND.sh",
        f"artifacts/capture-kit/{revup}_COMMON_PUBLIC_TRACE_ENV.sh",
    ]
    for rel in current_surface_required:
        if not (ROOT / rel).exists():
            errors.append("missing current execution surface file: " + rel)
    run_alias = (ROOT / "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh").read_text(encoding="utf-8", errors="replace") if (ROOT / "artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh").exists() else ""
    prep_alias = (ROOT / "artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh").read_text(encoding="utf-8", errors="replace") if (ROOT / "artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh").exists() else ""
    if f"{revup}_RUN_TINYLLAMA_PUBLIC_TRACE.sh" not in run_alias:
        errors.append("RUN_CURRENT_PUBLIC_TRACE.sh does not target current revision wrapper")
    if f"{revup}_PREPARE_TINYLLAMA_SNAPSHOT.sh" not in prep_alias:
        errors.append("PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh does not target current revision wrapper")
    validate_live_script_dependency_closure(errors, revup)

    entry_docs_to_check = ["README_RUNNER.md", "START_HERE.md", "PRIORITY-LIST.md", "MISSION-KERNEL.md"] if runner_mode else ["README.md", "START_HERE.md", "START_HERE_SLIM.md", "NEXT-TURN-PROMPT.md", "PRIORITY-LIST.md", "MISSION-KERNEL.md"]
    for rel in entry_docs_to_check:
        path = ROOT / rel
        if path.exists():
            head = path.read_text(encoding="utf-8", errors="replace")[:3500]
            if "RUN_CURRENT_PUBLIC_TRACE.sh" not in head and f"{revup}_RUN_TINYLLAMA_PUBLIC_TRACE.sh" not in head and "RUN_PUBLIC_TRACE.sh" not in head:
                errors.append(rel + " does not name the current run entrypoint near top")

    post_rel = f"artifacts/probe-results/{revup}_POST_TRANSFORM_TRACE_CONTRACT.json"
    post = maybe_load(post_rel)
    if post:
        summary = post.get("summary", {})
        if post.get("promotion_allowed") is not False or post.get("public_pretrained_trace_loaded") is not False or post.get("gpu_fused_kernel_measured") is not False:
            errors.append("post-transform contract artifact overclaim")
        for key in [
            "post_transform_contract_within_tolerance", "raw_projection_contract_rejected_or_out_of_tolerance",
            "finite_score_bias", "nonzero_finite_bias_exercised", "gate_external_nonpublic_loaded",
            "gate_actual_d_head_propagated", "gate_result_row_count_positive", "synthetic_public_claim_rejected",
        ]:
            if summary.get(key) is not True:
                errors.append("post-transform summary " + key + " missing")
        if int(summary.get("row_count", 0)) < 50:
            errors.append("post-transform row coverage too small")

    pre_rel = f"artifacts/probe-results/{revup}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT.json"
    pre = maybe_load(pre_rel)
    if pre:
        summary = pre.get("summary", {})
        if pre.get("promotion_allowed") is not False or pre.get("public_pretrained_trace_loaded") is not False or pre.get("gpu_fused_kernel_measured") is not False:
            errors.append("public trace preflight artifact overclaim")
        for key in [
            "all_cases_passed", "public_overclaim_prevented", "good_qkv_native_replay_compatible",
            "raw_projection_public_claim_rejected", "actual_q_head_dimension_propagated",
            "query_key_value_aliases_supported", "score_semantics_required", "dense_reference_recomputed",
            "forged_dense_reference_rejected", "immutable_model_revision_enforced", "immutable_tokenizer_revision_enforced",
        ]:
            if summary.get(key) is not True:
                errors.append("preflight " + key + " missing")
        if summary.get("score_only_bundle_native_replay_compatible") is not False:
            errors.append("score-only native replay veto missing")

    expected_status = {
        f"artifacts/audit/{revup}_POST_TRANSFORM_TRACE_CONTRACT_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_ACCEPTANCE_PREFLIGHT_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_MISSION_WASTE_TRACE_FIDELITY_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_REVISION_LINEAGE_STATIC_AUDIT.json": {"pass", "pass_with_debt"},
        f"artifacts/audit/{revup}_CURRENT_SCIENTIFIC_RUN_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_EVIDENCE_INTEGRITY_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_SESSION_DEEP_READ_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_REAL_MODEL_TRACE_ADAPTER_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_MASK_FIDELITY_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_DECODE_PHASE_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_ABSOLUTE_POSITION_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_ACTIVE_KEYMASK_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_KV_GROUP_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_PROBABILITY_SEMANTICS_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_ROTARY_POSITION_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_TOKEN_PROVENANCE_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_GENERATION_TOKEN_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_GENERATION_DETERMINISM_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_CAPTURE_READINESS_AUDIT.json": {"pass_with_blockers", "ready_to_run_cached_capture"},
        f"artifacts/audit/{revup}_REVISION_METADATA_COHERENCE_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_SEMANTIC_CURRENTNESS_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_SEMANTIC_POINTER_CONSISTENCY_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_ACTIVE_CAPTURE_KIT_PRUNE_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_FIRST_REAL_TRACE_STATUS.json": {"blocked_here", "real_trace_receipts_complete"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_RUN_MANIFEST_COHERENCE_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_COMMON_ENV_CONTRACT_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_CACHE_DUPLICATION_GUARD_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_HARDWARE_TIMING_BOUNDARY_AUDIT.json": {"pass_with_blockers"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_ACCEPTANCE_BUNDLE_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_EVALUATION_VERDICT_AUDIT.json": {"pass_with_blockers", "pass", "blocked_no_trace_bundle"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_EVALUATION_RECEIPT_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_SELECTOR_ENTRY_GATE_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_RECEIPT_RELOCATION_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_SELECTOR_ENTRY_RECEIPT_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_GATE_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_SELECTOR_RECEIPT_REPLAY_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_HANDOFF_ARCHIVE_GATE_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_HANDOFF_ARCHIVE_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_STANDALONE_TOOLPACK_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_CURRENT_ENTRYPOINT_CONSISTENCY_AUDIT.json": {"pass", "pass_with_debt"},
        f"artifacts/audit/{revup}_CAPTURE_SURFACE_REFACTOR_AUDIT.json": {"pass", "pass_with_debt"},
        f"artifacts/audit/{revup}_ACTIVE_SURFACE_TRIM_AUDIT.json": {"pass", "pass_with_debt"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_HANDOFF_BUILDER_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_CURRENT_LIVE_SCRIPT_DEPENDENCY_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_CAPTURE_PREFLIGHT_HANDOFF_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_EXTERNAL_RUNNER_PACKET_AUDIT.json": {"pass_with_expected_environment_blockers", "pass"},
        f"artifacts/audit/{revup}_CURRENT_EXTERNAL_RUNNER_RETENTION_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_READINESS_FAILFAST_CONTRACT_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_SNAPSHOT_PREPARE_PHASE_ORDER_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_SNAPSHOT_INTEGRITY_CONTRACT_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_TINYLLAMA_SNAPSHOT_THRESHOLD_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_DIGEST_ACCEPTANCE_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_HASH_PREFLIGHT_CONTRACT_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_CAPTURE_LOCAL_ONLY_CONTRACT_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_SELECTED_SNAPSHOT_CONTRACT_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_CAPTURE_START_PREFLIGHT_REPORT.json": {"blocked_here", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_CAPTURE_DECISION_REFACTOR_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_FAST_PREREQ_GATE.json": {"blocked_here_fast_prereq", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_SURROGATE_REJECTION_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_CURRENT_TRACE_LANE_AUDIT.json": {"pass_with_blockers", "pass"},
        f"artifacts/audit/{revup}_TRACE_RUN_PACKET_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_SOURCE_LOCK_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_DEPENDENCY_LOCK_AUDIT.json": {"blocked_here", "trace_env_ready", "pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_SNAPSHOT_LOCAL_ONLY_GATE_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_DOWNSTREAM_IDENTITY_RECEIPT_AUDIT.json": {"pass"},
        f"artifacts/audit/{revup}_PUBLIC_TRACE_ENV_PREFLIGHT.json": {"blocked_here", "trace_env_ready", "pass"},
    }
    for rel, allowed in expected_status.items():
        path = ROOT / rel
        if path.exists() and load(rel).get("status") not in allowed:
            errors.append(rel + " status wrong")

    validate_run_manifest_identity_live(errors, warnings, rev, revup, package_name, archive_name)
    validate_semantic_currentness_live(errors, warnings, rev, revup, package_name, archive_name)
    validate_semantic_pointer_consistency_live(errors, warnings, rev, revup)
    if not runner_mode:
        validate_active_capture_kit_pruned(errors, warnings, revup)
    validate_checksums(errors, warnings)

    print(json.dumps({
        "status": "pass" if not errors else "fail",
        "revision": rev,
        "revision_kind": meta.get("revision_kind"),
        "errors": errors,
        "warnings": warnings,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
