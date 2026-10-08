#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_oracle.py'

MATERIAL_ANCHOR = 'TTTMMMMMU'
STABILITY_ANCHOR = 'TTTMMMMUU'
CAPS = [10, 20, 10000]
CONTRACT_VERSION = '2026-03-07-family10-decision-packet-v1'
PACKET_KIND = 'rematch_proxy_delta_decision_packet'
ARCHIVE_LOCAL_PACKET_KIND = 'rematch_proxy_delta_decision_packet_archive_local'
ARCHIVE_LOCAL_PROFILE_REF = 'family10_decision_packet_profile_20260307_v1'
PACKET_REFERENCE_KIND = 'rematch_proxy_delta_decision_packet_reference'
ARCHIVE_LOCAL_REFERENCE_KIND = 'rematch_proxy_delta_ref_local'
ARCHIVE_LOCAL_CATALOG_REFERENCE_KIND = 'rematch_proxy_delta_ref_catalog_slot'
CODED_REFERENCE_KIND = 'grdr'
SEMANTIC_CORE_KIND = 'rematch_proxy_delta_decision_packet_semantic_core'
SEMANTIC_CORE_CONTRACT_VERSION = '2026-03-07-family10-decision-core-v1'
CODED_SEED_KIND = 'grdp_seed'
CODED_SEED_PROFILE_REF = 'f10s1'
CODED_SEED_MODE_CODES = {
    'oracle_coordinates': 'oc',
    'oracle_weights': 'ow',
    'probe_robustness_fixed': 'rf',
    'probe_robustness_adaptive': 'ra',
    'probe_strict_adaptive': 'sa',
    'probe_exact_checked_cap_path': 'xp',
}
CODED_SEED_MODE_FROM_CODE = {code: mode for mode, code in CODED_SEED_MODE_CODES.items()}
MICROFRAME_REFERENCE_TAG = '@'
PACKED_MODE_TAGS = {
    'oracle_coordinates': 0,
    'oracle_weights': 1,
    'probe_robustness_fixed': 2,
    'probe_robustness_adaptive': 3,
    'probe_strict_adaptive': 4,
    'probe_exact_checked_cap_path': 5,
    'reference': 6,
}
PACKED_MODE_FROM_TAG = {tag: mode for mode, tag in PACKED_MODE_TAGS.items()}
PACKED_ROUTE_CODES_ROBUSTNESS_ADAPTIVE = {
    '10:M': 0,
    '10:S;20:M': 1,
    '10:S;20:S': 2,
    '10:S;20:T': 3,
    '20:S': 4,
    '20:M;10:M': 5,
    '20:M;10:S': 6,
    '20:M;10:T': 7,
}
PACKED_ROUTE_FROM_CODE_ROBUSTNESS_ADAPTIVE = {
    code: route for route, code in PACKED_ROUTE_CODES_ROBUSTNESS_ADAPTIVE.items()
}
PACKED_ROUTE_CODES_STRICT_ADAPTIVE = {
    '10000:M;10:M': 0,
    '10000:M;10:S': 1,
    '10000:M;10:T': 2,
    '10000:S;20:M': 3,
    '10000:S;20:S': 4,
    '10000:S;20:T': 5,
}
PACKED_ROUTE_FROM_CODE_STRICT_ADAPTIVE = {
    code: route for route, code in PACKED_ROUTE_CODES_STRICT_ADAPTIVE.items()
}
PACKED_SIGNATURE_SYMBOL_TO_CODE = {'M': 0, 'S': 1, 'T': 2}
PACKED_SIGNATURE_CODE_TO_SYMBOL = {code: symbol for symbol, code in PACKED_SIGNATURE_SYMBOL_TO_CODE.items()}
WEIGHT_KEYS = (
    'w_width',
    'w_buffer',
    'w_knife',
    'w_delta',
    'w_material',
    'w_undecided',
    'w_ties',
    'w_hazard',
)
MIN_REFERENCE_PREFIX_HEX_LEN = 12
PACKED_SCALAR_ATOM_CODES = {
    '1': 0,
    '0.5': 1,
    '2': 2,
    '0.2': 3,
    '0.0001': 4,
    '0.000000': 5,
}
PACKED_SCALAR_FROM_ATOM = {code: value for value, code in PACKED_SCALAR_ATOM_CODES.items()}
PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG = -1
BYTEFRAME_WEIGHT_FORMAT_SPARSE = 0
BYTEFRAME_WEIGHT_FORMAT_GROUPED = 1
FINGERPRINT_CATALOG_PAGE_TAG = 126
FINGERPRINT_CATALOG_PAGE_FILTER_TAG = 125
FINGERPRINT_CATALOG_PAGE_ROUTE_BLOCK_TAG = 124
FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE = 16
CATALOG_REFERENCE_TAG = 127
FILTERED_FINGERPRINT_CATALOG_PAGE_SIZE_CANDIDATES = (8, 16, 32, 64, 128)
DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE = 16
COMPACT_REPEAT_STATE_KINDS = (
    'paged_catalog_only',
    'paged_catalog_with_filters',
    'paged_catalog_with_route_blocks',
)
SHORT_CATALOG_REFERENCE_PREFIX = 0x80
SHORT_CATALOG_REFERENCE_PREFIX_MASK = 0xC0
SHORT_CATALOG_REFERENCE_MAX_SLOT = 0x3FFF


class PacketError(ValueError):
    pass


def _packet_kind_tag(packet: Any) -> str | None:
    if isinstance(packet, dict):
        return packet.get('packet_kind', packet.get('k'))
    return None


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _normalize_symbol(symbol: str) -> str:
    cleaned = symbol.strip()
    upper = cleaned.upper()
    if upper in {'M', 'MATERIAL', MATERIAL_ANCHOR}:
        return 'M'
    if upper in {'S', 'STABILITY', STABILITY_ANCHOR}:
        return 'S'
    if upper in {'T', 'TIE', 'NONE'}:
        return 'T'
    raise PacketError(f'unsupported probe symbol: {symbol}')


def _checked_cap_signature(cap_rows: list[dict[str, Any]]) -> str:
    pieces: list[str] = []
    for row in cap_rows:
        outcome = row['outcome']
        winner = row['winner']
        if outcome == 'tie' or winner is None:
            pieces.append('T')
        elif winner == MATERIAL_ANCHOR:
            pieces.append('M')
        elif winner == STABILITY_ANCHOR:
            pieces.append('S')
        else:
            raise PacketError(f'unsupported winner label in cap rows: {winner}')
    return ''.join(pieces)


def _common_provenance() -> dict[str, Any]:
    return {
        'contract_version': CONTRACT_VERSION,
        'checked_caps': CAPS,
        'oracle_script': 'scripts/analysis/rematch_proxy_delta_decision_oracle.py',
        'decision_oracle_snapshot': 'artifacts/reports/rematch_proxy_delta_decision_oracle_snapshot_20260306.json',
        'question_targeted_probe_snapshot': 'artifacts/reports/rematch_proxy_delta_question_targeted_probe_snapshot_20260306.json',
    }


def archive_local_profile_registry() -> dict[str, dict[str, Any]]:
    return {
        ARCHIVE_LOCAL_PROFILE_REF: _common_provenance(),
    }


def archive_local_seed_profile_registry() -> dict[str, dict[str, Any]]:
    return {
        CODED_SEED_PROFILE_REF: {
            'mode_codes': CODED_SEED_MODE_CODES,
            'description': 'archive-local codebook for the minimal family10 rematch decision seeds',
        }
    }


def _validate_standalone_packet(packet: dict[str, Any]) -> None:
    if _packet_kind_tag(packet) != PACKET_KIND:
        raise PacketError(f"expected standalone packet_kind {PACKET_KIND}, got {_packet_kind_tag(packet)}")
    if packet.get('provenance') != _common_provenance():
        raise PacketError('standalone packet provenance does not match the canonical family10 decision-packet profile')


def _validate_archive_local_packet(packet: dict[str, Any]) -> None:
    if _packet_kind_tag(packet) != ARCHIVE_LOCAL_PACKET_KIND:
        raise PacketError(
            f"expected archive-local packet_kind {ARCHIVE_LOCAL_PACKET_KIND}, got {_packet_kind_tag(packet)}"
        )
    profile_ref = packet.get('profile_ref')
    if profile_ref not in archive_local_profile_registry():
        raise PacketError(f'unsupported archive-local profile_ref: {profile_ref}')


def _validate_semantic_core_packet(packet: dict[str, Any]) -> None:
    if _packet_kind_tag(packet) != SEMANTIC_CORE_KIND:
        raise PacketError(f"expected semantic-core packet_kind {SEMANTIC_CORE_KIND}, got {_packet_kind_tag(packet)}")
    if packet.get('core_contract_version') != SEMANTIC_CORE_CONTRACT_VERSION:
        raise PacketError(
            'semantic-core packet contract version does not match the canonical family10 semantic-core contract'
        )
    mode = packet.get('mode')
    required = {
        'oracle_coordinates': {'B', 'H'},
        'oracle_weights': {'weights'},
        'probe_robustness_fixed': {'signature'},
        'probe_robustness_adaptive': {'route'},
        'probe_strict_adaptive': {'route'},
        'probe_exact_checked_cap_path': {'signature'},
    }
    if mode not in required:
        raise PacketError(f'unsupported semantic-core mode: {mode}')
    missing = sorted(field for field in required[mode] if field not in packet)
    if missing:
        raise PacketError(f'semantic-core packet for mode {mode} is missing fields: {missing}')


def _validate_coded_seed_packet(packet: dict[str, Any]) -> None:
    if _packet_kind_tag(packet) != CODED_SEED_KIND:
        raise PacketError(f"expected coded-seed packet kind {CODED_SEED_KIND}, got {_packet_kind_tag(packet)}")
    if packet.get('p') not in archive_local_seed_profile_registry():
        raise PacketError(f"unsupported coded-seed profile ref: {packet.get('p')}")
    mode_code = packet.get('m')
    if mode_code not in CODED_SEED_MODE_FROM_CODE:
        raise PacketError(f'unsupported coded-seed mode code: {mode_code}')
    required = {
        'oc': {'B', 'H'},
        'ow': {'w'},
        'rf': {'s'},
        'ra': {'r'},
        'sa': {'r'},
        'xp': {'s'},
    }
    missing = sorted(field for field in required[mode_code] if field not in packet)
    if missing:
        raise PacketError(f'coded-seed packet for mode code {mode_code} is missing fields: {missing}')


def expand_packet(packet: Any) -> dict[str, Any]:
    if _is_byte_seed_packet(packet):
        return expand_byte_seed_packet(packet)
    if _is_packed_seed_packet(packet):
        return expand_packed_seed_packet(packet)
    if _is_micro_seed_packet(packet):
        return expand_micro_seed_packet(packet)
    packet_kind = _packet_kind_tag(packet)
    if packet_kind == PACKET_KIND:
        _validate_standalone_packet(packet)
        return packet
    if packet_kind == ARCHIVE_LOCAL_PACKET_KIND:
        return expand_archive_local_packet(packet)
    if packet_kind == SEMANTIC_CORE_KIND:
        return expand_semantic_core_packet(packet)
    if packet_kind == CODED_SEED_KIND:
        return expand_coded_seed_packet(packet)
    raise PacketError(f'unsupported packet_kind for expansion: {packet_kind}')


def packet_semantic_fingerprint(packet: Any) -> str:
    canonical = json.dumps(expand_packet(packet), sort_keys=True, separators=(',', ':')).encode('utf-8')
    return 'sha256:' + hashlib.sha256(canonical).hexdigest()


def packet_reference(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        'packet_kind': PACKET_REFERENCE_KIND,
        'semantic_fingerprint': packet_semantic_fingerprint(packet),
    }


def _normalize_fingerprint(fingerprint: str) -> str:
    if not fingerprint.startswith('sha256:'):
        raise PacketError(f'unsupported fingerprint format: {fingerprint}')
    hex_part = fingerprint.split(':', 1)[1]
    if len(hex_part) != 64 or any(ch not in '0123456789abcdef' for ch in hex_part):
        raise PacketError(f'unsupported sha256 fingerprint payload: {fingerprint}')
    return hex_part


