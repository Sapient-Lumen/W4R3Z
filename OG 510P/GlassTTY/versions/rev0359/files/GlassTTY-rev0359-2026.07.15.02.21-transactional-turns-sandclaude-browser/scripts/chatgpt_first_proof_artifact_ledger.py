#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACK_DIR = ROOT / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-artifact-ledger'
LEDGER_SCHEMA_VERSION = 1
ATTEMPT_KEYS = ('attempt_id', 'run_id', 'bundle_id', 'proof_id', 'session_id', 'capture_id')


class ArtifactSlot(NamedTuple):
    order: int
    filename: str
    phase: str
    artifact_type: str
    required_for: str
    purpose: str


ARTIFACT_SLOTS: tuple[ArtifactSlot, ...] = (
    ArtifactSlot(1, 'route-witness.json', 'capture', 'json', 'capture-ready', 'Record adapter, host, URL, tab_id, and route_posture before the write.'),
    ArtifactSlot(2, 'surface-screenshot.png', 'capture', 'image', 'capture-ready', 'Visible plain-chat surface for local review; publication requires redaction review.'),
    ArtifactSlot(3, 'receiver-posture.md', 'capture', 'markdown', 'capture-ready', 'Human note confirming no richer ChatGPT branch was entered.'),
    ArtifactSlot(4, 'composer-candidates.json', 'capture', 'json', 'capture-ready', 'Selected and rejected composer candidates with selector/actionability reasons.'),
    ArtifactSlot(5, 'composer-before.txt', 'capture', 'text', 'capture-ready', 'Composer text before write.'),
    ArtifactSlot(6, 'composer-after.txt', 'capture', 'text', 'capture-ready', 'Composer text after write; must exactly equal the checkpoint prompt after whitespace normalization.'),
    ArtifactSlot(7, 'composer-witness-receipt.json', 'capture', 'json', 'capture-ready', 'Machine-readable write witness with selected composer metadata.'),
    ArtifactSlot(8, 'probe-prompt.txt', 'capture', 'text', 'capture-ready', 'Exact checkpoint prompt used for the proof.'),
    ArtifactSlot(9, 'submit-evidence.json', 'capture', 'json', 'capture-ready', 'Operator-attested side-panel/manual submit row with URL, adapter, tab_id, and sequence index.'),
    ArtifactSlot(10, 'submit-prompt-readback.json', 'capture', 'json', 'capture-ready', 'Submit-time composer readback on the same submit row; must exactly equal the prompt.'),
    ArtifactSlot(11, 'generation-timeline.json', 'capture', 'json', 'capture-ready', 'Route and generation-state transitions after submit.'),
    ArtifactSlot(12, 'transcript-latest-action.json', 'capture', 'json', 'capture-ready', 'Latest assistant read on /c/<conversation-id> with exact checkpoint reply.'),
    ArtifactSlot(13, 'assistant-output-witness.json', 'capture', 'json', 'capture-ready', 'Leaf-like assistant turn witness with selector, role, order, frame, and text metadata.'),
    ArtifactSlot(14, 'assistant-output-text-coherence.json', 'capture', 'json', 'capture-ready', 'Proof that assistant witness text exactly matches the latest reply.'),
    ArtifactSlot(15, 'assistant-witness-scope.json', 'capture', 'json', 'capture-ready', 'Proof the assistant witness is not a parent/thread/wrapper containing user+assistant text.'),
    ArtifactSlot(16, 'user-turn-witness.json', 'capture', 'json', 'capture-ready', 'Visible user turn witness whose text exactly equals the checkpoint prompt.'),
    ArtifactSlot(17, 'user-witness-scope.json', 'capture', 'json', 'capture-ready', 'Proof the user witness is not a parent/thread/wrapper containing user+assistant text.'),
    ArtifactSlot(18, 'turn-pair-order-witness.json', 'capture', 'json', 'capture-ready', 'User-before-assistant document-order evidence.'),
    ArtifactSlot(19, 'turn-pair-frame-context-witness.json', 'capture', 'json', 'capture-ready', 'Explicit same-frame context for the user/assistant pair.'),
    ArtifactSlot(20, 'same-tab-context-witness.json', 'capture', 'json', 'capture-ready', 'Same explicit tab_id across write, submit, latest, and settled witness.'),
    ArtifactSlot(21, 'same-conversation-route-witness.json', 'capture', 'json', 'capture-ready', 'Same normalized /c/<conversation-id> path between latest and post-latest settled witness.'),
    ArtifactSlot(22, 'route-transition-witness.json', 'capture', 'json', 'capture-ready', 'Evidence of root/plain-chat to /c/<conversation-id> transition after submit.'),
    ArtifactSlot(23, 'exact-readback-witness.json', 'capture', 'json', 'capture-ready', 'Combined write and submit exact-readback proof.'),
    ArtifactSlot(24, 'settled-generation-witness.json', 'capture', 'json', 'capture-ready', 'Post-latest settled/idle generation state with no stop control present.'),
    ArtifactSlot(25, 'settled-generation-sequence-witness.json', 'capture', 'json', 'capture-ready', 'Later-sequenced settled fixture/snapshot with ChatGPT URL/adapter witness.'),
    ArtifactSlot(26, 'bundle-manifest.json', 'assembly', 'json', 'evaluator-ready', 'Single manifest joining all artifacts under one attempt_id and action sequence.'),
    ArtifactSlot(27, 'bundle-schema-validation.json', 'review', 'json', 'review-ready', 'Structural validation report against schemas/chatgpt-first-proof-bundle.schema.json.'),
    ArtifactSlot(28, 'chatgpt-first-proof-bundle-audit.json', 'review', 'json', 'review-ready', 'Local action graph, attempt summary, and check-registry audit before evaluator review.'),
    ArtifactSlot(29, 'chatgpt-first-proof-evaluation.json', 'review', 'json', 'review-ready', 'Output from the active ChatGPT first-proof evaluator.'),
    ArtifactSlot(30, 'privacy-redaction-review.md', 'review', 'markdown', 'publication-review-ready', 'Human redaction decision before any publication/support use.'),
)


