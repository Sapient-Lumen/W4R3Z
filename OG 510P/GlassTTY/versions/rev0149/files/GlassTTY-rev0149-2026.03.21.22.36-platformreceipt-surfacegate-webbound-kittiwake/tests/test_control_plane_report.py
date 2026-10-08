from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = ROOT / 'scripts' / 'control_plane_report.py'
SPEC = importlib.util.spec_from_file_location('control_plane_report', MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_control_plane_report = MODULE.build_control_plane_report
capture_control_plane_report = MODULE.capture_control_plane_report
parse_support_record = MODULE.parse_support_record
summarize_capture_history = MODULE.summarize_capture_history


def _doctor_report() -> dict:
    return {
        'project': 'GlassTTY',
        'socket': {'exists': False},
        'native_host': {'runtime': {'connected': False}},
        'validation': {
            'latest_report': {'exists': True, 'summary': {'complete': False}},
            'capture_history': {'capture_count': 0, 'latest_capture': None},
            'commands': {
                'resume_latest': 'python scripts/validate-release.py --out-dir validation/latest --resume',
                'capture_latest': 'python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture',
                'capture_history': 'python scripts/validate-release-capture.py history --pretty',
            },
        },
        'fixture_lab': {
            'latest_smoke_report': {'exists': True, 'summary': {'ok': False, 'error': 'missing worker'}},
            'smoke_capture_history': {'capture_count': 0, 'latest_capture': None},
            'commands': {
                'capture_latest': 'python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture',
                'capture_history': 'python scripts/e2e-fixturelab-capture.py history --pretty',
            },
        },
        'profiles': {
            'triage': {
                'best_profile': {
                    'name': 'main',
                    'tier': 'attach-ready',
                    'score': 91,
                    'attach_ready': True,
                },
                'commands': {},
            },
            'fleet_capture_history': {'capture_count': 0, 'latest_capture': None},
        },
        'playwright': {'available': True, 'extension_launch_plan': {'skip_reason': None}},
        'hints': [],
    }


def _write_record(path: Path, *, surface_key: str, record_status: str, rollout_priority: str, tier: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'''# Support record — {surface_key.title()}\n\n## Metadata\n- **surface key:** `{surface_key}`\n- **record status:** `{record_status}`\n- **default browser lane:** `chromium-live`\n- **last reviewed:** `2026-03-20`\n- **rollout priority:** `{rollout_priority}`\n\n## Scope and assumptions\nTest surface.\n\n## Workflow rows\n\n| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |\n|---|---|---|---|---|---|\n| surface-detect | {tier} | chromium-live | no formal record yet | route drift possible | capture one named support bundle |\n| support-capture | investigated | chromium-live | no formal record yet | bundle schema still being formalized | write first named support bundle |\n\n## Known blockers and risk notes\n- route drift possible\n\n## Next action\n- capture a real support bundle\n''',
        encoding='utf-8',
    )


def test_parse_support_record_reads_metadata_rows_and_next_action(tmp_path: Path) -> None:
    record_path = tmp_path / 'docs' / 'support-records' / 'chatgpt.md'
    _write_record(record_path, surface_key='chatgpt', record_status='seeded', rollout_priority='recommended second adapter', tier='investigated')
    parsed = parse_support_record(record_path)
    assert parsed['surface_key'] == 'chatgpt'
    assert parsed['record_status'] == 'seeded'
    assert parsed['workflow_rows'][0]['workflow'] == 'surface-detect'
    assert parsed['next_action'] == 'capture a real support bundle'


def test_build_control_plane_report_fuses_health_and_support_queue(tmp_path: Path) -> None:
    root = tmp_path
    _write_record(root / 'docs' / 'support-records' / 'claude.md', surface_key='claude', record_status='seeded', rollout_priority='reference adapter', tier='experimental')
    _write_record(root / 'docs' / 'support-records' / 'chatgpt.md', surface_key='chatgpt', record_status='seeded', rollout_priority='recommended second adapter', tier='investigated')
    report = build_control_plane_report(root=root, doctor_report=_doctor_report())
    assert report['health']['best_profile']['name'] == 'main'
    assert report['support']['surface_count'] == 2
    assert report['support']['review_queue'][0]['surface_key'] == 'claude'
    assert report['support']['review_queue'][0]['workflow'] == 'surface-detect'
    assert 'truth_surface_warning_count' in report['health']
    assert 'warnings' in report['truth_surfaces']


def test_capture_control_plane_report_writes_bundle_and_history(tmp_path: Path) -> None:
    root = tmp_path
    _write_record(root / 'docs' / 'support-records' / 'claude.md', surface_key='claude', record_status='seeded', rollout_priority='reference adapter', tier='experimental')
    output_dir = tmp_path / 'validation' / 'latest' / 'control-plane-report-capture'
    history_path = tmp_path / 'validation' / 'control-plane-report-captures.json'
    bundle = capture_control_plane_report(root=root, output_dir=output_dir, history_path=history_path, doctor_report=_doctor_report())
    assert bundle['history_update']['capture_count_after_write'] == 1
    assert (output_dir / 'control-plane-report.json').exists()
    assert (output_dir / 'doctor.json').exists()
    assert (output_dir / 'review-queue.md').exists()
    assert (output_dir / 'support-bundle-queue.md').exists()
    assert (output_dir / 'truth-surface-warnings.md').exists()
    assert (output_dir / 'capture-history.json').exists()
    assert (output_dir / 'capture-diff.json').exists()
    history = summarize_capture_history(history_path)
    assert history['capture_count'] == 1
    saved = json.loads((output_dir / 'control-plane-report.json').read_text(encoding='utf-8'))
    assert saved['support']['surface_count'] == 1


def test_doctor_exposes_control_plane_commands() -> None:
    output = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True))
    assert output['control_plane']['commands']['report'] == 'python scripts/control-plane-report.py --pretty'
    assert any('truth-surface warnings' in hint and 'python scripts/control-plane-report.py --pretty' in hint for hint in output['hints'])
