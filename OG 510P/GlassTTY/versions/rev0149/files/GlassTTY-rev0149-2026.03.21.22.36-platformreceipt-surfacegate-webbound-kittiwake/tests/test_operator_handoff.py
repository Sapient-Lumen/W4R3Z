from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_SPEC = importlib.util.spec_from_file_location('operator_handoff_script', ROOT / 'scripts' / 'operator_handoff.py')
assert MODULE_SPEC and MODULE_SPEC.loader
MODULE = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(MODULE)

build_operator_handoff = MODULE.build_operator_handoff
capture_operator_handoff = MODULE.capture_operator_handoff
summarize_capture_history = MODULE.summarize_capture_history


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _seed_root(root: Path) -> dict[str, Path]:
    for rel in [
        'README.md',
        'ROADMAP.md',
        'PROJECT_MAP.md',
        'STATUS.md',
        'TASKS.md',
        'DECISIONS.md',
        'MEMORY.md',
        '.llm/README.md',
        '.llm/SESSION_START.md',
        '.llm/SESSION_END.md',
        '.llm/WORKLOG.jsonl',
        'docs/handoff-rev0106-2026-03-18.md',
    ]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f'{rel}\n', encoding='utf-8')

    validation_dir = root / 'validation' / 'latest'
    (validation_dir / 'steps').mkdir(parents=True, exist_ok=True)
    (validation_dir / 'report.json').write_text(json.dumps({'ok': False, 'complete': False}, indent=2) + '\n', encoding='utf-8')
    (validation_dir / 'SUMMARY.md').write_text('# partial\n', encoding='utf-8')
    (validation_dir / 'current_step.json').write_text(json.dumps({'name': 'pytest_cli'}) + '\n', encoding='utf-8')
    (validation_dir / 'steps' / 'pytest_cli.stdout.txt').write_text('stdout\n', encoding='utf-8')

    smoke_report = root / 'validation' / 'latest' / 'e2e-fixturelab.json'
    smoke_report.write_text(json.dumps({'ok': True}, indent=2) + '\n', encoding='utf-8')

    profile_dir = root / 'profiles' / 'main'
    profile_dir.mkdir(parents=True, exist_ok=True)
    (profile_dir / 'glasstty-profile.json').write_text(json.dumps({'name': 'main'}, indent=2) + '\n', encoding='utf-8')
    (profile_dir / 'glasstty-native-host.json').write_text(json.dumps({'target': 'chromium'}, indent=2) + '\n', encoding='utf-8')
    (profile_dir / 'DevToolsActivePort').write_text('127.0.0.1\n9222\n', encoding='utf-8')
    (profile_dir / 'glasstty-profile-captures.json').write_text(json.dumps({'entries': []}, indent=2) + '\n', encoding='utf-8')

    readiness_capture_dir = root / 'validation' / 'latest' / 'readiness-report-capture'
    readiness_capture_dir.mkdir(parents=True, exist_ok=True)
    (readiness_capture_dir / 'SUMMARY.md').write_text('# readiness\n', encoding='utf-8')
    _write_json(root / 'validation' / 'readiness-report-captures.json', {
        'schema_version': 1,
        'capture_count': 1,
        'entries': [
            {'captured_at': '2026-03-18T00:00:00Z', 'output_dir': str(readiness_capture_dir)}
        ],
    })

    validation_capture_dir = root / 'validation' / 'latest' / 'validate-release-capture'
    validation_capture_dir.mkdir(parents=True, exist_ok=True)
    (validation_capture_dir / 'SUMMARY.md').write_text('# validate\n', encoding='utf-8')
    _write_json(root / 'validation' / 'validate-release-captures.json', {
        'schema_version': 1,
        'capture_count': 1,
        'entries': [
            {'captured_at': '2026-03-18T00:00:00Z', 'output_dir': str(validation_capture_dir)}
        ],
    })

    smoke_capture_dir = root / 'validation' / 'latest' / 'e2e-fixturelab-capture'
    smoke_capture_dir.mkdir(parents=True, exist_ok=True)
    (smoke_capture_dir / 'SUMMARY.md').write_text('# smoke\n', encoding='utf-8')
    _write_json(root / 'validation' / 'e2e-fixturelab-captures.json', {
        'schema_version': 1,
        'capture_count': 1,
        'entries': [
            {'captured_at': '2026-03-18T00:00:00Z', 'output_dir': str(smoke_capture_dir)}
        ],
    })

    fleet_capture_dir = root / 'validation' / 'latest' / 'profile-fleet-capture'
    fleet_capture_dir.mkdir(parents=True, exist_ok=True)
    (fleet_capture_dir / 'SUMMARY.md').write_text('# fleet\n', encoding='utf-8')
    _write_json(root / 'profiles' / 'glasstty-profile-fleet-captures.json', {
        'schema_version': 1,
        'capture_count': 1,
        'entries': [
            {'captured_at': '2026-03-18T00:00:00Z', 'output_dir': str(fleet_capture_dir)}
        ],
    })

    return {
        'validation_dir': validation_dir,
        'smoke_report': smoke_report,
        'profile_dir': profile_dir,
        'validation_capture_dir': validation_capture_dir,
        'smoke_capture_dir': smoke_capture_dir,
        'fleet_capture_dir': fleet_capture_dir,
        'readiness_capture_dir': readiness_capture_dir,
    }


