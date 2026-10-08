from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('validation_artifact_inventory', ROOT / 'scripts' / 'validation_artifact_inventory.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

build_validation_artifact_inventory = MODULE.build_validation_artifact_inventory
capture_validation_artifact_inventory = MODULE.capture_validation_artifact_inventory


def test_build_validation_artifact_inventory_groups_latest_tree(tmp_path: Path) -> None:
    latest = tmp_path / 'validation' / 'latest'
    (latest / 'control-plane-report-capture').mkdir(parents=True, exist_ok=True)
    (latest / 'control-plane-report-capture' / 'control-plane-report.json').write_text('{}\n', encoding='utf-8')
    (latest / 'manual').mkdir(parents=True, exist_ok=True)
    (latest / 'manual' / 'manual_cdp.json').write_text('{}\n', encoding='utf-8')
    (latest / 'steps').mkdir(parents=True, exist_ok=True)
    (latest / 'steps' / 'pytest_cli.stdout.txt').write_text('ok\n', encoding='utf-8')
    (latest / 'semantic-sample').mkdir(parents=True, exist_ok=True)
    (latest / 'semantic-sample' / 'left.json').write_text('{}\n', encoding='utf-8')
    (latest / 'doctor_pretty.json').write_text('{}\n', encoding='utf-8')
    payload = build_validation_artifact_inventory(validation_dir=latest)
    buckets = {item['bucket']: item for item in payload['buckets']}
    assert buckets['capture_bundles']['file_count'] == 1
    assert buckets['manual_and_forensics']['file_count'] == 1
    assert buckets['checks_and_tests']['file_count'] == 1
    assert buckets['fixture_samples_and_indexes']['file_count'] == 1
    assert buckets['status_and_reports']['file_count'] == 1


def test_capture_validation_artifact_inventory_writes_bundle(tmp_path: Path) -> None:
    latest = tmp_path / 'validation' / 'latest'
    latest.mkdir(parents=True, exist_ok=True)
    (latest / 'doctor_pretty.json').write_text('{}\n', encoding='utf-8')
    output_dir = latest / 'validation-artifact-inventory'
    payload = capture_validation_artifact_inventory(output_dir=output_dir, validation_dir=latest)
    assert (output_dir / 'artifact-buckets.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
    assert payload['total_file_count'] == 1
