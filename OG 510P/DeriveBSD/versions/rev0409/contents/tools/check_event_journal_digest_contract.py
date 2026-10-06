#!/usr/bin/env python3
"""Guardrail for exact event-journal digest examples.

Checks the canonical event examples end-to-end:
- prev_digest on event.record
- event.segment file/merkle/chain digests
- event.seal.receipt segments_root_digest
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / 'spec' / 'examples'


def load_json(name: str) -> dict:
    return json.loads((EX / name).read_text(encoding='utf-8'))


def jcs_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def digest_obj(obj: dict) -> str:
    return 'sha256:' + hashlib.sha256(jcs_bytes(obj)).hexdigest()


def merkle_root(digests: list[str]) -> str:
    if not digests:
        raise ValueError('merkle_root requires at least one digest')
    level = [bytes.fromhex(d.split(':', 1)[1]) for d in digests]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [hashlib.sha256(level[i] + level[i + 1]).digest() for i in range(0, len(level), 2)]
    return 'sha256:' + level[0].hex()


def main() -> int:
    problems: list[str] = []

    record = load_json('event.record.json')
    segment = load_json('event.segment.json')
    seal = load_json('event.seal.receipt.json')
    blob_path = EX / 'event.segment.host-host-4f2a.seg-000001.jsonl'
    blob_lines = [line for line in blob_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    records = [json.loads(line) for line in blob_lines]

    if len(records) != 2:
        problems.append(f'expected 2 records in {blob_path.name}, got {len(records)}')
    else:
        first_digest = digest_obj(records[0])
        second_digest = digest_obj(records[1])
        if records[1].get('prev_digest') != first_digest:
            problems.append('second record prev_digest does not match digest of first record')
        if record != records[1]:
            problems.append('spec/examples/event.record.json must match the second record in the companion segment blob')
        computed_merkle = merkle_root([first_digest, second_digest])
        if segment.get('merkle_root_digest') != computed_merkle:
            problems.append(f"segment merkle_root_digest {segment.get('merkle_root_digest')!r} != computed {computed_merkle}")

    computed_file_digest = 'sha256:' + hashlib.sha256(blob_path.read_bytes()).hexdigest()
    if segment.get('file_digest') != computed_file_digest:
        problems.append(f"segment file_digest {segment.get('file_digest')!r} != computed {computed_file_digest}")

    chain_env = {
        'stream_id': segment.get('stream_id'),
        'segment_id': segment.get('segment_id'),
        'file_digest': segment.get('file_digest'),
        'count': segment.get('count'),
        'first_at': segment.get('first_at'),
        'last_at': segment.get('last_at'),
    }
    if segment.get('merkle_root_digest') is not None:
        chain_env['merkle_root_digest'] = segment.get('merkle_root_digest')
    if segment.get('prev_chain_head_digest') is not None:
        chain_env['prev_chain_head_digest'] = segment.get('prev_chain_head_digest')
    computed_chain = digest_obj(chain_env)
    if segment.get('chain_head_digest') != computed_chain:
        problems.append(f"segment chain_head_digest {segment.get('chain_head_digest')!r} != computed {computed_chain}")

    seal_segments = (seal.get('seal') or {}).get('segments') or []
    expected_segments = [{'segment_id': segment.get('segment_id'), 'file_digest': segment.get('file_digest')}]
    if seal_segments != expected_segments:
        problems.append('event.seal.receipt seal.segments must exactly match the canonical event.segment example')
    seal_root = digest_obj({'stream_id': seal.get('stream_id'), 'segments': seal_segments})
    if (seal.get('seal') or {}).get('segments_root_digest') != seal_root:
        problems.append('event.seal.receipt segments_root_digest does not match the ordered committed segment list')
    if (seal.get('seal') or {}).get('segment_count') != len(seal_segments):
        problems.append('event.seal.receipt segment_count does not match seal.segments length')
    if seal_segments:
        if (seal.get('seal') or {}).get('first_segment_id') != seal_segments[0]['segment_id']:
            problems.append('event.seal.receipt first_segment_id does not match first sealed segment')
        if (seal.get('seal') or {}).get('last_segment_id') != seal_segments[-1]['segment_id']:
            problems.append('event.seal.receipt last_segment_id does not match last sealed segment')

    required_tokens = {
        'docs/623-event-journal-digests-stay-chain-exact-and-seal-list-bound.md': [
            'event.record.prev_digest',
            'event.segment.chain_head_digest',
            'event.seal.receipt.segments_root_digest',
            'tools/check_event_journal_digest_contract.py',
        ],
        'adrs/ADR-0213-event-journal-digests-stay-chain-exact-and-seal-list-bound.md': [
            'event.record.prev_digest',
            'event.seal.receipt.segments_root_digest',
            'spec/examples/event.segment.host-host-4f2a.seg-000001.jsonl',
        ],
        'docs/215-structured-event-log-as-evidence.md': [
            'spec/examples/event.segment.host-host-4f2a.seg-000001.jsonl',
            '`sha256` of the UTF-8 bytes of the JCS-canonicalized previous `event.record` object',
        ],
        'docs/424-forward-secure-event-log-sealing.md': [
            '`segments_root_digest` is `sha256(utf8(JCS({"stream_id": ..., "segments": [{"segment_id","file_digest"}, ...]})))`',
        ],
        'docs/98-archive-hygiene.md': [
            'check_event_journal_digest_contract.py',
        ],
        'docs/99-llm-runbook.md': [
            'check_event_journal_digest_contract.py',
        ],
        'README.md': [
            'docs/623-event-journal-digests-stay-chain-exact-and-seal-list-bound.md',
        ],
        'docs/00-index.md': [
            'docs/623-event-journal-digests-stay-chain-exact-and-seal-list-bound.md',
            '2026-03-21r353',
        ],
        'CHANGELOG.md': [
            '2026-03-21r353',
            'tools/check_event_journal_digest_contract.py',
        ],
    }
    for rel, needles in required_tokens.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for needle in needles:
            if needle not in text:
                problems.append(f'{rel} missing required token: {needle}')

    if problems:
        print('Event journal digest contract check FAILED')
        for problem in problems:
            print('-', problem)
        return 1

    print('Event journal digest contract check OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