def _doctor_report(root: Path, seeded: dict[str, Path], *, validation_complete: bool = False) -> dict:
    validation_summary = {
        'path': str(seeded['validation_dir'] / 'report.json'),
        'complete': validation_complete,
        'running_step_name': None if validation_complete else 'pytest_cli',
        'required_failed_step': None if validation_complete else 'pytest_cli',
        'latest_completed_step': 'extension_typecheck',
    }
    return {
        'project': 'GlassTTY',
        'root': str(root),
        'validation': {
            'latest_report': {'exists': True, 'path': str(seeded['validation_dir'] / 'report.json'), 'summary': validation_summary},
            'capture_history': {
                'path': str(root / 'validation' / 'validate-release-captures.json'),
                'capture_count': 1,
                'latest_capture': {'output_dir': str(seeded['validation_capture_dir'])},
            },
            'commands': {
                'resume_latest': 'python scripts/validate-release.py --out-dir validation/latest --resume',
                'capture_latest': 'python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture',
            },
        },
        'fixture_lab': {
            'latest_smoke_report': {
                'exists': True,
                'path': str(seeded['smoke_report']),
                'summary': {'report_timestamp': '2026-03-18T00:00:00Z', 'ok': True},
            },
            'smoke_capture_history': {
                'path': str(root / 'validation' / 'e2e-fixturelab-captures.json'),
                'capture_count': 1,
                'latest_capture': {'output_dir': str(seeded['smoke_capture_dir'])},
            },
            'commands': {'capture_latest': 'python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture'},
        },
        'profiles': {
            'triage': {
                'best_profile': {
                    'name': 'main',
                    'path': str(seeded['profile_dir']),
                    'tier': 'attach-ready',
                    'score': 95,
                    'attach_ready': True,
                    'next_command': './scripts/glasstty-profile.sh resume-proof main',
                    'commands': {'resume_proof': './scripts/glasstty-profile.sh resume-proof main'},
                },
                'commands': {
                    'triage': './scripts/glasstty-profile.sh triage --pretty',
                    'fleet_capture': './scripts/glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture',
                },
            },
            'fleet_capture_history': {
                'path': str(root / 'profiles' / 'glasstty-profile-fleet-captures.json'),
                'capture_count': 1,
                'latest_capture': {'output_dir': str(seeded['fleet_capture_dir'])},
            },
        },
        'playwright': {'extension_launch_plan': {'skip_reason': None}},
        'hints': [],
    }


def test_build_operator_handoff_collects_artifacts_and_primary_command(tmp_path: Path) -> None:
    seeded = _seed_root(tmp_path)
    report = build_operator_handoff(doctor_report=_doctor_report(tmp_path, seeded), root=tmp_path)
    assert report['readiness']['primary_next_kind'] == 'resume_validate_release'
    labels = {item['label'] for item in report['artifact_inventory']}
    assert 'validation:latest-report' in labels
    assert 'smoke:latest-report' in labels
    assert 'profiles:best-profile-metadata' in labels
    assert 'readiness:capture-history' in labels
    assert 'install-receipt:history' in labels
    assert 'support-surface:history' in labels
    assert 'docs:latest-handoff' in labels
    validation_artifact = next(item for item in report['artifact_inventory'] if item['label'] == 'validation:latest-report')
    assert validation_artifact['exists'] is True


def test_capture_operator_handoff_writes_bundle_history_diff_and_copies_artifacts(tmp_path: Path) -> None:
    seeded = _seed_root(tmp_path)
    output_dir = tmp_path / 'validation' / 'latest' / 'operator-handoff'
    history_path = tmp_path / 'validation' / 'operator-handoff-captures.json'

    bundle1 = capture_operator_handoff(output_dir=output_dir, history_path=history_path, doctor_report=_doctor_report(tmp_path, seeded), root=tmp_path)
    assert bundle1['bundle_summary']['primary_next_kind'] == 'resume_validate_release'
    assert (output_dir / 'doctor.json').exists()
    assert (output_dir / 'readiness-report.json').exists()
    assert (output_dir / 'artifact-index.json').exists()
    assert (output_dir / 'capture-history.json').exists()
    assert (output_dir / 'capture-diff.json').exists()
    assert (output_dir / 'artifacts' / 'validation' / 'latest' / 'report.json').exists()

    bundle2 = capture_operator_handoff(output_dir=output_dir, history_path=history_path, doctor_report=_doctor_report(tmp_path, seeded, validation_complete=True), root=tmp_path)
    diff = json.loads((output_dir / 'capture-diff.json').read_text(encoding='utf-8'))
    history = summarize_capture_history(history_path)
    assert bundle2['bundle_summary']['readiness_grade'] == 'live-lane-ready'
    assert 'readiness_grade' in diff['changed_fields']
    assert history['capture_count'] == 2


def test_doctor_exposes_operator_handoff_commands_and_hint() -> None:
    output = json.loads(subprocess.check_output([sys.executable, str(ROOT / 'scripts' / 'doctor.py')], text=True))
    assert output['operator_handoff']['commands']['capture_latest'] == 'python scripts/operator-handoff.py capture --output-dir validation/latest/operator-handoff'
    assert any('durable operator handoff bundle' in hint and 'python scripts/operator-handoff.py capture --output-dir validation/latest/operator-handoff' in hint for hint in output['hints'])
