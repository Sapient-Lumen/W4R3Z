from __future__ import annotations

import base64
import json
import struct
import zlib
from pathlib import Path
from typing import Any

from chatgpt_proof_ingest import ingest_capture, validate_capture
from chatgpt_proof_rehearsal import build_rehearsal_payload
from chatgpt_surface_contract import build_contract
from test_chatgpt_surface_contract import _surface


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)


def _png_data_url(width: int = 2, height: int = 2) -> str:
    # Filter byte per row + opaque red RGBA pixels.
    row = b'\x00' + (b'\xff\x00\x00\xff' * width)
    raw = row * height
    png = b'\x89PNG\r\n\x1a\n' + _png_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) + _png_chunk(b'IDAT', zlib.compress(raw)) + _png_chunk(b'IEND', b'')
    return 'data:image/png;base64,' + base64.b64encode(png).decode('ascii')


def _strip_rehearsal_flags(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if key in {'rehearsal_only', 'dry_run'}:
                continue
            if key == 'proof_mode' and item in {'offline-rehearsal', 'rehearsal', 'dry-run'}:
                out[key] = 'sidepanel-chatgpt-first-proof'
            else:
                out[key] = _strip_rehearsal_flags(item)
        return out
    if isinstance(value, list):
        return [_strip_rehearsal_flags(item) for item in value]
    return value


def _live_candidate_payload() -> dict[str, Any]:
    source = build_rehearsal_payload(contract=build_contract(_surface()))
    source = _strip_rehearsal_flags(source)
    source['capture_kind'] = 'sidepanel-manual-chatgpt-first-proof'
    source['live_proof'] = True
    source['visible_tab_screenshot_data_url'] = _png_data_url()
    source['single_tab_context'] = True
    source['same_conversation_route_after_latest'] = True
    source['proof_live_gate_ok_seen'] = True
    source['proof_live_gate_verdicts'] = ['proof-live-gate-ok']
    source['observed_conversation_route_paths'] = ['/c/rehearsal-checkpoint']
    return source


def test_validate_capture_accepts_live_candidate_with_gate_and_screenshot() -> None:
    report = validate_capture(_live_candidate_payload())

    assert report['ok'] is True
    assert report['verdict'] == 'proof-json-ingested-live-candidate'
    assert report['live_candidate'] is True
    assert report['screenshot']['valid_png_data_url'] is True
    assert report['screenshot']['dimensions'] == {'width': 2, 'height': 2}


def test_validate_capture_blocks_missing_screenshot() -> None:
    source = _live_candidate_payload()
    source.pop('visible_tab_screenshot_data_url')

    report = validate_capture(source)

    assert report['ok'] is False
    assert report['verdict'] == 'proof-json-ingest-blocked'
    assert any('screenshot' in blocker for blocker in report['blockers'])


def test_ingest_capture_writes_normalized_and_redacted_outputs(tmp_path: Path) -> None:
    source_path = tmp_path / 'downloaded-proof.json'
    source_path.write_text(json.dumps(_live_candidate_payload()), encoding='utf-8')
    out = tmp_path / 'normalized.json'
    redacted = tmp_path / 'redacted.json'
    summary = tmp_path / 'summary.json'

    report = ingest_capture(
        source_path,
        out=out,
        redacted_out=redacted,
        summary_out=summary,
        require_live_candidate=True,
    )

    assert report['ok'] is True
    assert out.exists()
    assert redacted.exists()
    assert summary.exists()
    redacted_text = redacted.read_text(encoding='utf-8')
    assert 'data:image/png;base64,' not in redacted_text
    assert 'redacted_data_url' in redacted_text
    normalized = json.loads(out.read_text(encoding='utf-8'))
    assert normalized['ingest']['source_sha256'] == report['source_sha256']
