#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKET = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
DEFAULT_EVIDENCE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
DEFAULT_SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DEFAULT_DECISION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_publication_bundle_receipt.schema.json'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _sha256_json(node: Any) -> str:
    return _sha256_bytes(json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))


def _relativize(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def _rendered_bytes(node: Any) -> int:
    return len((json.dumps(node, indent=2, sort_keys=True) + '\n').encode('utf-8'))


def _build_decision_emission(candidate: dict[str, Any], decision_contract: dict[str, Any], decision_contract_sha256: str) -> dict[str, Any]:
    bundle = candidate['compact_decision_bundle']
    emitted_sections = []
    for section_name in ['delay_contract', 'winner_contract', 'delta_contract']:
        question_ids = [
            row['question_id']
            for row in decision_contract['question_coverage']
            if row['contract_section'] == section_name
        ]
        emitted_sections.append(
            {
                'section': section_name,
                'question_ids': question_ids,
                'question_id_count': len(question_ids),
            }
        )

    allowed_open_interval_count = sum(
        1
        for row in bundle['delay_contract']['extortion_rows']
        for interval in row['predicted_nonnegative_delay_winner_intervals']
        if interval['end_delay'] is None
    )

    emitted_question_ids = [row['question_id'] for row in decision_contract['question_coverage']]
    return {
        'phase': 'SG-003.phase3_world_emission',
        'world_emission_ready': bool(bundle == decision_contract),
        'copied_bundle_sha256': _sha256_json(bundle),
        'standing_contract_sha256': decision_contract_sha256,
        'bundle_matches_standing_contract': bool(bundle == decision_contract),
        'emitted_sections': emitted_sections,
        'emitted_question_ids': emitted_question_ids,
        'emitted_question_id_count': len(emitted_question_ids),
        'allowed_open_interval_count': allowed_open_interval_count,
    }


def build_bundle_receipt(
    packet: dict[str, Any],
    evidence_receipt: dict[str, Any],
    seed: dict[str, Any],
    decision_contract: dict[str, Any],
    packet_path: Path,
    evidence_receipt_path: Path,
    seed_path: Path,
    decision_contract_path: Path,
    artifact_output_path: Path | None,
    patch_output_path: Path | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    compiler = _load_module(
        'compile_rematch_world_benchmark_fill_patch_from_evidence_packet',
        ROOT / 'scripts' / 'tools' / 'compile_rematch_world_benchmark_fill_patch_from_evidence_packet.py',
    )
    applier = _load_module(
        'apply_rematch_world_benchmark_fill_patch',
        ROOT / 'scripts' / 'tools' / 'apply_rematch_world_benchmark_fill_patch.py',
    )
    preflight = _load_module(
        'rematch_world_benchmark_publication_preflight',
        ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_publication_preflight.py',
    )

    patch = compiler.build_fill_patch(packet)
    candidate = applier.build_candidate_from_patch(patch, seed)
    preflight_summary = preflight.build_preflight_summary(
        candidate=candidate,
        seed=seed,
        decision_contract=decision_contract,
        inspection_mode='artifact' if artifact_output_path else 'patch_compile',
        inspection_target_path=_relativize(artifact_output_path) or _relativize(packet_path) or str(packet_path),
        seed_path=_relativize(seed_path) or str(seed_path),
        decision_contract_path=_relativize(decision_contract_path) or str(decision_contract_path),
    )

    packet_sha256 = _sha256_json(packet)
    evidence_receipt_sha256 = _sha256_json(evidence_receipt)
    seed_sha256 = _sha256_json(seed)
    decision_contract_sha256 = _sha256_json(decision_contract)
    patch_sha256 = _sha256_json(patch)
    candidate_sha256 = _sha256_json(candidate)

    evidence_receipt_matches_packet = (
        evidence_receipt.get('packet_sha256') == packet_sha256
        and evidence_receipt.get('source_run_label') == packet.get('source_run_label')
    )
    evidence_receipt_strict_coverage_passed = bool(evidence_receipt.get('strict_coverage_passed'))
    patch_elision_ready = bool(
        evidence_receipt_matches_packet
        and evidence_receipt_strict_coverage_passed
        and preflight_summary['preflight_ready']
        and preflight_summary['decision_bundle_digest_matches_contract']
    )
    patch_retention_required = not patch_elision_ready

    if artifact_output_path is not None:
        artifact_output_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_output_path.write_text(json.dumps(candidate, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if patch_output_path is not None:
        patch_output_path.parent.mkdir(parents=True, exist_ok=True)
        patch_output_path.write_text(json.dumps(patch, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    decision_emission = _build_decision_emission(candidate, decision_contract, decision_contract_sha256)

    if patch_elision_ready:
        recommended_next_move = (
            'Retain the evidence packet, evidence receipt, compiled benchmark artifact, and preflight receipt; let the compiled fill patch remain scratch-only because it is reproducible from the retained packet, and cite this bundle receipt as the compact proof that the first retained benchmark really emits the copied phase-3 decision contract.'
        )
    else:
        recommended_next_move = (
            'Do not elide the compiled fill patch yet; first repair packet provenance or benchmark readiness until the publication bundle is fully reproducible, preflight-ready, and explicit about phase-3 decision emission.'
        )

    receipt = {
        'snapshot_date': '2026-03-17',
        'focus': 'collapse the packet-to-patch-to-preflight chain into one publication bundle receipt so the compiled fill patch can stay scratch-only after a real rematch-world run',
        'receipt_version': '2026-03-17.rematch_world_benchmark_publication_bundle_receipt.v1',
        'analysis_script': 'scripts/tools/build_rematch_world_benchmark_publication_bundle_receipt.py',
        'packet_path': _relativize(packet_path) or str(packet_path),
        'packet_sha256': packet_sha256,
        'packet_source_run_label': packet['source_run_label'],
        'evidence_receipt_path': _relativize(evidence_receipt_path) or str(evidence_receipt_path),
        'evidence_receipt_sha256': evidence_receipt_sha256,
        'evidence_receipt_matches_packet': evidence_receipt_matches_packet,
        'evidence_receipt_strict_coverage_passed': evidence_receipt_strict_coverage_passed,
        'seed_path': _relativize(seed_path) or str(seed_path),
        'seed_sha256': seed_sha256,
        'decision_contract_path': _relativize(decision_contract_path) or str(decision_contract_path),
        'decision_contract_sha256': decision_contract_sha256,
        'transient_patch': {
            'byte_count': _rendered_bytes(patch),
            'patch_sha256': patch_sha256,
            'patch_output_path': _relativize(patch_output_path),
        },
        'compiled_candidate': {
            'artifact_state': candidate.get('artifact_state'),
            'artifact_sha256': candidate_sha256,
            'artifact_output_path': _relativize(artifact_output_path),
            'byte_count': _rendered_bytes(candidate),
        },
        'decision_emission': decision_emission,
        'patch_written': patch_output_path is not None,
        'artifact_written': artifact_output_path is not None,
        'patch_elision_ready': patch_elision_ready,
        'patch_retention_required': patch_retention_required,
        'preflight': {
            'preflight_ready': bool(preflight_summary['preflight_ready']),
            'mutation_surface_ok': bool(preflight_summary['mutation_surface_ok']),
            'decision_bundle_digest_matches_contract': bool(preflight_summary['decision_bundle_digest_matches_contract']),
            'blocking_fill_slot_count': int(preflight_summary['status_counts']['blocking_fill_slot_count']),
            'forbidden_changed_path_count': int(preflight_summary['status_counts']['forbidden_changed_path_count']),
            'allowed_decision_null_count': int(preflight_summary['status_counts']['allowed_decision_null_count']),
            'filled_world_section_count': int(preflight_summary['status_counts']['filled_world_section_count']),
            'template_blocker_count': int(preflight_summary['status_counts']['template_blocker_count']),
        },
        'recommended_retained_objects': [
            'evidence_packet',
            'evidence_receipt',
            'compiled_benchmark_artifact',
            'preflight_receipt',
        ],
        'recommended_next_move': recommended_next_move,
    }
    return receipt, patch, candidate


def main() -> int:
    parser = argparse.ArgumentParser(description='Build one publication-bundle receipt from a rematch-world evidence packet and provenance receipt, optionally writing the compiled artifact while leaving the patch transient.')
    parser.add_argument('packet', nargs='?', default=str(DEFAULT_PACKET), help='Path to the rematch-world evidence packet JSON.')
    parser.add_argument('--evidence-receipt', default=str(DEFAULT_EVIDENCE_RECEIPT), help='Path to the rematch-world evidence receipt JSON.')
    parser.add_argument('--seed', default=str(DEFAULT_SEED), help='Path to the standing rematch-world benchmark seed JSON.')
    parser.add_argument('--decision-contract', default=str(DEFAULT_DECISION_CONTRACT), help='Path to the standing compact decision contract JSON.')
    parser.add_argument('--artifact-output', help='Optional path to write the compiled benchmark artifact.')
    parser.add_argument('--patch-output', help='Optional path to write the compiled fill patch. Omit to keep the patch transient.')
    parser.add_argument('--output', help='Write the publication-bundle receipt to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit only a compact summary instead of the full receipt.')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero unless the packet provenance and compiled benchmark are ready for patch elision.')
    args = parser.parse_args()

    packet_path = Path(args.packet)
    evidence_receipt_path = Path(args.evidence_receipt)
    seed_path = Path(args.seed)
    decision_contract_path = Path(args.decision_contract)
    artifact_output_path = Path(args.artifact_output).resolve() if args.artifact_output else None
    patch_output_path = Path(args.patch_output).resolve() if args.patch_output else None

    if not packet_path.is_absolute():
        packet_path = (ROOT / packet_path).resolve()
    if not evidence_receipt_path.is_absolute():
        evidence_receipt_path = (ROOT / evidence_receipt_path).resolve()
    if not seed_path.is_absolute():
        seed_path = (ROOT / seed_path).resolve()
    if not decision_contract_path.is_absolute():
        decision_contract_path = (ROOT / decision_contract_path).resolve()

    packet = load_json(packet_path)
    evidence_receipt = load_json(evidence_receipt_path)
    seed = load_json(seed_path)
    decision_contract = load_json(decision_contract_path)

    receipt, _patch, _candidate = build_bundle_receipt(
        packet=packet,
        evidence_receipt=evidence_receipt,
        seed=seed,
        decision_contract=decision_contract,
        packet_path=packet_path,
        evidence_receipt_path=evidence_receipt_path,
        seed_path=seed_path,
        decision_contract_path=decision_contract_path,
        artifact_output_path=artifact_output_path,
        patch_output_path=patch_output_path,
    )

    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)

    if args.summary_json:
        summary = {
            'packet_sha256': receipt['packet_sha256'],
            'packet_source_run_label': receipt['packet_source_run_label'],
            'evidence_receipt_matches_packet': receipt['evidence_receipt_matches_packet'],
            'evidence_receipt_strict_coverage_passed': receipt['evidence_receipt_strict_coverage_passed'],
            'patch_elision_ready': receipt['patch_elision_ready'],
            'patch_retention_required': receipt['patch_retention_required'],
            'patch_written': receipt['patch_written'],
            'artifact_written': receipt['artifact_written'],
            'transient_patch_byte_count': receipt['transient_patch']['byte_count'],
            'compiled_candidate_byte_count': receipt['compiled_candidate']['byte_count'],
            'decision_world_emission_ready': receipt['decision_emission']['world_emission_ready'],
            'decision_emitted_question_id_count': receipt['decision_emission']['emitted_question_id_count'],
            'preflight_ready': receipt['preflight']['preflight_ready'],
            'blocking_fill_slot_count': receipt['preflight']['blocking_fill_slot_count'],
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
        if args.output:
            output_path = Path(args.output)
            if not output_path.is_absolute():
                output_path = (ROOT / output_path).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered, encoding='utf-8')
            print(
                'rematch-world-benchmark-publication-bundle: '
                f'wrote {_relativize(output_path)} (patch_elision_ready={str(receipt["patch_elision_ready"]).lower()}, '
                f'patch_written={str(receipt["patch_written"]).lower()}, artifact_written={str(receipt["artifact_written"]).lower()})'
            )
        else:
            print(rendered, end='')

    if args.strict and not receipt['patch_elision_ready']:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