def minimal_unique_reference_prefix_hex_len(
    fingerprint: str,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> int:
    hex_part = _normalize_fingerprint(fingerprint)
    known = {fp for fp in known_fingerprints if fp != fingerprint}
    floor = max(1, int(min_hex_len))
    for length in range(floor, len(hex_part) + 1):
        prefix = hex_part[:length]
        if all(not _normalize_fingerprint(other).startswith(prefix) for other in known):
            return length
    raise PacketError(f'could not find a unique fingerprint prefix for {fingerprint}')


def _has_stable_fingerprint_catalog(known_fingerprints: set[str] | list[str] | tuple[str, ...]) -> bool:
    return not isinstance(known_fingerprints, set)


def ordered_fingerprint_catalog(known_fingerprints: list[str] | tuple[str, ...]) -> list[str]:
    if isinstance(known_fingerprints, set):
        raise PacketError('catalog-slot references require an ordered append-only fingerprint catalog, not an unordered set')
    ordered: list[str] = []
    seen: set[str] = set()
    for fingerprint in known_fingerprints:
        normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
        if normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def fingerprint_catalog_lookup(known_fingerprints: list[str] | tuple[str, ...]) -> dict[str, int]:
    return {fingerprint: index for index, fingerprint in enumerate(ordered_fingerprint_catalog(known_fingerprints))}


def _fingerprint_digest_bytes(fingerprint: str) -> bytes:
    return bytes.fromhex(_normalize_fingerprint(fingerprint))


def _fingerprint_from_digest_bytes(raw: bytes) -> str:
    if not isinstance(raw, (bytes, bytearray)) or len(raw) != 32:
        raise PacketError(f'fingerprint digest payloads must be exactly 32 bytes, got {len(raw) if isinstance(raw, (bytes, bytearray)) else raw!r}')
    return 'sha256:' + bytes(raw).hex()


def fingerprint_catalog_page(
    fingerprints: list[str] | tuple[str, ...],
) -> str:
    ordered = ordered_fingerprint_catalog(fingerprints)
    if not ordered:
        raise PacketError('fingerprint catalog pages must contain at least one ordered fingerprint')
    raw = bytearray([FINGERPRINT_CATALOG_PAGE_TAG])
    for fingerprint in ordered:
        raw.extend(_fingerprint_digest_bytes(fingerprint))
    return _base64url_encode_bytes(bytes(raw))


def _decode_fingerprint_catalog_page_payload(page: str) -> tuple[bytes, int]:
    raw = _base64url_decode_bytes(page)
    if not raw or raw[0] != FINGERPRINT_CATALOG_PAGE_TAG:
        raise PacketError(f'unsupported fingerprint catalog page tag: {raw[0] if raw else None}')
    payload = raw[1:]
    if not payload or len(payload) % 32 != 0:
        raise PacketError('fingerprint catalog page payload must contain a non-empty whole-number count of 32-byte digests')
    return payload, len(payload) // 32



def expand_fingerprint_catalog_page(page: str) -> list[str]:
    payload, entry_count = _decode_fingerprint_catalog_page_payload(page)
    return [
        _fingerprint_from_digest_bytes(payload[offset : offset + 32])
        for offset in range(0, entry_count * 32, 32)
    ]



def fingerprint_catalog_pages(
    known_fingerprints: list[str] | tuple[str, ...],
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> list[str]:
    ordered = ordered_fingerprint_catalog(known_fingerprints)
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    if not ordered:
        return []
    return [
        fingerprint_catalog_page(ordered[offset : offset + page_size])
        for offset in range(0, len(ordered), page_size)
    ]



def expand_fingerprint_catalog_pages(pages: list[str] | tuple[str, ...]) -> list[str]:
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    ordered: list[str] = []
    seen: set[str] = set()
    for page in pages:
        for fingerprint in expand_fingerprint_catalog_page(page):
            if fingerprint in seen:
                raise PacketError(f'duplicate fingerprint {fingerprint} encountered while expanding paged catalog')
            seen.add(fingerprint)
            ordered.append(fingerprint)
    return ordered



def fingerprint_catalog_lookup_from_pages(pages: list[str] | tuple[str, ...]) -> dict[str, int]:
    return {fingerprint: index for index, fingerprint in enumerate(expand_fingerprint_catalog_pages(pages))}



def find_fingerprint_catalog_slot_from_pages(
    fingerprint: str,
    pages: list[str] | tuple[str, ...],
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> int | None:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    slot_base = 0
    for page_index, page in enumerate(pages):
        payload, entry_count = _decode_fingerprint_catalog_page_payload(page)
        if entry_count > page_size:
            raise PacketError(
                f'catalog page {page_index} exceeds configured page_size {page_size} with {entry_count} entries'
            )
        if page_index < len(pages) - 1 and entry_count != page_size:
            raise PacketError(
                f'catalog page {page_index} must contain exactly {page_size} entries before the tail page, got {entry_count}'
            )
        for entry_index in range(entry_count):
            start = entry_index * 32
            if payload[start : start + 32] == target_digest:
                return slot_base + entry_index
        slot_base += entry_count
    return None



def fingerprint_catalog_page_filter(page: str) -> str:
    payload, entry_count = _decode_fingerprint_catalog_page_payload(page)
    if entry_count > 0xFF:
        raise PacketError(f'fingerprint catalog page filters only support up to 255 entries per page, got {entry_count}')
    mask = bytearray(32)
    for offset in range(0, entry_count * 32, 32):
        value = payload[offset]
        mask[value >> 3] |= 1 << (value & 7)
    return _base64url_encode_bytes(bytes([FINGERPRINT_CATALOG_PAGE_FILTER_TAG, entry_count]) + bytes(mask))



def _decode_fingerprint_catalog_page_filter_payload(page_filter: str) -> tuple[int, bytes]:
    raw = _base64url_decode_bytes(page_filter)
    if not raw or raw[0] != FINGERPRINT_CATALOG_PAGE_FILTER_TAG:
        raise PacketError(f'unsupported fingerprint catalog page-filter tag: {raw[0] if raw else None}')
    if len(raw) != 34:
        raise PacketError(f'fingerprint catalog page filters must be 34 raw bytes, got {len(raw)}')
    entry_count = raw[1]
    if entry_count <= 0:
        raise PacketError('fingerprint catalog page filters must encode at least one entry')
    return entry_count, raw[2:]



def fingerprint_catalog_page_filters(pages: list[str] | tuple[str, ...]) -> list[str]:
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog page filters must be provided as a list or tuple of page-filter payloads')
    return [fingerprint_catalog_page_filter(page) for page in pages]



def fingerprint_catalog_page_filter_entry_count(page_filter: str) -> int:
    entry_count, _ = _decode_fingerprint_catalog_page_filter_payload(page_filter)
    return entry_count



def fingerprint_catalog_page_filter_might_contain(
    fingerprint: str,
    page_filter: str,
) -> bool:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    _, mask = _decode_fingerprint_catalog_page_filter_payload(page_filter)
    value = target_digest[0]
    return bool(mask[value >> 3] & (1 << (value & 7)))



def append_fingerprint_catalog_page_filters(
    page_filters: list[str] | tuple[str, ...],
    fingerprint: str,
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> list[str]:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    if not isinstance(page_size, int) or page_size <= 0 or page_size > 0xFF:
        raise PacketError(
            f'fingerprint catalog page filters require a page_size between 1 and 255 entries, got {page_size!r}'
        )
    if not isinstance(page_filters, (list, tuple)):
        raise PacketError('fingerprint catalog page filters must be provided as a list or tuple of page-filter payloads')
    materialized = list(page_filters) if isinstance(page_filters, tuple) else page_filters.copy()
    if not materialized:
        mask = bytearray(32)
        value = target_digest[0]
        mask[value >> 3] |= 1 << (value & 7)
        return [_base64url_encode_bytes(bytes([FINGERPRINT_CATALOG_PAGE_FILTER_TAG, 1]) + bytes(mask))]
    tail_count, tail_mask = _decode_fingerprint_catalog_page_filter_payload(materialized[-1])
    if tail_count < page_size:
        updated_mask = bytearray(tail_mask)
        value = target_digest[0]
        updated_mask[value >> 3] |= 1 << (value & 7)
        materialized[-1] = _base64url_encode_bytes(
            bytes([FINGERPRINT_CATALOG_PAGE_FILTER_TAG, tail_count + 1]) + bytes(updated_mask)
        )
        return materialized
    mask = bytearray(32)
    value = target_digest[0]
    mask[value >> 3] |= 1 << (value & 7)
    materialized.append(_base64url_encode_bytes(bytes([FINGERPRINT_CATALOG_PAGE_FILTER_TAG, 1]) + bytes(mask)))
    return materialized



def _fingerprint_catalog_route_block_bitmap_len(page_count: int) -> int:
    if not isinstance(page_count, int) or page_count <= 0:
        raise PacketError(f'fingerprint catalog route blocks require a positive page_count, got {page_count!r}')
    return (page_count + 7) // 8



def _fingerprint_catalog_route_block_bitmap_pages(bitmap: bytes, page_count: int) -> list[int]:
    pages: list[int] = []
    for page_index in range(page_count):
        if bitmap[page_index >> 3] & (1 << (page_index & 7)):
            pages.append(page_index)
    return pages



def fingerprint_catalog_page_route_block(
    pages: list[str] | tuple[str, ...],
    block_index: int,
) -> str:
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    if not isinstance(block_index, int) or block_index < 0 or block_index >= (256 // FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE):
        raise PacketError(f'fingerprint catalog route block index must be between 0 and 15, got {block_index!r}')
    page_count = len(pages)
    bitmap_len = _fingerprint_catalog_route_block_bitmap_len(page_count)
    bitmaps = [bytearray(bitmap_len) for _ in range(FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE)]
    for page_index, page in enumerate(pages):
        payload, entry_count = _decode_fingerprint_catalog_page_payload(page)
        for offset in range(0, entry_count * 32, 32):
            value = payload[offset]
            if value >> 4 != block_index:
                continue
            low_nibble = value & 0x0F
            bitmaps[low_nibble][page_index >> 3] |= 1 << (page_index & 7)
    raw = bytearray([FINGERPRINT_CATALOG_PAGE_ROUTE_BLOCK_TAG, block_index])
    for bitmap in bitmaps:
        raw.extend(bitmap)
    return _base64url_encode_bytes(bytes(raw))



def _decode_fingerprint_catalog_page_route_block_payload(
    route_block: str,
    *,
    page_count: int,
) -> tuple[int, list[bytes]]:
    bitmap_len = _fingerprint_catalog_route_block_bitmap_len(page_count)
    raw = _base64url_decode_bytes(route_block)
    if not raw or raw[0] != FINGERPRINT_CATALOG_PAGE_ROUTE_BLOCK_TAG:
        raise PacketError(f'unsupported fingerprint catalog route-block tag: {raw[0] if raw else None}')
    expected_len = 2 + FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE * bitmap_len
    if len(raw) != expected_len:
        raise PacketError(
            f'fingerprint catalog route block for page_count {page_count} must be {expected_len} raw bytes, got {len(raw)}'
        )
    block_index = raw[1]
    if block_index >= (256 // FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE):
        raise PacketError(f'unsupported fingerprint catalog route block index: {block_index}')
    payload = raw[2:]
    bitmaps = [
        payload[offset : offset + bitmap_len]
        for offset in range(0, len(payload), bitmap_len)
    ]
    if len(bitmaps) != FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE:
        raise PacketError(
            f'fingerprint catalog route block must contain {FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE} page bitmaps, got {len(bitmaps)}'
        )
    return block_index, bitmaps



def fingerprint_catalog_page_route_blocks(pages: list[str] | tuple[str, ...]) -> list[str]:
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    if not pages:
        return []
    return [
        fingerprint_catalog_page_route_block(pages, block_index)
        for block_index in range(256 // FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE)
    ]



def fingerprint_catalog_route_block_candidate_pages(
    fingerprint: str,
    route_blocks: list[str] | tuple[str, ...],
    *,
    page_count: int,
) -> list[int]:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    if not isinstance(route_blocks, (list, tuple)):
        raise PacketError('fingerprint catalog route blocks must be provided as a list or tuple of route-block payloads')
    expected_blocks = 256 // FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE
    if len(route_blocks) != expected_blocks:
        raise PacketError(
            f'fingerprint catalog route blocks must contain exactly {expected_blocks} blocks, got {len(route_blocks)}'
        )
    block_index = target_digest[0] >> 4
    decoded_block_index, bitmaps = _decode_fingerprint_catalog_page_route_block_payload(
        route_blocks[block_index],
        page_count=page_count,
    )
    if decoded_block_index != block_index:
        raise PacketError(
            f'fingerprint catalog route block {block_index} decoded as block {decoded_block_index}'
        )
    return _fingerprint_catalog_route_block_bitmap_pages(bitmaps[target_digest[0] & 0x0F], page_count)



def append_fingerprint_catalog_page_route_blocks(
    route_blocks: list[str] | tuple[str, ...],
    pages: list[str] | tuple[str, ...],
    fingerprint: str,
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> list[str]:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog route blocks require a positive page_size, got {page_size!r}')
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    if not pages:
        return fingerprint_catalog_page_route_blocks(fingerprint_catalog_pages([normalized], page_size=page_size))
    materialized = list(route_blocks) if isinstance(route_blocks, tuple) else route_blocks.copy()
    expected_blocks = 256 // FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE
    if len(materialized) != expected_blocks:
        raise PacketError(
            f'fingerprint catalog route blocks must contain exactly {expected_blocks} blocks, got {len(materialized)}'
        )
    tail_payload, tail_entry_count = _decode_fingerprint_catalog_page_payload(pages[-1])
    if tail_entry_count > page_size:
        raise PacketError(
            f'catalog tail page exceeds configured page_size {page_size} with {tail_entry_count} entries'
        )
    page_count_before = len(pages)
    target_page_index = page_count_before - 1 if tail_entry_count < page_size else page_count_before
    page_count_after = target_page_index + 1
    bitmap_len_before = _fingerprint_catalog_route_block_bitmap_len(page_count_before)
    bitmap_len_after = _fingerprint_catalog_route_block_bitmap_len(page_count_after)
    block_index = target_digest[0] >> 4
    low_nibble = target_digest[0] & 0x0F
    if bitmap_len_after != bitmap_len_before:
        rebuilt_pages = append_fingerprint_catalog_pages(pages, normalized, page_size=page_size)
        return fingerprint_catalog_page_route_blocks(rebuilt_pages)
    decoded_block_index, bitmaps = _decode_fingerprint_catalog_page_route_block_payload(
        materialized[block_index],
        page_count=page_count_before,
    )
    if decoded_block_index != block_index:
        raise PacketError(
            f'fingerprint catalog route block {block_index} decoded as block {decoded_block_index}'
        )
    updated = bytearray(bitmaps[low_nibble])
    updated[target_page_index >> 3] |= 1 << (target_page_index & 7)
    bitmaps[low_nibble] = bytes(updated)
    raw = bytearray([FINGERPRINT_CATALOG_PAGE_ROUTE_BLOCK_TAG, block_index])
    for bitmap in bitmaps:
        raw.extend(bitmap)
    materialized[block_index] = _base64url_encode_bytes(bytes(raw))
    return materialized



def find_fingerprint_catalog_slot_from_pages_with_route_blocks(
    fingerprint: str,
    pages: list[str] | tuple[str, ...],
    route_blocks: list[str] | tuple[str, ...],
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> int | None:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    candidate_pages = fingerprint_catalog_route_block_candidate_pages(
        normalized,
        route_blocks,
        page_count=len(pages),
    )
    for page_index in candidate_pages:
        page = pages[page_index]
        payload, entry_count = _decode_fingerprint_catalog_page_payload(page)
        if entry_count > page_size:
            raise PacketError(
                f'catalog page {page_index} exceeds configured page_size {page_size} with {entry_count} entries'
            )
        if page_index < len(pages) - 1 and entry_count != page_size:
            raise PacketError(
                f'catalog page {page_index} must contain exactly {page_size} entries before the tail page, got {entry_count}'
            )
        slot_base = page_index * page_size
        for entry_index in range(entry_count):
            start = entry_index * 32
            if payload[start : start + 32] == target_digest:
                return slot_base + entry_index
    return None



def _fingerprint_catalog_page_lookup_bytes(
    fingerprint: str,
    pages: list[str] | tuple[str, ...],
    page_bytes: list[int],
) -> tuple[int, int | None]:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    if len(page_bytes) != len(pages):
        raise PacketError(f'page-bytes metadata must align one-to-one with pages, got {len(page_bytes)} values for {len(pages)} pages')
    slot_base = 0
    bytes_touched = 0
    for page_index, page in enumerate(pages):
        bytes_touched += page_bytes[page_index]
        payload, entry_count = _decode_fingerprint_catalog_page_payload(page)
        for entry_index in range(entry_count):
            start = entry_index * 32
            if payload[start : start + 32] == target_digest:
                return bytes_touched, slot_base + entry_index
        slot_base += entry_count
    return bytes_touched, None



def _fingerprint_catalog_page_filter_lookup_bytes(
    fingerprint: str,
    pages: list[str] | tuple[str, ...],
    page_filters: list[str] | tuple[str, ...],
    page_bytes: list[int],
    filter_bytes: list[int],
) -> tuple[int, int, int | None]:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    if not isinstance(page_filters, (list, tuple)):
        raise PacketError('fingerprint catalog page filters must be provided as a list or tuple of page-filter payloads')
    if len(page_filters) != len(pages):
        raise PacketError(
            f'fingerprint catalog page filters must align one-to-one with pages, got {len(page_filters)} filters for {len(pages)} pages'
        )
    if len(page_bytes) != len(pages):
        raise PacketError(f'page-bytes metadata must align one-to-one with pages, got {len(page_bytes)} values for {len(pages)} pages')
    if len(filter_bytes) != len(page_filters):
        raise PacketError(
            f'page-filter byte metadata must align one-to-one with page filters, got {len(filter_bytes)} values for {len(page_filters)} filters'
        )
    value = target_digest[0]
    slot_base = 0
    bytes_touched = 0
    false_positive_pages = 0
    for page_index, (page, page_filter) in enumerate(zip(pages, page_filters)):
        bytes_touched += filter_bytes[page_index]
        entry_count, mask = _decode_fingerprint_catalog_page_filter_payload(page_filter)
        if not mask[value >> 3] & (1 << (value & 7)):
            slot_base += entry_count
            continue
        bytes_touched += page_bytes[page_index]
        payload, payload_entry_count = _decode_fingerprint_catalog_page_payload(page)
        if payload_entry_count != entry_count:
            raise PacketError(
                f'catalog page {page_index} entry count {payload_entry_count} does not match page filter count {entry_count}'
            )
        for entry_index in range(entry_count):
            start = entry_index * 32
            if payload[start : start + 32] == target_digest:
                return bytes_touched, false_positive_pages, slot_base + entry_index
        false_positive_pages += 1
        slot_base += entry_count
    return bytes_touched, false_positive_pages, None



def _fingerprint_catalog_route_block_lookup_bytes(
    fingerprint: str,
    pages: list[str] | tuple[str, ...],
    route_blocks: list[str] | tuple[str, ...],
    page_bytes: list[int],
    route_block_bytes: list[int],
) -> tuple[int, int, int | None]:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    if not isinstance(route_blocks, (list, tuple)):
        raise PacketError('fingerprint catalog route blocks must be provided as a list or tuple of route-block payloads')
    if len(page_bytes) != len(pages):
        raise PacketError(f'page-bytes metadata must align one-to-one with pages, got {len(page_bytes)} values for {len(pages)} pages')
    expected_blocks = 256 // FINGERPRINT_CATALOG_ROUTE_BLOCK_STRIDE
    if len(route_blocks) != expected_blocks:
        raise PacketError(
            f'fingerprint catalog route blocks must contain exactly {expected_blocks} blocks, got {len(route_blocks)}'
        )
    if len(route_block_bytes) != len(route_blocks):
        raise PacketError(
            f'route-block byte metadata must align one-to-one with route blocks, got {len(route_block_bytes)} values for {len(route_blocks)} blocks'
        )
    block_index = target_digest[0] >> 4
    bytes_touched = route_block_bytes[block_index]
    false_positive_pages = 0
    slot_base_by_page: list[int] = []
    slot_base = 0
    for page in pages:
        slot_base_by_page.append(slot_base)
        slot_base += _decode_fingerprint_catalog_page_payload(page)[1]
    candidate_pages = fingerprint_catalog_route_block_candidate_pages(
        normalized,
        route_blocks,
        page_count=len(pages),
    )
    for page_index in candidate_pages:
        bytes_touched += page_bytes[page_index]
        payload, entry_count = _decode_fingerprint_catalog_page_payload(pages[page_index])
        for entry_index in range(entry_count):
            start = entry_index * 32
            if payload[start : start + 32] == target_digest:
                return bytes_touched, false_positive_pages, slot_base_by_page[page_index] + entry_index
        false_positive_pages += 1
    return bytes_touched, false_positive_pages, None



def fingerprint_catalog_compact_repeat_state_metrics(
    pages: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    if not isinstance(pages, (list, tuple)) or not pages:
        raise PacketError('compact repeat-state metrics require a non-empty list or tuple of fingerprint catalog pages')
    fingerprints = expand_fingerprint_catalog_pages(pages)
    if not fingerprints:
        raise PacketError('compact repeat-state metrics require at least one fingerprint in the paged catalog')
    page_filters = fingerprint_catalog_page_filters(pages)
    route_blocks = fingerprint_catalog_page_route_blocks(pages)
    page_bytes = [packet_minified_bytes(page) for page in pages]
    filter_bytes = [packet_minified_bytes(page_filter) for page_filter in page_filters]
    route_block_bytes = [packet_minified_bytes(route_block) for route_block in route_blocks]

    total_page_lookup_bytes = 0
    total_filter_lookup_bytes = 0
    total_route_lookup_bytes = 0
    total_filter_false_positive_pages = 0
    total_route_false_positive_pages = 0

    for fingerprint in fingerprints:
        page_lookup_bytes, page_slot = _fingerprint_catalog_page_lookup_bytes(fingerprint, pages, page_bytes)
        filter_lookup_bytes, filter_false_positive_pages, filter_slot = _fingerprint_catalog_page_filter_lookup_bytes(
            fingerprint,
            pages,
            page_filters,
            page_bytes,
            filter_bytes,
        )
        route_lookup_bytes, route_false_positive_pages, route_slot = _fingerprint_catalog_route_block_lookup_bytes(
            fingerprint,
            pages,
            route_blocks,
            page_bytes,
            route_block_bytes,
        )
        if page_slot is None or filter_slot is None or route_slot is None:
            raise PacketError('compact repeat-state metrics could not resolve a known fingerprint from one of the compact states')
        if page_slot != filter_slot or filter_slot != route_slot:
            raise PacketError(
                f'compact repeat-state metrics resolved inconsistent slots for {fingerprint}: '
                f'page={page_slot}, filters={filter_slot}, route_blocks={route_slot}'
            )
        total_page_lookup_bytes += page_lookup_bytes
        total_filter_lookup_bytes += filter_lookup_bytes
        total_route_lookup_bytes += route_lookup_bytes
        total_filter_false_positive_pages += filter_false_positive_pages
        total_route_false_positive_pages += route_false_positive_pages

    entry_count = len(fingerprints)
    rows = {
        'paged_catalog_only': {
            'kind': 'paged_catalog_only',
            'compact_state_bytes': packet_minified_bytes(pages),
            'average_repeat_lookup_bytes': round(total_page_lookup_bytes / entry_count, 6),
            'average_false_positive_pages_before_hit': 0.0,
        },
        'paged_catalog_with_filters': {
            'kind': 'paged_catalog_with_filters',
            'compact_state_bytes': packet_minified_bytes(pages) + packet_minified_bytes(page_filters),
            'average_repeat_lookup_bytes': round(total_filter_lookup_bytes / entry_count, 6),
            'average_false_positive_pages_before_hit': round(total_filter_false_positive_pages / entry_count, 6),
        },
        'paged_catalog_with_route_blocks': {
            'kind': 'paged_catalog_with_route_blocks',
            'compact_state_bytes': packet_minified_bytes(pages) + packet_minified_bytes(route_blocks),
            'average_repeat_lookup_bytes': round(total_route_lookup_bytes / entry_count, 6),
            'average_false_positive_pages_before_hit': round(total_route_false_positive_pages / entry_count, 6),
        },
    }
    for kind in COMPACT_REPEAT_STATE_KINDS:
        row = rows[kind]
        row['combined_state_plus_one_repeat_objective'] = round(
            row['compact_state_bytes'] + row['average_repeat_lookup_bytes'],
            6,
        )
    return {
        'entry_count': entry_count,
        'page_count': len(pages),
        'page_bytes': page_bytes,
        'page_filter_bytes': filter_bytes,
        'route_block_bytes': route_block_bytes,
        'rows': rows,
    }



def compact_repeat_state_break_even_repeat_lookups(
    baseline_compact_state_bytes: int,
    baseline_average_repeat_lookup_bytes: float,
    candidate_compact_state_bytes: int,
    candidate_average_repeat_lookup_bytes: float,
) -> float | None:
    lookup_savings = baseline_average_repeat_lookup_bytes - candidate_average_repeat_lookup_bytes
    if lookup_savings <= 0:
        return None
    state_delta = candidate_compact_state_bytes - baseline_compact_state_bytes
    if state_delta <= 0:
        return 0.0
    return round(state_delta / lookup_savings, 6)



def recommend_fingerprint_catalog_compact_repeat_state_from_metrics(
    metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float = 1.0,
) -> dict[str, Any]:
    if expected_repeat_lookups < 0:
        raise PacketError(f'expected_repeat_lookups must be non-negative, got {expected_repeat_lookups!r}')
    if not isinstance(metrics, dict) or 'rows' not in metrics:
        raise PacketError('compact repeat-state recommendation requires metrics with row data')
    scored_rows = []
    for kind in COMPACT_REPEAT_STATE_KINDS:
        row = metrics['rows'][kind]
        objective = row['compact_state_bytes'] + expected_repeat_lookups * row['average_repeat_lookup_bytes']
        scored_rows.append({
            'kind': kind,
            'compact_state_bytes': row['compact_state_bytes'],
            'average_repeat_lookup_bytes': row['average_repeat_lookup_bytes'],
            'combined_objective': round(objective, 6),
        })
    ranked_rows = sorted(
        scored_rows,
        key=lambda row: (row['combined_objective'], row['average_repeat_lookup_bytes'], row['compact_state_bytes'], row['kind']),
    )
    winner = ranked_rows[0]
    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'recommended_state_kind': winner['kind'],
        'combined_objective': winner['combined_objective'],
        'candidates': ranked_rows,
        'why': (
            'choose the compact repeat sidecar that minimizes '
            'compact_state_bytes + expected_repeat_lookups * average_repeat_lookup_bytes '
            'for the current paged digest catalog'
        ),
    }



def recommend_fingerprint_catalog_compact_repeat_state(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float = 1.0,
) -> dict[str, Any]:
    metrics = fingerprint_catalog_compact_repeat_state_metrics(pages)
    return recommend_fingerprint_catalog_compact_repeat_state_from_metrics(
        metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )



def project_fingerprint_catalog_pages(
    pages: list[str] | tuple[str, ...],
    *,
    unique_append_count: int = 0,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> list[str]:
    if not isinstance(unique_append_count, int) or unique_append_count < 0:
        raise PacketError(f'unique_append_count must be a non-negative integer, got {unique_append_count!r}')
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    if not isinstance(pages, (list, tuple)) or not pages:
        raise PacketError('projected fingerprint catalog pages require a non-empty list or tuple of page payloads')
    projected_pages = list(pages) if isinstance(pages, tuple) else pages.copy()
    known_fingerprints = set(expand_fingerprint_catalog_pages(projected_pages))
    for growth_index in range(1, unique_append_count + 1):
        fingerprint = _synthetic_unique_growth_fingerprint(known_fingerprints, growth_index)
        known_fingerprints.add(fingerprint)
        projected_pages = append_fingerprint_catalog_pages(projected_pages, fingerprint, page_size=page_size)
    return projected_pages




def fingerprint_catalog_compact_repeat_state_horizon_metrics(
    pages: list[str] | tuple[str, ...],
    *,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    if not isinstance(max_unique_appends, int) or max_unique_appends < 0:
        raise PacketError(f'max_unique_appends must be a non-negative integer, got {max_unique_appends!r}')
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    if not isinstance(pages, (list, tuple)) or not pages:
        raise PacketError('compact repeat-state horizon metrics require a non-empty list or tuple of fingerprint catalog pages')

    append_rows: list[dict[str, Any]] = []
    for unique_append_count in range(0, max_unique_appends + 1):
        projected_pages = project_fingerprint_catalog_pages(
            pages,
            unique_append_count=unique_append_count,
            page_size=page_size,
        )
        metrics = fingerprint_catalog_compact_repeat_state_metrics(projected_pages)
        append_rows.append({
            'unique_append_count': unique_append_count,
            'entry_count': metrics['entry_count'],
            'page_count': metrics['page_count'],
            'tail_entry_count': fingerprint_catalog_page_entry_count(projected_pages[-1]),
            'route_block_bitmap_len': _fingerprint_catalog_route_block_bitmap_len(metrics['page_count']),
            'rows': {
                kind: {
                    'compact_state_bytes': metrics['rows'][kind]['compact_state_bytes'],
                    'average_repeat_lookup_bytes': metrics['rows'][kind]['average_repeat_lookup_bytes'],
                }
                for kind in COMPACT_REPEAT_STATE_KINDS
            },
        })

    return {
        'max_unique_appends': max_unique_appends,
        'entry_count': len(expand_fingerprint_catalog_pages(pages)),
        'page_count': len(pages),
        'tail_entry_count': fingerprint_catalog_page_entry_count(pages[-1]),
        'route_block_bitmap_len': _fingerprint_catalog_route_block_bitmap_len(len(pages)),
        'append_rows': append_rows,
    }



def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float,
) -> dict[str, Any]:
    if expected_repeat_lookups < 0:
        raise PacketError(f'expected_repeat_lookups must be non-negative, got {expected_repeat_lookups!r}')
    if not isinstance(horizon_metrics, dict) or 'append_rows' not in horizon_metrics:
        raise PacketError('compact repeat-state horizon policy requires horizon metrics with append_rows')

    append_rows = horizon_metrics['append_rows']
    dynamic_total_objective = 0.0
    dynamic_state_counts = {kind: 0 for kind in COMPACT_REPEAT_STATE_KINDS}
    dynamic_interval_rows: list[dict[str, Any]] = []
    fixed_totals = {kind: 0.0 for kind in COMPACT_REPEAT_STATE_KINDS}
    previous_kind: str | None = None
    current_interval: dict[str, Any] | None = None

    for row in append_rows:
        scored_rows = []
        for kind in COMPACT_REPEAT_STATE_KINDS:
            state_row = row['rows'][kind]
            objective = state_row['compact_state_bytes'] + expected_repeat_lookups * state_row['average_repeat_lookup_bytes']
            scored_rows.append({
                'kind': kind,
                'combined_objective': round(objective, 6),
                'compact_state_bytes': state_row['compact_state_bytes'],
                'average_repeat_lookup_bytes': state_row['average_repeat_lookup_bytes'],
            })
            fixed_totals[kind] += objective
        ranked_rows = sorted(
            scored_rows,
            key=lambda scored: (
                scored['combined_objective'],
                scored['average_repeat_lookup_bytes'],
                scored['compact_state_bytes'],
                scored['kind'],
            ),
        )
        winner = ranked_rows[0]
        recommended_kind = winner['kind']
        dynamic_total_objective += winner['combined_objective']
        dynamic_state_counts[recommended_kind] += 1

        if current_interval is None:
            current_interval = {
                'start_unique_appends': row['unique_append_count'],
                'recommended_state_kind': recommended_kind,
                'start_page_count': row['page_count'],
                'start_tail_entry_count': row['tail_entry_count'],
                'start_route_block_bitmap_len': row['route_block_bitmap_len'],
            }
        elif recommended_kind != previous_kind:
            current_interval['end_unique_appends'] = row['unique_append_count'] - 1
            dynamic_interval_rows.append(current_interval)
            current_interval = {
                'start_unique_appends': row['unique_append_count'],
                'recommended_state_kind': recommended_kind,
                'start_page_count': row['page_count'],
                'start_tail_entry_count': row['tail_entry_count'],
                'start_route_block_bitmap_len': row['route_block_bitmap_len'],
            }
        previous_kind = recommended_kind

    if current_interval is None:
        raise PacketError('compact repeat-state horizon policy could not establish an interval for the provided metrics')
    current_interval['end_unique_appends'] = append_rows[-1]['unique_append_count']
    dynamic_interval_rows.append(current_interval)

    fixed_rows = []
    for kind in COMPACT_REPEAT_STATE_KINDS:
        fixed_rows.append({
            'state_kind': kind,
            'cumulative_objective': round(fixed_totals[kind], 6),
        })
    fixed_rows.sort(key=lambda row: (row['cumulative_objective'], row['state_kind']))
    best_fixed = fixed_rows[0]
    best_fixed_regret = round(best_fixed['cumulative_objective'] - dynamic_total_objective, 6)

    for row in fixed_rows:
        regret = round(row['cumulative_objective'] - dynamic_total_objective, 6)
        if abs(regret) <= 1e-6:
            regret = 0.0
        row['regret_vs_dynamic'] = regret
        row['regret_per_append_state'] = round(regret / len(append_rows), 6)
        row['regret_share_of_dynamic_objective'] = round(regret / dynamic_total_objective, 6) if dynamic_total_objective else 0.0
        row['exact_dynamic_match'] = regret == 0.0

    dynamic_total_objective = round(dynamic_total_objective, 6)
    dynamic_transition_count = max(0, len(dynamic_interval_rows) - 1)
    transition_penalty_break_even_per_switch_bytes = (
        round(best_fixed_regret / dynamic_transition_count, 6)
        if dynamic_transition_count > 0
        else None
    )

    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'max_unique_appends': horizon_metrics['max_unique_appends'],
        'entry_count': horizon_metrics['entry_count'],
        'page_count': horizon_metrics['page_count'],
        'tail_entry_count': horizon_metrics['tail_entry_count'],
        'route_block_bitmap_len': horizon_metrics['route_block_bitmap_len'],
        'dynamic_total_objective': dynamic_total_objective,
        'dynamic_state_counts': dynamic_state_counts,
        'dynamic_interval_rows': dynamic_interval_rows,
        'dynamic_transition_count': dynamic_transition_count,
        'best_fixed_state_kind': best_fixed['state_kind'],
        'best_fixed_total_objective': best_fixed['cumulative_objective'],
        'best_fixed_regret_vs_dynamic': best_fixed_regret,
        'best_fixed_regret_per_append_state': round(best_fixed_regret / len(append_rows), 6),
        'best_fixed_regret_share_of_dynamic_objective': round(best_fixed_regret / dynamic_total_objective, 6) if dynamic_total_objective else 0.0,
        'transition_penalty_break_even_total_bytes': best_fixed_regret,
        'transition_penalty_break_even_per_switch_bytes': transition_penalty_break_even_per_switch_bytes,
        'fixed_rows': fixed_rows,
        'why': (
            'compare the fully restaged dynamic compact repeat-state objective against the best single fixed sidecar '
            'over the whole novel-append horizon so the archive can trade sidecar churn against measured regret'
        ),
    }



def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    horizon_metrics = fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=max_unique_appends,
        page_size=page_size,
    )
    return recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )



def _fingerprint_catalog_compact_repeat_state_interval_rows_from_sequence(
    append_rows: list[dict[str, Any]],
    state_sequence: list[str] | tuple[str, ...],
) -> list[dict[str, Any]]:
    if not append_rows:
        return []
    if len(state_sequence) != len(append_rows):
        raise PacketError(
            f'compact repeat-state sequence length must match append_rows length, got {len(state_sequence)} values for {len(append_rows)} rows'
        )

    interval_rows: list[dict[str, Any]] = []
    interval_start = 0
    for row_index in range(1, len(state_sequence) + 1):
        if row_index < len(state_sequence) and state_sequence[row_index] == state_sequence[interval_start]:
            continue
        start_row = append_rows[interval_start]
        end_row = append_rows[row_index - 1]
        interval_rows.append({
            'start_unique_appends': start_row['unique_append_count'],
            'end_unique_appends': end_row['unique_append_count'],
            'recommended_state_kind': state_sequence[interval_start],
            'start_page_count': start_row['page_count'],
            'end_page_count': end_row['page_count'],
            'start_tail_entry_count': start_row['tail_entry_count'],
            'end_tail_entry_count': end_row['tail_entry_count'],
            'start_route_block_bitmap_len': start_row['route_block_bitmap_len'],
            'end_route_block_bitmap_len': end_row['route_block_bitmap_len'],
        })
        interval_start = row_index
    return interval_rows



def _fingerprint_catalog_compact_repeat_state_transition_candidate_rows_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float,
) -> list[dict[str, Any]]:
    if expected_repeat_lookups < 0:
        raise PacketError(f'expected_repeat_lookups must be non-negative, got {expected_repeat_lookups!r}')
    if not isinstance(horizon_metrics, dict) or 'append_rows' not in horizon_metrics:
        raise PacketError('compact repeat-state transition candidates require horizon metrics with append_rows')

    append_rows = horizon_metrics['append_rows']
    if not append_rows:
        raise PacketError('compact repeat-state transition candidates require at least one append row')

    dp_costs: list[dict[str, dict[int, float]]] = []
    backpointers: list[dict[str, dict[int, tuple[str, int] | None]]] = []

    for row_index, row in enumerate(append_rows):
        row_costs: dict[str, dict[int, float]] = {}
        row_backpointers: dict[str, dict[int, tuple[str, int] | None]] = {}
        state_objectives = {
            kind: row['rows'][kind]['compact_state_bytes'] + expected_repeat_lookups * row['rows'][kind]['average_repeat_lookup_bytes']
            for kind in COMPACT_REPEAT_STATE_KINDS
        }
        for kind in COMPACT_REPEAT_STATE_KINDS:
            transition_costs: dict[int, float] = {}
            transition_backpointers: dict[int, tuple[str, int] | None] = {}
            if row_index == 0:
                transition_costs[0] = state_objectives[kind]
                transition_backpointers[0] = None
            else:
                for previous_kind in COMPACT_REPEAT_STATE_KINDS:
                    previous_costs = dp_costs[row_index - 1][previous_kind]
                    for previous_transition_count, previous_cost in previous_costs.items():
                        transition_count = previous_transition_count + (0 if previous_kind == kind else 1)
                        candidate_cost = previous_cost + state_objectives[kind]
                        incumbent_cost = transition_costs.get(transition_count)
                        incumbent_backpointer = transition_backpointers.get(transition_count)
                        candidate_backpointer = (previous_kind, previous_transition_count)
                        if incumbent_cost is None:
                            transition_costs[transition_count] = candidate_cost
                            transition_backpointers[transition_count] = candidate_backpointer
                            continue
                        incumbent_tiebreak = (
                            incumbent_cost,
                            0 if incumbent_backpointer is not None and incumbent_backpointer[0] == kind else 1,
                            incumbent_backpointer[0] if incumbent_backpointer is not None else '',
                        )
                        candidate_tiebreak = (
                            candidate_cost,
                            0 if previous_kind == kind else 1,
                            previous_kind,
                        )
                        if candidate_tiebreak < incumbent_tiebreak:
                            transition_costs[transition_count] = candidate_cost
                            transition_backpointers[transition_count] = candidate_backpointer
            row_costs[kind] = transition_costs
            row_backpointers[kind] = transition_backpointers
        dp_costs.append(row_costs)
        backpointers.append(row_backpointers)

    best_by_transition_count: dict[int, dict[str, Any]] = {}
    for kind in COMPACT_REPEAT_STATE_KINDS:
        for transition_count, cumulative_objective in dp_costs[-1][kind].items():
            incumbent = best_by_transition_count.get(transition_count)
            candidate = {
                'transition_count': transition_count,
                'cumulative_objective_without_transition_penalty': round(cumulative_objective, 6),
                'end_state_kind': kind,
            }
            if incumbent is None or (
                candidate['cumulative_objective_without_transition_penalty'],
                candidate['end_state_kind'],
            ) < (
                incumbent['cumulative_objective_without_transition_penalty'],
                incumbent['end_state_kind'],
            ):
                best_by_transition_count[transition_count] = candidate

    candidate_rows: list[dict[str, Any]] = []
    for transition_count in sorted(best_by_transition_count):
        candidate = best_by_transition_count[transition_count]
        end_state_kind = candidate['end_state_kind']
        state_sequence: list[str] = []
        current_kind = end_state_kind
        current_transition_count = transition_count
        for row_index in range(len(append_rows) - 1, -1, -1):
            state_sequence.append(current_kind)
            previous = backpointers[row_index][current_kind][current_transition_count]
            if previous is None:
                break
            current_kind, current_transition_count = previous
        state_sequence.reverse()
        if len(state_sequence) != len(append_rows):
            raise PacketError(
                f'compact repeat-state transition reconstruction produced {len(state_sequence)} states for {len(append_rows)} append rows'
            )

        interval_rows = _fingerprint_catalog_compact_repeat_state_interval_rows_from_sequence(
            append_rows,
            state_sequence,
        )
        state_counts = {kind: state_sequence.count(kind) for kind in COMPACT_REPEAT_STATE_KINDS}
        candidate_rows.append({
            'transition_count': transition_count,
            'cumulative_objective_without_transition_penalty': candidate['cumulative_objective_without_transition_penalty'],
            'end_state_kind': end_state_kind,
            'state_counts': state_counts,
            'interval_rows': interval_rows,
        })
    return candidate_rows



def fingerprint_catalog_compact_repeat_state_switch_penalty_frontier_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float,
) -> dict[str, Any]:
    candidate_rows = _fingerprint_catalog_compact_repeat_state_transition_candidate_rows_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )

    frontier_rows: list[dict[str, Any]] = []
    for candidate in sorted(candidate_rows, key=lambda row: (-row['transition_count'], row['cumulative_objective_without_transition_penalty'])):
        row = candidate.copy()
        row['transition_penalty_start_bytes'] = 0.0
        while frontier_rows:
            previous = frontier_rows[-1]
            if previous['transition_count'] == row['transition_count']:
                if row['cumulative_objective_without_transition_penalty'] >= previous['cumulative_objective_without_transition_penalty']:
                    row = None
                    break
                frontier_rows.pop()
                continue
            intersection = (
                row['cumulative_objective_without_transition_penalty']
                - previous['cumulative_objective_without_transition_penalty']
            ) / (previous['transition_count'] - row['transition_count'])
            row['transition_penalty_start_bytes'] = round(intersection, 6)
            if row['transition_penalty_start_bytes'] <= previous['transition_penalty_start_bytes']:
                frontier_rows.pop()
                row['transition_penalty_start_bytes'] = 0.0
                continue
            break
        if row is None:
            continue
        if row['transition_penalty_start_bytes'] < 0:
            row['transition_penalty_start_bytes'] = 0.0
        frontier_rows.append(row)

    for index, row in enumerate(frontier_rows):
        row['transition_penalty_end_bytes'] = (
            frontier_rows[index + 1]['transition_penalty_start_bytes']
            if index + 1 < len(frontier_rows)
            else None
        )

    if not frontier_rows:
        raise PacketError('compact repeat-state switch-penalty frontier could not establish a non-empty frontier')

    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'max_unique_appends': horizon_metrics['max_unique_appends'],
        'entry_count': horizon_metrics['entry_count'],
        'page_count': horizon_metrics['page_count'],
        'tail_entry_count': horizon_metrics['tail_entry_count'],
        'route_block_bitmap_len': horizon_metrics['route_block_bitmap_len'],
        'frontier_rows': frontier_rows,
        'candidate_row_count': len(candidate_rows),
        'why': (
            'price each compact repeat-sidecar schedule as cumulative objective plus transition_penalty * switch_count '
            'so the archive can pick an exact churn-aware staging regime instead of relying on average switch regret alone'
        ),
    }



def fingerprint_catalog_compact_repeat_state_switch_penalty_frontier(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    horizon_metrics = fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=max_unique_appends,
        page_size=page_size,
    )
    return fingerprint_catalog_compact_repeat_state_switch_penalty_frontier_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )



def fingerprint_catalog_compact_repeat_state_transition_budget_frontier_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float,
) -> dict[str, Any]:
    candidate_rows = _fingerprint_catalog_compact_repeat_state_transition_candidate_rows_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )
    if not candidate_rows:
        raise PacketError('compact repeat-state transition-budget frontier could not establish any candidate rows')

    dynamic_row = min(
        candidate_rows,
        key=lambda row: (
            row['cumulative_objective_without_transition_penalty'],
            row['transition_count'],
            row['end_state_kind'],
        ),
    )
    budget_rows: list[dict[str, Any]] = []
    best_so_far: dict[str, Any] | None = None
    for max_transition_count in range(candidate_rows[-1]['transition_count'] + 1):
        selected_row = min(
            (row for row in candidate_rows if row['transition_count'] <= max_transition_count),
            key=lambda row: (
                row['cumulative_objective_without_transition_penalty'],
                row['transition_count'],
                row['end_state_kind'],
            ),
        )
        previous_objective = (
            best_so_far['cumulative_objective_without_transition_penalty']
            if best_so_far is not None
            else selected_row['cumulative_objective_without_transition_penalty']
        )
        budget_row = {
            'max_transition_count': max_transition_count,
            'selected_transition_count': selected_row['transition_count'],
            'cumulative_objective_without_transition_penalty': selected_row['cumulative_objective_without_transition_penalty'],
            'regret_vs_unbounded_dynamic': round(
                selected_row['cumulative_objective_without_transition_penalty']
                - dynamic_row['cumulative_objective_without_transition_penalty'],
                6,
            ),
            'objective_improvement_vs_previous_budget': round(
                previous_objective - selected_row['cumulative_objective_without_transition_penalty'],
                6,
            ),
            'end_state_kind': selected_row['end_state_kind'],
            'state_counts': selected_row['state_counts'],
            'interval_rows': selected_row['interval_rows'],
        }
        budget_rows.append(budget_row)
        best_so_far = budget_row

    frontier_rows: list[dict[str, Any]] = []
    for row in budget_rows:
        if frontier_rows and frontier_rows[-1]['selected_transition_count'] == row['selected_transition_count']:
            frontier_rows[-1]['budget_end_transition_count'] = row['max_transition_count']
            continue
        frontier_rows.append({
            **row,
            'budget_start_transition_count': row['max_transition_count'],
            'budget_end_transition_count': row['max_transition_count'],
        })

    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'max_unique_appends': horizon_metrics['max_unique_appends'],
        'entry_count': horizon_metrics['entry_count'],
        'page_count': horizon_metrics['page_count'],
        'tail_entry_count': horizon_metrics['tail_entry_count'],
        'route_block_bitmap_len': horizon_metrics['route_block_bitmap_len'],
        'dynamic_transition_count': dynamic_row['transition_count'],
        'dynamic_cumulative_objective_without_transition_penalty': dynamic_row['cumulative_objective_without_transition_penalty'],
        'frontier_rows': frontier_rows,
        'budget_rows': budget_rows,
        'candidate_row_count': len(candidate_rows),
        'why': (
            'price compact repeat-sidecar schedules under an explicit max-transition budget '
            'so the archive can spend a small number of rewrites on the highest-value state changes first'
        ),
    }