CAPTURE_READY_REQUIREMENTS = {'capture-ready'}
EVALUATOR_READY_REQUIREMENTS = {'capture-ready', 'evaluator-ready'}
REVIEW_READY_REQUIREMENTS = {'capture-ready', 'evaluator-ready', 'review-ready'}
PUBLICATION_REVIEW_READY_REQUIREMENTS = {'capture-ready', 'evaluator-ready', 'review-ready', 'publication-review-ready'}


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def display_path(path: Path, *, root: Path = ROOT) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _walk_json(value: Any) -> list[Any]:
    values: list[Any] = []

    def walk(item: Any) -> None:
        values.append(item)
        if isinstance(item, dict):
            for child in item.values():
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return values


def attempt_ids_from_json(value: Any) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for item in _walk_json(value):
        if not isinstance(item, dict):
            continue
        for key in ATTEMPT_KEYS:
            candidate = item.get(key)
            if isinstance(candidate, str) and candidate.strip() and candidate.strip() not in seen:
                cleaned = candidate.strip()
                ids.append(cleaned)
                seen.add(cleaned)
    return ids


def _artifact_content_status(path: Path, artifact_type: str) -> dict[str, Any]:
    status: dict[str, Any] = {
        'exists': path.exists(),
        'size': None,
        'sha256': None,
        'parse_ok': None,
        'parse_error': None,
        'nonempty': None,
        'attempt_ids': [],
    }
    if not path.exists():
        return status
    status['size'] = path.stat().st_size
    status['sha256'] = sha256_file(path)
    status['nonempty'] = path.stat().st_size > 0
    if artifact_type == 'json':
        try:
            payload = read_json(path)
            status['parse_ok'] = True
            status['attempt_ids'] = attempt_ids_from_json(payload)
        except Exception as exc:  # pragma: no cover - exception type depends on parser internals
            status['parse_ok'] = False
            status['parse_error'] = str(exc)
    elif artifact_type in {'text', 'markdown'}:
        try:
            status['nonempty'] = bool(path.read_text(encoding='utf-8').strip())
        except UnicodeDecodeError as exc:
            status['parse_ok'] = False
            status['parse_error'] = str(exc)
    return status


def artifact_registry() -> list[dict[str, Any]]:
    return [slot._asdict() for slot in ARTIFACT_SLOTS]


