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
DEFAULT_ARTIFACT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_compiled_artifact.json'
DEFAULT_PREFLIGHT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_preflight_receipt.json'
DEFAULT_BUNDLE = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_bundle_receipt.json'
SCHEMA_PATH = ROOT / 'schemas' / 'rematch_world_benchmark_publication_spine_audit.schema.json'


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


def _relativize(path: Path) -> str:
    resolved = path.resolve()
    return resolved.relative_to(ROOT).as_posix() if resolved.is_relative_to(ROOT) else str(path)


def _render_bytes(node: Any) -> bytes:
    return (json.dumps(node, indent=2, sort_keys=True) + '\n').encode('utf-8')


def build_audit_receipt(
    packet: dict[str, Any],
    evidence_receipt: dict[str, Any],
    seed: dict[str, Any],
    decision_contract: dict[str, Any],
    compiled_artifact: dict[str, Any],
    preflight_receipt: dict[str, Any],
    bundle_receipt: dict[str, Any],
    packet_path: Path,
    evidence_receipt_path: Path,
    seed_path: Path,
    decision_contract_path: Path,
    compiled_artifact_path: Path,
    preflight_receipt_path: Path,
    bundle_receipt_path: Path,
) -> dict[str, Any]:
    bundle_tool = _load_module(
        'build_rematch_world_benchmark_publication_bundle_receipt',
        ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_publication_bundle_receipt.py',
    )
    preflight_tool = _load_module(
        'rematch_world_benchmark_publication_preflight',
        ROOT / 'scripts' / 'tools' / 'rematch_world_benchmark_publication_preflight.py',
    )

    expected_bundle, _patch, expected_candidate = bundle_tool.build_bundle_receipt(
        packet=packet,
        evidence_receipt=evidence_receipt,
        seed=seed,
        decision_contract=decision_contract,
        packet_path=packet_path,
        evidence_receipt_path=evidence_receipt_path,
        seed_path=seed_path,
        decision_contract_path=decision_contract_path,
        artifact_output_path=compiled_artifact_path,
        patch_output_path=None,
    )
    expected_bundle['compiled_candidate']['artifact_output_path'] = _relativize(compiled_artifact_path)
    expected_bundle['artifact_written'] = True
    expected_preflight = preflight_tool.build_preflight_summary(
        candidate=expected_candidate,
        seed=seed,
        decision_contract=decision_contract,
        inspection_mode='artifact',
        inspection_target_path=_relativize(compiled_artifact_path),
        seed_path=_relativize(seed_path),
        decision_contract_path=_relativize(decision_contract_path),
    )

    retained_packet_sha256 = _sha256_json(packet)
    retained_evidence_receipt_sha256 = _sha256_json(evidence_receipt)
    retained_artifact_sha256 = _sha256_json(compiled_artifact)
    retained_preflight_sha256 = _sha256_json(preflight_receipt)
    retained_bundle_sha256 = _sha256_json(bundle_receipt)

    expected_artifact_sha256 = _sha256_json(expected_candidate)
    expected_preflight_sha256 = _sha256_json(expected_preflight)
    expected_bundle_sha256 = _sha256_json(expected_bundle)

    packet_digest_matches_evidence_receipt = evidence_receipt.get('packet_sha256') == retained_packet_sha256
    evidence_receipt_strict_coverage_passed = bool(evidence_receipt.get('strict_coverage_passed'))
    artifact_rebuild_matches_retained = compiled_artifact == expected_candidate
    artifact_hash_matches_rebuild = retained_artifact_sha256 == expected_artifact_sha256
    preflight_rebuild_matches_retained = preflight_receipt == expected_preflight
    preflight_hash_matches_rebuild = retained_preflight_sha256 == expected_preflight_sha256
    bundle_rebuild_matches_retained = bundle_receipt == expected_bundle
    bundle_hash_matches_rebuild = retained_bundle_sha256 == expected_bundle_sha256
    retained_artifact_matches_bundle = bundle_receipt['compiled_candidate']['artifact_sha256'] == retained_artifact_sha256
    retained_preflight_matches_artifact = preflight_receipt['artifact_fingerprints']['artifact_sha256'] == retained_artifact_sha256
    retained_preflight_ready = bool(preflight_receipt.get('preflight_ready'))
    retained_bundle_patch_elision_ready = bool(bundle_receipt.get('patch_elision_ready'))
    retained_decision_digest_matches_contract = bool(preflight_receipt.get('decision_bundle_digest_matches_contract'))

    publication_spine_ready = bool(
        packet_digest_matches_evidence_receipt
        and evidence_receipt_strict_coverage_passed
        and artifact_rebuild_matches_retained
        and artifact_hash_matches_rebuild
        and preflight_rebuild_matches_retained
        and preflight_hash_matches_rebuild
        and bundle_rebuild_matches_retained
        and bundle_hash_matches_rebuild
        and retained_artifact_matches_bundle
        and retained_preflight_matches_artifact
        and retained_preflight_ready
        and retained_bundle_patch_elision_ready
        and retained_decision_digest_matches_contract
    )

    if publication_spine_ready:
        recommended_next_move = (
            'For a real run, retain the audited four-object publication spine plus the compact bundle receipt and let the fill patch remain scratch-only.'
        )
    else:
        recommended_next_move = (
            'Do not treat the retained publication spine as settled yet; rebuild the packet-to-artifact path and repair any detected drift before relying on the retained receipts.'
        )

    return {
        'snapshot_date': '2026-03-17',
        'receipt_version': '2026-03-17.rematch_world_benchmark_publication_spine_audit.v1',
        'analysis_script': 'scripts/tools/audit_rematch_world_benchmark_publication_spine.py',
        'focus': 'audit the retained rematch-world publication spine by deterministic rebuild so future inheritors can trust the retained artifact and receipts without keeping the fill patch',
        'packet_path': _relativize(packet_path),
        'evidence_receipt_path': _relativize(evidence_receipt_path),
        'seed_path': _relativize(seed_path),
        'decision_contract_path': _relativize(decision_contract_path),
        'compiled_artifact_path': _relativize(compiled_artifact_path),
        'preflight_receipt_path': _relativize(preflight_receipt_path),
        'bundle_receipt_path': _relativize(bundle_receipt_path),
        'retained_bytes': {
            'packet_bytes': len(_render_bytes(packet)),
            'evidence_receipt_bytes': len(_render_bytes(evidence_receipt)),
            'compiled_artifact_bytes': len(_render_bytes(compiled_artifact)),
            'preflight_receipt_bytes': len(_render_bytes(preflight_receipt)),
            'bundle_receipt_bytes': len(_render_bytes(bundle_receipt)),
            'durable_spine_bytes': len(_render_bytes(packet)) + len(_render_bytes(evidence_receipt)) + len(_render_bytes(compiled_artifact)) + len(_render_bytes(preflight_receipt)),
        },
        'retained_hashes': {
            'packet_sha256': retained_packet_sha256,
            'evidence_receipt_sha256': retained_evidence_receipt_sha256,
            'compiled_artifact_sha256': retained_artifact_sha256,
            'preflight_receipt_sha256': retained_preflight_sha256,
            'bundle_receipt_sha256': retained_bundle_sha256,
        },
        'rebuild_hashes': {
            'compiled_artifact_sha256': expected_artifact_sha256,
            'preflight_receipt_sha256': expected_preflight_sha256,
            'bundle_receipt_sha256': expected_bundle_sha256,
        },
        'checks': {
            'packet_digest_matches_evidence_receipt': packet_digest_matches_evidence_receipt,
            'evidence_receipt_strict_coverage_passed': evidence_receipt_strict_coverage_passed,
            'artifact_rebuild_matches_retained': artifact_rebuild_matches_retained,
            'artifact_hash_matches_rebuild': artifact_hash_matches_rebuild,
            'preflight_rebuild_matches_retained': preflight_rebuild_matches_retained,
            'preflight_hash_matches_rebuild': preflight_hash_matches_rebuild,
            'bundle_rebuild_matches_retained': bundle_rebuild_matches_retained,
            'bundle_hash_matches_rebuild': bundle_hash_matches_rebuild,
            'retained_artifact_matches_bundle': retained_artifact_matches_bundle,
            'retained_preflight_matches_artifact': retained_preflight_matches_artifact,
            'retained_preflight_ready': retained_preflight_ready,
            'retained_bundle_patch_elision_ready': retained_bundle_patch_elision_ready,
            'retained_decision_digest_matches_contract': retained_decision_digest_matches_contract,
        },
        'retained_preflight_status': {
            'blocking_fill_slot_count': int(preflight_receipt['status_counts']['blocking_fill_slot_count']),
            'forbidden_changed_path_count': int(preflight_receipt['status_counts']['forbidden_changed_path_count']),
            'allowed_decision_null_count': int(preflight_receipt['status_counts']['allowed_decision_null_count']),
            'filled_world_section_count': int(preflight_receipt['status_counts']['filled_world_section_count']),
        },
        'publication_spine_ready': publication_spine_ready,
        'recommended_next_move': recommended_next_move,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Audit a retained rematch-world publication spine by rebuilding the compiled artifact, preflight receipt, and bundle receipt from the retained packet and evidence receipt.')
    parser.add_argument('--packet', default=str(DEFAULT_PACKET), help='Path to the retained evidence packet JSON.')
    parser.add_argument('--evidence-receipt', default=str(DEFAULT_EVIDENCE_RECEIPT), help='Path to the retained evidence receipt JSON.')
    parser.add_argument('--seed', default=str(DEFAULT_SEED), help='Path to the standing benchmark seed JSON.')
    parser.add_argument('--decision-contract', default=str(DEFAULT_DECISION_CONTRACT), help='Path to the standing compact decision contract JSON.')
    parser.add_argument('--artifact', default=str(DEFAULT_ARTIFACT), help='Path to the retained compiled benchmark artifact JSON.')
    parser.add_argument('--preflight', default=str(DEFAULT_PREFLIGHT), help='Path to the retained preflight receipt JSON.')
    parser.add_argument('--bundle', default=str(DEFAULT_BUNDLE), help='Path to the retained publication-bundle receipt JSON.')
    parser.add_argument('--output', help='Write the audit receipt to this path instead of stdout.')
    parser.add_argument('--summary-json', action='store_true', help='Emit a compact summary instead of the full audit receipt.')
    parser.add_argument('--strict', action='store_true', help='Exit nonzero unless the retained publication spine is fully rebuild-audited and ready.')
    args = parser.parse_args()

    def resolve(path_str: str) -> Path:
        path = Path(path_str)
        return path.resolve() if path.is_absolute() else (ROOT / path).resolve()

    packet_path = resolve(args.packet)
    evidence_receipt_path = resolve(args.evidence_receipt)
    seed_path = resolve(args.seed)
    decision_contract_path = resolve(args.decision_contract)
    artifact_path = resolve(args.artifact)
    preflight_path = resolve(args.preflight)
    bundle_path = resolve(args.bundle)

    receipt = build_audit_receipt(
        packet=load_json(packet_path),
        evidence_receipt=load_json(evidence_receipt_path),
        seed=load_json(seed_path),
        decision_contract=load_json(decision_contract_path),
        compiled_artifact=load_json(artifact_path),
        preflight_receipt=load_json(preflight_path),
        bundle_receipt=load_json(bundle_path),
        packet_path=packet_path,
        evidence_receipt_path=evidence_receipt_path,
        seed_path=seed_path,
        decision_contract_path=decision_contract_path,
        compiled_artifact_path=artifact_path,
        preflight_receipt_path=preflight_path,
        bundle_receipt_path=bundle_path,
    )

    schema = load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt, schema)

    if args.summary_json:
        rendered = json.dumps(
            {
                'publication_spine_ready': receipt['publication_spine_ready'],
                'durable_spine_bytes': receipt['retained_bytes']['durable_spine_bytes'],
                'bundle_receipt_bytes': receipt['retained_bytes']['bundle_receipt_bytes'],
                'artifact_rebuild_matches_retained': receipt['checks']['artifact_rebuild_matches_retained'],
                'preflight_rebuild_matches_retained': receipt['checks']['preflight_rebuild_matches_retained'],
                'bundle_rebuild_matches_retained': receipt['checks']['bundle_rebuild_matches_retained'],
                'blocking_fill_slot_count': receipt['retained_preflight_status']['blocking_fill_slot_count'],
                'forbidden_changed_path_count': receipt['retained_preflight_status']['forbidden_changed_path_count'],
            },
            indent=2,
            sort_keys=True,
        ) + '\n'
    else:
        rendered = json.dumps(receipt, indent=2, sort_keys=True) + '\n'

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = (ROOT / output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding='utf-8')
        print(
            'rematch-world-benchmark-publication-spine-audit: '
            f'wrote {_relativize(output_path)} (publication_spine_ready={str(receipt["publication_spine_ready"]).lower()})'
        )
    else:
        print(rendered, end='')

    if args.strict and not receipt['publication_spine_ready']:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
