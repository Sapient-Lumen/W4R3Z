#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKET = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_packet.json'
DEFAULT_EVIDENCE_RECEIPT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_evidence_receipt.json'
DEFAULT_SEED = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_seed.json'
DEFAULT_DECISION_CONTRACT = ROOT / 'artifacts' / 'reports' / 'rematch_decision_contract_snapshot_20260316.json'
DEFAULT_ARTIFACT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_compiled_artifact.json'
DEFAULT_PREFLIGHT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_preflight_receipt.json'
DEFAULT_BUNDLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
DEFAULT_AUDIT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_spine_audit_receipt.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_retention_exit_receipt.schema.json'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _sha256_json(node: Any) -> str:
    return _sha256_bytes(json.dumps(node, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))


def _render_bytes(node: Any) -> bytes:
    return (json.dumps(node, indent=2, sort_keys=True) + '\n').encode('utf-8')


def _relativize(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def build_retention_exit_receipt(
    *,
    packet: dict[str, Any],
    evidence_receipt: dict[str, Any],
    seed: dict[str, Any],
    decision_contract: dict[str, Any],
    compiled_artifact: dict[str, Any],
    preflight_receipt: dict[str, Any],
    bundle_receipt: dict[str, Any],
    audit_receipt: dict[str, Any],
    packet_path: Path,
    evidence_receipt_path: Path,
    seed_path: Path,
    decision_contract_path: Path,
    compiled_artifact_path: Path,
    preflight_receipt_path: Path,
    bundle_receipt_path: Path,
    audit_receipt_path: Path,
) -> dict[str, Any]:
    retained_objects = [
        ('evidence_packet', packet_path, packet),
        ('evidence_receipt', evidence_receipt_path, evidence_receipt),
        ('compiled_benchmark_artifact', compiled_artifact_path, compiled_artifact),
        ('preflight_receipt', preflight_receipt_path, preflight_receipt),
        ('publication_bundle_receipt', bundle_receipt_path, bundle_receipt),
        ('publication_spine_audit_receipt', audit_receipt_path, audit_receipt),
    ]
    durable_retained_objects = [
        {
            'label': label,
            'path': _relativize(path),
            'byte_count': len(_render_bytes(node)),
            'sha256': _sha256_json(node),
            'retention_class': 'durable_retained',
        }
        for label, path, node in retained_objects
    ]

    scratch_hashes_match_receipt_now = True
    scratch_exit_objects: list[dict[str, Any]] = []
    for source in evidence_receipt.get('scratch_sources', []):
        scratch_path = ROOT / source['scratch_path']
        exists_now = scratch_path.exists()
        sha256 = source['sha256']
        byte_count = int(source['byte_count'])
        if exists_now:
            sha256_now = _sha256_bytes(scratch_path.read_bytes())
            scratch_hashes_match_receipt_now = scratch_hashes_match_receipt_now and sha256_now == sha256
        else:
            scratch_hashes_match_receipt_now = False
        scratch_exit_objects.append(
            {
                'label': f"scratch_source:{source['label']}",
                'path': source['scratch_path'],
                'byte_count': byte_count,
                'sha256': sha256,
                'retention_class': 'scratch_exit_candidate',
                'exit_ready': False,
            }
        )

    patch_info = bundle_receipt['transient_patch']
    exit_ready_transient_objects = [
        {
            'label': 'compiled_fill_patch',
            'path': patch_info.get('patch_output_path'),
            'byte_count': int(patch_info['byte_count']),
            'sha256': patch_info['patch_sha256'],
            'retention_class': 'reconstructible_intermediate',
            'exit_ready': False,
        },
        *scratch_exit_objects,
    ]

    evidence_receipt_strict_coverage_passed = bool(evidence_receipt.get('strict_coverage_passed'))
    bundle_patch_elision_ready = bool(bundle_receipt.get('patch_elision_ready'))
    publication_spine_ready = bool(audit_receipt.get('publication_spine_ready'))
    retained_preflight_ready = bool(preflight_receipt.get('preflight_ready'))
    retention_exit_ready = bool(
        evidence_receipt_strict_coverage_passed
        and bundle_patch_elision_ready
        and publication_spine_ready
        and retained_preflight_ready
        and scratch_hashes_match_receipt_now
    )

    for row in exit_ready_transient_objects:
        row['exit_ready'] = retention_exit_ready

    durable_publication_spine_bytes = int(audit_receipt['retained_bytes']['durable_spine_bytes'])
    retained_publication_set_bytes = sum(int(row['byte_count']) for row in durable_retained_objects)
    transient_exit_bytes = sum(int(row['byte_count']) for row in exit_ready_transient_objects)
    full_publication_lifecycle_bytes = retained_publication_set_bytes + transient_exit_bytes
    transient_exit_share = round(transient_exit_bytes / full_publication_lifecycle_bytes, 6) if full_publication_lifecycle_bytes else 0.0

    if retention_exit_ready:
        recommended_next_move = (
            'Retain the packet, evidence receipt, compiled artifact, preflight receipt, bundle receipt, and spine-audit receipt; the compiled fill patch and hashed scratch sources may now leave the long-term archive.'
        )
    else:
        recommended_next_move = (
            'Do not drop scratch or the compiled fill patch yet; first restore packet provenance, rebuild stability, and publication readiness until the exit conditions all pass.'
        )

    return {
        'snapshot_date': '2026-03-17',
        'receipt_version': '2026-03-17.rematch_world_benchmark_retention_exit_receipt.v1',
        'analysis_script': 'scripts/tools/build_rematch_world_benchmark_retention_exit_receipt.py',
        'focus': 'mark the exact rematch-world publication objects that must stay durable versus the scratch and intermediate objects that may exit once provenance, preflight, and rebuild audit all pass',
        'packet_path': _relativize(packet_path),
        'evidence_receipt_path': _relativize(evidence_receipt_path),
        'seed_path': _relativize(seed_path),
        'decision_contract_path': _relativize(decision_contract_path),
        'compiled_artifact_path': _relativize(compiled_artifact_path),
        'preflight_receipt_path': _relativize(preflight_receipt_path),
        'bundle_receipt_path': _relativize(bundle_receipt_path),
        'audit_receipt_path': _relativize(audit_receipt_path),
        'durable_retained_objects': durable_retained_objects,
        'exit_ready_transient_objects': exit_ready_transient_objects,
        'exit_conditions': {
            'evidence_receipt_strict_coverage_passed': evidence_receipt_strict_coverage_passed,
            'bundle_patch_elision_ready': bundle_patch_elision_ready,
            'publication_spine_ready': publication_spine_ready,
            'retained_preflight_ready': retained_preflight_ready,
            'scratch_hashes_match_receipt_now': scratch_hashes_match_receipt_now,
            'retention_exit_ready': retention_exit_ready,
        },
        'retained_byte_totals': {
            'durable_publication_spine_bytes': durable_publication_spine_bytes,
            'retained_publication_set_bytes': retained_publication_set_bytes,
            'transient_exit_bytes': transient_exit_bytes,
            'transient_exit_share_of_publication_lifecycle': transient_exit_share,
        },
        'recommended_next_move': recommended_next_move,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a compact retention-exit receipt for the rematch-world publication spine.')
    parser.add_argument('--packet', default=str(DEFAULT_PACKET), help='Path to the evidence packet JSON.')
    parser.add_argument('--evidence-receipt', default=str(DEFAULT_EVIDENCE_RECEIPT), help='Path to the evidence receipt JSON.')
    parser.add_argument('--seed', default=str(DEFAULT_SEED), help='Path to the standing seed JSON.')
    parser.add_argument('--decision-contract', default=str(DEFAULT_DECISION_CONTRACT), help='Path to the standing decision contract JSON.')
    parser.add_argument('--artifact', default=str(DEFAULT_ARTIFACT), help='Path to the compiled benchmark artifact JSON.')
    parser.add_argument('--preflight', default=str(DEFAULT_PREFLIGHT), help='Path to the preflight receipt JSON.')
    parser.add_argument('--bundle', default=str(DEFAULT_BUNDLE), help='Path to the publication-bundle receipt JSON.')
    parser.add_argument('--audit', default=str(DEFAULT_AUDIT), help='Path to the publication-spine audit receipt JSON.')
    parser.add_argument('--output', help='Write the retention-exit receipt to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit a compact summary instead of the full receipt.')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero unless the retention exit conditions all pass.')
    args = parser.parse_args()

    def resolve(raw: str) -> Path:
        path = Path(raw)
        return path.resolve() if path.is_absolute() else (ROOT / path).resolve()

    packet_path = resolve(args.packet)
    evidence_receipt_path = resolve(args.evidence_receipt)
    seed_path = resolve(args.seed)
    decision_contract_path = resolve(args.decision_contract)
    artifact_path = resolve(args.artifact)
    preflight_path = resolve(args.preflight)
    bundle_path = resolve(args.bundle)
    audit_path = resolve(args.audit)

    receipt = build_retention_exit_receipt(
        packet=load_json(packet_path),
        evidence_receipt=load_json(evidence_receipt_path),
        seed=load_json(seed_path),
        decision_contract=load_json(decision_contract_path),
        compiled_artifact=load_json(artifact_path),
        preflight_receipt=load_json(preflight_path),
        bundle_receipt=load_json(bundle_path),
        audit_receipt=load_json(audit_path),
        packet_path=packet_path,
        evidence_receipt_path=evidence_receipt_path,
        seed_path=seed_path,
        decision_contract_path=decision_contract_path,
        compiled_artifact_path=artifact_path,
        preflight_receipt_path=preflight_path,
        bundle_receipt_path=bundle_path,
        audit_receipt_path=audit_path,
    )

    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)

    if args.strict and not receipt['exit_conditions']['retention_exit_ready']:
        print('rematch-world-benchmark-retention-exit: retention exit conditions not yet satisfied', flush=True)
        return 1

    if args.summary_json:
        summary = {
            'retention_exit_ready': receipt['exit_conditions']['retention_exit_ready'],
            'retained_publication_set_bytes': receipt['retained_byte_totals']['retained_publication_set_bytes'],
            'transient_exit_bytes': receipt['retained_byte_totals']['transient_exit_bytes'],
            'transient_exit_share_of_publication_lifecycle': receipt['retained_byte_totals']['transient_exit_share_of_publication_lifecycle'],
            'durable_object_count': len(receipt['durable_retained_objects']),
            'transient_object_count': len(receipt['exit_ready_transient_objects']),
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.output:
        output_path = resolve(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
        print(
            'rematch-world-benchmark-retention-exit: '
            f'wrote {_relativize(output_path)} (retention_exit_ready={str(receipt["exit_conditions"]["retention_exit_ready"]).lower()})'
        )
    else:
        print(rendered, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
