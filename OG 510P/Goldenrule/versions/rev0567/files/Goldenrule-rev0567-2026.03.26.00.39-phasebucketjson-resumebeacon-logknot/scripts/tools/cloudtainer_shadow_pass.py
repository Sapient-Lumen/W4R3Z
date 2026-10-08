#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / 'artifacts' / 'process'
DEFAULT_CHECKPOINT_PATH = ARTIFACT_DIR / 'cloudtainer_shadow_pass_checkpoint.json'
DEFAULT_FRONTIER_REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'cloudtainer_shadow_pass_frontier.json'

STEPS: list[dict[str, object]] = [
    {
        'id': 'doctor_probe',
        'lane': 'environment_boundary',
        'command': './scripts/doctor.sh',
        'allow_blocked': True,
        'purpose': 'record current local tool boundary before shadow work',
    },
    {
        'id': 'update_rust_surface_inventory',
        'lane': 'static_navigation',
        'command': 'make update-rust-surface-inventory',
        'purpose': 'refresh the static Rust source-text navigation surface',
    },
    {
        'id': 'test_rust_surface_inventory',
        'lane': 'static_navigation',
        'command': 'make test-rust-surface-inventory',
        'purpose': 'confirm the static Rust source-text inventory is reproducible',
    },
    {
        'id': 'update_rust_restart_map',
        'lane': 'static_navigation',
        'command': 'make update-rust-restart-map',
        'purpose': 'refresh the static Rust restart-priority map for blocked sessions',
    },
    {
        'id': 'test_rust_restart_map',
        'lane': 'static_navigation',
        'command': 'make test-rust-restart-map',
        'purpose': 'confirm the static Rust restart-priority map is reproducible',
    },
    {
        'id': 'update_rust_test_contracts',
        'lane': 'static_navigation',
        'command': 'make update-rust-test-contracts',
        'purpose': 'refresh the static Rust semantic-contract ledger for blocked sessions',
    },
    {
        'id': 'test_rust_test_contracts',
        'lane': 'static_navigation',
        'command': 'make test-rust-test-contracts',
        'purpose': 'confirm the static Rust semantic-contract ledger is reproducible',
    },
    {
        'id': 'update_rust_test_scenario_coverage',
        'lane': 'static_navigation',
        'command': 'make update-rust-test-scenario-coverage',
        'purpose': 'refresh the static Rust scenario-coverage ledger for blocked sessions',
    },
    {
        'id': 'test_rust_test_scenario_coverage',
        'lane': 'static_navigation',
        'command': 'make test-rust-test-scenario-coverage',
        'purpose': 'confirm the static Rust scenario-coverage ledger is reproducible',
    },
    {
        'id': 'update_rust_gap_witness_queue',
        'lane': 'static_navigation',
        'command': 'make update-rust-gap-witness-queue',
        'purpose': 'refresh the static gap-to-witness bridge for later Rust-capable test recovery',
    },
    {
        'id': 'test_rust_gap_witness_queue',
        'lane': 'static_navigation',
        'command': 'make test-rust-gap-witness-queue',
        'purpose': 'confirm the static gap-to-witness bridge is reproducible',
    },
    {
        'id': 'update_rust_gap_probe_seed_index',
        'lane': 'static_navigation',
        'command': 'make update-rust-gap-probe-seed-index',
        'purpose': 'refresh the compact probe-seed index for weak Rust scenarios',
    },
    {
        'id': 'test_rust_gap_probe_seed_index',
        'lane': 'static_navigation',
        'command': 'make test-rust-gap-probe-seed-index',
        'purpose': 'confirm the probe-seed index is reproducible',
    },
    {
        'id': 'update_rust_external_test_queue',
        'lane': 'static_navigation',
        'command': 'make update-rust-external-test-queue',
        'purpose': 'refresh the external-test lift queue for the weak Rust scenario seeds',
    },
    {
        'id': 'test_rust_external_test_queue',
        'lane': 'static_navigation',
        'command': 'make test-rust-external-test-queue',
        'purpose': 'confirm the external-test lift queue is reproducible',
    },
    {
        'id': 'update_rust_seed_loader_readiness',
        'lane': 'static_navigation',
        'command': 'make update-rust-seed-loader-readiness',
        'purpose': 'audit whether the preferred lift-queue seeds are directly loadable ProbeSpec fixtures',
    },
    {
        'id': 'test_rust_seed_loader_readiness',
        'lane': 'static_navigation',
        'command': 'make test-rust-seed-loader-readiness',
        'purpose': 'confirm the seed-loader readiness audit is reproducible',
    },
    {
        'id': 'update_rust_lift_bundle_plan',
        'lane': 'static_navigation',
        'command': 'make update-rust-lift-bundle-plan',
        'purpose': 'refresh the shared-fixture Rust lift bundle plan for later external-test implementation',
    },
    {
        'id': 'test_rust_lift_bundle_plan',
        'lane': 'static_navigation',
        'command': 'make test-rust-lift-bundle-plan',
        'purpose': 'confirm the Rust lift bundle plan is reproducible',
    },
    {
        'id': 'update_rust_external_test_patchset',
        'lane': 'static_navigation',
        'command': 'make update-rust-external-test-patchset',
        'purpose': 'refresh the replayable unified patch for the first external Rust comeback edits',
    },
    {
        'id': 'test_rust_external_test_patchset',
        'lane': 'static_navigation',
        'command': 'make test-rust-external-test-patchset',
        'purpose': 'confirm the replayable external-test patchset is reproducible',
    },
    {
        'id': 'update_rust_external_test_patch_shards',
        'lane': 'static_navigation',
        'command': 'make update-rust-external-test-patch-shards',
        'purpose': 'refresh the ordered cumulative patch-shard series for the external-test comeback',
    },
    {
        'id': 'test_rust_external_test_patch_shards',
        'lane': 'static_navigation',
        'command': 'make test-rust-external-test-patch-shards',
        'purpose': 'confirm the ordered cumulative patch-shard series is reproducible',
    },
    {
        'id': 'update_rust_external_test_patch_rehearsal',
        'lane': 'static_navigation',
        'command': 'make update-rust-external-test-patch-rehearsal',
        'purpose': 'rehearse the monolithic patchset and cumulative shard series on scratch copies and compare the final target-file states',
    },
    {
        'id': 'test_rust_external_test_patch_rehearsal',
        'lane': 'static_navigation',
        'command': 'make test-rust-external-test-patch-rehearsal',
        'purpose': 'confirm the patch rehearsal equivalence report is reproducible',
    },
    {
        'id': 'update_rust_standing_bootstrap_guard',
        'lane': 'static_navigation',
        'command': 'make update-rust-standing-bootstrap-guard',
        'purpose': 'emit the standalone Rust regression patch for the simple-standing bootstrap seam using a dedicated test file',
    },
    {
        'id': 'test_rust_standing_bootstrap_guard',
        'lane': 'static_navigation',
        'command': 'make test-rust-standing-bootstrap-guard',
        'purpose': 'confirm the standalone bootstrap guard patch/card stays reproducible',
    },
    {
        'id': 'update_rust_standing_bootstrap_guard_rehearsal',
        'lane': 'static_navigation',
        'command': 'make update-rust-standing-bootstrap-guard-rehearsal',
        'purpose': 'scratch-apply the standalone bootstrap guard patch and verify the landed test file bytes match the generated report',
    },
    {
        'id': 'test_rust_standing_bootstrap_guard_rehearsal',
        'lane': 'static_navigation',
        'command': 'make test-rust-standing-bootstrap-guard-rehearsal',
        'purpose': 'confirm the standalone bootstrap guard rehearsal stays reproducible',
    },
    {
        'id': 'update_rust_standing_bootstrap_repair_patch',
        'lane': 'static_navigation',
        'command': 'make update-rust-standing-bootstrap-repair-patch',
        'purpose': 'emit the smallest source-level Rust repair patch for the probe-local simple-standing bootstrap seam',
    },
    {
        'id': 'test_rust_standing_bootstrap_repair_patch',
        'lane': 'static_navigation',
        'command': 'make test-rust-standing-bootstrap-repair-patch',
        'purpose': 'confirm the minimal probe-local bootstrap repair patch/card stays reproducible',
    },
    {
        'id': 'update_rust_standing_bootstrap_repair_rehearsal',
        'lane': 'static_navigation',
        'command': 'make update-rust-standing-bootstrap-repair-rehearsal',
        'purpose': 'scratch-apply the repair patch and then the standalone guard patch to prove the intended first-machine sequence lands cleanly',
    },
    {
        'id': 'test_rust_standing_bootstrap_repair_rehearsal',
        'lane': 'static_navigation',
        'command': 'make test-rust-standing-bootstrap-repair-rehearsal',
        'purpose': 'confirm the bootstrap repair plus guard sequence rehearsal stays reproducible',
    },
    {
        'id': 'update_rust_standing_bootstrap_integration_rehearsal',
        'lane': 'static_navigation',
        'command': 'make update-rust-standing-bootstrap-integration-rehearsal',
        'purpose': 'prove the narrow bootstrap repair and guard remain operationally orthogonal to the larger comeback patchset across both landing orders',
    },
    {
        'id': 'test_rust_standing_bootstrap_integration_rehearsal',
        'lane': 'static_navigation',
        'command': 'make test-rust-standing-bootstrap-integration-rehearsal',
        'purpose': 'confirm the bootstrap integration rehearsal stays reproducible',
    },
    {
        'id': 'update_rust_standing_bootstrap_comeback_bundle',
        'lane': 'static_navigation',
        'command': 'make update-rust-standing-bootstrap-comeback-bundle',
        'purpose': 'emit a one-shot clean-head Rust bundle that compresses repair plus guard plus the monolithic comeback patchset into one apply step',
    },
    {
        'id': 'test_rust_standing_bootstrap_comeback_bundle',
        'lane': 'static_navigation',
        'command': 'make test-rust-standing-bootstrap-comeback-bundle',
        'purpose': 'confirm the one-shot comeback bundle still matches the hashed final state of the layered repair->guard->patchset sequence',
    },
    {
        'id': 'update_rust_standing_bootstrap_comeback_bundle_rehearsal',
        'lane': 'static_navigation',
        'command': 'make update-rust-standing-bootstrap-comeback-bundle-rehearsal',
        'purpose': 'scratch-apply the one-shot comeback bundle and verify its landed file hashes match the generated bundle report',
    },
    {
        'id': 'test_rust_standing_bootstrap_comeback_bundle_rehearsal',
        'lane': 'static_navigation',
        'command': 'make test-rust-standing-bootstrap-comeback-bundle-rehearsal',
        'purpose': 'confirm the one-shot comeback bundle rehearsal stays reproducible',
    },
    {
        'id': 'update_rust_standing_bootstrap_verification_ladder',
        'lane': 'static_navigation',
        'command': 'make update-rust-standing-bootstrap-verification-ladder',
        'purpose': 'emit the final-state standing-focused verification ladder so the first Rust-capable inheritor can prove the repair with the smallest exact post-apply witness sequence',
    },
    {
        'id': 'test_rust_standing_bootstrap_verification_ladder',
        'lane': 'static_navigation',
        'command': 'make test-rust-standing-bootstrap-verification-ladder',
        'purpose': 'confirm the final-state bootstrap verification ladder stays reproducible and still tracks the exact affected queue rows',
    },
    {
        'id': 'update_rust_standing_bootstrap_verification_ladder_rehearsal',
        'lane': 'static_navigation',
        'command': 'make update-rust-standing-bootstrap-verification-ladder-rehearsal',
        'purpose': 'scratch-check that the verification ladder only emits after exact final_full and otherwise routes back to apply sequencing',
    },
    {
        'id': 'test_rust_standing_bootstrap_verification_ladder_rehearsal',
        'lane': 'static_navigation',
        'command': 'make test-rust-standing-bootstrap-verification-ladder-rehearsal',
        'purpose': 'confirm the bootstrap verification-ladder rehearsal stays reproducible',
    },
    {
        'id': 'update_rust_patch_prefix_frontier',
        'lane': 'static_navigation',
        'command': 'make update-rust-patch-prefix-frontier',
        'purpose': 'quantify useful stopping points across the ordered patch-shard series so the comeback can land partially and intentionally',
    },
    {
        'id': 'test_rust_patch_prefix_frontier',
        'lane': 'static_navigation',
        'command': 'make test-rust-patch-prefix-frontier',
        'purpose': 'confirm the patch-prefix frontier report is reproducible',
    },
    {
        'id': 'update_cloudtainer_shadow_pass_history',
        'lane': 'archive_hygiene',
        'command': 'make update-cloudtainer-shadow-pass-history',
        'purpose': 'refresh the longitudinal history of cloudtainer shadow-pass receipts and stable budget cutpoints',
    },
    {
        'id': 'test_cloudtainer_shadow_pass_history',
        'lane': 'archive_hygiene',
        'command': 'make test-cloudtainer-shadow-pass-history',
        'purpose': 'confirm the cloudtainer shadow-pass history report is reproducible and internally consistent',
    },
    {
        'id': 'update_cloudtainer_rust_probe_oracles',
        'lane': 'archive_hygiene',
        'command': 'make update-cloudtainer-rust-probe-oracles',
        'purpose': 'refresh the blocked-session exact/expectation oracle layer for the current Rust comeback probe seeds',
    },
    {
        'id': 'test_cloudtainer_rust_probe_oracles',
        'lane': 'archive_hygiene',
        'command': 'make test-cloudtainer-rust-probe-oracles',
        'purpose': 'confirm the blocked-session Rust probe oracle layer is reproducible and internally consistent',
    },
    {
        'id': 'examples_json_check',
        'lane': 'python_shadow_checks',
        'command': 'python3 ./scripts/test/check_examples_json.py',
        'purpose': 'confirm the example seeds remain valid JSON while Rust is blocked',
    },
    {
        'id': 'examples_unique_ids_check',
        'lane': 'python_shadow_checks',
        'command': 'python3 ./scripts/test/check_examples_unique_ids.py',
        'purpose': 'confirm newly added example seeds do not collide on top-level ids',
    },
    {
        'id': 'update_command_inventory',
        'lane': 'archive_hygiene',
        'command': 'make update-command-inventory',
        'purpose': 'refresh the Makefile command index after command-surface edits',
    },
    {
        'id': 'update_artifact_buckets',
        'lane': 'archive_hygiene',
        'command': 'make update-artifact-buckets',
        'purpose': 'refresh artifact-bucket summary after new process receipts land',
    },
    {
        'id': 'readme_command_surface_check',
        'lane': 'python_shadow_checks',
        'command': 'python3 ./scripts/test/check_readme_command_surface.py',
        'purpose': 'keep README command examples aligned with Makefile reality',
    },
    {
        'id': 'generated_docs_presence_check',
        'lane': 'python_shadow_checks',
        'command': 'python3 ./scripts/test/check_generated_docs_presence.py',
        'purpose': 'confirm generated-doc placeholders remain present and current',
    },
    {
        'id': 'control_tests',
        'lane': 'python_shadow_checks',
        'command': "python3 -u -m unittest discover -s tests/control -p 'test_*.py'",
        'purpose': 'run deterministic governance/control tests that do not need Rust',
    },
    {
        'id': 'grlab_certify_tests',
        'lane': 'python_shadow_checks',
        'command': 'python3 -u -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli grlab.tests.test_certify_schema',
        'purpose': 'recheck the local Python certification lane while Rust remains blocked',
    },
]

