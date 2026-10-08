from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_SPEC = importlib.util.spec_from_file_location('support_surface_snapshot', ROOT / 'scripts' / 'support_surface_snapshot.py')
SNAPSHOT_MODULE = importlib.util.module_from_spec(SNAPSHOT_SPEC)
assert SNAPSHOT_SPEC.loader is not None
SNAPSHOT_SPEC.loader.exec_module(SNAPSHOT_MODULE)

CONTRACT_SPEC = importlib.util.spec_from_file_location('check_support_record_contract', ROOT / 'scripts' / 'check_support_record_contract.py')
CONTRACT_MODULE = importlib.util.module_from_spec(CONTRACT_SPEC)
assert CONTRACT_SPEC.loader is not None
CONTRACT_SPEC.loader.exec_module(CONTRACT_MODULE)

build_support_surface_snapshot = SNAPSHOT_MODULE.build_support_surface_snapshot
capture_support_surface_snapshot = SNAPSHOT_MODULE.capture_support_surface_snapshot
summarize_capture_history = SNAPSHOT_MODULE.summarize_capture_history
build_contract_report = CONTRACT_MODULE.build_contract_report


def _write_record(path: Path, *, surface_key: str, title: str = 'ChatGPT', record_status: str = 'seeded', rollout_priority: str = 'recommended second adapter') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workflows = [
        ('surface-detect', 'investigated'),
        ('receiver-resolve', 'investigated'),
        ('composer-read', 'investigated'),
        ('composer-write', 'investigated'),
        ('turn-submit', 'investigated'),
        ('generation-read', 'investigated'),
        ('latest-turn-read', 'investigated'),
        ('support-capture', 'investigated'),
    ]
    rows = '\n'.join(
        f"| {workflow} | {tier} | chromium-live | named bundle pending | caveat for {workflow} | promotion step for {workflow} |"
        for workflow, tier in workflows
    )
    path.write_text(
        f'''# Support record — {title}\n\n## Metadata\n- **surface key:** `{surface_key}`\n- **record status:** `{record_status}`\n- **default browser lane:** `chromium-live`\n- **last reviewed:** `2026-03-20`\n- **rollout priority:** `{rollout_priority}`\n\n## Scope and assumptions\nTest surface.\n\n## Workflow rows\n\n| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |\n|---|---|---|---|---|---|\n{rows}\n\n## Known blockers and risk notes\n- example blocker\n\n## Next action\n- capture one named bundle\n''',
        encoding='utf-8',
    )


def test_build_support_surface_snapshot_flattens_records_and_contract() -> None:
    # use the real repo records because they are already contract-valid
    snapshot = build_support_surface_snapshot(root=ROOT)
    assert snapshot['support_surface']['surface_count'] >= 1
    assert snapshot['record_contract']['all_valid'] is True
    assert snapshot['support_surface']['workflow_rows']


def test_capture_support_surface_snapshot_writes_bundle_history_and_diff(tmp_path: Path) -> None:
    root = tmp_path
    _write_record(root / 'docs' / 'support-records' / 'chatgpt.md', surface_key='chatgpt')
    output_dir = tmp_path / 'validation' / 'latest' / 'support-surface-capture'
    history_path = tmp_path / 'validation' / 'support-surface-captures.json'

    bundle = capture_support_surface_snapshot(output_dir=output_dir, history_path=history_path, root=root)
    assert bundle['history_update']['capture_count_after_write'] == 1
    assert (output_dir / 'support-surface.json').exists()
    assert (output_dir / 'record-contract.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert (output_dir / 'capture-history.json').exists()
    assert (output_dir / 'capture-diff.json').exists()
    saved = json.loads((output_dir / 'support-surface.json').read_text(encoding='utf-8'))
    assert saved['support_surface']['surface_count'] == 1
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1


def test_contract_report_flags_missing_core_workflows(tmp_path: Path) -> None:
    record_path = tmp_path / 'docs' / 'support-records' / 'chatgpt.md'
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(
        '''# Support record — ChatGPT\n\n## Metadata\n- **surface key:** `chatgpt`\n- **record status:** `seeded`\n- **default browser lane:** `chromium-live`\n- **last reviewed:** `2026-03-20`\n- **rollout priority:** `recommended second adapter`\n\n## Workflow rows\n\n| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |\n|---|---|---|---|---|---|\n| surface-detect | investigated | chromium-live | pending | caveat | promote |\n\n## Known blockers and risk notes\n- blocker\n\n## Next action\n- do more work\n''',
        encoding='utf-8',
    )
    report = build_contract_report(root=tmp_path)
    assert report['all_valid'] is False
    assert report['error_count'] >= 1
    assert any('missing core workflow row' in error for error in report['records'][0]['errors'])


def test_doctor_exposes_support_surface_commands_and_hint() -> None:
    output = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True))
    assert output['support_surface']['commands']['report'] == 'python scripts/support-surface-snapshot.py --pretty'
    assert any('machine-readable support surface' in hint and 'python scripts/support-surface-snapshot.py --pretty' in hint for hint in output['hints'])