def _required_phases_for(level: str) -> set[str]:
    if level == 'capture-ready':
        return set(CAPTURE_READY_REQUIREMENTS)
    if level == 'evaluator-ready':
        return set(EVALUATOR_READY_REQUIREMENTS)
    if level == 'review-ready':
        return set(REVIEW_READY_REQUIREMENTS)
    if level == 'publication-review-ready':
        return set(PUBLICATION_REVIEW_READY_REQUIREMENTS)
    raise ValueError(f'unknown readiness level: {level}')


def _slot_required_for_level(slot: ArtifactSlot, level: str) -> bool:
    return slot.required_for in _required_phases_for(level)


def build_artifact_ledger(pack_dir: Path = DEFAULT_PACK_DIR, *, readiness_level: str = 'evaluator-ready') -> dict[str, Any]:
    pack_dir = pack_dir.resolve()
    required_phases = _required_phases_for(readiness_level)
    rows: list[dict[str, Any]] = []
    attempt_ids_by_file: dict[str, list[str]] = {}
    for slot in ARTIFACT_SLOTS:
        path = pack_dir / slot.filename
        content_status = _artifact_content_status(path, slot.artifact_type)
        row = {
            **slot._asdict(),
            'required_for_selected_readiness': slot.required_for in required_phases,
            'path': display_path(path),
            **content_status,
        }
        rows.append(row)
        ids = content_status.get('attempt_ids') or []
        if ids:
            attempt_ids_by_file[slot.filename] = ids

    missing_required = [row['filename'] for row in rows if row['required_for_selected_readiness'] and not row['exists']]
    invalid_json = [row['filename'] for row in rows if row['exists'] and row['artifact_type'] == 'json' and row.get('parse_ok') is False]
    empty_required = [row['filename'] for row in rows if row['required_for_selected_readiness'] and row['exists'] and row.get('nonempty') is False]
    all_attempt_ids = sorted({attempt_id for ids in attempt_ids_by_file.values() for attempt_id in ids})
    canonical_attempt_id = all_attempt_ids[0] if len(all_attempt_ids) == 1 else None
    attempt_id_consistent = len(all_attempt_ids) <= 1
    attempt_id_missing_json_files = [
        row['filename']
        for row in rows
        if row['required_for_selected_readiness']
        and row['artifact_type'] == 'json'
        and row['exists']
        and row.get('parse_ok') is True
        and not row.get('attempt_ids')
        and row['filename'] != 'bundle-schema-validation.json'
    ]
    ready = not (missing_required or invalid_json or empty_required or not attempt_id_consistent)
    counts = {
        'slot_count': len(rows),
        'present_count': sum(1 for row in rows if row['exists']),
        'missing_count': sum(1 for row in rows if not row['exists']),
        'selected_required_count': sum(1 for row in rows if row['required_for_selected_readiness']),
        'selected_required_present_count': sum(1 for row in rows if row['required_for_selected_readiness'] and row['exists']),
        'json_present_count': sum(1 for row in rows if row['exists'] and row['artifact_type'] == 'json'),
    }
    return {
        'schema_version': LEDGER_SCHEMA_VERSION,
        'ledger_key': 'chatgpt-first-proof-artifact-ledger',
        'generated_at': utcnow(),
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'pack_dir': display_path(pack_dir),
        'readiness_level': readiness_level,
        'ready': ready,
        'counts': counts,
        'missing_required_files': missing_required,
        'invalid_json_files': invalid_json,
        'empty_required_files': empty_required,
        'attempt_id_consistency': {
            'ok': attempt_id_consistent,
            'canonical_attempt_id': canonical_attempt_id,
            'observed_attempt_ids': all_attempt_ids,
            'attempt_ids_by_file': attempt_ids_by_file,
            'json_files_without_attempt_id': attempt_id_missing_json_files,
        },
        'slots': rows,
        'support_claim_effect': 'none; this ledger only audits local artifact materiality and never widens support claims',
        'operator_notes': [
            'Capture-ready means raw capture slots 1-25 are present and parseable where applicable.',
            'Evaluator-ready additionally requires bundle-manifest.json to exist and be parseable.',
            'Review-ready additionally expects schema-validation, bundle-audit, and evaluator report artifacts.',
            'Publication-review-ready additionally expects the human privacy-redaction-review.md file.',
            'A ready ledger is local materiality only; semantic acceptance still requires the schema validator, bundle audit, evaluator, and human redaction review.',
        ],
    }


