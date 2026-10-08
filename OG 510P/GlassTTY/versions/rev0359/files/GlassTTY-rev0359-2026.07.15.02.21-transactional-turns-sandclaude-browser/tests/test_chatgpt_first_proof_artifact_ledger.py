from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('chatgpt_first_proof_artifact_ledger', ROOT / 'scripts' / 'chatgpt_first_proof_artifact_ledger.py')
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

ARTIFACT_SLOTS = MODULE.ARTIFACT_SLOTS
build_artifact_ledger = MODULE.build_artifact_ledger
artifact_registry = MODULE.artifact_registry
summary_markdown = MODULE.summary_markdown
write_artifact_ledger = MODULE.write_artifact_ledger

ATTEMPT_ID = 'chatgpt-proof-attempt-001'


def _write_slot_file(pack_dir: Path, slot: object, *, attempt_id: str = ATTEMPT_ID) -> None:
    path = pack_dir / slot.filename
    path.parent.mkdir(parents=True, exist_ok=True)
    if slot.artifact_type == 'json':
        path.write_text(json.dumps({'attempt_id': attempt_id, 'slot': slot.filename}, indent=2) + '\n', encoding='utf-8')
    elif slot.artifact_type == 'image':
        path.write_bytes(b'\x89PNG\r\n\x1a\nminimal-local-placeholder')
    else:
        path.write_text(f'{slot.filename}\nattempt_id={attempt_id}\n', encoding='utf-8')


def _seed_pack(pack_dir: Path, *, readiness_level: str = 'evaluator-ready') -> None:
    required = set(MODULE._required_phases_for(readiness_level))
    for slot in ARTIFACT_SLOTS:
        if slot.required_for in required:
            _write_slot_file(pack_dir, slot)


def test_artifact_registry_matches_runbook_and_evidence_pack_readme() -> None:
    filenames = [slot['filename'] for slot in artifact_registry()]
    runbook = (ROOT / 'docs' / 'chatgpt-first-proof-runbook.md').read_text(encoding='utf-8')
    evidence_readme = (ROOT / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack' / 'README.md').read_text(encoding='utf-8')

    assert len(filenames) == 30
    assert len(filenames) == len(set(filenames))
    for filename in filenames:
        assert filename in runbook
        assert filename in evidence_readme


def test_artifact_ledger_reports_missing_pack_without_public_claim(tmp_path: Path) -> None:
    pack_dir = tmp_path / 'pack'

    ledger = build_artifact_ledger(pack_dir, readiness_level='evaluator-ready')

    assert ledger['schema_version'] == 1
    assert ledger['ready'] is False
    assert ledger['counts']['present_count'] == 0
    assert 'route-witness.json' in ledger['missing_required_files']
    assert 'bundle-manifest.json' in ledger['missing_required_files']
    assert ledger['attempt_id_consistency']['ok'] is True
    assert ledger['support_claim_effect'].startswith('none;')


def test_artifact_ledger_accepts_evaluator_ready_pack_with_one_attempt_id(tmp_path: Path) -> None:
    pack_dir = tmp_path / 'pack'
    _seed_pack(pack_dir, readiness_level='evaluator-ready')

    ledger = build_artifact_ledger(pack_dir, readiness_level='evaluator-ready')

    assert ledger['ready'] is True
    assert ledger['missing_required_files'] == []
    assert ledger['invalid_json_files'] == []
    assert ledger['attempt_id_consistency']['canonical_attempt_id'] == ATTEMPT_ID
    assert ledger['counts']['selected_required_present_count'] == ledger['counts']['selected_required_count']
    assert summary_markdown(ledger).startswith('# ChatGPT first-proof artifact ledger')


def test_artifact_ledger_blocks_attempt_id_drift(tmp_path: Path) -> None:
    pack_dir = tmp_path / 'pack'
    _seed_pack(pack_dir, readiness_level='evaluator-ready')
    (pack_dir / 'submit-evidence.json').write_text(json.dumps({'attempt_id': 'other-attempt'}, indent=2) + '\n', encoding='utf-8')

    ledger = build_artifact_ledger(pack_dir, readiness_level='evaluator-ready')

    assert ledger['ready'] is False
    assert ledger['attempt_id_consistency']['ok'] is False
    assert ledger['attempt_id_consistency']['observed_attempt_ids'] == [ATTEMPT_ID, 'other-attempt']


def test_write_artifact_ledger_writes_json_and_summary(tmp_path: Path) -> None:
    pack_dir = tmp_path / 'pack'
    output_dir = tmp_path / 'ledger-output'
    _seed_pack(pack_dir, readiness_level='capture-ready')

    ledger = write_artifact_ledger(pack_dir, output_dir=output_dir, readiness_level='capture-ready')

    assert ledger['ready'] is True
    assert (output_dir / 'chatgpt-first-proof-artifact-ledger.json').exists()
    assert (output_dir / 'SUMMARY.md').exists()