STEP_BY_ID = {str(step['id']): step for step in STEPS}
BLOCKED_MARKERS = {
    'cargo': ['cargo unavailable', 'cargo: missing', 'command not found: cargo'],
    'junest': ['junest', 'could not find junest', 'run: /run/sandworm/toolroot/bin/junest setup'],
    'rustc': ['rustc direct probe failed', 'command not found: rustc', 'rustc: missing'],
}

class IntentionalStop(Exception):
    pass

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def isoformat_z(dt: datetime) -> str:
    return dt.isoformat().replace('+00:00', 'Z')

def default_output_path() -> Path:
    stamp = utc_now().strftime('%Y%m%dT%H%M%SZ')
    return ARTIFACT_DIR / f'cloudtainer_shadow_pass_{stamp}.json'

def relative_path_text(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()

def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', dir=path.parent, prefix=path.name, suffix='.tmp') as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write('\n')
        temp_name = handle.name
    os.replace(temp_name, path)

def base_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault('TZ', 'UTC')
    env.setdefault('LANG', 'C')
    env.setdefault('LC_ALL', 'C')
    env.setdefault('PYTHONHASHSEED', '0')
    env.setdefault('TEST_SEED', '424242')
    env.setdefault('NO_NETWORK', '1')
    for key in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY']:
        env.pop(key, None)
    return env

def detect_tools() -> dict[str, str | None]:
    junest_path = None
    if shutil.which('junest'):
        junest_path = shutil.which('junest')
    elif Path('/run/sandworm/toolroot/bin/junest').exists():
        junest_path = '/run/sandworm/toolroot/bin/junest'
    return {
        'python3': shutil.which('python3'),
        'cargo': shutil.which('cargo'),
        'rustc': shutil.which('rustc'),
        'junest': junest_path,
        'node': shutil.which('node'),
        'gcc': shutil.which('gcc'),
        'make': shutil.which('make'),
    }

def detect_missing_tools(text: str) -> list[str]:
    lowered = text.lower()
    missing: list[str] = []
    for tool, markers in BLOCKED_MARKERS.items():
        if any(marker in lowered for marker in markers):
            missing.append(tool)
    if 'cargo unavailable' in lowered and 'rustc' not in missing:
        missing.append('rustc')
    return sorted(set(missing))

def classify_status(returncode: int, text: str, allow_blocked: bool) -> tuple[str, str | None, list[str]]:
    if returncode == 0:
        return ('pass', None, [])
    missing_tools = detect_missing_tools(text)
    if allow_blocked and missing_tools:
        return ('blocked', 'missing_toolchain', missing_tools)
    return ('fail', None, missing_tools)

def summarize_output(text: str, limit: int = 6) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return 'no output'
    if len(lines) <= limit:
        return ' | '.join(lines)
    head = ' | '.join(lines[: limit - 1])
    return f'{head} | … ({len(lines)} lines total)'

def filter_steps(step_ids_text: str | None) -> list[dict[str, object]]:
    if not step_ids_text:
        return list(STEPS)
    selected_ids = [part.strip() for part in step_ids_text.split(',') if part.strip()]
    if not selected_ids:
        raise SystemExit('--step-ids requires at least one non-empty step id')
    unknown = [step_id for step_id in selected_ids if step_id not in STEP_BY_ID]
    if unknown:
        raise SystemExit(f"unknown step ids: {', '.join(unknown)}")
    seen: set[str] = set()
    filtered: list[dict[str, object]] = []
    for step_id in selected_ids:
        if step_id in seen:
            continue
        filtered.append(STEP_BY_ID[step_id])
        seen.add(step_id)
    return filtered

def load_budget_profiles(frontier_report_path: Path) -> dict[str, dict[str, Any]]:
    if not frontier_report_path.exists():
        raise SystemExit(
            'budget profile report missing; regenerate it with make update-cloudtainer-shadow-pass-frontier'
        )
    payload = json.loads(frontier_report_path.read_text(encoding='utf-8'))
    frontier_by_label = {str(entry['label']): entry for entry in payload.get('frontiers') or []}
    profiles: dict[str, dict[str, Any]] = {}
    for entry in payload.get('recommended_budget_prefixes') or []:
        label = str(entry['label'])
        frontier_label = str(entry['frontier_label'])
        frontier = frontier_by_label.get(frontier_label)
        if frontier is None:
            raise SystemExit(f'frontier label {frontier_label!r} missing from {relative_path_text(frontier_report_path)}')
        profiles[label] = {
            'profile_label': label,
            'frontier_label': frontier_label,
            'step_index': int(frontier['step_index']),
            'step_id': str(frontier['step_id']),
            'cumulative_seconds': float(frontier['cumulative_seconds']),
            'remaining_seconds': float(frontier['remaining_seconds']),
            'why_choose_it': str(entry.get('why_choose_it') or frontier.get('rationale') or ''),
            'command': str(entry.get('command') or ''),
            'resume_command': str(entry.get('resume_command') or 'make cloudtainer-shadow-pass-resume'),
        }
    for frontier_label, frontier in frontier_by_label.items():
        profiles.setdefault(
            frontier_label,
            {
                'profile_label': frontier_label,
                'frontier_label': frontier_label,
                'step_index': int(frontier['step_index']),
                'step_id': str(frontier['step_id']),
                'cumulative_seconds': float(frontier['cumulative_seconds']),
                'remaining_seconds': float(frontier['remaining_seconds']),
                'why_choose_it': str(frontier.get('rationale') or ''),
                'command': '',
                'resume_command': 'make cloudtainer-shadow-pass-resume',
            },
        )
    return profiles

def render_budget_profile_lines(profiles: dict[str, dict[str, Any]]) -> list[str]:
    lines = []
    for label in sorted(profiles, key=lambda item: (profiles[item]['step_index'], item)):
        profile = profiles[label]
        command = profile['command'] or f'python3 ./scripts/tools/cloudtainer_shadow_pass.py --budget-profile {label}'
        lines.append(
            f"{label}: step={profile['step_index']} id={profile['step_id']} "
            f"seconds={round(float(profile['cumulative_seconds']), 3)} command={command}"
        )
    return lines

def resolve_budget_profile_stop_after_step(args: argparse.Namespace, selected_steps: list[dict[str, object]]) -> tuple[int | None, dict[str, Any] | None]:
    if args.budget_profile is None:
        return args.stop_after_step, None
    if args.stop_after_step is not None:
        raise SystemExit('--budget-profile cannot be combined with --stop-after-step')
    if args.resume:
        raise SystemExit('--budget-profile cannot be combined with --resume; use make cloudtainer-shadow-pass-resume after the intentional stop')
    if args.step_ids:
        raise SystemExit('--budget-profile currently requires the full canonical step order; omit --step-ids')
    frontier_report_path = args.frontier_report
    if not frontier_report_path.is_absolute():
        frontier_report_path = (ROOT / frontier_report_path).resolve()
    profiles = load_budget_profiles(frontier_report_path)
    if args.list_budget_profiles:
        for line in render_budget_profile_lines(profiles):
            print(line)
        raise SystemExit(0)
    profile = profiles.get(args.budget_profile)
    if profile is None:
        known = ', '.join(sorted(profiles))
        raise SystemExit(f"unknown budget profile {args.budget_profile!r}; known profiles: {known}")
    stop_after_step = int(profile['step_index'])
    if stop_after_step < 1 or stop_after_step > len(selected_steps):
        raise SystemExit(
            f"budget profile {args.budget_profile!r} resolves to step {stop_after_step}, outside selected step count {len(selected_steps)}"
        )
    return stop_after_step, profile

def start_output_reader(proc: subprocess.Popen[str], line_queue: queue.Queue[str | None]) -> threading.Thread:
    def _reader() -> None:
        assert proc.stdout is not None
        try:
            for line in proc.stdout:
                line_queue.put(line)
        finally:
            line_queue.put(None)
    thread = threading.Thread(target=_reader, daemon=True)
    thread.start()
    return thread

def run_step(step: dict[str, object], env: dict[str, str], *, verbose: bool, heartbeat_seconds: float) -> dict[str, object]:
    command = str(step['command'])
    started = time.time()
    captured_parts: list[str] = []
    if verbose:
        proc = subprocess.Popen(['bash', '-lc', command], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        line_queue: queue.Queue[str | None] = queue.Queue()
        start_output_reader(proc, line_queue)
        reader_done = False
        last_activity = time.time()
        while not reader_done:
            try:
                item = line_queue.get(timeout=max(heartbeat_seconds, 0.1))
            except queue.Empty:
                elapsed = round(time.time() - started, 1)
                print(f"cloudtainer-shadow-pass: heartbeat {step['id']} elapsed={elapsed}s", flush=True)
                last_activity = time.time()
                continue
            if item is None:
                reader_done = True
                continue
            captured_parts.append(item)
            print(item.rstrip(), flush=True)
            last_activity = time.time()
        returncode = proc.wait()
        if time.time() - last_activity >= heartbeat_seconds:
            elapsed = round(time.time() - started, 1)
            print(f"cloudtainer-shadow-pass: heartbeat {step['id']} elapsed={elapsed}s", flush=True)
    else:
        proc = subprocess.run(['bash', '-lc', command], cwd=ROOT, env=env, capture_output=True, text=True)
        returncode = proc.returncode
        captured_parts.extend(part for part in [proc.stdout, proc.stderr] if part)
    elapsed = round(time.time() - started, 3)
    output_text = ''.join(captured_parts)
    status, outcome_code, missing_tools = classify_status(returncode, output_text, bool(step.get('allow_blocked')))
    row: dict[str, object] = {
        'id': step['id'], 'lane': step['lane'], 'purpose': step['purpose'], 'command': command,
        'status': status, 'duration_seconds': elapsed, 'returncode': returncode, 'summary': summarize_output(output_text),
    }
    if outcome_code is not None:
        row['outcome_code'] = outcome_code
    if missing_tools:
        row['missing_tools'] = missing_tools
    return row

def build_checkpoint_payload(*, checkpoint_path: Path, output_path: Path, selected_steps: list[dict[str, object]], tool_paths: dict[str, str | None], started_at: datetime, rows: list[dict[str, object]], next_step_index: int, run_status: str) -> dict[str, Any]:
    return {
        'checkpoint_type': 'cloudtainer_shadow_pass_checkpoint',
        'checkpoint_version': 1,
        'profile': 'rust_blocked_shadow_v2',
        'created_at_utc': isoformat_z(started_at),
        'updated_at_utc': isoformat_z(utc_now()),
        'checkpoint_path': relative_path_text(checkpoint_path),
        'output_path': relative_path_text(output_path),
        'selected_step_ids': [str(step['id']) for step in selected_steps],
        'total_step_count': len(selected_steps),
        'next_step_index': next_step_index,
        'completed_step_count': len(rows),
        'completed_step_ids': [str(row['id']) for row in rows],
        'tool_paths': tool_paths,
        'rows': rows,
        'run_status': run_status,
    }

def load_checkpoint(checkpoint_path: Path, selected_steps: list[dict[str, object]]) -> tuple[datetime, list[dict[str, object]], int, Path]:
    payload = json.loads(checkpoint_path.read_text(encoding='utf-8'))
    if payload.get('checkpoint_type') != 'cloudtainer_shadow_pass_checkpoint':
        raise SystemExit(f'invalid checkpoint type in {relative_path_text(checkpoint_path)}')
    expected_ids = [str(step['id']) for step in selected_steps]
    stored_ids = payload.get('selected_step_ids') or []
    if stored_ids != expected_ids:
        raise SystemExit('checkpoint step selection mismatch: ' f'expected {expected_ids}, found {stored_ids}')
    started_at = datetime.fromisoformat(str(payload['created_at_utc']).replace('Z', '+00:00'))
    rows = payload.get('rows') or []
    next_step_index = int(payload.get('next_step_index', len(rows)))
    output_path = Path(str(payload['output_path']))
    if not output_path.is_absolute():
        output_path = (ROOT / output_path).resolve()
    return started_at, rows, next_step_index, output_path

def write_checkpoint(checkpoint_path: Path, output_path: Path, selected_steps: list[dict[str, object]], tool_paths: dict[str, str | None], started_at: datetime, rows: list[dict[str, object]], next_step_index: int, run_status: str) -> None:
    payload = build_checkpoint_payload(checkpoint_path=checkpoint_path, output_path=output_path, selected_steps=selected_steps, tool_paths=tool_paths, started_at=started_at, rows=rows, next_step_index=next_step_index, run_status=run_status)
    write_json_atomic(checkpoint_path, payload)

def build_final_receipt(*, output_path: Path, checkpoint_path: Path, selected_steps: list[dict[str, object]], started_at: datetime, ended_at: datetime, tool_paths: dict[str, str | None], rows: list[dict[str, object]], resumed_from_checkpoint: bool, initial_completed_rows: int) -> dict[str, Any]:
    pass_count = sum(1 for row in rows if row['status'] == 'pass')
    blocked_count = sum(1 for row in rows if row['status'] == 'blocked')
    fail_count = sum(1 for row in rows if row['status'] == 'fail')
    missing_tools = sorted({tool for row in rows for tool in row.get('missing_tools', [])})
    if fail_count == 0 and blocked_count == 0:
        decision = 'usable_full_toolchain'
    elif fail_count == 0 and blocked_count > 0 and all(row['status'] != 'blocked' or row['lane'] == 'environment_boundary' for row in rows):
        decision = 'usable_rust_blocked'
    else:
        decision = 'attention_required'
    recommended_next_actions = ['use_make_cloudtainer_shadow_pass_for_blocked_sessions', 'keep_runtime_semantic_claims_blocked_until_rust_lane_reruns']
    if resumed_from_checkpoint:
        recommended_next_actions.append('prefer_make_cloudtainer_shadow_pass_resume_after_wrapper_interruptions')
    if 'cargo' in missing_tools:
        recommended_next_actions.append('rerun_make_doctor_after_cargo_available')
    if 'junest' in missing_tools:
        recommended_next_actions.append('rerun_make_test_quick_after_junest_available')
    return {
        'receipt_type': 'cloudtainer_shadow_pass',
        'receipt_version': 2,
        'profile': 'rust_blocked_shadow_v2',
        'created_at_utc': isoformat_z(started_at),
        'completed_at_utc': isoformat_z(ended_at),
        'repo_root': '.',
        'output_path': relative_path_text(output_path),
        'tool_paths': tool_paths,
        'selected_step_ids': [str(step['id']) for step in selected_steps],
        'summary_counts': {'pass_count': pass_count, 'blocked_count': blocked_count, 'fail_count': fail_count, 'step_count': len(rows)},
        'environment_boundary': {'rust_lane_status': 'blocked_missing_toolchain' if missing_tools else 'available', 'missing_tools': missing_tools},
        'decision': decision,
        'recommended_next_actions': recommended_next_actions,
        'checkpointing': {
            'checkpoint_path': relative_path_text(checkpoint_path),
            'resumed_from_checkpoint': resumed_from_checkpoint,
            'initial_completed_rows': initial_completed_rows,
            'checkpoint_cleared_on_success': True,
        },
        'steps': rows,
        'rationale': (
            'This receipt captures the smallest productive local pass for cloudtainer sessions where Python and docs tooling are available but the Rust lane may still be blocked. '
            'It is meant to preserve one repeatable command surface and one compact local verification summary without pretending that Rust runtime claims were revalidated. '
            'Version 2 adds checkpoint-and-resume support so wrapper interruptions do not erase already-completed blocked-session work.'
        ),
    }

def refresh_artifact_buckets_post_write() -> None:
    proc = subprocess.run(['bash', '-lc', 'make update-artifact-buckets'], cwd=ROOT, env=base_env(), capture_output=True, text=True)
    if proc.returncode != 0:
        summary = summarize_output('\n'.join(part for part in [proc.stdout, proc.stderr] if part))
        print(f'cloudtainer-shadow-pass: post-write artifact-bucket refresh failed: {summary}', file=sys.stderr)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run the canonical cloudtainer shadow pass and write a compact process receipt.')
    parser.add_argument('--output', type=Path, default=None, help='output JSON path (default: artifacts/process/cloudtainer_shadow_pass_<timestamp>.json)')
    parser.add_argument('--checkpoint', type=Path, default=DEFAULT_CHECKPOINT_PATH, help='checkpoint JSON path used for resumable shadow-pass runs')
    parser.add_argument('--resume', action='store_true', help='resume from an existing checkpoint if present')
    parser.add_argument('--step-ids', default=None, help='comma-separated subset of step ids to run in order')
    parser.add_argument('--stop-after-step', type=int, default=None, help='intentionally stop after N selected steps (test/rehearsal helper)')
    parser.add_argument('--budget-profile', default=None, help='named intentional-stop profile from the shadow-pass frontier report (for example: short_budget, medium_budget, long_budget)')
    parser.add_argument('--frontier-report', type=Path, default=DEFAULT_FRONTIER_REPORT_PATH, help='frontier JSON used to resolve --budget-profile labels')
    parser.add_argument('--list-budget-profiles', action='store_true', help='list known budget-profile labels and exit')
    parser.add_argument('--heartbeat-seconds', type=float, default=8.0, help='seconds between heartbeat lines while a step stays quiet')
    parser.add_argument('--print-path-only', action='store_true', help='print only the receipt path after success')
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    selected_steps = filter_steps(args.step_ids)
    if args.list_budget_profiles and args.budget_profile is None:
        frontier_report_path = args.frontier_report
        if not frontier_report_path.is_absolute():
            frontier_report_path = (ROOT / frontier_report_path).resolve()
        profiles = load_budget_profiles(frontier_report_path)
        for line in render_budget_profile_lines(profiles):
            print(line)
        return 0
    resolved_stop_after_step, selected_budget_profile = resolve_budget_profile_stop_after_step(args, selected_steps)
    checkpoint_path = args.checkpoint
    if not checkpoint_path.is_absolute():
        checkpoint_path = (ROOT / checkpoint_path).resolve()
    output_path = args.output or default_output_path()
    if not output_path.is_absolute():
        output_path = (ROOT / output_path).resolve()
    env = base_env()
    tool_paths = detect_tools()
    verbose = not args.print_path_only
    resumed_from_checkpoint = False
    initial_completed_rows = 0
    if args.resume and checkpoint_path.exists():
        started_at, rows, next_step_index, resume_output_path = load_checkpoint(checkpoint_path, selected_steps)
        output_path = resume_output_path
        resumed_from_checkpoint = True
        initial_completed_rows = len(rows)
        if verbose:
            print(f'cloudtainer-shadow-pass: resuming from {relative_path_text(checkpoint_path)} at step_index={next_step_index} completed={initial_completed_rows}', flush=True)
    else:
        started_at = utc_now()
        rows = []
        next_step_index = 0
        write_checkpoint(checkpoint_path, output_path, selected_steps, tool_paths, started_at, rows, next_step_index, 'in_progress')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        for idx in range(next_step_index, len(selected_steps)):
            step = selected_steps[idx]
            if verbose:
                print(f"cloudtainer-shadow-pass: start {step['id']} ({idx + 1}/{len(selected_steps)})", flush=True)
            row = run_step(step, env, verbose=verbose, heartbeat_seconds=max(args.heartbeat_seconds, 0.1))
            rows.append(row)
            write_checkpoint(checkpoint_path, output_path, selected_steps, tool_paths, started_at, rows, idx + 1, 'in_progress')
            if verbose:
                print(f"cloudtainer-shadow-pass: done {step['id']} status={row['status']} duration={row['duration_seconds']}s", flush=True)
            if resolved_stop_after_step is not None and (idx + 1) >= resolved_stop_after_step:
                write_checkpoint(checkpoint_path, output_path, selected_steps, tool_paths, started_at, rows, idx + 1, 'intentional_stop')
                raise IntentionalStop
    except IntentionalStop:
        if args.print_path_only:
            print(relative_path_text(checkpoint_path))
        else:
            profile_hint = ''
            if selected_budget_profile is not None:
                profile_hint = f" via budget_profile={selected_budget_profile['profile_label']} frontier={selected_budget_profile['frontier_label']}"
            print(f'cloudtainer-shadow-pass: intentional stop after {len(rows)}/{len(selected_steps)} steps{profile_hint}; resume with make cloudtainer-shadow-pass-resume', flush=True)
            print(f'cloudtainer-shadow-pass: checkpoint {relative_path_text(checkpoint_path)}', flush=True)
        return 0
    ended_at = utc_now()
    receipt = build_final_receipt(output_path=output_path, checkpoint_path=checkpoint_path, selected_steps=selected_steps, started_at=started_at, ended_at=ended_at, tool_paths=tool_paths, rows=rows, resumed_from_checkpoint=resumed_from_checkpoint, initial_completed_rows=initial_completed_rows)
    write_json_atomic(output_path, receipt)
    refresh_artifact_buckets_post_write()
    if checkpoint_path.exists():
        checkpoint_path.unlink()
    if args.print_path_only:
        print(relative_path_text(output_path))
    else:
        print(f"cloudtainer-shadow-pass: wrote {relative_path_text(output_path)}")
        print(f"cloudtainer-shadow-pass: decision={receipt['decision']} pass={receipt['summary_counts']['pass_count']} blocked={receipt['summary_counts']['blocked_count']} fail={receipt['summary_counts']['fail_count']}", flush=True)
    return 0 if receipt['decision'] != 'attention_required' else 1

if __name__ == '__main__':
    raise SystemExit(main())