def fingerprint_catalog_compact_repeat_state_transition_budget_frontier(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    horizon_metrics = fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=max_unique_appends,
        page_size=page_size,
    )
    return fingerprint_catalog_compact_repeat_state_transition_budget_frontier_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )



def _fingerprint_catalog_compact_repeat_state_fixed_objective_from_append_rows(
    append_rows: list[dict[str, Any]],
    *,
    state_kind: str,
    expected_repeat_lookups: float,
) -> float:
    if state_kind not in COMPACT_REPEAT_STATE_KINDS:
        raise PacketError(f'unsupported compact repeat state kind {state_kind!r}')
    total = 0.0
    for row in append_rows:
        state_row = row['rows'][state_kind]
        total += state_row['compact_state_bytes'] + expected_repeat_lookups * state_row['average_repeat_lookup_bytes']
    return round(total, 6)


def _fingerprint_catalog_compact_repeat_state_interval_summary(
    interval_rows: list[dict[str, Any]],
) -> str:
    kind_labels = {
        'paged_catalog_only': 'pages',
        'paged_catalog_with_filters': 'filters',
        'paged_catalog_with_route_blocks': 'route-blocks',
    }
    return '; '.join(
        f"{kind_labels.get(row['recommended_state_kind'], row['recommended_state_kind'])} {row['start_unique_appends']}–{row['end_unique_appends']}"
        for row in interval_rows
    )


def _fingerprint_catalog_compact_repeat_state_min_interval_dwell_unique_appends(
    interval_rows: list[dict[str, Any]],
) -> int:
    if not interval_rows:
        raise PacketError('compact repeat-state minimum dwell requires at least one interval row')
    min_interval_dwell = min(
        row['end_unique_appends'] - row['start_unique_appends'] + 1
        for row in interval_rows
    )
    if min_interval_dwell <= 0:
        raise PacketError(f'compact repeat-state interval dwell must be positive, got {min_interval_dwell!r}')
    return min_interval_dwell


def _compact_repeat_state_preserved_gain_share(
    selected_gain_vs_fixed_route_blocks: float,
    full_dynamic_gain_vs_fixed_route_blocks: float,
) -> float:
    if full_dynamic_gain_vs_fixed_route_blocks <= 0:
        return 1.0 if selected_gain_vs_fixed_route_blocks >= full_dynamic_gain_vs_fixed_route_blocks else 0.0
    return round(
        max(0.0, min(1.0, selected_gain_vs_fixed_route_blocks / full_dynamic_gain_vs_fixed_route_blocks)),
        6,
    )


def fingerprint_catalog_compact_repeat_state_min_dwell_frontier_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float,
) -> dict[str, Any]:
    candidate_rows = _fingerprint_catalog_compact_repeat_state_transition_candidate_rows_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )
    if not candidate_rows:
        raise PacketError('compact repeat-state minimum-dwell frontier could not establish any candidate rows')

    dynamic_row = min(
        candidate_rows,
        key=lambda row: (
            row['cumulative_objective_without_transition_penalty'],
            row['transition_count'],
            row['end_state_kind'],
        ),
    )
    fixed_route_blocks_objective = _fingerprint_catalog_compact_repeat_state_fixed_objective_from_append_rows(
        horizon_metrics['append_rows'],
        state_kind='paged_catalog_with_route_blocks',
        expected_repeat_lookups=expected_repeat_lookups,
    )
    full_dynamic_gain_vs_fixed_route_blocks = round(
        fixed_route_blocks_objective - dynamic_row['cumulative_objective_without_transition_penalty'],
        6,
    )
    dwell_rows: list[dict[str, Any]] = []
    max_dwell = horizon_metrics['max_unique_appends'] + 1
    for minimum_dwell_unique_appends in range(1, max_dwell + 1):
        selected_row = min(
            (
                row for row in candidate_rows
                if _fingerprint_catalog_compact_repeat_state_min_interval_dwell_unique_appends(row['interval_rows'])
                >= minimum_dwell_unique_appends
            ),
            key=lambda row: (
                row['cumulative_objective_without_transition_penalty'],
                row['transition_count'],
                row['end_state_kind'],
            ),
        )
        cumulative_gain_vs_fixed_route_blocks = round(
            fixed_route_blocks_objective - selected_row['cumulative_objective_without_transition_penalty'],
            6,
        )
        dwell_rows.append({
            'minimum_dwell_unique_appends': minimum_dwell_unique_appends,
            'selected_transition_count': selected_row['transition_count'],
            'minimum_interval_dwell_unique_appends': _fingerprint_catalog_compact_repeat_state_min_interval_dwell_unique_appends(selected_row['interval_rows']),
            'cumulative_objective_without_transition_penalty': selected_row['cumulative_objective_without_transition_penalty'],
            'regret_vs_unbounded_dynamic': round(
                selected_row['cumulative_objective_without_transition_penalty']
                - dynamic_row['cumulative_objective_without_transition_penalty'],
                6,
            ),
            'cumulative_gain_vs_fixed_route_blocks': cumulative_gain_vs_fixed_route_blocks,
            'gain_share_of_full_dynamic_savings': _compact_repeat_state_preserved_gain_share(
                cumulative_gain_vs_fixed_route_blocks,
                full_dynamic_gain_vs_fixed_route_blocks,
            ),
            'end_state_kind': selected_row['end_state_kind'],
            'state_counts': selected_row['state_counts'],
            'interval_rows': selected_row['interval_rows'],
            'interval_summary': _fingerprint_catalog_compact_repeat_state_interval_summary(selected_row['interval_rows']),
        })

    frontier_rows: list[dict[str, Any]] = []
    for row in dwell_rows:
        if frontier_rows and frontier_rows[-1]['selected_transition_count'] == row['selected_transition_count'] and frontier_rows[-1]['interval_rows'] == row['interval_rows']:
            frontier_rows[-1]['minimum_dwell_end_unique_appends'] = row['minimum_dwell_unique_appends']
            continue
        frontier_rows.append({
            **row,
            'minimum_dwell_start_unique_appends': row['minimum_dwell_unique_appends'],
            'minimum_dwell_end_unique_appends': row['minimum_dwell_unique_appends'],
        })

    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'max_unique_appends': horizon_metrics['max_unique_appends'],
        'entry_count': horizon_metrics['entry_count'],
        'page_count': horizon_metrics['page_count'],
        'tail_entry_count': horizon_metrics['tail_entry_count'],
        'route_block_bitmap_len': horizon_metrics['route_block_bitmap_len'],
        'fixed_route_blocks_cumulative_objective_without_transition_penalty': fixed_route_blocks_objective,
        'full_dynamic_gain_vs_fixed_route_blocks': full_dynamic_gain_vs_fixed_route_blocks,
        'dynamic_transition_count': dynamic_row['transition_count'],
        'dynamic_cumulative_objective_without_transition_penalty': dynamic_row['cumulative_objective_without_transition_penalty'],
        'frontier_rows': frontier_rows,
        'dwell_rows': dwell_rows,
        'candidate_row_count': len(candidate_rows),
        'why': (
            'require each compact repeat-sidecar regime to persist for at least a minimum dwell length '
            'so the archive can suppress cliff toggles and other short-lived rewrites without replaying the full frontier'
        ),
    }


def fingerprint_catalog_compact_repeat_state_min_dwell_frontier(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    horizon_metrics = fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=max_unique_appends,
        page_size=page_size,
    )
    return fingerprint_catalog_compact_repeat_state_min_dwell_frontier_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )





def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_frontier(
    frontier: dict[str, Any],
    *,
    minimum_gain_share_of_full_dynamic_savings: float,
) -> dict[str, Any]:
    if not isinstance(minimum_gain_share_of_full_dynamic_savings, (int, float)):
        raise PacketError(
            'minimum_gain_share_of_full_dynamic_savings must be numeric, '
            f'got {minimum_gain_share_of_full_dynamic_savings!r}'
        )
    minimum_gain_share_of_full_dynamic_savings = float(minimum_gain_share_of_full_dynamic_savings)
    if minimum_gain_share_of_full_dynamic_savings < 0.0 or minimum_gain_share_of_full_dynamic_savings > 1.0:
        raise PacketError(
            'minimum_gain_share_of_full_dynamic_savings must be between 0.0 and 1.0 inclusive, '
            f'got {minimum_gain_share_of_full_dynamic_savings!r}'
        )

    frontier_rows = frontier.get('frontier_rows')
    if not frontier_rows:
        raise PacketError('minimum-dwell frontier did not contain any breakpoint rows')

    eligible_rows = [
        row for row in frontier_rows
        if row['gain_share_of_full_dynamic_savings'] >= minimum_gain_share_of_full_dynamic_savings
    ]
    if not eligible_rows:
        raise PacketError(
            'minimum-dwell frontier did not contain any plateau that meets '
            f'the requested gain share {minimum_gain_share_of_full_dynamic_savings!r}'
        )

    selected_row = max(
        eligible_rows,
        key=lambda row: (
            row['minimum_dwell_end_unique_appends'] - row['minimum_dwell_start_unique_appends'] + 1,
            row['minimum_dwell_end_unique_appends'],
            row['gain_share_of_full_dynamic_savings'],
            -row['selected_transition_count'],
        ),
    )
    plateau_width = (
        selected_row['minimum_dwell_end_unique_appends']
        - selected_row['minimum_dwell_start_unique_appends']
        + 1
    )
    anchor_minimum_dwell_unique_appends = (
        selected_row['minimum_dwell_start_unique_appends']
        + selected_row['minimum_dwell_end_unique_appends']
    ) // 2
    anchor_margin_unique_appends = min(
        anchor_minimum_dwell_unique_appends - selected_row['minimum_dwell_start_unique_appends'],
        selected_row['minimum_dwell_end_unique_appends'] - anchor_minimum_dwell_unique_appends,
    )

    return {
        'minimum_gain_share_of_full_dynamic_savings': round(minimum_gain_share_of_full_dynamic_savings, 6),
        'anchor_minimum_dwell_unique_appends': anchor_minimum_dwell_unique_appends,
        'anchor_margin_unique_appends': anchor_margin_unique_appends,
        'minimum_dwell_start_unique_appends': selected_row['minimum_dwell_start_unique_appends'],
        'minimum_dwell_end_unique_appends': selected_row['minimum_dwell_end_unique_appends'],
        'plateau_width_unique_appends': plateau_width,
        'selected_transition_count': selected_row['selected_transition_count'],
        'minimum_interval_dwell_unique_appends': selected_row['minimum_interval_dwell_unique_appends'],
        'gain_share_of_full_dynamic_savings': selected_row['gain_share_of_full_dynamic_savings'],
        'regret_vs_unbounded_dynamic': selected_row['regret_vs_unbounded_dynamic'],
        'cumulative_gain_vs_fixed_route_blocks': selected_row['cumulative_gain_vs_fixed_route_blocks'],
        'state_counts': selected_row['state_counts'],
        'interval_summary': selected_row['interval_summary'],
        'why': (
            'choose the midpoint of the widest admissible minimum-dwell plateau '
            'so small forecast errors do not knock the archive onto a different sidecar schedule'
        ),
    }


def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float,
    minimum_gain_share_of_full_dynamic_savings: float,
) -> dict[str, Any]:
    frontier = fingerprint_catalog_compact_repeat_state_min_dwell_frontier_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )
    result = recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_frontier(
        frontier,
        minimum_gain_share_of_full_dynamic_savings=minimum_gain_share_of_full_dynamic_savings,
    )
    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'max_unique_appends': frontier['max_unique_appends'],
        'entry_count': frontier['entry_count'],
        'page_count': frontier['page_count'],
        'tail_entry_count': frontier['tail_entry_count'],
        'route_block_bitmap_len': frontier['route_block_bitmap_len'],
        'frontier_row_count': len(frontier['frontier_rows']),
        **result,
    }


def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float,
    minimum_gain_share_of_full_dynamic_savings: float,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    horizon_metrics = fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=max_unique_appends,
        page_size=page_size,
    )
    return recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
        minimum_gain_share_of_full_dynamic_savings=minimum_gain_share_of_full_dynamic_savings,
    )

def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_under_repeat_uncertainty_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups_values: list[float] | tuple[float, ...],
    minimum_gain_share_of_full_dynamic_savings: float,
) -> dict[str, Any]:
    if not isinstance(expected_repeat_lookups_values, (list, tuple)) or not expected_repeat_lookups_values:
        raise PacketError('expected_repeat_lookups_values must be a non-empty list or tuple of numeric values')

    normalized_repeat_values: list[float] = []
    for value in expected_repeat_lookups_values:
        if not isinstance(value, (int, float)):
            raise PacketError(f'expected_repeat_lookups_values must be numeric, got {value!r}')
        value = float(value)
        if value < 0:
            raise PacketError(f'expected_repeat_lookups_values must be non-negative, got {value!r}')
        normalized_repeat_values.append(round(value, 6))
    normalized_repeat_values = sorted(set(normalized_repeat_values))

    per_repeat_rows: list[dict[str, Any]] = []
    overlap_start = 1
    overlap_end: int | None = None
    for expected_repeat_lookups in normalized_repeat_values:
        frontier = fingerprint_catalog_compact_repeat_state_min_dwell_frontier_from_metrics(
            horizon_metrics,
            expected_repeat_lookups=expected_repeat_lookups,
        )
        eligible_rows = [
            row for row in frontier['dwell_rows']
            if row['gain_share_of_full_dynamic_savings'] >= minimum_gain_share_of_full_dynamic_savings
        ]
        if not eligible_rows:
            raise PacketError(
                'repeat-uncertainty minimum-dwell anchor could not find any admissible dwell rows for '
                f'expected_repeat_lookups={expected_repeat_lookups!r} at gain share '
                f'{minimum_gain_share_of_full_dynamic_savings!r}'
            )
        admissible_end = eligible_rows[-1]['minimum_dwell_unique_appends']
        overlap_end = admissible_end if overlap_end is None else min(overlap_end, admissible_end)
        per_repeat_rows.append({
            'expected_repeat_lookups': expected_repeat_lookups,
            'admissible_minimum_dwell_start_unique_appends': 1,
            'admissible_minimum_dwell_end_unique_appends': admissible_end,
            'frontier_row_count': len(frontier['frontier_rows']),
            'dynamic_transition_count': frontier['dynamic_transition_count'],
            'full_dynamic_gain_vs_fixed_route_blocks': frontier['full_dynamic_gain_vs_fixed_route_blocks'],
            'dwell_rows': frontier['dwell_rows'],
        })

    assert overlap_end is not None
    anchor_minimum_dwell_unique_appends = (overlap_start + overlap_end) // 2
    anchor_margin_unique_appends = min(
        anchor_minimum_dwell_unique_appends - overlap_start,
        overlap_end - anchor_minimum_dwell_unique_appends,
    )

    anchor_rows: list[dict[str, Any]] = []
    for row in per_repeat_rows:
        anchor_row = row['dwell_rows'][anchor_minimum_dwell_unique_appends - 1]
        anchor_rows.append({
            'expected_repeat_lookups': row['expected_repeat_lookups'],
            'selected_transition_count': anchor_row['selected_transition_count'],
            'gain_share_of_full_dynamic_savings': anchor_row['gain_share_of_full_dynamic_savings'],
            'regret_vs_unbounded_dynamic': anchor_row['regret_vs_unbounded_dynamic'],
            'cumulative_gain_vs_fixed_route_blocks': anchor_row['cumulative_gain_vs_fixed_route_blocks'],
            'interval_summary': anchor_row['interval_summary'],
            'admissible_minimum_dwell_end_unique_appends': row['admissible_minimum_dwell_end_unique_appends'],
        })

    return {
        'minimum_gain_share_of_full_dynamic_savings': round(minimum_gain_share_of_full_dynamic_savings, 6),
        'expected_repeat_lookups_values': normalized_repeat_values,
        'expected_repeat_lookups_start': normalized_repeat_values[0],
        'expected_repeat_lookups_end': normalized_repeat_values[-1],
        'anchor_minimum_dwell_unique_appends': anchor_minimum_dwell_unique_appends,
        'anchor_margin_unique_appends': anchor_margin_unique_appends,
        'minimum_dwell_overlap_start_unique_appends': overlap_start,
        'minimum_dwell_overlap_end_unique_appends': overlap_end,
        'overlap_width_unique_appends': overlap_end - overlap_start + 1,
        'worst_case_gain_share_of_full_dynamic_savings': min(
            row['gain_share_of_full_dynamic_savings'] for row in anchor_rows
        ),
        'best_case_gain_share_of_full_dynamic_savings': max(
            row['gain_share_of_full_dynamic_savings'] for row in anchor_rows
        ),
        'minimum_selected_transition_count': min(row['selected_transition_count'] for row in anchor_rows),
        'maximum_selected_transition_count': max(row['selected_transition_count'] for row in anchor_rows),
        'anchor_rows': anchor_rows,
        'why': (
            'choose the midpoint of the minimum-dwell overlap that survives every repeat budget in the uncertainty band '
            'so one preset remains safe even when repeat volume is only known approximately'
        ),
    }


def recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_under_repeat_uncertainty(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups_values: list[float] | tuple[float, ...],
    minimum_gain_share_of_full_dynamic_savings: float,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    horizon_metrics = fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=max_unique_appends,
        page_size=page_size,
    )
    result = recommend_fingerprint_catalog_compact_repeat_state_min_dwell_anchor_under_repeat_uncertainty_from_metrics(
        horizon_metrics,
        expected_repeat_lookups_values=expected_repeat_lookups_values,
        minimum_gain_share_of_full_dynamic_savings=minimum_gain_share_of_full_dynamic_savings,
    )
    return {
        'max_unique_appends': horizon_metrics['max_unique_appends'],
        'entry_count': horizon_metrics['entry_count'],
        'page_count': horizon_metrics['page_count'],
        'tail_entry_count': horizon_metrics['tail_entry_count'],
        'route_block_bitmap_len': horizon_metrics['route_block_bitmap_len'],
        **result,
    }


def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_transition_budget_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float,
    max_transition_count: int,
) -> dict[str, Any]:
    if not isinstance(max_transition_count, int) or max_transition_count < 0:
        raise PacketError(f'max_transition_count must be a non-negative integer, got {max_transition_count!r}')

    frontier = fingerprint_catalog_compact_repeat_state_transition_budget_frontier_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )
    capped_budget = min(max_transition_count, frontier['budget_rows'][-1]['max_transition_count'])
    selected_row = frontier['budget_rows'][capped_budget]
    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'max_transition_count': max_transition_count,
        'effective_max_transition_count': capped_budget,
        'max_unique_appends': frontier['max_unique_appends'],
        'entry_count': frontier['entry_count'],
        'page_count': frontier['page_count'],
        'tail_entry_count': frontier['tail_entry_count'],
        'route_block_bitmap_len': frontier['route_block_bitmap_len'],
        'selected_transition_count': selected_row['selected_transition_count'],
        'recommended_state_counts': selected_row['state_counts'],
        'interval_rows': selected_row['interval_rows'],
        'cumulative_objective_without_transition_penalty': selected_row['cumulative_objective_without_transition_penalty'],
        'regret_vs_unbounded_dynamic': selected_row['regret_vs_unbounded_dynamic'],
        'objective_improvement_vs_previous_budget': selected_row['objective_improvement_vs_previous_budget'],
        'frontier_row_count': len(frontier['frontier_rows']),
        'why': frontier['why'],
    }



def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_transition_budget(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float,
    max_transition_count: int,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    horizon_metrics = fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=max_unique_appends,
        page_size=page_size,
    )
    return recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_transition_budget_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
        max_transition_count=max_transition_count,
    )



def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_min_dwell_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float,
    minimum_dwell_unique_appends: int,
) -> dict[str, Any]:
    if not isinstance(minimum_dwell_unique_appends, int) or minimum_dwell_unique_appends <= 0:
        raise PacketError(
            f'minimum_dwell_unique_appends must be a positive integer, got {minimum_dwell_unique_appends!r}'
        )

    frontier = fingerprint_catalog_compact_repeat_state_min_dwell_frontier_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )
    capped_minimum_dwell = min(minimum_dwell_unique_appends, frontier['dwell_rows'][-1]['minimum_dwell_unique_appends'])
    selected_row = frontier['dwell_rows'][capped_minimum_dwell - 1]
    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'minimum_dwell_unique_appends': minimum_dwell_unique_appends,
        'effective_minimum_dwell_unique_appends': capped_minimum_dwell,
        'max_unique_appends': frontier['max_unique_appends'],
        'entry_count': frontier['entry_count'],
        'page_count': frontier['page_count'],
        'tail_entry_count': frontier['tail_entry_count'],
        'route_block_bitmap_len': frontier['route_block_bitmap_len'],
        'selected_transition_count': selected_row['selected_transition_count'],
        'minimum_interval_dwell_unique_appends': selected_row['minimum_interval_dwell_unique_appends'],
        'recommended_state_counts': selected_row['state_counts'],
        'interval_rows': selected_row['interval_rows'],
        'cumulative_objective_without_transition_penalty': selected_row['cumulative_objective_without_transition_penalty'],
        'regret_vs_unbounded_dynamic': selected_row['regret_vs_unbounded_dynamic'],
        'frontier_row_count': len(frontier['frontier_rows']),
        'why': frontier['why'],
    }



def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_min_dwell(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float,
    minimum_dwell_unique_appends: int,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    horizon_metrics = fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=max_unique_appends,
        page_size=page_size,
    )
    return recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_min_dwell_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
        minimum_dwell_unique_appends=minimum_dwell_unique_appends,
    )



def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_transition_penalty_from_metrics(
    horizon_metrics: dict[str, Any],
    *,
    expected_repeat_lookups: float,
    transition_penalty_per_switch_bytes: float,
) -> dict[str, Any]:
    if transition_penalty_per_switch_bytes < 0:
        raise PacketError(
            f'transition_penalty_per_switch_bytes must be non-negative, got {transition_penalty_per_switch_bytes!r}'
        )

    frontier = fingerprint_catalog_compact_repeat_state_switch_penalty_frontier_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
    )
    selected_row = frontier['frontier_rows'][0]
    for row in frontier['frontier_rows']:
        start = row['transition_penalty_start_bytes']
        end = row['transition_penalty_end_bytes']
        if transition_penalty_per_switch_bytes >= start and (
            end is None or transition_penalty_per_switch_bytes < end
        ):
            selected_row = row
            break

    cumulative_objective = round(
        selected_row['cumulative_objective_without_transition_penalty']
        + transition_penalty_per_switch_bytes * selected_row['transition_count'],
        6,
    )
    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'transition_penalty_per_switch_bytes': transition_penalty_per_switch_bytes,
        'max_unique_appends': frontier['max_unique_appends'],
        'entry_count': frontier['entry_count'],
        'page_count': frontier['page_count'],
        'tail_entry_count': frontier['tail_entry_count'],
        'route_block_bitmap_len': frontier['route_block_bitmap_len'],
        'recommended_state_counts': selected_row['state_counts'],
        'transition_count': selected_row['transition_count'],
        'interval_rows': selected_row['interval_rows'],
        'cumulative_objective_without_transition_penalty': selected_row['cumulative_objective_without_transition_penalty'],
        'cumulative_objective_with_transition_penalty': cumulative_objective,
        'active_transition_penalty_start_bytes': selected_row['transition_penalty_start_bytes'],
        'active_transition_penalty_end_bytes': selected_row['transition_penalty_end_bytes'],
        'frontier_row_count': len(frontier['frontier_rows']),
        'why': frontier['why'],
    }



def recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_transition_penalty(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float,
    transition_penalty_per_switch_bytes: float,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    horizon_metrics = fingerprint_catalog_compact_repeat_state_horizon_metrics(
        pages,
        max_unique_appends=max_unique_appends,
        page_size=page_size,
    )
    return recommend_fingerprint_catalog_compact_repeat_state_horizon_policy_with_transition_penalty_from_metrics(
        horizon_metrics,
        expected_repeat_lookups=expected_repeat_lookups,
        transition_penalty_per_switch_bytes=transition_penalty_per_switch_bytes,
    )


def fingerprint_catalog_compact_repeat_state_budget_staging_plan(
    pages: list[str] | tuple[str, ...],
    *,
    expected_repeat_lookups: float,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    if expected_repeat_lookups < 0:
        raise PacketError(f'expected_repeat_lookups must be non-negative, got {expected_repeat_lookups!r}')
    if not isinstance(max_unique_appends, int) or max_unique_appends < 0:
        raise PacketError(f'max_unique_appends must be a non-negative integer, got {max_unique_appends!r}')
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    if not isinstance(pages, (list, tuple)) or not pages:
        raise PacketError('compact repeat-state staging requires a non-empty list or tuple of fingerprint catalog pages')

    projected_pages = list(pages) if isinstance(pages, tuple) else pages.copy()
    known_fingerprints = set(expand_fingerprint_catalog_pages(projected_pages))
    interval_rows: list[dict[str, Any]] = []
    transition_rows: list[dict[str, Any]] = []
    current_interval: dict[str, Any] | None = None
    previous_page_count: int | None = None
    previous_tail_entry_count: int | None = None
    previous_bitmap_len: int | None = None
    previous_kind: str | None = None

    for unique_append_count in range(0, max_unique_appends + 1):
        metrics = fingerprint_catalog_compact_repeat_state_metrics(projected_pages)
        recommendation = recommend_fingerprint_catalog_compact_repeat_state_from_metrics(
            metrics,
            expected_repeat_lookups=expected_repeat_lookups,
        )
        page_count = metrics['page_count']
        tail_entry_count = fingerprint_catalog_page_entry_count(projected_pages[-1])
        bitmap_len = _fingerprint_catalog_route_block_bitmap_len(page_count)
        thresholds = {
            'paged_catalog_only_to_filters': compact_repeat_state_break_even_repeat_lookups(
                metrics['rows']['paged_catalog_only']['compact_state_bytes'],
                metrics['rows']['paged_catalog_only']['average_repeat_lookup_bytes'],
                metrics['rows']['paged_catalog_with_filters']['compact_state_bytes'],
                metrics['rows']['paged_catalog_with_filters']['average_repeat_lookup_bytes'],
            ),
            'filters_to_route_blocks': compact_repeat_state_break_even_repeat_lookups(
                metrics['rows']['paged_catalog_with_filters']['compact_state_bytes'],
                metrics['rows']['paged_catalog_with_filters']['average_repeat_lookup_bytes'],
                metrics['rows']['paged_catalog_with_route_blocks']['compact_state_bytes'],
                metrics['rows']['paged_catalog_with_route_blocks']['average_repeat_lookup_bytes'],
            ),
            'paged_catalog_only_to_route_blocks': compact_repeat_state_break_even_repeat_lookups(
                metrics['rows']['paged_catalog_only']['compact_state_bytes'],
                metrics['rows']['paged_catalog_only']['average_repeat_lookup_bytes'],
                metrics['rows']['paged_catalog_with_route_blocks']['compact_state_bytes'],
                metrics['rows']['paged_catalog_with_route_blocks']['average_repeat_lookup_bytes'],
            ),
        }
        recommended_kind = recommendation['recommended_state_kind']
        if current_interval is None:
            current_interval = {
                'start_unique_appends': unique_append_count,
                'recommended_state_kind': recommended_kind,
                'start_page_count': page_count,
                'start_tail_entry_count': tail_entry_count,
                'start_route_block_bitmap_len': bitmap_len,
            }
        elif recommended_kind != previous_kind:
            current_interval['end_unique_appends'] = unique_append_count - 1
            current_interval['end_page_count'] = previous_page_count
            current_interval['end_tail_entry_count'] = previous_tail_entry_count
            current_interval['end_route_block_bitmap_len'] = previous_bitmap_len
            interval_rows.append(current_interval)
            transition_rows.append({
                'unique_append_count': unique_append_count,
                'page_count': page_count,
                'tail_entry_count': tail_entry_count,
                'route_block_bitmap_len': bitmap_len,
                'from_state_kind': previous_kind,
                'to_state_kind': recommended_kind,
                'break_even_repeat_lookups': thresholds,
            })
            current_interval = {
                'start_unique_appends': unique_append_count,
                'recommended_state_kind': recommended_kind,
                'start_page_count': page_count,
                'start_tail_entry_count': tail_entry_count,
                'start_route_block_bitmap_len': bitmap_len,
            }
        previous_kind = recommended_kind
        previous_page_count = page_count
        previous_tail_entry_count = tail_entry_count
        previous_bitmap_len = bitmap_len
        if unique_append_count >= max_unique_appends:
            continue
        fingerprint = _synthetic_unique_growth_fingerprint(known_fingerprints, unique_append_count + 1)
        known_fingerprints.add(fingerprint)
        projected_pages = append_fingerprint_catalog_pages(projected_pages, fingerprint, page_size=page_size)

    if current_interval is None or previous_page_count is None or previous_tail_entry_count is None or previous_bitmap_len is None:
        raise PacketError('compact repeat-state staging plan could not establish an interval for the provided pages')
    current_interval['end_unique_appends'] = max_unique_appends
    current_interval['end_page_count'] = previous_page_count
    current_interval['end_tail_entry_count'] = previous_tail_entry_count
    current_interval['end_route_block_bitmap_len'] = previous_bitmap_len
    interval_rows.append(current_interval)

    return {
        'expected_repeat_lookups': expected_repeat_lookups,
        'max_unique_appends': max_unique_appends,
        'entry_count': len(expand_fingerprint_catalog_pages(pages)),
        'page_count': len(pages),
        'tail_entry_count': fingerprint_catalog_page_entry_count(pages[-1]),
        'route_block_bitmap_len': _fingerprint_catalog_route_block_bitmap_len(len(pages)),
        'interval_rows': interval_rows,
        'transition_rows': transition_rows,
    }



def _synthetic_unique_growth_fingerprint(
    known_fingerprints: set[str],
    growth_index: int,
) -> str:
    if not isinstance(growth_index, int) or growth_index < 1:
        raise PacketError(f'growth_index must be a positive integer, got {growth_index!r}')
    salt = 0
    while True:
        seed = f'gr-growth-{growth_index}-{salt}'.encode('utf-8')
        fingerprint = 'sha256:' + hashlib.sha256(seed).hexdigest()
        if fingerprint not in known_fingerprints:
            return fingerprint
        salt += 1



def project_fingerprint_catalog_compact_repeat_state(
    pages: list[str] | tuple[str, ...],
    *,
    unique_append_count: int = 0,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    if not isinstance(unique_append_count, int) or unique_append_count < 0:
        raise PacketError(f'unique_append_count must be a non-negative integer, got {unique_append_count!r}')
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    if not isinstance(pages, (list, tuple)) or not pages:
        raise PacketError('projected compact repeat-state requires a non-empty list or tuple of fingerprint catalog pages')

    projected_pages = list(pages) if isinstance(pages, tuple) else pages.copy()
    projected_filters = fingerprint_catalog_page_filters(projected_pages)
    projected_route_blocks = fingerprint_catalog_page_route_blocks(projected_pages)
    known_fingerprints = set(expand_fingerprint_catalog_pages(projected_pages))

    for growth_index in range(1, unique_append_count + 1):
        fingerprint = _synthetic_unique_growth_fingerprint(known_fingerprints, growth_index)
        known_fingerprints.add(fingerprint)
        next_pages = append_fingerprint_catalog_pages(projected_pages, fingerprint, page_size=page_size)
        projected_filters = append_fingerprint_catalog_page_filters(
            projected_filters,
            fingerprint,
            page_size=page_size,
        )
        projected_route_blocks = append_fingerprint_catalog_page_route_blocks(
            projected_route_blocks,
            projected_pages,
            fingerprint,
            page_size=page_size,
        )
        projected_pages = next_pages

    page_state_bytes = packet_minified_bytes(projected_pages)
    filter_sidecar_state_bytes = packet_minified_bytes(projected_filters)
    route_block_sidecar_state_bytes = packet_minified_bytes(projected_route_blocks)
    entry_count = len(expand_fingerprint_catalog_pages(projected_pages))
    page_count = len(projected_pages)
    tail_entry_count = fingerprint_catalog_page_entry_count(projected_pages[-1])

    return {
        'unique_append_count': unique_append_count,
        'entry_count': entry_count,
        'page_count': page_count,
        'tail_entry_count': tail_entry_count,
        'route_block_bitmap_len': _fingerprint_catalog_route_block_bitmap_len(page_count),
        'rows': {
            'paged_catalog_only': {
                'kind': 'paged_catalog_only',
                'compact_state_bytes': page_state_bytes,
                'extra_sidecar_state_bytes': 0,
            },
            'paged_catalog_with_filters': {
                'kind': 'paged_catalog_with_filters',
                'compact_state_bytes': page_state_bytes + filter_sidecar_state_bytes,
                'extra_sidecar_state_bytes': filter_sidecar_state_bytes,
            },
            'paged_catalog_with_route_blocks': {
                'kind': 'paged_catalog_with_route_blocks',
                'compact_state_bytes': page_state_bytes + route_block_sidecar_state_bytes,
                'extra_sidecar_state_bytes': route_block_sidecar_state_bytes,
            },
        },
    }



def _sign(value: int) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0



def fingerprint_catalog_compact_repeat_state_growth_events(
    pages: list[str] | tuple[str, ...],
    *,
    max_unique_appends: int = 256,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    if not isinstance(max_unique_appends, int) or max_unique_appends < 0:
        raise PacketError(f'max_unique_appends must be a non-negative integer, got {max_unique_appends!r}')
    baseline = project_fingerprint_catalog_compact_repeat_state(
        pages,
        unique_append_count=0,
        page_size=page_size,
    )
    previous = baseline
    previous_filter_minus_route = (
        previous['rows']['paged_catalog_with_filters']['compact_state_bytes']
        - previous['rows']['paged_catalog_with_route_blocks']['compact_state_bytes']
    )
    event_rows: list[dict[str, Any]] = []

    for unique_append_count in range(1, max_unique_appends + 1):
        projected = project_fingerprint_catalog_compact_repeat_state(
            pages,
            unique_append_count=unique_append_count,
            page_size=page_size,
        )
        filter_minus_route = (
            projected['rows']['paged_catalog_with_filters']['compact_state_bytes']
            - projected['rows']['paged_catalog_with_route_blocks']['compact_state_bytes']
        )
        event_kinds: list[str] = []
        if projected['page_count'] != previous['page_count']:
            event_kinds.append('new_page_birth')
        if projected['route_block_bitmap_len'] != previous['route_block_bitmap_len']:
            event_kinds.append('route_block_bitmap_cliff')
        if _sign(filter_minus_route) != _sign(previous_filter_minus_route):
            event_kinds.append('filter_route_state_order_flip')
        if not event_kinds:
            previous = projected
            previous_filter_minus_route = filter_minus_route
            continue
        event_rows.append({
            'unique_append_count': unique_append_count,
            'entry_count': projected['entry_count'],
            'page_count': projected['page_count'],
            'tail_entry_count': projected['tail_entry_count'],
            'route_block_bitmap_len': projected['route_block_bitmap_len'],
            'event_kinds': event_kinds,
            'paged_catalog_only_compact_state_bytes': projected['rows']['paged_catalog_only']['compact_state_bytes'],
            'filters_compact_state_bytes': projected['rows']['paged_catalog_with_filters']['compact_state_bytes'],
            'filters_extra_sidecar_state_bytes': projected['rows']['paged_catalog_with_filters']['extra_sidecar_state_bytes'],
            'route_blocks_compact_state_bytes': projected['rows']['paged_catalog_with_route_blocks']['compact_state_bytes'],
            'route_blocks_extra_sidecar_state_bytes': projected['rows']['paged_catalog_with_route_blocks']['extra_sidecar_state_bytes'],
            'filter_minus_route_compact_state_bytes': filter_minus_route,
        })
        previous = projected
        previous_filter_minus_route = filter_minus_route

    return {
        'entry_count': baseline['entry_count'],
        'page_count': baseline['page_count'],
        'tail_entry_count': baseline['tail_entry_count'],
        'route_block_bitmap_len': baseline['route_block_bitmap_len'],
        'baseline_rows': [baseline['rows'][kind] for kind in COMPACT_REPEAT_STATE_KINDS],
        'event_rows': event_rows,
    }



def find_fingerprint_catalog_slot_from_pages_with_filters(
    fingerprint: str,
    pages: list[str] | tuple[str, ...],
    page_filters: list[str] | tuple[str, ...],
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> int | None:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    target_digest = _fingerprint_digest_bytes(normalized)
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    if not isinstance(pages, (list, tuple)):
        raise PacketError('fingerprint catalog pages must be provided as a list or tuple of page payloads')
    if not isinstance(page_filters, (list, tuple)):
        raise PacketError('fingerprint catalog page filters must be provided as a list or tuple of page-filter payloads')
    if len(page_filters) != len(pages):
        raise PacketError(
            f'fingerprint catalog page filters must align one-to-one with pages, got {len(page_filters)} filters for {len(pages)} pages'
        )
    mask_value = target_digest[0]
    slot_base = 0
    for page_index, (page, page_filter) in enumerate(zip(pages, page_filters)):
        entry_count, mask = _decode_fingerprint_catalog_page_filter_payload(page_filter)
        if entry_count > page_size:
            raise PacketError(
                f'catalog page filter {page_index} exceeds configured page_size {page_size} with {entry_count} entries'
            )
        if page_index < len(pages) - 1 and entry_count != page_size:
            raise PacketError(
                f'catalog page filter {page_index} must contain exactly {page_size} entries before the tail page, got {entry_count}'
            )
        if not mask[mask_value >> 3] & (1 << (mask_value & 7)):
            slot_base += entry_count
            continue
        payload, payload_entry_count = _decode_fingerprint_catalog_page_payload(page)
        if payload_entry_count != entry_count:
            raise PacketError(
                f'catalog page {page_index} entry count {payload_entry_count} does not match page filter count {entry_count}'
            )
        for entry_index in range(entry_count):
            start = entry_index * 32
            if payload[start : start + 32] == target_digest:
                return slot_base + entry_index
        slot_base += entry_count
    return None



def fingerprint_catalog_page_entry_count(page: str) -> int:
    _, entry_count = _decode_fingerprint_catalog_page_payload(page)
    return entry_count


def resolve_fingerprint_catalog_slot_from_pages(
    slot: int,
    pages: list[str] | tuple[str, ...],
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> str:
    if not isinstance(slot, int) or slot < 0:
        raise PacketError(f'catalog slot must be a non-negative integer, got {slot!r}')
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    if not isinstance(pages, (list, tuple)) or not pages:
        raise PacketError('catalog-slot page resolution requires a non-empty list or tuple of page payloads')
    page_index = slot // page_size
    entry_index = slot % page_size
    if page_index >= len(pages):
        raise PacketError(f'catalog slot {slot} is out of range for {len(pages)} pages of size {page_size}')
    page = expand_fingerprint_catalog_page(pages[page_index])
    if page_index < len(pages) - 1 and len(page) != page_size:
        raise PacketError(
            f'catalog page {page_index} must contain exactly {page_size} entries before the tail page, got {len(page)}'
        )
    if entry_index >= len(page):
        total_lower_bound = page_index * page_size + len(page)
        raise PacketError(f'catalog slot {slot} is out of range for a paged catalog with fewer than {total_lower_bound + 1} entries')
    return page[entry_index]


def append_fingerprint_catalog_pages(
    pages: list[str] | tuple[str, ...],
    fingerprint: str,
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> list[str]:
    normalized = 'sha256:' + _normalize_fingerprint(fingerprint)
    if not isinstance(page_size, int) or page_size <= 0:
        raise PacketError(f'fingerprint catalog page_size must be a positive integer, got {page_size!r}')
    materialized = list(pages) if isinstance(pages, tuple) else pages.copy()
    if not materialized:
        return fingerprint_catalog_pages([normalized], page_size=page_size)
    ordered = expand_fingerprint_catalog_pages(materialized)
    if normalized in set(ordered):
        return materialized
    tail = expand_fingerprint_catalog_page(materialized[-1])
    if len(tail) < page_size:
        tail.append(normalized)
        materialized[-1] = fingerprint_catalog_page(tail)
        return materialized
    materialized.append(fingerprint_catalog_page([normalized]))
    return materialized


def _encode_uvarint(value: int) -> bytes:
    if not isinstance(value, int) or value < 0:
        raise PacketError(f'uvarint encoding requires a non-negative integer, got {value!r}')
    out = bytearray()
    remaining = value
    while True:
        byte = remaining & 0x7F
        remaining >>= 7
        if remaining:
            out.append(0x80 | byte)
        else:
            out.append(byte)
            return bytes(out)


def _decode_uvarint(raw: bytes, offset: int = 0) -> tuple[int, int]:
    if not isinstance(raw, (bytes, bytearray)):
        raise PacketError('uvarint decoding requires raw bytes')
    shift = 0
    value = 0
    while True:
        if offset >= len(raw):
            raise PacketError('truncated uvarint payload')
        byte = raw[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7
        if shift > 63:
            raise PacketError('uvarint payload is too large')


def resolve_archive_local_reference(
    reference: dict[str, Any],
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
) -> str:
    if reference.get('packet_kind') != ARCHIVE_LOCAL_REFERENCE_KIND:
        raise PacketError(
            f"expected archive-local reference packet_kind {ARCHIVE_LOCAL_REFERENCE_KIND}, got {reference.get('packet_kind')}"
        )
    prefix = reference.get('prefix')
    if not isinstance(prefix, str) or not prefix:
        raise PacketError('archive-local reference must include a non-empty prefix')
    if any(ch not in '0123456789abcdef' for ch in prefix):
        raise PacketError(f'archive-local reference prefix must be lowercase hex, got {prefix}')
    matches = [fp for fp in known_fingerprints if _normalize_fingerprint(fp).startswith(prefix)]
    if not matches:
        raise PacketError(f'archive-local fingerprint prefix {prefix} does not resolve to a known semantic fingerprint')
    if len(matches) != 1:
        raise PacketError(f'archive-local fingerprint prefix {prefix} is ambiguous across {len(matches)} known semantic fingerprints')
    return matches[0]


def _validate_catalog_reference_packet(packet: str) -> None:
    if not _is_catalog_reference_packet(packet):
        raise PacketError('expected a catalog-slot reference encoded as a base64url string with the catalog tag byte')
    expand_catalog_reference_packet(packet)



def _validate_short_catalog_reference_packet(packet: str) -> None:
    if not _is_short_catalog_reference_packet(packet):
        raise PacketError('expected a short catalog-slot reference encoded as a 2-byte base64url string with the short-slot prefix bits')
    expand_short_catalog_reference_packet(packet)


def expand_catalog_reference_packet(packet: str) -> dict[str, Any]:
    raw = _base64url_decode_bytes(packet)
    if raw[0] != CATALOG_REFERENCE_TAG:
        raise PacketError(f'unsupported catalog-slot reference tag: {raw[0]}')
    slot, offset = _decode_uvarint(raw, 1)
    if offset != len(raw):
        raise PacketError('catalog-slot reference has trailing bytes')
    return {
        'packet_kind': ARCHIVE_LOCAL_CATALOG_REFERENCE_KIND,
        'slot': slot,
    }


def expand_short_catalog_reference_packet(packet: str) -> dict[str, Any]:
    raw = _base64url_decode_bytes(packet)
    if len(raw) != 2 or raw[0] & SHORT_CATALOG_REFERENCE_PREFIX_MASK != SHORT_CATALOG_REFERENCE_PREFIX:
        raise PacketError('short catalog-slot reference must decode to exactly 2 bytes with the short-slot prefix bits')
    slot = ((raw[0] & 0x3F) << 8) | raw[1]
    return {
        'packet_kind': ARCHIVE_LOCAL_CATALOG_REFERENCE_KIND,
        'slot': slot,
    }


def resolve_archive_catalog_reference(
    reference: dict[str, Any],
    known_fingerprints: list[str] | tuple[str, ...],
) -> str:
    if reference.get('packet_kind') != ARCHIVE_LOCAL_CATALOG_REFERENCE_KIND:
        raise PacketError(
            f"expected catalog-slot reference packet_kind {ARCHIVE_LOCAL_CATALOG_REFERENCE_KIND}, got {reference.get('packet_kind')}"
        )
    slot = reference.get('slot')
    if not isinstance(slot, int) or slot < 0:
        raise PacketError(f'catalog-slot reference must include a non-negative integer slot, got {slot!r}')
    catalog = ordered_fingerprint_catalog(known_fingerprints)
    if slot >= len(catalog):
        raise PacketError(f'catalog-slot reference {slot} is out of range for a catalog of size {len(catalog)}')
    return catalog[slot]


def resolve_archive_catalog_reference_from_pages(
    reference: dict[str, Any],
    pages: list[str] | tuple[str, ...],
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> str:
    if reference.get('packet_kind') != ARCHIVE_LOCAL_CATALOG_REFERENCE_KIND:
        raise PacketError(
            f"expected catalog-slot reference packet_kind {ARCHIVE_LOCAL_CATALOG_REFERENCE_KIND}, got {reference.get('packet_kind')}"
        )
    slot = reference.get('slot')
    return resolve_fingerprint_catalog_slot_from_pages(slot, pages, page_size=page_size)


def resolve_archive_any_catalog_reference_from_pages(
    reference: Any,
    pages: list[str] | tuple[str, ...],
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> str:
    if _is_short_catalog_reference_packet(reference):
        return resolve_archive_catalog_reference_from_pages(
            expand_short_catalog_reference_packet(reference),
            pages,
            page_size=page_size,
        )
    if _is_catalog_reference_packet(reference):
        return resolve_archive_catalog_reference_from_pages(
            expand_catalog_reference_packet(reference),
            pages,
            page_size=page_size,
        )
    return resolve_archive_catalog_reference_from_pages(reference, pages, page_size=page_size)


def _validate_coded_reference_packet(packet: dict[str, Any]) -> None:
    if _packet_kind_tag(packet) != CODED_REFERENCE_KIND:
        raise PacketError(f"expected coded-reference packet kind {CODED_REFERENCE_KIND}, got {_packet_kind_tag(packet)}")
    prefix = packet.get('x')
    if not isinstance(prefix, str) or not prefix:
        raise PacketError('coded reference packet must include a non-empty x prefix field')
    if any(ch not in '0123456789abcdef' for ch in prefix):
        raise PacketError(f'coded reference prefix must be lowercase hex, got {prefix}')


def expand_coded_reference_packet(packet: dict[str, Any]) -> dict[str, Any]:
    _validate_coded_reference_packet(packet)
    return {
        'packet_kind': ARCHIVE_LOCAL_REFERENCE_KIND,
        'prefix': packet['x'],
    }


def resolve_archive_any_reference(
    reference: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
) -> str:
    if _is_short_catalog_reference_packet(reference):
        if isinstance(known_fingerprints, set):
            raise PacketError('catalog-slot references require an ordered append-only fingerprint catalog for resolution')
        return resolve_archive_catalog_reference(expand_short_catalog_reference_packet(reference), known_fingerprints)
    if _is_catalog_reference_packet(reference):
        if isinstance(known_fingerprints, set):
            raise PacketError('catalog-slot references require an ordered append-only fingerprint catalog for resolution')
        return resolve_archive_catalog_reference(expand_catalog_reference_packet(reference), known_fingerprints)
    if _is_byte_reference_packet(reference):
        return resolve_archive_local_reference(expand_byte_reference_packet(reference), known_fingerprints)
    if _is_packed_reference_packet(reference):
        return resolve_archive_local_reference(expand_packed_reference_packet(reference), known_fingerprints)
    if _is_micro_reference_packet(reference):
        return resolve_archive_local_reference(expand_micro_reference_packet(reference), known_fingerprints)
    kind = _packet_kind_tag(reference)
    if kind == CODED_REFERENCE_KIND:
        return resolve_archive_local_reference(expand_coded_reference_packet(reference), known_fingerprints)
    return resolve_archive_local_reference(reference, known_fingerprints)


def packet_archive_local_reference(
    packet: dict[str, Any],
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    fingerprint = packet_semantic_fingerprint(packet)
    if fingerprint not in set(known_fingerprints):
        raise PacketError(
            'archive-local prefix references require the semantic fingerprint to already exist in the archive index'
        )
    prefix_len = minimal_unique_reference_prefix_hex_len(
        fingerprint,
        known_fingerprints,
        min_hex_len=min_hex_len,
    )
    return {
        'packet_kind': ARCHIVE_LOCAL_REFERENCE_KIND,
        'prefix': _normalize_fingerprint(fingerprint)[:prefix_len],
    }


def packet_archive_local_reference_write_plan(
    packet: dict[str, Any],
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint not in known:
        raise PacketError('archive-local prefix references are only valid for already-known semantic fingerprints')
    reference = packet_archive_local_reference(expanded, known, min_hex_len=min_hex_len)
    return {
        'recommended_write_kind': 'archive_local_reference',
        'semantic_fingerprint': semantic_fingerprint,
        'reference': reference,
        'why': 'the archive already has this semantic body, so the repeat can shrink from a full fingerprint reference to the shortest unique archive-local prefix reference',
    }


def packet_coded_reference(
    packet: dict[str, Any],
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    archive_local_reference = packet_archive_local_reference(packet, known_fingerprints, min_hex_len=min_hex_len)
    return {
        'k': CODED_REFERENCE_KIND,
        'x': archive_local_reference['prefix'],
    }


def packet_coded_reference_write_plan(
    packet: dict[str, Any],
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint not in known:
        raise PacketError('coded references are only valid for already-known semantic fingerprints')
    reference = packet_coded_reference(expanded, known, min_hex_len=min_hex_len)
    return {
        'recommended_write_kind': 'coded_reference',
        'semantic_fingerprint': semantic_fingerprint,
        'reference': reference,
        'why': 'the archive already has this semantic body, so the repeat can shrink below the archive-local prefix reference by moving the reference wrapper itself into the local codebook',
    }


def packet_archive_write_plan(packet: dict[str, Any], known_fingerprints: set[str] | list[str] | tuple[str, ...]) -> dict[str, Any]:
    expanded = expand_packet(packet)
    archive_local_packet = _archive_localize_packet(expanded)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint in known:
        return {
            'recommended_write_kind': 'reference',
            'semantic_fingerprint': semantic_fingerprint,
            'reference': packet_reference(expanded),
            'why': 'the archive already has a packet body for this semantic decision, so storing only a fingerprint reference avoids duplicate packet bodies',
        }
    return {
        'recommended_write_kind': 'archive_local_body',
        'semantic_fingerprint': semantic_fingerprint,
        'packet': archive_local_packet,
        'why': 'this semantic decision is not yet present, so the archive should store one archive-local packet body keyed by fingerprint',
    }


def _archive_localize_packet(packet: dict[str, Any], profile_ref: str = ARCHIVE_LOCAL_PROFILE_REF) -> dict[str, Any]:
    _validate_standalone_packet(packet)
    if profile_ref not in archive_local_profile_registry():
        raise PacketError(f'unsupported archive-local profile_ref: {profile_ref}')
    return {
        'packet_kind': ARCHIVE_LOCAL_PACKET_KIND,
        'profile_ref': profile_ref,
        'mode': packet['mode'],
        'question_scope': packet['question_scope'],
        'evidence': packet['evidence'],
        'result': packet['result'],
    }


def expand_archive_local_packet(packet: dict[str, Any]) -> dict[str, Any]:
    _validate_archive_local_packet(packet)
    profile_ref = packet['profile_ref']
    profile = archive_local_profile_registry()[profile_ref]
    return {
        'packet_kind': PACKET_KIND,
        'mode': packet['mode'],
        'question_scope': packet['question_scope'],
        'evidence': packet['evidence'],
        'result': packet['result'],
        'provenance': profile,
    }


def packet_storage_decision(*, need_standalone_portability: bool) -> dict[str, Any]:
    if need_standalone_portability:
        return {
            'recommended_storage_form': 'standalone',
            'why': 'standalone packets repeat provenance so they can travel outside the archive without an external profile registry',
        }
    return {
        'recommended_storage_form': 'archive_local',
        'why': 'archive-local packets replace repeated provenance with a shared profile reference and are smaller for long-lived in-archive storage',
    }


def packet_repeat_storage_decision(
    *,
    need_standalone_portability: bool,
    archive_has_reference_codebook: bool = False,
    archive_has_reference_microframe_codec: bool = False,
    archive_has_reference_packed_codec: bool = False,
    archive_has_reference_byteframe_codec: bool = False,
) -> dict[str, Any]:
    if need_standalone_portability:
        return {
            'recommended_storage_form': 'reference',
            'why': 'portable repeats outside the archive should carry the full semantic fingerprint because the receiver may not have the local prefix index, reference codebook, microframe codec, or packed-prefix codec',
        }
    if archive_has_reference_byteframe_codec:
        return {
            'recommended_storage_form': 'byte_reference',
            'why': 'when the archive preserves the byteframe codec, repeats can shrink below packed references by storing the numeric tag byte and resolved local prefix bytes as one base64url string',
        }
    if archive_has_reference_packed_codec:
        return {
            'recommended_storage_form': 'packed_reference',
            'why': 'when the archive preserves the packed-prefix codec, repeats can shrink below tagged microframes by base64url-packing the shortest even-length local prefix behind a numeric tag',
        }
    if archive_has_reference_microframe_codec:
        return {
            'recommended_storage_form': 'micro_reference',
            'why': 'when the archive preserves the local microframe codec, repeats can collapse to a tagged tuple containing only the shortest unique local prefix',
        }
    if archive_has_reference_codebook:
        return {
            'recommended_storage_form': 'coded_reference',
            'why': 'when the archive preserves the local reference codebook, repeats can shrink below archive-local prefix references by encoding the wrapper itself as a tiny local code',
        }
    return {
        'recommended_storage_form': 'archive_local_reference',
        'why': 'without the extra reference codebook, the best in-archive repeat form is still the shortest unique archive-local prefix reference',
    }


def _dedupe_preserving_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _choose_smallest_storage_form(
    candidate_bytes: dict[str, int],
    *,
    preferred_order: list[str],
) -> tuple[str, int, list[str]]:
    if not candidate_bytes:
        raise PacketError('storage-form selection requires at least one candidate')
    best_bytes = min(candidate_bytes.values())
    tied_forms = sorted(name for name, size in candidate_bytes.items() if size == best_bytes)
    for name in _dedupe_preserving_order(preferred_order + tied_forms):
        if name in tied_forms:
            return name, best_bytes, tied_forms
    raise PacketError('could not choose a smallest storage form from the candidate frontier')


def packet_body_storage_frontier(
    packet: Any,
    *,
    need_standalone_portability: bool,
    need_human_readable_packet: bool = False,
    archive_has_core_expander: bool = True,
    archive_has_seed_codebook: bool = False,
    archive_has_seed_microframe_codec: bool = False,
    archive_has_seed_packed_codec: bool = False,
    archive_has_seed_byteframe_codec: bool = False,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    default_decision = packet_body_storage_decision(
        need_standalone_portability=need_standalone_portability,
        need_human_readable_packet=need_human_readable_packet,
        archive_has_core_expander=archive_has_core_expander,
        archive_has_seed_codebook=archive_has_seed_codebook,
        archive_has_seed_microframe_codec=archive_has_seed_microframe_codec,
        archive_has_seed_packed_codec=archive_has_seed_packed_codec,
        archive_has_seed_byteframe_codec=archive_has_seed_byteframe_codec,
    )
    candidates: dict[str, Any] = {}
    if need_standalone_portability:
        candidates['standalone'] = expanded
    elif need_human_readable_packet:
        candidates['archive_local'] = _archive_localize_packet(expanded)
    else:
        candidates['archive_local'] = _archive_localize_packet(expanded)
        if archive_has_core_expander:
            candidates['semantic_core'] = packet_semantic_core(expanded)
            if archive_has_seed_codebook:
                candidates['coded_seed'] = packet_coded_seed(expanded)
                if archive_has_seed_microframe_codec:
                    candidates['micro_seed'] = packet_micro_seed(expanded)
                    if archive_has_seed_packed_codec:
                        candidates['packed_seed'] = packet_packed_seed(expanded)
                        if archive_has_seed_byteframe_codec:
                            candidates['byte_seed'] = packet_byte_seed(expanded)
    candidate_minified_bytes = {name: packet_minified_bytes(obj) for name, obj in candidates.items()}
    winner, best_bytes, tied_forms = _choose_smallest_storage_form(
        candidate_minified_bytes,
        preferred_order=[
            default_decision['recommended_storage_form'],
            'byte_seed',
            'packed_seed',
            'micro_seed',
            'coded_seed',
            'semantic_core',
            'archive_local',
            'standalone',
        ],
    )
    default_form = default_decision['recommended_storage_form']
    default_bytes = candidate_minified_bytes[default_form]
    if winner == default_form:
        why = (
            f'measured candidate bytes agree with the coarse ladder for this packet: '
            f'{winner} is smallest-or-tied at {best_bytes} minified bytes'
        )
    else:
        why = (
            f'measured candidate bytes override the coarse ladder for this packet: '
            f'{winner} is {best_bytes} minified bytes while the coarse default {default_form} is {default_bytes}'
        )
    return {
        'recommended_storage_form': winner,
        'smallest_minified_bytes': best_bytes,
        'tied_storage_forms': tied_forms,
        'candidate_minified_bytes': candidate_minified_bytes,
        'default_storage_form': default_form,
        'default_storage_form_bytes': default_bytes,
        'bytes_saved_vs_default': default_bytes - best_bytes,
        'why': why,
    }


def packet_repeat_storage_frontier(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    need_standalone_portability: bool,
    archive_has_reference_codebook: bool = False,
    archive_has_reference_microframe_codec: bool = False,
    archive_has_reference_packed_codec: bool = False,
    archive_has_reference_byteframe_codec: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    default_decision = packet_repeat_storage_decision(
        need_standalone_portability=need_standalone_portability,
        archive_has_reference_codebook=archive_has_reference_codebook,
        archive_has_reference_microframe_codec=archive_has_reference_microframe_codec,
        archive_has_reference_packed_codec=archive_has_reference_packed_codec,
        archive_has_reference_byteframe_codec=archive_has_reference_byteframe_codec,
    )
    candidates: dict[str, Any] = {'reference': packet_reference(expanded)}
    if not need_standalone_portability:
        if semantic_fingerprint not in known:
            raise PacketError('repeat-storage frontier requires the semantic fingerprint to already exist in the archive index')
        candidates['archive_local_reference'] = packet_archive_local_reference(
            expanded,
            known,
            min_hex_len=min_reference_prefix_hex_len,
        )
        if archive_has_reference_codebook:
            candidates['coded_reference'] = packet_coded_reference(
                expanded,
                known,
                min_hex_len=min_reference_prefix_hex_len,
            )
            if archive_has_reference_microframe_codec:
                candidates['micro_reference'] = packet_micro_reference(
                    expanded,
                    known,
                    min_hex_len=min_reference_prefix_hex_len,
                )
                if archive_has_reference_packed_codec:
                    candidates['packed_reference'] = packet_packed_reference(
                        expanded,
                        known,
                        min_hex_len=min_reference_prefix_hex_len,
                    )
                    if archive_has_reference_byteframe_codec:
                        candidates['byte_reference'] = packet_byte_reference(
                            expanded,
                            known,
                            min_hex_len=min_reference_prefix_hex_len,
                        )
    candidate_minified_bytes = {name: packet_minified_bytes(obj) for name, obj in candidates.items()}
    winner, best_bytes, tied_forms = _choose_smallest_storage_form(
        candidate_minified_bytes,
        preferred_order=[
            default_decision['recommended_storage_form'],
            'byte_reference',
            'packed_reference',
            'micro_reference',
            'coded_reference',
            'archive_local_reference',
            'reference',
        ],
    )
    default_form = default_decision['recommended_storage_form']
    default_bytes = candidate_minified_bytes[default_form]
    if winner == default_form:
        why = (
            f'measured repeat-candidate bytes agree with the coarse ladder for this packet: '
            f'{winner} is smallest-or-tied at {best_bytes} minified bytes'
        )
    else:
        why = (
            f'measured repeat-candidate bytes override the coarse ladder for this packet: '
            f'{winner} is {best_bytes} minified bytes while the coarse default {default_form} is {default_bytes}'
        )
    return {
        'recommended_storage_form': winner,
        'smallest_minified_bytes': best_bytes,
        'tied_storage_forms': tied_forms,
        'candidate_minified_bytes': candidate_minified_bytes,
        'default_storage_form': default_form,
        'default_storage_form_bytes': default_bytes,
        'bytes_saved_vs_default': default_bytes - best_bytes,
        'semantic_fingerprint': semantic_fingerprint,
        'why': why,
    }




def _packed_seed_minified_bytes_exact(packet: list[Any] | tuple[Any, ...]) -> int:
    _validate_packed_seed_packet(packet)
    return _json_minified_array_len(packet)



def _packed_seed_raw_len_exact(packet: list[Any] | tuple[Any, ...]) -> int:
    _validate_packed_seed_packet(packet)
    tag = packet[0]
    if tag == PACKED_MODE_TAGS['oracle_coordinates']:
        return 1 + _byte_scalar_token_len(packet[1]) + _byte_scalar_token_len(packet[2])
    if tag == PACKED_MODE_TAGS['oracle_weights']:
        return _byte_weight_seed_raw_len_from_payload(packet[1:])
    return 2



def _byte_seed_minified_bytes_exact_from_packed_seed(packet: list[Any] | tuple[Any, ...]) -> int:
    return 2 + _base64url_unpadded_len(_packed_seed_raw_len_exact(packet))



def packet_seed_storage_exact_choice(
    packet: Any,
    *,
    atomize_scalars: bool = True,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    packed_seed = packet_packed_seed(expanded, atomize_scalars=atomize_scalars)
    candidate_minified_bytes = {
        'packed_seed': _packed_seed_minified_bytes_exact(packed_seed),
        'byte_seed': _byte_seed_minified_bytes_exact_from_packed_seed(packed_seed),
    }
    winner, best_bytes, tied_forms = _choose_smallest_storage_form(
        candidate_minified_bytes,
        preferred_order=['byte_seed', 'packed_seed'],
    )
    return {
        'recommended_storage_form': winner,
        'smallest_minified_bytes': best_bytes,
        'tied_storage_forms': tied_forms,
        'candidate_storage_forms': ['packed_seed', 'byte_seed'],
        'candidate_minified_bytes': candidate_minified_bytes,
        'candidate_evaluation_count': 1,
        'packed_seed_packet_preview': packed_seed,
        'why': 'local first writes can now choose exactly between packed_seed and byte_seed by byte arithmetic on the shared packed payload instead of materializing both candidates and re-measuring their minified JSON bodies',
    }



def oracle_weight_seed_storage_choice(
    packet: Any,
    *,
    atomize_scalars: bool = True,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    if expanded['mode'] != 'oracle_weights':
        raise PacketError('oracle_weight_seed_storage_choice only supports oracle_weights packets')
    exact = packet_seed_storage_exact_choice(expanded, atomize_scalars=atomize_scalars)
    payload = exact['packed_seed_packet_preview'][1:]
    if payload and payload[0] == PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG:
        payload_shape = 'grouped_atom_masks'
        group_count = (len(payload) - 1) // 2
        active_axes = sum(mask.bit_count() for mask in payload[1::2])
    else:
        payload_shape = 'sparse_vector'
        group_count = 1 if payload and payload[0] else 0
        active_axes = payload[0].bit_count() if payload else 0
    return {
        'recommended_storage_form': exact['recommended_storage_form'],
        'smallest_minified_bytes': exact['smallest_minified_bytes'],
        'tied_storage_forms': exact['tied_storage_forms'],
        'candidate_storage_forms': exact['candidate_storage_forms'],
        'candidate_minified_bytes': exact['candidate_minified_bytes'],
        'candidate_evaluation_count': exact['candidate_evaluation_count'],
        'packed_seed_packet_preview': exact['packed_seed_packet_preview'],
        'payload_shape': payload_shape,
        'group_count': group_count,
        'active_axis_count': active_axes,
        'payload_token_count': len(payload),
        'why': 'oracle-weight first writes can now choose between packed_seed and byte_seed by exact payload-byte formulas instead of materializing both candidates and re-measuring their minified JSON bodies',
    }



def _packed_reference_minified_bytes_from_prefix(prefix_hex: str) -> int:
    return _json_minified_array_len([PACKED_MODE_TAGS['reference'], _prefix_hex_to_base64url(prefix_hex)])



def _byte_reference_minified_bytes_from_prefix(prefix_hex: str) -> int:
    if not isinstance(prefix_hex, str) or not prefix_hex or len(prefix_hex) % 2 != 0:
        raise PacketError(f'byte reference sizing requires a non-empty even-length lowercase-hex prefix, got {prefix_hex!r}')
    return 2 + _base64url_unpadded_len(1 + len(prefix_hex) // 2)



def packet_repeat_storage_exact_choice(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint not in known:
        raise PacketError('exact repeat-storage choice requires the semantic fingerprint to already exist in the archive index')
    prefix_hex = _even_unique_reference_prefix(
        semantic_fingerprint,
        known,
        min_hex_len=min_reference_prefix_hex_len,
    )
    candidate_minified_bytes = {
        'packed_reference': _packed_reference_minified_bytes_from_prefix(prefix_hex),
        'byte_reference': _byte_reference_minified_bytes_from_prefix(prefix_hex),
    }
    winner, best_bytes, tied_forms = _choose_smallest_storage_form(
        candidate_minified_bytes,
        preferred_order=['byte_reference', 'packed_reference'],
    )
    return {
        'recommended_storage_form': winner,
        'smallest_minified_bytes': best_bytes,
        'tied_storage_forms': tied_forms,
        'candidate_storage_forms': ['packed_reference', 'byte_reference'],
        'candidate_minified_bytes': candidate_minified_bytes,
        'candidate_evaluation_count': 1,
        'prefix_hex': prefix_hex,
        'prefix_hex_len': len(prefix_hex),
        'semantic_fingerprint': semantic_fingerprint,
        'why': 'local repeat writes can now choose exactly between packed_reference and byte_reference by byte arithmetic on the resolved even-length local prefix instead of materializing both candidates and re-measuring their minified JSON bodies',
    }

def packet_body_storage_compiled_frontier(
    packet: Any,
    *,
    need_human_readable_packet: bool = False,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    if need_human_readable_packet:
        archive_local = _archive_localize_packet(expanded)
        archive_local_bytes = packet_minified_bytes(archive_local)
        return {
            'recommended_storage_form': 'archive_local',
            'candidate_storage_forms': ['archive_local'],
            'candidate_minified_bytes': {'archive_local': archive_local_bytes},
            'candidate_evaluation_count': 1,
            'why': 'human-readable archive storage still needs the archive-local packet, so the compiled zepto frontier can stop before measuring any seed codecs',
        }

    exact = packet_seed_storage_exact_choice(expanded)
    return {
        'recommended_storage_form': exact['recommended_storage_form'],
        'smallest_minified_bytes': exact['smallest_minified_bytes'],
        'tied_storage_forms': exact['tied_storage_forms'],
        'candidate_storage_forms': exact['candidate_storage_forms'],
        'candidate_minified_bytes': exact['candidate_minified_bytes'],
        'candidate_evaluation_count': exact['candidate_evaluation_count'],
        'why': exact['why'],
    }


def packet_repeat_storage_compiled_frontier(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint not in known:
        raise PacketError('compiled repeat-storage frontier requires the semantic fingerprint to already exist in the archive index')
    exact = packet_repeat_storage_exact_choice(
        expanded,
        known,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )
    return {
        'recommended_storage_form': exact['recommended_storage_form'],
        'smallest_minified_bytes': exact['smallest_minified_bytes'],
        'tied_storage_forms': exact['tied_storage_forms'],
        'candidate_storage_forms': exact['candidate_storage_forms'],
        'candidate_minified_bytes': exact['candidate_minified_bytes'],
        'candidate_evaluation_count': exact['candidate_evaluation_count'],
        'semantic_fingerprint': semantic_fingerprint,
        'why': exact['why'],
    }


def packet_body_storage_decision(
    *,
    need_standalone_portability: bool,
    need_human_readable_packet: bool = False,
    archive_has_core_expander: bool = True,
    archive_has_seed_codebook: bool = False,
    archive_has_seed_microframe_codec: bool = False,
    archive_has_seed_packed_codec: bool = False,
    archive_has_seed_byteframe_codec: bool = False,
) -> dict[str, Any]:
    if need_standalone_portability:
        return {
            'recommended_storage_form': 'standalone',
            'why': 'portable storage outside the archive still requires the full standalone packet because the receiver may not have the shared profile registry, semantic-core expander, microframe codec, or packed seed codec',
        }
    if (
        archive_has_seed_byteframe_codec
        and archive_has_seed_packed_codec
        and archive_has_seed_microframe_codec
        and archive_has_seed_codebook
        and archive_has_core_expander
        and not need_human_readable_packet
    ):
        return {
            'recommended_storage_form': 'byte_seed',
            'why': 'when the archive preserves the byteframe codec alongside the packed seed codec, microframe codec, seed codebook, and executable expander, the byteframe seed is the smallest-or-tied durable body because it removes numeric-array wrapper bytes whenever those wrappers would cost extra storage',
        }
    if (
        archive_has_seed_packed_codec
        and archive_has_seed_microframe_codec
        and archive_has_seed_codebook
        and archive_has_core_expander
        and not need_human_readable_packet
    ):
        return {
            'recommended_storage_form': 'packed_seed',
            'why': 'when the archive preserves the packed seed codec, microframe codec, seed codebook, and executable expander, the smallest durable body is the packed seed rather than the longer tagged microframe seed',
        }
    if archive_has_seed_microframe_codec and archive_has_seed_codebook and archive_has_core_expander and not need_human_readable_packet:
        return {
            'recommended_storage_form': 'micro_seed',
            'why': 'when the archive preserves the local microframe codec, seed codebook, and executable expander, the smallest durable body is the tagged microframe seed rather than the larger object-wrapped coded seed',
        }
    if archive_has_seed_codebook and archive_has_core_expander and not need_human_readable_packet:
        return {
            'recommended_storage_form': 'coded_seed',
            'why': 'when the archive preserves the local seed codebook and the executable expander, the smallest durable body is the mode-coded seed rather than the more self-describing semantic core',
        }
    if archive_has_core_expander and not need_human_readable_packet:
        return {
            'recommended_storage_form': 'semantic_core',
            'why': 'the archive already contains the executable expander, so long-lived storage can keep only the minimal semantic seed and reconstruct the archive-local or standalone packet on demand',
        }
    return {
        'recommended_storage_form': 'archive_local',
        'why': 'when operators want a directly readable packet body inside the archive, archive-local packets keep the shared provenance profile while avoiding semantic-core reconstruction at read time',
    }


def _packet(mode: str, question_scope: str, evidence: dict[str, Any], result: dict[str, Any], *, archive_local: bool = False) -> dict[str, Any]:
    packet = {
        'packet_kind': PACKET_KIND,
        'mode': mode,
        'question_scope': question_scope,
        'evidence': evidence,
        'result': result,
        'provenance': _common_provenance(),
    }
    return _archive_localize_packet(packet) if archive_local else packet


def packet_minified_bytes(packet: Any) -> int:
    return len(json.dumps(packet, sort_keys=True, separators=(',', ':')).encode('utf-8'))


def packet_semantic_core(packet: dict[str, Any]) -> dict[str, Any]:
    expanded = expand_packet(packet)
    mode = expanded['mode']
    core = {
        'packet_kind': SEMANTIC_CORE_KIND,
        'core_contract_version': SEMANTIC_CORE_CONTRACT_VERSION,
        'mode': mode,
    }
    if mode == 'oracle_coordinates':
        core['B'] = expanded['evidence']['B']
        core['H'] = expanded['evidence']['H']
        return core
    if mode == 'oracle_weights':
        core['weights'] = expanded['evidence']['weights']
        return core
    if mode == 'probe_robustness_fixed':
        core['signature'] = expanded['evidence']['observed_signature']
        return core
    if mode == 'probe_robustness_adaptive':
        core['route'] = expanded['evidence']['observed_route']
        return core
    if mode == 'probe_strict_adaptive':
        core['route'] = expanded['evidence']['observed_route']
        return core
    if mode == 'probe_exact_checked_cap_path':
        core['signature'] = expanded['evidence']['observed_signature']
        return core
    raise PacketError(f'unsupported packet mode for semantic-core conversion: {mode}')


def packet_coded_seed(packet: dict[str, Any]) -> dict[str, Any]:
    core = packet_semantic_core(packet)
    mode = core['mode']
    seed = {
        'k': CODED_SEED_KIND,
        'p': CODED_SEED_PROFILE_REF,
        'm': CODED_SEED_MODE_CODES[mode],
    }
    if mode == 'oracle_coordinates':
        seed['B'] = core['B']
        seed['H'] = core['H']
        return seed
    if mode == 'oracle_weights':
        seed['w'] = core['weights']
        return seed
    if mode == 'probe_robustness_fixed':
        seed['s'] = core['signature']
        return seed
    if mode == 'probe_robustness_adaptive':
        seed['r'] = core['route']
        return seed
    if mode == 'probe_strict_adaptive':
        seed['r'] = core['route']
        return seed
    if mode == 'probe_exact_checked_cap_path':
        seed['s'] = core['signature']
        return seed
    raise PacketError(f'unsupported packet mode for coded-seed conversion: {mode}')


def expand_coded_seed_packet(packet: dict[str, Any], *, archive_local: bool = False) -> dict[str, Any]:
    _validate_coded_seed_packet(packet)
    mode = CODED_SEED_MODE_FROM_CODE[packet['m']]
    core = {
        'packet_kind': SEMANTIC_CORE_KIND,
        'core_contract_version': SEMANTIC_CORE_CONTRACT_VERSION,
        'mode': mode,
    }
    if mode == 'oracle_coordinates':
        core['B'] = packet['B']
        core['H'] = packet['H']
    elif mode == 'oracle_weights':
        core['weights'] = packet['w']
    elif mode == 'probe_robustness_fixed':
        core['signature'] = packet['s']
    elif mode == 'probe_robustness_adaptive':
        core['route'] = packet['r']
    elif mode == 'probe_strict_adaptive':
        core['route'] = packet['r']
    elif mode == 'probe_exact_checked_cap_path':
        core['signature'] = packet['s']
    else:
        raise PacketError(f'unsupported coded-seed mode: {mode}')
    return expand_semantic_core_packet(core, archive_local=archive_local)


def _is_microframe_packet(packet: Any) -> bool:
    return isinstance(packet, (list, tuple)) and bool(packet) and isinstance(packet[0], str)


def _is_micro_seed_packet(packet: Any) -> bool:
    return _is_microframe_packet(packet) and packet[0] in CODED_SEED_MODE_FROM_CODE


def _is_micro_reference_packet(packet: Any) -> bool:
    return _is_microframe_packet(packet) and packet[0] == MICROFRAME_REFERENCE_TAG


def _validate_micro_seed_packet(packet: Any) -> None:
    if not _is_micro_seed_packet(packet):
        raise PacketError('expected a seed microframe with a supported mode-code tag in slot 0')
    tag = packet[0]
    if tag == 'oc':
        if len(packet) != 3:
            raise PacketError(f'oracle-coordinate microframe must have length 3, got {len(packet)}')
        if not isinstance(packet[1], str) or not isinstance(packet[2], str):
            raise PacketError('oracle-coordinate microframe must store string B and H payloads')
        return
    if tag == 'ow':
        if len(packet) != 2:
            raise PacketError(f'oracle-weight microframe must have length 2, got {len(packet)}')
        if not isinstance(packet[1], dict):
            raise PacketError('oracle-weight microframe must store the weights mapping in slot 1')
        return
    if tag in {'rf', 'ra', 'sa', 'xp'}:
        if len(packet) != 2:
            raise PacketError(f'microframe for mode tag {tag} must have length 2, got {len(packet)}')
        if not isinstance(packet[1], str):
            raise PacketError(f'microframe payload for mode tag {tag} must be a string')
        return
    raise PacketError(f'unsupported microframe seed mode tag: {tag}')


def _validate_micro_reference_packet(packet: Any) -> None:
    if not _is_micro_reference_packet(packet):
        raise PacketError(f'expected a reference microframe tagged with {MICROFRAME_REFERENCE_TAG!r} in slot 0')
    if len(packet) != 2:
        raise PacketError(f'reference microframe must have length 2, got {len(packet)}')
    prefix = packet[1]
    if not isinstance(prefix, str) or not prefix:
        raise PacketError('reference microframe must include a non-empty lowercase-hex prefix in slot 1')
    if any(ch not in '0123456789abcdef' for ch in prefix):
        raise PacketError(f'reference microframe prefix must be lowercase hex, got {prefix}')


def packet_micro_seed(packet: Any) -> list[Any]:
    coded_seed = packet_coded_seed(packet)
    mode_code = coded_seed['m']
    if mode_code == 'oc':
        return [mode_code, coded_seed['B'], coded_seed['H']]
    if mode_code == 'ow':
        return [mode_code, coded_seed['w']]
    if mode_code in {'rf', 'xp'}:
        return [mode_code, coded_seed['s']]
    if mode_code in {'ra', 'sa'}:
        return [mode_code, coded_seed['r']]
    raise PacketError(f'unsupported coded-seed mode for microframe conversion: {mode_code}')


def expand_micro_seed_packet(packet: Any, *, archive_local: bool = False) -> dict[str, Any]:
    _validate_micro_seed_packet(packet)
    mode_code = packet[0]
    coded_seed = {'k': CODED_SEED_KIND, 'p': CODED_SEED_PROFILE_REF, 'm': mode_code}
    if mode_code == 'oc':
        coded_seed['B'] = packet[1]
        coded_seed['H'] = packet[2]
    elif mode_code == 'ow':
        coded_seed['w'] = packet[1]
    elif mode_code in {'rf', 'xp'}:
        coded_seed['s'] = packet[1]
    elif mode_code in {'ra', 'sa'}:
        coded_seed['r'] = packet[1]
    else:
        raise PacketError(f'unsupported microframe seed mode: {mode_code}')
    return expand_coded_seed_packet(coded_seed, archive_local=archive_local)


def packet_micro_reference(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> list[str]:
    archive_local_reference = packet_archive_local_reference(packet, known_fingerprints, min_hex_len=min_hex_len)
    return [MICROFRAME_REFERENCE_TAG, archive_local_reference['prefix']]


def expand_micro_reference_packet(packet: Any) -> dict[str, Any]:
    _validate_micro_reference_packet(packet)
    return {'packet_kind': ARCHIVE_LOCAL_REFERENCE_KIND, 'prefix': packet[1]}



def _is_packedframe_packet(packet: Any) -> bool:
    return isinstance(packet, (list, tuple)) and bool(packet) and isinstance(packet[0], int)


def _is_byteframe_packet(packet: Any) -> bool:
    if not isinstance(packet, str) or not packet:
        return False
    try:
        _base64url_decode_bytes(packet)
    except PacketError:
        return False
    return True


def _is_catalog_reference_packet(packet: Any) -> bool:
    if not _is_byteframe_packet(packet):
        return False
    try:
        raw = _base64url_decode_bytes(packet)
    except PacketError:
        return False
    return bool(raw) and raw[0] == CATALOG_REFERENCE_TAG


def _is_short_catalog_reference_packet(packet: Any) -> bool:
    if not _is_byteframe_packet(packet):
        return False
    try:
        raw = _base64url_decode_bytes(packet)
    except PacketError:
        return False
    return len(raw) == 2 and raw[0] & SHORT_CATALOG_REFERENCE_PREFIX_MASK == SHORT_CATALOG_REFERENCE_PREFIX


def _is_byte_seed_packet(packet: Any) -> bool:
    if not _is_byteframe_packet(packet):
        return False
    try:
        raw = _base64url_decode_bytes(packet)
    except PacketError:
        return False
    return bool(raw) and raw[0] in set(PACKED_MODE_TAGS.values()) - {PACKED_MODE_TAGS['reference']}


def _is_byte_reference_packet(packet: Any) -> bool:
    if not _is_byteframe_packet(packet):
        return False
    try:
        raw = _base64url_decode_bytes(packet)
    except PacketError:
        return False
    return bool(raw) and raw[0] == PACKED_MODE_TAGS['reference']


def _is_packed_seed_packet(packet: Any) -> bool:
    return _is_packedframe_packet(packet) and packet[0] in set(PACKED_MODE_TAGS.values()) - {PACKED_MODE_TAGS['reference']}


def _is_packed_reference_packet(packet: Any) -> bool:
    return _is_packedframe_packet(packet) and packet[0] == PACKED_MODE_TAGS['reference']


def _encode_signature_code(signature: str) -> int:
    value = 0
    for symbol in signature:
        normalized = _normalize_symbol(symbol)
        value = value * 3 + PACKED_SIGNATURE_SYMBOL_TO_CODE[normalized]
    return value


def _decode_signature_code(value: int, *, width: int) -> str:
    if not isinstance(value, int) or value < 0 or value >= 3**width:
        raise PacketError(f'signature code must be an integer in [0,{3**width - 1}], got {value}')
    digits: list[str] = []
    current = value
    for _ in range(width):
        current, remainder = divmod(current, 3)
        digits.append(PACKED_SIGNATURE_CODE_TO_SYMBOL[remainder])
    return ''.join(reversed(digits))


def _pack_scalar_atom(value: Any) -> int | str:
    normalized = str(value)
    return PACKED_SCALAR_ATOM_CODES.get(normalized, normalized)


def _expand_scalar_atom(value: Any) -> str:
    if isinstance(value, int):
        if value not in PACKED_SCALAR_FROM_ATOM:
            raise PacketError(f'unsupported packed scalar atom code: {value}')
        return PACKED_SCALAR_FROM_ATOM[value]
    if isinstance(value, str):
        return value
    raise PacketError(f'packed scalar payloads must be strings or atom integers, got {type(value).__name__}')


def _normalize_weight_mapping(weights: dict[str, Any]) -> dict[str, str]:
    if not isinstance(weights, dict):
        raise PacketError('weight payload must be a mapping')
    normalized: dict[str, str] = {}
    for key in WEIGHT_KEYS:
        if key not in weights:
            raise PacketError(f'weight payload is missing required key {key}')
        normalized[key] = str(weights[key])
    extra = sorted(key for key in weights if key not in WEIGHT_KEYS)
    if extra:
        raise PacketError(f'weight payload has unsupported extra keys: {extra}')
    return normalized


def pack_weight_vector(weights: dict[str, Any], *, atomize_scalars: bool = True) -> list[Any]:
    normalized = _normalize_weight_mapping(weights)
    mask = 0
    payload: list[Any] = []
    for bit, key in enumerate(WEIGHT_KEYS):
        value = normalized[key]
        if value != '0':
            mask |= 1 << bit
            payload.append(_pack_scalar_atom(value) if atomize_scalars else value)
    return [mask, *payload]


def pack_weight_atom_masks(weights: dict[str, Any], *, atomize_scalars: bool = True) -> list[Any]:
    normalized = _normalize_weight_mapping(weights)
    masks_by_value: dict[Any, int] = {}
    order: list[Any] = []
    for bit, key in enumerate(WEIGHT_KEYS):
        value = normalized[key]
        if value == '0':
            continue
        encoded = _pack_scalar_atom(value) if atomize_scalars else value
        if encoded not in masks_by_value:
            masks_by_value[encoded] = 0
            order.append(encoded)
        masks_by_value[encoded] |= 1 << bit
    payload: list[Any] = [PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG]
    for encoded in order:
        payload.extend([masks_by_value[encoded], encoded])
    return payload


def pack_weight_vector_best(weights: dict[str, Any], *, atomize_scalars: bool = True) -> list[Any]:
    vector_payload = pack_weight_vector(weights, atomize_scalars=atomize_scalars)
    atom_mask_payload = pack_weight_atom_masks(weights, atomize_scalars=atomize_scalars)
    if packet_minified_bytes(atom_mask_payload) < packet_minified_bytes(vector_payload):
        return atom_mask_payload
    return vector_payload


def _expand_sparse_packed_weight_vector(payload: list[Any] | tuple[Any, ...]) -> dict[str, str]:
    if not payload or not isinstance(payload[0], int):
        raise PacketError('packed weight payload must start with an integer bitmask')
    mask = payload[0]
    if mask < 0 or mask >= 1 << len(WEIGHT_KEYS):
        raise PacketError(f'packed weight bitmask must be in [0,{(1 << len(WEIGHT_KEYS)) - 1}], got {mask}')
    expected_values = mask.bit_count()
    if len(payload) != 1 + expected_values:
        raise PacketError(
            f'packed weight payload with bitmask {mask} must carry {expected_values} nonzero values, got {len(payload) - 1}'
        )
    values = list(payload[1:])
    expanded_values = [_expand_scalar_atom(value) for value in values]
    expanded: dict[str, str] = {}
    value_index = 0
    for bit, key in enumerate(WEIGHT_KEYS):
        if mask & (1 << bit):
            expanded[key] = expanded_values[value_index]
            value_index += 1
        else:
            expanded[key] = '0'
    return expanded


def _expand_atom_mask_weight_vector(payload: list[Any] | tuple[Any, ...]) -> dict[str, str]:
    if not payload or payload[0] != PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG:
        raise PacketError('packed grouped weight payload must start with the atom-mask format tag')
    if len(payload) == 1:
        return {key: '0' for key in WEIGHT_KEYS}
    if (len(payload) - 1) % 2 != 0:
        raise PacketError('packed grouped weight payload must store alternating mask/value pairs after the format tag')
    expanded = {key: '0' for key in WEIGHT_KEYS}
    seen_mask = 0
    full_mask = (1 << len(WEIGHT_KEYS)) - 1
    for index in range(1, len(payload), 2):
        mask = payload[index]
        value = payload[index + 1]
        if not isinstance(mask, int):
            raise PacketError('packed grouped weight payload masks must be integers')
        if mask <= 0 or mask > full_mask:
            raise PacketError(f'packed grouped weight payload masks must be in [1,{full_mask}], got {mask}')
        if seen_mask & mask:
            raise PacketError('packed grouped weight payload masks must not overlap')
        scalar = _expand_scalar_atom(value)
        seen_mask |= mask
        for bit, key in enumerate(WEIGHT_KEYS):
            if mask & (1 << bit):
                expanded[key] = scalar
    return expanded


def expand_packed_weight_vector(payload: Any) -> dict[str, str]:
    if not isinstance(payload, (list, tuple)):
        raise PacketError('packed weight payload must be a list or tuple')
    if not payload or not isinstance(payload[0], int):
        raise PacketError('packed weight payload must start with an integer bitmask or grouped-format tag')
    if payload[0] == PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG:
        return _expand_atom_mask_weight_vector(payload)
    return _expand_sparse_packed_weight_vector(payload)


def _prefix_hex_to_base64url(prefix_hex: str) -> str:
    if not isinstance(prefix_hex, str) or not prefix_hex or len(prefix_hex) % 2 != 0:
        raise PacketError(f'packed prefix encoding requires a non-empty even-length lowercase-hex prefix, got {prefix_hex!r}')
    if any(ch not in '0123456789abcdef' for ch in prefix_hex):
        raise PacketError(f'packed prefix encoding requires lowercase hex, got {prefix_hex!r}')
    return base64.urlsafe_b64encode(bytes.fromhex(prefix_hex)).decode('ascii').rstrip('=')


def _prefix_base64url_to_hex(prefix_b64: str) -> str:
    if not isinstance(prefix_b64, str) or not prefix_b64:
        raise PacketError('packed prefix decoding requires a non-empty base64url string')
    padded = prefix_b64 + '=' * ((4 - len(prefix_b64) % 4) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode('ascii'))
    except Exception as exc:
        raise PacketError(f'could not decode packed prefix payload {prefix_b64!r}') from exc
    if not raw:
        raise PacketError('packed prefix decoding produced an empty byte string')
    return raw.hex()


def _base64url_encode_bytes(raw: bytes) -> str:
    if not isinstance(raw, (bytes, bytearray)) or not raw:
        raise PacketError('byteframe encoding requires a non-empty byte string')
    return base64.urlsafe_b64encode(bytes(raw)).decode('ascii').rstrip('=')


def _base64url_decode_bytes(payload: str) -> bytes:
    if not isinstance(payload, str) or not payload:
        raise PacketError('byteframe decoding requires a non-empty base64url string')
    padded = payload + '=' * ((4 - len(payload) % 4) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode('ascii'))
    except Exception as exc:
        raise PacketError(f'could not decode byteframe payload {payload!r}') from exc
    if not raw:
        raise PacketError('byteframe decoding produced an empty byte string')
    return raw



def _base64url_unpadded_len(raw_len: int) -> int:
    if not isinstance(raw_len, int) or raw_len <= 0:
        raise PacketError(f'base64url length requires a positive raw byte length, got {raw_len!r}')
    return (raw_len * 4 + 2) // 3



def _json_minified_scalar_len(value: Any) -> int:
    if isinstance(value, bool):
        return 4 if value else 5
    if value is None:
        return 4
    if isinstance(value, int):
        return len(str(value))
    if isinstance(value, str):
        return len(json.dumps(value, separators=(',', ':')))
    raise PacketError(f'unsupported scalar type for minified-json length: {type(value).__name__}')



def _json_minified_array_len(values: list[Any] | tuple[Any, ...]) -> int:
    if not isinstance(values, (list, tuple)):
        raise PacketError('minified-json array length requires a list or tuple payload')
    if not values:
        return 2
    return 2 + (len(values) - 1) + sum(_json_minified_scalar_len(value) for value in values)



def _byte_scalar_token_len(token: Any) -> int:
    if isinstance(token, int):
        if token not in PACKED_SCALAR_FROM_ATOM:
            raise PacketError(f'unsupported scalar atom token for byteframe sizing: {token}')
        return 1
    if isinstance(token, str):
        raw = token.encode('utf-8')
        if not raw:
            raise PacketError('byteframe scalar literals must be non-empty')
        if len(raw) > 127:
            raise PacketError(f'byteframe scalar literals must fit in 127 bytes, got {len(raw)}')
        return 1 + len(raw)
    raise PacketError(f'unsupported scalar token type for byteframe sizing: {type(token).__name__}')



def _packed_weight_seed_minified_bytes_from_payload(payload: list[Any] | tuple[Any, ...]) -> int:
    if not isinstance(payload, (list, tuple)) or not payload:
        raise PacketError('packed weight seed sizing requires a non-empty payload list or tuple')
    return _json_minified_array_len([PACKED_MODE_TAGS['oracle_weights'], *payload])



def _byte_weight_seed_raw_len_from_payload(payload: list[Any] | tuple[Any, ...]) -> int:
    if not isinstance(payload, (list, tuple)) or not payload:
        raise PacketError('byte weight seed sizing requires a non-empty payload list or tuple')
    raw_len = 3
    if payload[0] == PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG:
        if (len(payload) - 1) % 2 != 0:
            raise PacketError('grouped packed-weight payload must have mask/value pairs after the grouped-format tag')
        for index in range(1, len(payload), 2):
            mask = payload[index]
            if not isinstance(mask, int) or not 0 <= mask <= 0xFF:
                raise PacketError(f'byteframe grouped weight masks must be 0..255, got {mask!r}')
            raw_len += 1 + _byte_scalar_token_len(payload[index + 1])
        return raw_len
    mask = payload[0]
    if not isinstance(mask, int) or not 0 <= mask <= 0xFF:
        raise PacketError(f'byteframe sparse weight mask must be 0..255, got {mask!r}')
    return raw_len + sum(_byte_scalar_token_len(value) for value in payload[1:])



def _byte_weight_seed_minified_bytes_from_payload(payload: list[Any] | tuple[Any, ...]) -> int:
    return 2 + _base64url_unpadded_len(_byte_weight_seed_raw_len_from_payload(payload))


def _encode_byte_scalar_token(token: Any) -> bytes:
    if isinstance(token, int):
        if token not in PACKED_SCALAR_FROM_ATOM:
            raise PacketError(f'unsupported scalar atom token for byteframe encoding: {token}')
        return bytes([token])
    if isinstance(token, str):
        raw = token.encode('utf-8')
        if not raw:
            raise PacketError('byteframe scalar literals must be non-empty')
        if len(raw) > 127:
            raise PacketError(f'byteframe scalar literals must fit in 127 bytes, got {len(raw)}')
        return bytes([0x80 | len(raw)]) + raw
    raise PacketError(f'unsupported byteframe scalar token type: {type(token).__name__}')


def _decode_byte_scalar_token(raw: bytes, offset: int) -> tuple[Any, int]:
    if offset >= len(raw):
        raise PacketError('byteframe scalar token is truncated')
    header = raw[offset]
    offset += 1
    if header < 0x80:
        if header not in PACKED_SCALAR_FROM_ATOM:
            raise PacketError(f'unsupported scalar atom code in byteframe payload: {header}')
        return header, offset
    literal_len = header & 0x7F
    if literal_len == 0:
        raise PacketError('byteframe scalar literal length must be positive')
    end = offset + literal_len
    if end > len(raw):
        raise PacketError('byteframe scalar literal overruns payload')
    return raw[offset:end].decode('utf-8'), end


def _packed_seed_to_byteframe_raw(packet: list[Any]) -> bytes:
    _validate_packed_seed_packet(packet)
    tag = packet[0]
    raw = bytearray([tag])
    if tag == PACKED_MODE_TAGS['oracle_coordinates']:
        raw.extend(_encode_byte_scalar_token(packet[1]))
        raw.extend(_encode_byte_scalar_token(packet[2]))
        return bytes(raw)
    if tag == PACKED_MODE_TAGS['oracle_weights']:
        payload = packet[1:]
        if payload and payload[0] == PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG:
            if (len(payload) - 1) % 2 != 0:
                raise PacketError('grouped packed-weight payload must have mask/value pairs after the grouped-format tag')
            group_count = (len(payload) - 1) // 2
            if group_count > 255:
                raise PacketError(f'byteframe grouped weight payload supports at most 255 groups, got {group_count}')
            raw.extend([BYTEFRAME_WEIGHT_FORMAT_GROUPED, group_count])
            for index in range(group_count):
                mask = payload[1 + 2 * index]
                value = payload[2 + 2 * index]
                if not isinstance(mask, int) or not 0 <= mask <= 0xFF:
                    raise PacketError(f'byteframe grouped weight masks must be 0..255, got {mask!r}')
                raw.append(mask)
                raw.extend(_encode_byte_scalar_token(value))
            return bytes(raw)
        if not payload:
            raise PacketError('sparse packed-weight payload must include at least the active-axis mask')
        mask = payload[0]
        if not isinstance(mask, int) or not 0 <= mask <= 0xFF:
            raise PacketError(f'byteframe sparse weight mask must be 0..255, got {mask!r}')
        raw.extend([BYTEFRAME_WEIGHT_FORMAT_SPARSE, mask])
        for value in payload[1:]:
            raw.extend(_encode_byte_scalar_token(value))
        return bytes(raw)
    if len(packet) != 2 or not isinstance(packet[1], int) or not 0 <= packet[1] <= 0xFF:
        raise PacketError('non-weight byteframe seed modes must carry one integer payload byte')
    raw.append(packet[1])
    return bytes(raw)


def _byteframe_raw_to_packed_seed(raw: bytes) -> list[Any]:
    if not raw:
        raise PacketError('byteframe seed payload must not be empty')
    tag = raw[0]
    offset = 1
    if tag == PACKED_MODE_TAGS['oracle_coordinates']:
        first, offset = _decode_byte_scalar_token(raw, offset)
        second, offset = _decode_byte_scalar_token(raw, offset)
        if offset != len(raw):
            raise PacketError('byteframe coordinate seed has trailing bytes')
        return [tag, first, second]
    if tag == PACKED_MODE_TAGS['oracle_weights']:
        if offset + 2 > len(raw):
            raise PacketError('byteframe weight seed is truncated before its format byte and mask metadata')
        format_tag = raw[offset]
        offset += 1
        if format_tag == BYTEFRAME_WEIGHT_FORMAT_SPARSE:
            mask = raw[offset]
            offset += 1
            payload: list[Any] = [mask]
            for _ in range(mask.bit_count()):
                token, offset = _decode_byte_scalar_token(raw, offset)
                payload.append(token)
            if offset != len(raw):
                raise PacketError('byteframe sparse weight seed has trailing bytes')
            packed = [tag, *payload]
            _validate_packed_seed_packet(packed)
            return packed
        if format_tag == BYTEFRAME_WEIGHT_FORMAT_GROUPED:
            group_count = raw[offset]
            offset += 1
            payload = [PACKED_WEIGHT_ATOM_MASK_FORMAT_TAG]
            for _ in range(group_count):
                if offset >= len(raw):
                    raise PacketError('byteframe grouped weight seed is truncated before a group mask')
                mask = raw[offset]
                offset += 1
                token, offset = _decode_byte_scalar_token(raw, offset)
                payload.extend([mask, token])
            if offset != len(raw):
                raise PacketError('byteframe grouped weight seed has trailing bytes')
            packed = [tag, *payload]
            _validate_packed_seed_packet(packed)
            return packed
        raise PacketError(f'unsupported byteframe weight format tag: {format_tag}')
    if tag not in set(PACKED_MODE_TAGS.values()) - {PACKED_MODE_TAGS['reference']}:
        raise PacketError(f'unsupported byteframe seed tag: {tag}')
    if len(raw) != 2:
        raise PacketError('non-weight byteframe seeds must have exactly two bytes')
    packed = [tag, raw[1]]
    _validate_packed_seed_packet(packed)
    return packed


def _byteframe_raw_to_packed_reference(raw: bytes) -> list[Any]:
    if len(raw) < 2:
        raise PacketError('byteframe reference payload must have a tag byte plus at least one prefix byte')
    if raw[0] != PACKED_MODE_TAGS['reference']:
        raise PacketError(f'unsupported byteframe reference tag: {raw[0]}')
    return [PACKED_MODE_TAGS['reference'], _base64url_encode_bytes(raw[1:])]


def _even_unique_reference_prefix(
    fingerprint: str,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> str:
    required_len = minimal_unique_reference_prefix_hex_len(
        fingerprint,
        known_fingerprints,
        min_hex_len=min_hex_len,
    )
    prefix_len = required_len if required_len % 2 == 0 else required_len + 1
    hex_part = _normalize_fingerprint(fingerprint)
    if prefix_len > len(hex_part):
        raise PacketError(f'could not round fingerprint prefix length {required_len} to an even-length prefix')
    prefix = hex_part[:prefix_len]
    matches = [fp for fp in known_fingerprints if _normalize_fingerprint(fp).startswith(prefix)]
    if len(matches) != 1:
        raise PacketError(f'even-length fingerprint prefix {prefix} is ambiguous across {len(matches)} known semantic fingerprints')
    return prefix


def _validate_packed_seed_packet(packet: Any) -> None:
    if not _is_packed_seed_packet(packet):
        raise PacketError('expected a packed seed with a supported numeric mode tag in slot 0')
    tag = packet[0]
    if tag == PACKED_MODE_TAGS['oracle_coordinates']:
        if len(packet) != 3:
            raise PacketError('packed coordinate seed must have numeric tag plus B and H payloads')
        _expand_scalar_atom(packet[1])
        _expand_scalar_atom(packet[2])
        return
    if tag == PACKED_MODE_TAGS['oracle_weights']:
        if len(packet) < 2:
            raise PacketError('packed weight seed must have numeric tag plus a packed weight vector payload')
        expand_packed_weight_vector(packet[1:])
        return
    if tag == PACKED_MODE_TAGS['probe_robustness_fixed']:
        if len(packet) != 2 or not isinstance(packet[1], int):
            raise PacketError('packed fixed-robustness seed must carry an integer signature code')
        _decode_signature_code(packet[1], width=2)
        return
    if tag == PACKED_MODE_TAGS['probe_robustness_adaptive']:
        if len(packet) != 2 or packet[1] not in PACKED_ROUTE_FROM_CODE_ROBUSTNESS_ADAPTIVE:
            raise PacketError('packed adaptive seed must carry a supported adaptive route code')
        return
    if tag == PACKED_MODE_TAGS['probe_strict_adaptive']:
        if len(packet) != 2 or packet[1] not in PACKED_ROUTE_FROM_CODE_STRICT_ADAPTIVE:
            raise PacketError('packed strict-adaptive seed must carry a supported strict route code')
        return
    if tag == PACKED_MODE_TAGS['probe_exact_checked_cap_path']:
        if len(packet) != 2 or not isinstance(packet[1], int):
            raise PacketError('packed exact checked-cap seed must carry an integer signature code')
        _decode_signature_code(packet[1], width=3)
        return
    raise PacketError(f'unsupported packed seed tag: {tag}')


def _validate_packed_reference_packet(packet: Any) -> None:
    if not _is_packed_reference_packet(packet):
        raise PacketError('expected a packed reference with numeric reference tag in slot 0')
    if len(packet) != 2 or not isinstance(packet[1], str):
        raise PacketError('packed references must carry a single base64url payload string in slot 1')
    _prefix_base64url_to_hex(packet[1])


def packet_packed_seed(packet: Any, *, atomize_scalars: bool = True) -> list[Any]:
    expanded = expand_packet(packet)
    mode = expanded['mode']
    tag = PACKED_MODE_TAGS[mode]
    if mode == 'oracle_coordinates':
        return [tag, _pack_scalar_atom(expanded['evidence']['B']) if atomize_scalars else expanded['evidence']['B'], _pack_scalar_atom(expanded['evidence']['H']) if atomize_scalars else expanded['evidence']['H']]
    if mode == 'oracle_weights':
        return [tag, *pack_weight_vector_best(expanded['evidence']['weights'], atomize_scalars=atomize_scalars)]
    if mode == 'probe_robustness_fixed':
        return [tag, _encode_signature_code(expanded['evidence']['observed_signature'])]
    if mode == 'probe_robustness_adaptive':
        return [tag, PACKED_ROUTE_CODES_ROBUSTNESS_ADAPTIVE[expanded['evidence']['observed_route']]]
    if mode == 'probe_strict_adaptive':
        return [tag, PACKED_ROUTE_CODES_STRICT_ADAPTIVE[expanded['evidence']['observed_route']]]
    if mode == 'probe_exact_checked_cap_path':
        return [tag, _encode_signature_code(expanded['evidence']['observed_signature'])]
    raise PacketError(f'unsupported packet mode for packed-seed conversion: {mode}')


def expand_packed_seed_packet(packet: Any, *, archive_local: bool = False) -> dict[str, Any]:
    _validate_packed_seed_packet(packet)
    tag = packet[0]
    if tag == PACKED_MODE_TAGS['oracle_coordinates']:
        return packet_from_coordinates(_expand_scalar_atom(packet[1]), _expand_scalar_atom(packet[2]), archive_local=archive_local)
    if tag == PACKED_MODE_TAGS['oracle_weights']:
        return packet_from_weights(expand_packed_weight_vector(packet[1:]), archive_local=archive_local)
    if tag == PACKED_MODE_TAGS['probe_robustness_fixed']:
        signature = _decode_signature_code(packet[1], width=2)
        return packet_from_robustness_fixed(signature[0], signature[1], archive_local=archive_local)
    if tag == PACKED_MODE_TAGS['probe_robustness_adaptive']:
        route = PACKED_ROUTE_FROM_CODE_ROBUSTNESS_ADAPTIVE[packet[1]]
        first_cap, first_symbol, second_symbol = _parse_robustness_adaptive_route(route)
        return packet_from_robustness_adaptive(first_cap, first_symbol, second_symbol, archive_local=archive_local)
    if tag == PACKED_MODE_TAGS['probe_strict_adaptive']:
        route = PACKED_ROUTE_FROM_CODE_STRICT_ADAPTIVE[packet[1]]
        first_symbol, second_symbol = _parse_strict_adaptive_route(route)
        return packet_from_strict_adaptive(first_symbol, second_symbol, archive_local=archive_local)
    if tag == PACKED_MODE_TAGS['probe_exact_checked_cap_path']:
        signature = _decode_signature_code(packet[1], width=3)
        return packet_from_exact_checked_cap_path(signature[0], signature[1], signature[2], archive_local=archive_local)
    raise PacketError(f'unsupported packed seed tag: {tag}')


def packet_packed_reference(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> list[Any]:
    expanded = expand_packet(packet)
    fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if fingerprint not in known:
        raise PacketError('packed references are only valid for already-known semantic fingerprints')
    prefix_hex = _even_unique_reference_prefix(fingerprint, known, min_hex_len=min_hex_len)
    return [PACKED_MODE_TAGS['reference'], _prefix_hex_to_base64url(prefix_hex)]


def expand_packed_reference_packet(packet: Any) -> dict[str, Any]:
    _validate_packed_reference_packet(packet)
    return {
        'packet_kind': ARCHIVE_LOCAL_REFERENCE_KIND,
        'prefix': _prefix_base64url_to_hex(packet[1]),
    }


def packet_packed_reference_write_plan(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint not in known:
        raise PacketError('packed references are only valid for already-known semantic fingerprints')
    reference = packet_packed_reference(expanded, known, min_hex_len=min_hex_len)
    return {
        'recommended_write_kind': 'packed_reference',
        'semantic_fingerprint': semantic_fingerprint,
        'reference': reference,
        'why': 'the archive already has this semantic body, so the repeat can shrink below tagged microframes by packing the shortest even-length local prefix into a base64url payload behind a numeric tag',
    }


def _validate_byte_seed_packet(packet: Any) -> None:
    if not _is_byte_seed_packet(packet):
        raise PacketError('expected a byteframe seed encoded as a base64url string with a supported non-reference tag byte')
    _validate_packed_seed_packet(_byteframe_raw_to_packed_seed(_base64url_decode_bytes(packet)))


def _validate_byte_reference_packet(packet: Any) -> None:
    if not _is_byte_reference_packet(packet):
        raise PacketError('expected a byteframe reference encoded as a base64url string with the reference tag byte')
    _validate_packed_reference_packet(_byteframe_raw_to_packed_reference(_base64url_decode_bytes(packet)))


def packet_byte_seed(packet: Any, *, atomize_scalars: bool = True) -> str:
    packed = packet_packed_seed(packet, atomize_scalars=atomize_scalars)
    return _base64url_encode_bytes(_packed_seed_to_byteframe_raw(packed))


def expand_byte_seed_packet(packet: Any, *, archive_local: bool = False) -> dict[str, Any]:
    _validate_byte_seed_packet(packet)
    packed = _byteframe_raw_to_packed_seed(_base64url_decode_bytes(packet))
    return expand_packed_seed_packet(packed, archive_local=archive_local)


def packet_byte_reference(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> str:
    packed = packet_packed_reference(packet, known_fingerprints, min_hex_len=min_hex_len)
    raw_prefix = _base64url_decode_bytes(packed[1])
    return _base64url_encode_bytes(bytes([PACKED_MODE_TAGS['reference']]) + raw_prefix)


def expand_byte_reference_packet(packet: Any) -> dict[str, Any]:
    _validate_byte_reference_packet(packet)
    packed = _byteframe_raw_to_packed_reference(_base64url_decode_bytes(packet))
    return expand_packed_reference_packet(packed)


def packet_byte_reference_write_plan(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint not in known:
        raise PacketError('byteframe references are only valid for already-known semantic fingerprints')
    reference = packet_byte_reference(expanded, known, min_hex_len=min_hex_len)
    return {
        'recommended_write_kind': 'byte_reference',
        'semantic_fingerprint': semantic_fingerprint,
        'reference': reference,
        'why': 'the archive already has this semantic body, so the repeat can shrink below packed references by encoding the numeric tag and resolved local prefix bytes as one base64url byteframe string',
    }


def packet_catalog_reference_from_slot(slot: int) -> str:
    if not isinstance(slot, int) or slot < 0:
        raise PacketError(f'catalog-slot references require a non-negative integer slot, got {slot!r}')
    return _base64url_encode_bytes(bytes([CATALOG_REFERENCE_TAG]) + _encode_uvarint(slot))


def packet_catalog_reference(
    packet: Any,
    known_fingerprints: list[str] | tuple[str, ...],
) -> str:
    expanded = expand_packet(packet)
    fingerprint = packet_semantic_fingerprint(expanded)
    lookup = fingerprint_catalog_lookup(known_fingerprints)
    if fingerprint not in lookup:
        raise PacketError('catalog-slot references are only valid for already-known semantic fingerprints in the ordered archive catalog')
    return packet_catalog_reference_from_slot(lookup[fingerprint])


def packet_short_catalog_reference_from_slot(slot: int) -> str:
    if not isinstance(slot, int) or slot < 0:
        raise PacketError(f'short catalog-slot references require a non-negative integer slot, got {slot!r}')
    if slot > SHORT_CATALOG_REFERENCE_MAX_SLOT:
        raise PacketError(
            f'short catalog-slot references only support slots up to {SHORT_CATALOG_REFERENCE_MAX_SLOT}, got {slot}'
        )
    return _base64url_encode_bytes(bytes([SHORT_CATALOG_REFERENCE_PREFIX | (slot >> 8), slot & 0xFF]))


def packet_short_catalog_reference(
    packet: Any,
    known_fingerprints: list[str] | tuple[str, ...],
) -> str:
    expanded = expand_packet(packet)
    fingerprint = packet_semantic_fingerprint(expanded)
    lookup = fingerprint_catalog_lookup(known_fingerprints)
    if fingerprint not in lookup:
        raise PacketError('short catalog-slot references are only valid for already-known semantic fingerprints in the ordered archive catalog')
    return packet_short_catalog_reference_from_slot(lookup[fingerprint])


def packet_catalog_reference_write_plan(
    packet: Any,
    known_fingerprints: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    lookup = fingerprint_catalog_lookup(known_fingerprints)
    if semantic_fingerprint not in lookup:
        raise PacketError('catalog-slot references are only valid for already-known semantic fingerprints in the ordered archive catalog')
    reference = packet_catalog_reference(expanded, known_fingerprints)
    return {
        'recommended_write_kind': 'catalog_reference',
        'semantic_fingerprint': semantic_fingerprint,
        'catalog_slot': lookup[semantic_fingerprint],
        'reference': reference,
        'why': 'the archive already has this semantic body and preserves an append-only fingerprint catalog, so the repeat can shrink below prefix byteframes by storing the local catalog slot as a uvarint behind one tag byte',
    }


def packet_short_catalog_reference_write_plan(
    packet: Any,
    known_fingerprints: list[str] | tuple[str, ...],
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    lookup = fingerprint_catalog_lookup(known_fingerprints)
    if semantic_fingerprint not in lookup:
        raise PacketError('short catalog-slot references are only valid for already-known semantic fingerprints in the ordered archive catalog')
    slot = lookup[semantic_fingerprint]
    if slot > SHORT_CATALOG_REFERENCE_MAX_SLOT:
        raise PacketError(
            f'short catalog-slot references only support slots up to {SHORT_CATALOG_REFERENCE_MAX_SLOT}, got {slot}'
        )
    reference = packet_short_catalog_reference(expanded, known_fingerprints)
    return {
        'recommended_write_kind': 'short_catalog_reference',
        'semantic_fingerprint': semantic_fingerprint,
        'catalog_slot': slot,
        'reference': reference,
        'why': 'the archive already has this semantic body and preserves an append-only fingerprint catalog under 16384 entries, so the repeat can shrink below uvarint catalog references by packing the slot into one 14-bit short token',
    }



def packet_catalog_reference_write_plan_from_pages(
    packet: Any,
    pages: list[str] | tuple[str, ...],
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    slot = find_fingerprint_catalog_slot_from_pages(semantic_fingerprint, pages, page_size=page_size)
    if slot is None:
        raise PacketError('catalog-slot references are only valid for already-known semantic fingerprints in the paged archive catalog')
    reference = packet_catalog_reference_from_slot(slot)
    return {
        'recommended_write_kind': 'catalog_reference',
        'semantic_fingerprint': semantic_fingerprint,
        'catalog_slot': slot,
        'reference': reference,
        'why': 'the archive already has this semantic body and preserves append-only fingerprint pages, so the repeat can store the local catalog slot without rebuilding the full ordered sha256-string catalog first',
    }



def packet_short_catalog_reference_write_plan_from_pages(
    packet: Any,
    pages: list[str] | tuple[str, ...],
    *,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    slot = find_fingerprint_catalog_slot_from_pages(semantic_fingerprint, pages, page_size=page_size)
    if slot is None:
        raise PacketError('short catalog-slot references are only valid for already-known semantic fingerprints in the paged archive catalog')
    if slot > SHORT_CATALOG_REFERENCE_MAX_SLOT:
        raise PacketError(
            f'short catalog-slot references only support slots up to {SHORT_CATALOG_REFERENCE_MAX_SLOT}, got {slot}'
        )
    reference = packet_short_catalog_reference_from_slot(slot)
    return {
        'recommended_write_kind': 'short_catalog_reference',
        'semantic_fingerprint': semantic_fingerprint,
        'catalog_slot': slot,
        'reference': reference,
        'why': 'the archive already has this semantic body and preserves append-only fingerprint pages under 16384 entries, so the repeat can resolve the slot directly from compact page state and store one 14-bit short token',
    }



def _packet_archive_zepto_first_write_plan(
    expanded: dict[str, Any],
    *,
    need_human_readable_packet: bool = False,
) -> dict[str, Any] | None:
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    storage = packet_body_storage_compiled_frontier(
        expanded,
        need_human_readable_packet=need_human_readable_packet,
    )
    if storage['recommended_storage_form'] == 'byte_seed':
        return {
            'recommended_write_kind': 'byte_seed_body',
            'semantic_fingerprint': semantic_fingerprint,
            'body': packet_byte_seed(expanded),
            'why': storage['why'],
        }
    if storage['recommended_storage_form'] == 'packed_seed':
        return {
            'recommended_write_kind': 'packed_seed_body',
            'semantic_fingerprint': semantic_fingerprint,
            'body': packet_packed_seed(expanded),
            'why': storage['why'],
        }
    if storage['recommended_storage_form'] == 'archive_local':
        return {
            'recommended_write_kind': 'archive_local_body',
            'semantic_fingerprint': semantic_fingerprint,
            'body': _archive_localize_packet(expanded),
            'why': storage['why'],
        }
    return None


def _parse_robustness_adaptive_route(route: str) -> tuple[int, str, str | None]:
    if route == '10:M':
        return 10, 'M', None
    if route.startswith('10:S;20:') and len(route) == len('10:S;20:X'):
        return 10, 'S', route[-1]
    if route == '20:S':
        return 20, 'S', None
    if route.startswith('20:M;10:') and len(route) == len('20:M;10:X'):
        return 20, 'M', route[-1]
    raise PacketError(f'unsupported robustness-adaptive semantic-core route: {route}')


def _parse_strict_adaptive_route(route: str) -> tuple[str, str]:
    if route.startswith('10000:M;10:') and len(route) == len('10000:M;10:X'):
        return 'M', route[-1]
    if route.startswith('10000:S;20:') and len(route) == len('10000:S;20:X'):
        return 'S', route[-1]
    raise PacketError(f'unsupported strict-adaptive semantic-core route: {route}')


def expand_semantic_core_packet(packet: dict[str, Any], *, archive_local: bool = False) -> dict[str, Any]:
    _validate_semantic_core_packet(packet)
    mode = packet['mode']
    if mode == 'oracle_coordinates':
        return packet_from_coordinates(packet['B'], packet['H'], archive_local=archive_local)
    if mode == 'oracle_weights':
        return packet_from_weights(packet['weights'], archive_local=archive_local)
    if mode == 'probe_robustness_fixed':
        signature = packet['signature']
        if len(signature) != 2:
            raise PacketError(f'robustness-fixed semantic-core signature must have length 2, got {signature}')
        return packet_from_robustness_fixed(signature[0], signature[1], archive_local=archive_local)
    if mode == 'probe_robustness_adaptive':
        first_cap, first_symbol, second_symbol = _parse_robustness_adaptive_route(packet['route'])
        return packet_from_robustness_adaptive(first_cap, first_symbol, second_symbol, archive_local=archive_local)
    if mode == 'probe_strict_adaptive':
        first_symbol, second_symbol = _parse_strict_adaptive_route(packet['route'])
        return packet_from_strict_adaptive(first_symbol, second_symbol, archive_local=archive_local)
    if mode == 'probe_exact_checked_cap_path':
        signature = packet['signature']
        if len(signature) != 3:
            raise PacketError(f'exact checked-cap semantic-core signature must have length 3, got {signature}')
        return packet_from_exact_checked_cap_path(signature[0], signature[1], signature[2], archive_local=archive_local)
    raise PacketError(f'unsupported semantic-core mode: {mode}')


def packet_archive_compact_write_plan(
    packet: dict[str, Any],
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint in known:
        return {
            'recommended_write_kind': 'reference',
            'semantic_fingerprint': semantic_fingerprint,
            'reference': packet_reference(expanded),
            'why': 'the archive already has a body for this semantic decision, so storing only a fingerprint reference avoids duplicate bodies in every storage form',
        }
    storage = packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=need_human_readable_packet,
        archive_has_core_expander=True,
    )
    if storage['recommended_storage_form'] == 'semantic_core':
        return {
            'recommended_write_kind': 'semantic_core_body',
            'semantic_fingerprint': semantic_fingerprint,
            'body': packet_semantic_core(expanded),
            'why': 'this semantic decision is new, and the archive already contains the executable expander, so the smallest durable body is the semantic core',
        }
    return {
        'recommended_write_kind': 'archive_local_body',
        'semantic_fingerprint': semantic_fingerprint,
        'body': _archive_localize_packet(expanded),
        'why': 'this semantic decision is new, and a directly readable archive-local packet body was requested for in-archive use',
    }


def packet_archive_ultracompact_write_plan(
    packet: dict[str, Any],
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint in known:
        return packet_archive_local_reference_write_plan(
            expanded,
            known,
            min_hex_len=min_reference_prefix_hex_len,
        )
    return packet_archive_compact_write_plan(
        expanded,
        known,
        need_human_readable_packet=need_human_readable_packet,
    )


def packet_archive_nano_write_plan(
    packet: dict[str, Any],
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint in known:
        return packet_archive_local_reference_write_plan(
            expanded,
            known,
            min_hex_len=min_reference_prefix_hex_len,
        )
    storage = packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=need_human_readable_packet,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
    )
    if storage['recommended_storage_form'] == 'coded_seed':
        return {
            'recommended_write_kind': 'coded_seed_body',
            'semantic_fingerprint': semantic_fingerprint,
            'body': packet_coded_seed(expanded),
            'why': 'this semantic decision is new, and the archive already preserves the local seed codebook, so the smallest durable body is the coded seed rather than the larger self-describing semantic core',
        }
    return packet_archive_ultracompact_write_plan(
        expanded,
        known,
        need_human_readable_packet=need_human_readable_packet,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )


def packet_archive_pico_write_plan(
    packet: dict[str, Any],
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint in known:
        return packet_coded_reference_write_plan(
            expanded,
            known,
            min_hex_len=min_reference_prefix_hex_len,
        )
    return packet_archive_nano_write_plan(
        expanded,
        known,
        need_human_readable_packet=need_human_readable_packet,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )


def packet_micro_reference_write_plan(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    min_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint not in known:
        raise PacketError('micro references are only valid for already-known semantic fingerprints')
    reference = packet_micro_reference(expanded, known, min_hex_len=min_hex_len)
    return {
        'recommended_write_kind': 'micro_reference',
        'semantic_fingerprint': semantic_fingerprint,
        'reference': reference,
        'why': 'the archive already has this semantic body, so the repeat can shrink below the coded-reference wrapper by storing only a tagged microframe carrying the shortest unique local prefix',
    }


def packet_archive_femto_write_plan(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint in known:
        return packet_micro_reference_write_plan(
            expanded,
            known,
            min_hex_len=min_reference_prefix_hex_len,
        )
    storage = packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=need_human_readable_packet,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
        archive_has_seed_microframe_codec=True,
    )
    if storage['recommended_storage_form'] == 'micro_seed':
        return {
            'recommended_write_kind': 'micro_seed_body',
            'semantic_fingerprint': semantic_fingerprint,
            'body': packet_micro_seed(expanded),
            'why': 'this semantic decision is new, and the archive already preserves the executable expander, local seed codebook, and microframe codec, so the smallest durable body is the tagged microframe seed',
        }
    return packet_archive_pico_write_plan(
        expanded,
        known,
        need_human_readable_packet=need_human_readable_packet,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )


def packet_archive_atto_write_plan(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint in known:
        return packet_packed_reference_write_plan(
            expanded,
            known,
            min_hex_len=min_reference_prefix_hex_len,
        )
    storage = packet_body_storage_decision(
        need_standalone_portability=False,
        need_human_readable_packet=need_human_readable_packet,
        archive_has_core_expander=True,
        archive_has_seed_codebook=True,
        archive_has_seed_microframe_codec=True,
        archive_has_seed_packed_codec=True,
    )
    if storage['recommended_storage_form'] == 'packed_seed':
        return {
            'recommended_write_kind': 'packed_seed_body',
            'semantic_fingerprint': semantic_fingerprint,
            'body': packet_packed_seed(expanded),
            'why': 'this semantic decision is new, and the archive preserves the packed seed codec, microframe codec, seed codebook, and executable expander, so the smallest durable body is the packed seed',
        }
    return packet_archive_femto_write_plan(
        expanded,
        known,
        need_human_readable_packet=need_human_readable_packet,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )



def packet_archive_zepto_write_plan(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    known = set(known_fingerprints)
    if semantic_fingerprint in known:
        repeat_frontier = packet_repeat_storage_compiled_frontier(
            expanded,
            known,
            min_reference_prefix_hex_len=min_reference_prefix_hex_len,
        )
        if repeat_frontier['recommended_storage_form'] == 'byte_reference':
            return packet_byte_reference_write_plan(
                expanded,
                known,
                min_hex_len=min_reference_prefix_hex_len,
            )
        return packet_archive_atto_write_plan(
            expanded,
            known,
            need_human_readable_packet=need_human_readable_packet,
            min_reference_prefix_hex_len=min_reference_prefix_hex_len,
        )
    first_write = _packet_archive_zepto_first_write_plan(
        expanded,
        need_human_readable_packet=need_human_readable_packet,
    )
    if first_write is not None:
        return first_write
    return packet_archive_atto_write_plan(
        expanded,
        known,
        need_human_readable_packet=need_human_readable_packet,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )



def packet_archive_yocto_write_plan_from_pages(
    packet: Any,
    pages: list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    if not need_human_readable_packet:
        slot = find_fingerprint_catalog_slot_from_pages(semantic_fingerprint, pages, page_size=page_size)
        if slot is not None:
            if slot <= SHORT_CATALOG_REFERENCE_MAX_SLOT:
                return packet_short_catalog_reference_write_plan_from_pages(
                    expanded,
                    pages,
                    page_size=page_size,
                )
            return packet_catalog_reference_write_plan_from_pages(
                expanded,
                pages,
                page_size=page_size,
            )
    first_write = _packet_archive_zepto_first_write_plan(
        expanded,
        need_human_readable_packet=need_human_readable_packet,
    )
    if first_write is not None:
        return first_write
    return packet_archive_atto_write_plan(
        expanded,
        set(expand_fingerprint_catalog_pages(pages)),
        need_human_readable_packet=need_human_readable_packet,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )



def packet_archive_yocto_write_plan_from_pages_with_filters(
    packet: Any,
    pages: list[str] | tuple[str, ...],
    page_filters: list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    if not need_human_readable_packet:
        slot = find_fingerprint_catalog_slot_from_pages_with_filters(
            semantic_fingerprint,
            pages,
            page_filters,
            page_size=page_size,
        )
        if slot is not None:
            if slot <= SHORT_CATALOG_REFERENCE_MAX_SLOT:
                return {
                    'recommended_write_kind': 'short_catalog_reference',
                    'semantic_fingerprint': semantic_fingerprint,
                    'catalog_slot': slot,
                    'reference': packet_short_catalog_reference_from_slot(slot),
                    'why': 'the archive already has this semantic body and preserves append-only fingerprint pages plus aligned page filters, so the repeat can resolve straight to the compact local short-slot reference without rebuilding the ordered fingerprint catalog',
                }
            return {
                'recommended_write_kind': 'catalog_reference',
                'semantic_fingerprint': semantic_fingerprint,
                'catalog_slot': slot,
                'reference': packet_catalog_reference_from_slot(slot),
                'why': 'the archive already has this semantic body and preserves append-only fingerprint pages plus aligned page filters, so the repeat can resolve straight to the local catalog-slot reference without rebuilding the ordered fingerprint catalog',
            }
    first_write = _packet_archive_zepto_first_write_plan(
        expanded,
        need_human_readable_packet=need_human_readable_packet,
    )
    if first_write is not None:
        return first_write
    return packet_archive_atto_write_plan(
        expanded,
        set(expand_fingerprint_catalog_pages(pages)),
        need_human_readable_packet=need_human_readable_packet,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )



def packet_archive_yocto_write_plan_from_pages_with_route_blocks(
    packet: Any,
    pages: list[str] | tuple[str, ...],
    route_blocks: list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
    page_size: int = DEFAULT_FINGERPRINT_CATALOG_PAGE_SIZE,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    if not need_human_readable_packet:
        slot = find_fingerprint_catalog_slot_from_pages_with_route_blocks(
            semantic_fingerprint,
            pages,
            route_blocks,
            page_size=page_size,
        )
        if slot is not None:
            if slot <= SHORT_CATALOG_REFERENCE_MAX_SLOT:
                return {
                    'recommended_write_kind': 'short_catalog_reference',
                    'semantic_fingerprint': semantic_fingerprint,
                    'catalog_slot': slot,
                    'reference': packet_short_catalog_reference_from_slot(slot),
                    'why': 'the archive already has this semantic body and preserves append-only fingerprint pages plus digest-byte route blocks, so the repeat can jump straight to candidate compact pages and resolve to the local short-slot reference without scanning the page-filter list',
                }
            return {
                'recommended_write_kind': 'catalog_reference',
                'semantic_fingerprint': semantic_fingerprint,
                'catalog_slot': slot,
                'reference': packet_catalog_reference_from_slot(slot),
                'why': 'the archive already has this semantic body and preserves append-only fingerprint pages plus digest-byte route blocks, so the repeat can jump straight to candidate compact pages and resolve to the local catalog-slot reference without scanning the page-filter list',
            }
    first_write = _packet_archive_zepto_first_write_plan(
        expanded,
        need_human_readable_packet=need_human_readable_packet,
    )
    if first_write is not None:
        return first_write
    return packet_archive_atto_write_plan(
        expanded,
        set(expand_fingerprint_catalog_pages(pages)),
        need_human_readable_packet=need_human_readable_packet,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )



def packet_archive_yocto_write_plan(
    packet: Any,
    known_fingerprints: set[str] | list[str] | tuple[str, ...],
    *,
    need_human_readable_packet: bool = False,
    min_reference_prefix_hex_len: int = MIN_REFERENCE_PREFIX_HEX_LEN,
) -> dict[str, Any]:
    expanded = expand_packet(packet)
    semantic_fingerprint = packet_semantic_fingerprint(expanded)
    if (
        not need_human_readable_packet
        and _has_stable_fingerprint_catalog(known_fingerprints)
        and semantic_fingerprint in set(known_fingerprints)
    ):
        slot = fingerprint_catalog_lookup(known_fingerprints)[semantic_fingerprint]
        if slot <= SHORT_CATALOG_REFERENCE_MAX_SLOT:
            return packet_short_catalog_reference_write_plan(expanded, known_fingerprints)
        return packet_catalog_reference_write_plan(expanded, known_fingerprints)
    return packet_archive_zepto_write_plan(
        expanded,
        known_fingerprints,
        need_human_readable_packet=need_human_readable_packet,
        min_reference_prefix_hex_len=min_reference_prefix_hex_len,
    )


def recommend_minimal_packet_mode(
    *,
    question_scope: str,
    available_interface: str,
    need_portable_nonprocedural_record: bool = False,
) -> dict[str, Any]:
    available = available_interface.strip().lower()
    question = question_scope.strip().lower()
    if available == 'projective_coordinates':
        return {
            'recommended_mode': 'oracle_coordinates',
            'why': 'direct (B,H) coordinates answer every supported question with zero probes',
        }
    if available == 'weights':
        return {
            'recommended_mode': 'oracle_weights',
            'why': 'declared weights answer every supported question with zero probes',
        }
    if available != 'black_box':
        raise PacketError(f'unsupported available_interface: {available_interface}')

    if question == 'robustness_only':
        if need_portable_nonprocedural_record:
            return {
                'recommended_mode': 'probe_robustness_fixed',
                'why': 'portable nonprocedural storage should record the exact [10,20] signature for universal robustness triage',
            }
        return {
            'recommended_mode': 'probe_robustness_adaptive',
            'why': 'robustness-only black-box diagnosis can stop after one probe in the robust cases and otherwise needs only one follow-up probe',
        }
    if question == 'strict_class_only':
        return {
            'recommended_mode': 'probe_strict_adaptive',
            'why': 'strict class separation needs only the adaptive 10000 -> (10 after M, 20 after S) tree when ties do not need to be recorded',
        }
    if question in {'full_checked_cap_classification', 'exact_tie_cap'}:
        return {
            'recommended_mode': 'probe_exact_checked_cap_path',
            'why': 'exact checked-cap paths and tie-cap identification require the full fixed signature on [10,20,10000]',
        }
    raise PacketError(f'unsupported question_scope: {question_scope}')


def packet_from_coordinates(B: str, H: str, *, archive_local: bool = False) -> dict[str, Any]:
    oracle = _load_oracle_module()
    result = oracle.classify_from_direct_coordinates(B, H)
    return _packet(
        mode='oracle_coordinates',
        question_scope='full_checked_cap_classification',
        evidence={'B': str(B), 'H': str(H)},
        result={
            'closure_label': result['closure_label'],
            'strict_path_class': result['strict_path_class'],
            'robustness_class': result['robustness_class'],
            'checked_cap_signature': _checked_cap_signature(result['checked_cap_outcomes']),
            'recommended_black_box_probe_contract': result['recommended_black_box_probe_contract'],
        },
        archive_local=archive_local,
    )


def packet_from_weights(weights: dict[str, str], *, archive_local: bool = False) -> dict[str, Any]:
    oracle = _load_oracle_module()
    result = oracle.classify_from_weights(weights)
    return _packet(
        mode='oracle_weights',
        question_scope='full_checked_cap_classification',
        evidence={
            'weights': result['declared_weights'],
            'derived_B': result['baseline_nonhazard_surplus'],
            'derived_H': result['w_hazard'],
        },
        result={
            'closure_label': result['closure_label'],
            'strict_path_class': result['strict_path_class'],
            'robustness_class': result['robustness_class'],
            'checked_cap_signature': _checked_cap_signature(result['checked_cap_outcomes']),
            'recommended_black_box_probe_contract': result['recommended_black_box_probe_contract'],
        },
        archive_local=archive_local,
    )


def packet_from_robustness_fixed(cap10_symbol: str, cap20_symbol: str, *, archive_local: bool = False) -> dict[str, Any]:
    signature = _normalize_symbol(cap10_symbol) + _normalize_symbol(cap20_symbol)
    mapping = {
        'MM': 'material_robust_all_checked_caps',
        'SM': 'cap_sensitive_across_checked_caps',
        'SS': 'stability_robust_all_checked_caps',
    }
    if signature not in mapping:
        raise PacketError('robustness fixed packet supports only strict winner symbols M/S on caps [10,20]')
    return _packet(
        mode='probe_robustness_fixed',
        question_scope='robustness_only',
        evidence={
            'observed_signature': signature,
        },
        result={
            'robustness_class': mapping[signature],
        },
        archive_local=archive_local,
    )


def packet_from_robustness_adaptive(
    first_probe_cap: int,
    first_symbol: str,
    second_symbol: str | None = None,
    *,
    archive_local: bool = False,
) -> dict[str, Any]:
    cap = int(first_probe_cap)
    first = _normalize_symbol(first_symbol)
    if cap == 10:
        if first == 'M':
            if second_symbol is not None:
                raise PacketError('second_symbol must be omitted after early-stop M at cap 10')
            route = '10:M'
            robustness = 'material_robust_all_checked_caps'
        elif first == 'S':
            if second_symbol is None:
                raise PacketError('second_symbol required after S at cap 10')
            second = _normalize_symbol(second_symbol)
            if second not in {'M', 'S'}:
                raise PacketError('second_symbol must be M or S for robustness adaptive packets')
            route = f'10:S;20:{second}'
            robustness = 'cap_sensitive_across_checked_caps' if second == 'M' else 'stability_robust_all_checked_caps'
        else:
            raise PacketError('first_symbol must be M or S for robustness adaptive packets')
    elif cap == 20:
        if first == 'S':
            if second_symbol is not None:
                raise PacketError('second_symbol must be omitted after early-stop S at cap 20')
            route = '20:S'
            robustness = 'stability_robust_all_checked_caps'
        elif first == 'M':
            if second_symbol is None:
                raise PacketError('second_symbol required after M at cap 20')
            second = _normalize_symbol(second_symbol)
            if second not in {'M', 'S'}:
                raise PacketError('second_symbol must be M or S for robustness adaptive packets')
            route = f'20:M;10:{second}'
            robustness = 'material_robust_all_checked_caps' if second == 'M' else 'cap_sensitive_across_checked_caps'
        else:
            raise PacketError('first_symbol must be M or S for robustness adaptive packets')
    else:
        raise PacketError('robustness adaptive packet requires first_probe_cap 10 or 20')
    return _packet(
        mode='probe_robustness_adaptive',
        question_scope='robustness_only',
        evidence={'observed_route': route},
        result={'robustness_class': robustness},
        archive_local=archive_local,
    )


def packet_from_strict_adaptive(cap10000_symbol: str, second_symbol: str, *, archive_local: bool = False) -> dict[str, Any]:
    first = _normalize_symbol(cap10000_symbol)
    second = _normalize_symbol(second_symbol)
    if first == 'M':
        if second not in {'M', 'S'}:
            raise PacketError('second_symbol must be M or S after M at cap 10000')
        route = f'10000:M;10:{second}'
        closure = 'MMM' if second == 'M' else 'SMM'
        signature = 'MMM' if second == 'M' else 'SMM'
    elif first == 'S':
        if second not in {'M', 'S'}:
            raise PacketError('second_symbol must be M or S after S at cap 10000')
        route = f'10000:S;20:{second}'
        closure = 'SMS' if second == 'M' else 'SSS'
        signature = 'SMS' if second == 'M' else 'SSS'
    else:
        raise PacketError('strict adaptive packet supports only strict winner symbols at cap 10000')
    robustness = 'cap_sensitive_across_checked_caps' if closure in {'SMM', 'SMS'} else (
        'material_robust_all_checked_caps' if closure == 'MMM' else 'stability_robust_all_checked_caps'
    )
    return _packet(
        mode='probe_strict_adaptive',
        question_scope='strict_class_only',
        evidence={'observed_route': route},
        result={
            'closure_label': closure,
            'strict_path_class': closure,
            'robustness_class': robustness,
            'checked_cap_signature': signature,
        },
        archive_local=archive_local,
    )


def packet_from_exact_checked_cap_path(
    cap10_symbol: str,
    cap20_symbol: str,
    cap10000_symbol: str,
    *,
    archive_local: bool = False,
) -> dict[str, Any]:
    signature = ''.join([
        _normalize_symbol(cap10_symbol),
        _normalize_symbol(cap20_symbol),
        _normalize_symbol(cap10000_symbol),
    ])
    mapping = {
        'MMM': ('MMM', 'MMM', 'material_robust_all_checked_caps'),
        'SMM': ('SMM', 'SMM', 'cap_sensitive_across_checked_caps'),
        'SMS': ('SMS', 'SMS', 'cap_sensitive_across_checked_caps'),
        'SSS': ('SSS', 'SSS', 'stability_robust_all_checked_caps'),
        'TMM': ('TIE_tau10', None, 'boundary_tie_at_cap_10'),
        'SMT': ('TIE_tau10000', None, 'boundary_tie_at_cap_10000'),
        'STS': ('TIE_tau20', None, 'boundary_tie_at_cap_20'),
        'TTT': ('TIE_origin', None, 'exact_tie_all_checked_caps'),
    }
    if signature not in mapping:
        raise PacketError(f'unsupported exact checked-cap signature: {signature}')
    closure, strict_path, robustness = mapping[signature]
    return _packet(
        mode='probe_exact_checked_cap_path',
        question_scope='full_checked_cap_classification',
        evidence={
            'observed_signature': signature,
        },
        result={
            'closure_label': closure,
            'strict_path_class': strict_path,
            'robustness_class': robustness,
            'checked_cap_signature': signature,
        },
        archive_local=archive_local,
    )


def _print_packet(packet: dict[str, Any]) -> None:
    print(json.dumps(packet, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Build compact rematch-proxy decision packets.')
    subparsers = parser.add_subparsers(dest='cmd', required=True)

    route = subparsers.add_parser('route')
    route.add_argument('--question-scope', required=True, choices=['robustness_only', 'strict_class_only', 'full_checked_cap_classification', 'exact_tie_cap'])
    route.add_argument('--available-interface', required=True, choices=['projective_coordinates', 'weights', 'black_box'])
    route.add_argument('--portable-record', action='store_true')

    storage = subparsers.add_parser('storage')
    storage.add_argument('--portable', action='store_true')

    body_storage = subparsers.add_parser('body-storage')
    body_storage.add_argument('--portable', action='store_true')
    body_storage.add_argument('--human-readable-packet', action='store_true')
    body_storage.add_argument('--no-core-expander', action='store_true')
    body_storage.add_argument('--seed-codebook', action='store_true')

    repeat_storage = subparsers.add_parser('repeat-storage')
    repeat_storage.add_argument('--portable', action='store_true')
    repeat_storage.add_argument('--reference-codebook', action='store_true')

    profiles = subparsers.add_parser('profiles')

    direct = subparsers.add_parser('coordinates')
    direct.add_argument('--B', required=True)
    direct.add_argument('--H', required=True)
    direct.add_argument('--archive-local', action='store_true')

    weights = subparsers.add_parser('weights')
    for arg in ['w-width', 'w-buffer', 'w-knife', 'w-delta', 'w-material', 'w-undecided', 'w-ties', 'w-hazard']:
        weights.add_argument(f'--{arg}', required=True)
    weights.add_argument('--archive-local', action='store_true')

    robust_fixed = subparsers.add_parser('robustness-fixed')
    robust_fixed.add_argument('--cap10', required=True)
    robust_fixed.add_argument('--cap20', required=True)
    robust_fixed.add_argument('--archive-local', action='store_true')

    robust_adaptive = subparsers.add_parser('robustness-adaptive')
    robust_adaptive.add_argument('--first-cap', required=True, type=int, choices=[10, 20])
    robust_adaptive.add_argument('--first-symbol', required=True)
    robust_adaptive.add_argument('--second-symbol')
    robust_adaptive.add_argument('--archive-local', action='store_true')

    strict_adaptive = subparsers.add_parser('strict-adaptive')
    strict_adaptive.add_argument('--cap10000', required=True)
    strict_adaptive.add_argument('--second-symbol', required=True)
    strict_adaptive.add_argument('--archive-local', action='store_true')

    exact = subparsers.add_parser('exact-path')
    exact.add_argument('--cap10', required=True)
    exact.add_argument('--cap20', required=True)
    exact.add_argument('--cap10000', required=True)
    exact.add_argument('--archive-local', action='store_true')

    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.cmd == 'route':
        payload = recommend_minimal_packet_mode(
            question_scope=args.question_scope,
            available_interface=args.available_interface,
            need_portable_nonprocedural_record=args.portable_record,
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if args.cmd == 'storage':
        print(json.dumps(packet_storage_decision(need_standalone_portability=args.portable), indent=2, sort_keys=True))
        return
    if args.cmd == 'body-storage':
        print(json.dumps(packet_body_storage_decision(
            need_standalone_portability=args.portable,
            need_human_readable_packet=args.human_readable_packet,
            archive_has_core_expander=not args.no_core_expander,
            archive_has_seed_codebook=args.seed_codebook,
        ), indent=2, sort_keys=True))
        return
    if args.cmd == 'repeat-storage':
        print(json.dumps(packet_repeat_storage_decision(
            need_standalone_portability=args.portable,
            archive_has_reference_codebook=args.reference_codebook,
        ), indent=2, sort_keys=True))
        return
    if args.cmd == 'profiles':
        print(json.dumps(archive_local_profile_registry(), indent=2, sort_keys=True))
        return
    if args.cmd == 'coordinates':
        _print_packet(packet_from_coordinates(args.B, args.H, archive_local=args.archive_local))
        return
    if args.cmd == 'weights':
        _print_packet(packet_from_weights({
            'w_width': args.w_width,
            'w_buffer': args.w_buffer,
            'w_knife': args.w_knife,
            'w_delta': args.w_delta,
            'w_material': args.w_material,
            'w_undecided': args.w_undecided,
            'w_ties': args.w_ties,
            'w_hazard': args.w_hazard,
        }, archive_local=args.archive_local))
        return
    if args.cmd == 'robustness-fixed':
        _print_packet(packet_from_robustness_fixed(args.cap10, args.cap20, archive_local=args.archive_local))
        return
    if args.cmd == 'robustness-adaptive':
        _print_packet(packet_from_robustness_adaptive(args.first_cap, args.first_symbol, args.second_symbol, archive_local=args.archive_local))
        return
    if args.cmd == 'strict-adaptive':
        _print_packet(packet_from_strict_adaptive(args.cap10000, args.second_symbol, archive_local=args.archive_local))
        return
    if args.cmd == 'exact-path':
        _print_packet(packet_from_exact_checked_cap_path(args.cap10, args.cap20, args.cap10000, archive_local=args.archive_local))
        return
    raise SystemExit(f'unhandled command: {args.cmd}')


if __name__ == '__main__':
    main()