def summary_markdown(ledger: dict[str, Any]) -> str:
    counts = ledger.get('counts') or {}
    attempt = ledger.get('attempt_id_consistency') or {}
    lines = [
        '# ChatGPT first-proof artifact ledger',
        '',
        f"- generated_at: `{ledger.get('generated_at')}`",
        f"- pack_dir: `{ledger.get('pack_dir')}`",
        f"- readiness_level: `{ledger.get('readiness_level')}`",
        f"- ready: `{ledger.get('ready')}`",
        f"- present_count: `{counts.get('present_count')}` / `{counts.get('slot_count')}`",
        f"- selected_required_present_count: `{counts.get('selected_required_present_count')}` / `{counts.get('selected_required_count')}`",
        f"- missing_required_files: `{ledger.get('missing_required_files')}`",
        f"- invalid_json_files: `{ledger.get('invalid_json_files')}`",
        f"- attempt_id_consistency_ok: `{attempt.get('ok')}`",
        f"- observed_attempt_ids: `{attempt.get('observed_attempt_ids')}`",
        '',
        '## Artifact slots',
        '',
        '| order | filename | required_for | present | sha256 |',
        '|---:|---|---|---:|---|',
    ]
    for row in ledger.get('slots') or []:
        sha = row.get('sha256') or ''
        sha_short = sha[:12] if isinstance(sha, str) and sha else ''
        lines.append(f"| {row.get('order')} | `{row.get('filename')}` | {row.get('required_for')} | `{row.get('exists')}` | `{sha_short}` |")
    lines.extend(['', '## Operator notes', ''])
    for note in ledger.get('operator_notes') or []:
        lines.append(f'- {note}')
    return '\n'.join(lines) + '\n'


def write_artifact_ledger(pack_dir: Path = DEFAULT_PACK_DIR, *, output_dir: Path = DEFAULT_OUTPUT_DIR, readiness_level: str = 'evaluator-ready') -> dict[str, Any]:
    ledger = build_artifact_ledger(pack_dir, readiness_level=readiness_level)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / 'chatgpt-first-proof-artifact-ledger.json', ledger)
    (output_dir / 'SUMMARY.md').write_text(summary_markdown(ledger), encoding='utf-8')
    return ledger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Audit the material artifact slots for a ChatGPT first-proof evidence pack.')
    sub = parser.add_subparsers(dest='command')
    registry_cmd = sub.add_parser('registry', help='Print the canonical ChatGPT first-proof artifact-slot registry')
    registry_cmd.add_argument('--pretty', action='store_true')
    audit_cmd = sub.add_parser('audit', help='Audit an evidence-pack directory against the artifact-slot registry')
    audit_cmd.add_argument('--pack-dir', type=Path, default=DEFAULT_PACK_DIR)
    audit_cmd.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    audit_cmd.add_argument('--readiness-level', choices=['capture-ready', 'evaluator-ready', 'review-ready', 'publication-review-ready'], default='evaluator-ready')
    audit_cmd.add_argument('--pretty', action='store_true')
    audit_cmd.add_argument('--require-ready', action='store_true', help='Exit nonzero unless the selected readiness level is satisfied')
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in (None, 'audit'):
        pack_dir = getattr(args, 'pack_dir', DEFAULT_PACK_DIR)
        output_dir = getattr(args, 'output_dir', DEFAULT_OUTPUT_DIR)
        readiness_level = getattr(args, 'readiness_level', 'evaluator-ready')
        ledger = write_artifact_ledger(pack_dir, output_dir=output_dir, readiness_level=readiness_level)
        print(json.dumps(ledger, indent=2 if getattr(args, 'pretty', False) else None))
        if getattr(args, 'require_ready', False) and not ledger.get('ready'):
            return 1
        return 0
    if args.command == 'registry':
        print(json.dumps({'schema_version': LEDGER_SCHEMA_VERSION, 'artifact_slots': artifact_registry()}, indent=2 if args.pretty else None))
        return 0
    parser.error(f'unknown command {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
