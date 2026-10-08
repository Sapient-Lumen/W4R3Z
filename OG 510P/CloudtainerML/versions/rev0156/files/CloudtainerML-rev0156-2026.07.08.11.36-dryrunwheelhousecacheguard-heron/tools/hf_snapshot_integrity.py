#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIGEST_RECEIPT_CONTRACT = 'stat_bound_model_safetensors_sha256_receipt_v1'
DIGEST_RECEIPT_CACHE_DIR = ROOT / 'artifacts' / 'runtime' / 'snapshot-digest-cache'

DEFAULT_MODEL_ID = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
DEFAULT_REVISION = 'fe8a4ea1ffedaf415f4da2f062534de366a451e6'
EXPECTED_MODEL_SAFETENSORS_SHA256 = '6e6001da2106d4757498752a021df6c2bdc332c650aae4bae6b0c004dcf14933'
EXPECTED_MODEL_SAFETENSORS_XET_HASH = '78613135f161e5f517e18a405e22facb700d9737e3936330effa276e7bfc1c2a'
REQUIRED_SNAPSHOT_FILES = [
    'config.json',
    'generation_config.json',
    'model.safetensors',
    'special_tokens_map.json',
    'tokenizer.json',
    'tokenizer.model',
    'tokenizer_config.json',
]
ALLOW_PATTERNS = REQUIRED_SNAPSHOT_FILES + ['README.md']
PUBLISHED_SIZE_BYTES = {
    # Locked TinyLlama tree at fe8a4ea1ffedaf415f4da2f062534de366a451e6.
    # These are source-observed hints, not a substitute for content/hash checks.
    'config.json': 608,
    'generation_config.json': 124,
    'model.safetensors': 2_200_000_000,
    'special_tokens_map.json': 551,
    'tokenizer.json': 1_840_000,
    'tokenizer.model': 500_000,
    'tokenizer_config.json': 1_290,
}
MIN_BYTES = {
    'config.json': 500,
    'generation_config.json': 20,
    'model.safetensors': 2_000_000_000,
    'special_tokens_map.json': 20,
    'tokenizer.json': 100_000,
    'tokenizer.model': 100_000,
    'tokenizer_config.json': 100,
}
EXPECTED_CONFIG_FIELDS = {
    'model_type': 'llama',
    'hidden_size': 2048,
    'intermediate_size': 5632,
    'num_attention_heads': 32,
    'num_key_value_heads': 4,
    'num_hidden_layers': 22,
    'max_position_embeddings': 2048,
}
REQUIRED_TENSOR_NAMES = [
    'model.embed_tokens.weight',
    'model.layers.0.self_attn.q_proj.weight',
    'model.layers.0.self_attn.k_proj.weight',
    'model.layers.0.self_attn.v_proj.weight',
    'model.layers.0.self_attn.o_proj.weight',
    'model.norm.weight',
    'lm_head.weight',
]


def cache_roots(cache_dir: str | None = None) -> list[Path]:
    roots: list[Path] = []
    if cache_dir:
        roots.append(Path(cache_dir).expanduser())
    if os.environ.get('HF_HUB_CACHE'):
        roots.append(Path(os.environ['HF_HUB_CACHE']).expanduser())
    if os.environ.get('HF_HOME'):
        roots.append(Path(os.environ['HF_HOME']).expanduser() / 'hub')
    if os.environ.get('XDG_CACHE_HOME') and not os.environ.get('HF_HOME'):
        roots.append(Path(os.environ['XDG_CACHE_HOME']).expanduser() / 'huggingface' / 'hub')
    roots.append(Path.home() / '.cache' / 'huggingface' / 'hub')
    out: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key not in seen:
            seen.add(key)
            out.append(root)
    return out


def snapshot_path(cache_root: Path, model_id: str, revision: str) -> Path:
    return cache_root / ('models--' + model_id.replace('/', '--')) / 'snapshots' / revision


def snapshot_candidate_paths(model_id: str = DEFAULT_MODEL_ID, revision: str = DEFAULT_REVISION, *, cache_dir: str | None = None) -> list[Path]:
    paths: list[Path] = []
    if os.environ.get('LOCAL_SNAPSHOT_DIR'):
        paths.append(Path(os.environ['LOCAL_SNAPSHOT_DIR']).expanduser())
    if os.environ.get('HF_SNAPSHOT_DIR'):
        paths.append(Path(os.environ['HF_SNAPSHOT_DIR']).expanduser())
    for root in cache_roots(cache_dir):
        paths.append(snapshot_path(root, model_id, revision))
    out: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            out.append(path)
    return out


def _parse_json_file(path: Path) -> dict[str, Any]:
    try:
        return {'ok': True, 'data': json.loads(path.read_text(encoding='utf-8'))}
    except Exception as exc:
        return {'ok': False, 'error': type(exc).__name__ + ': ' + repr(exc)}



def _file_identity(path: Path) -> dict[str, Any]:
    st = path.stat()
    resolved = path.resolve()
    return {
        'path': str(path),
        'resolved_path': str(resolved),
        'size': int(st.st_size),
        'mtime_ns': int(getattr(st, 'st_mtime_ns', int(st.st_mtime * 1_000_000_000))),
        'ctime_ns': int(getattr(st, 'st_ctime_ns', int(st.st_ctime * 1_000_000_000))),
        'device': int(getattr(st, 'st_dev', 0)),
        'inode': int(getattr(st, 'st_ino', 0)),
        'mode': int(getattr(st, 'st_mode', 0)),
    }


def _identity_matches(a: dict[str, Any], b: dict[str, Any]) -> bool:
    for key in ['resolved_path', 'size', 'mtime_ns', 'ctime_ns', 'device', 'inode']:
        if a.get(key) != b.get(key):
            return False
    return True


def _digest_receipt_path(identity: dict[str, Any]) -> Path:
    key_src = json.dumps({k: identity.get(k) for k in ['resolved_path', 'size', 'mtime_ns', 'ctime_ns', 'device', 'inode']}, sort_keys=True, separators=(',', ':'))
    key = hashlib.sha256(key_src.encode('utf-8')).hexdigest()
    return DIGEST_RECEIPT_CACHE_DIR / key[:2] / (key + '.json')


def sha256_file_with_receipt(path: Path, *, expected_sha256: str | None = None, purpose: str = 'model_safetensors_snapshot_integrity') -> dict[str, Any]:
    """Hash a file, reusing only a stat-bound receipt from a prior full hash.

    The first successful call still reads the entire file and writes a receipt.
    Later gates may reuse that receipt only when path identity, resolved path,
    size, mtime, ctime, device, and inode are unchanged and the cached digest
    still matches the expected digest when one is provided.
    """
    identity = _file_identity(path)
    receipt_path = _digest_receipt_path(identity)
    disable_cache = os.environ.get('PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE') == '1'
    cache_error = None
    if not disable_cache and receipt_path.exists():
        try:
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            receipt_identity = receipt.get('file_identity') if isinstance(receipt, dict) else None
            sha = str(receipt.get('sha256') or '') if isinstance(receipt, dict) else ''
            if (
                isinstance(receipt_identity, dict)
                and receipt.get('contract') == DIGEST_RECEIPT_CONTRACT
                and _identity_matches(identity, receipt_identity)
                and sha
                and (expected_sha256 is None or sha == expected_sha256)
            ):
                return {
                    'sha256': sha,
                    'sha256_source': 'stat_bound_digest_receipt_cache',
                    'digest_receipt_contract': DIGEST_RECEIPT_CONTRACT,
                    'digest_receipt_path': str(receipt_path),
                    'digest_receipt_reused': True,
                    'digest_receipt_written': False,
                    'file_identity': identity,
                }
        except Exception as exc:
            cache_error = type(exc).__name__ + ': ' + repr(exc)
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    sha = h.hexdigest()
    receipt_written = False
    receipt_write_error = None
    if not disable_cache:
        try:
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = receipt_path.with_suffix('.tmp')
            receipt = {
                'contract': DIGEST_RECEIPT_CONTRACT,
                'sha256': sha,
                'expected_sha256': expected_sha256,
                'sha256_matches_expected': (sha == expected_sha256) if expected_sha256 else None,
                'purpose': purpose,
                'file_identity': identity,
                'cache_safety_boundary': 'Reuse allowed only while stat identity is unchanged; set PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE=1 to force full rehash.',
            }
            tmp.write_text(json.dumps(receipt, indent=2, sort_keys=False) + '\n', encoding='utf-8')
            tmp.replace(receipt_path)
            receipt_written = True
        except Exception as exc:
            receipt_write_error = type(exc).__name__ + ': ' + repr(exc)
    return {
        'sha256': sha,
        'sha256_source': 'computed_full_file',
        'digest_receipt_contract': DIGEST_RECEIPT_CONTRACT,
        'digest_receipt_path': str(receipt_path),
        'digest_receipt_reused': False,
        'digest_receipt_written': receipt_written,
        'digest_receipt_cache_error': cache_error,
        'digest_receipt_write_error': receipt_write_error,
        'file_identity': identity,
    }


def _sha256_file(path: Path) -> str:
    return sha256_file_with_receipt(path).get('sha256', '')


def _allocated_bytes(path: Path) -> int | None:
    try:
        st = path.stat()
        blocks = getattr(st, 'st_blocks', None)
        if blocks is None:
            return None
        return int(blocks) * 512
    except Exception:
        return None


def _inspect_safetensors(path: Path) -> dict[str, Any]:
    rec: dict[str, Any] = {
        'present': path.exists(),
        'path': str(path),
        'header_ok': False,
        'tensor_count': 0,
        'required_tensor_names_present': [],
        'required_tensor_names_missing': REQUIRED_TENSOR_NAMES[:],
        'blockers': [],
        'warnings': [],
    }
    if not path.exists() or not path.is_file():
        rec['blockers'].append('model_safetensors_missing')
        return rec
    size = int(path.stat().st_size)
    rec['bytes'] = size
    allocated = _allocated_bytes(path)
    rec['allocated_bytes'] = allocated
    if size < MIN_BYTES['model.safetensors']:
        rec['blockers'].append('model_safetensors_smaller_than_expected_remote_file')
    if allocated is not None and size >= MIN_BYTES['model.safetensors'] and allocated < int(size * 0.80):
        rec['blockers'].append('model_safetensors_sparse_or_not_fully_materialized')
    if size < 8:
        rec['blockers'].append('model_safetensors_too_small_for_header')
        return rec
    try:
        with path.open('rb') as f:
            header_len = struct.unpack('<Q', f.read(8))[0]
            rec['header_len'] = int(header_len)
            if header_len <= 0:
                rec['blockers'].append('model_safetensors_header_length_zero')
                return rec
            if header_len > 100_000_000:
                rec['blockers'].append('model_safetensors_header_larger_than_100mb')
                return rec
            if 8 + header_len > size:
                rec['blockers'].append('model_safetensors_header_extends_past_file')
                return rec
            header_bytes = f.read(header_len)
        if not header_bytes.startswith(b'{'):
            rec['blockers'].append('model_safetensors_header_does_not_start_with_json_object')
            return rec
        header = json.loads(header_bytes.rstrip(b' ').decode('utf-8'))
        tensor_names = sorted(k for k in header.keys() if k != '__metadata__')
        rec['header_ok'] = True
        rec['tensor_count'] = len(tensor_names)
        rec['metadata'] = header.get('__metadata__', {}) if isinstance(header.get('__metadata__', {}), dict) else {}
        present = [name for name in REQUIRED_TENSOR_NAMES if name in header]
        missing = [name for name in REQUIRED_TENSOR_NAMES if name not in header]
        rec['required_tensor_names_present'] = present
        rec['required_tensor_names_missing'] = missing
        if len(tensor_names) < 150:
            rec['blockers'].append('model_safetensors_tensor_count_too_small_for_tinyllama')
        if missing:
            rec['blockers'].append('model_safetensors_missing_required_llama_tensor_names')
        max_end = 0
        malformed = []
        for name in tensor_names:
            item = header.get(name)
            if not isinstance(item, dict):
                malformed.append(name); continue
            offs = item.get('data_offsets')
            if not (isinstance(offs, list) and len(offs) == 2 and all(isinstance(x, int) for x in offs) and offs[0] <= offs[1]):
                malformed.append(name); continue
            max_end = max(max_end, int(offs[1]))
        rec['max_tensor_data_offset'] = max_end
        rec['data_buffer_bytes'] = max(0, size - 8 - int(rec.get('header_len') or 0))
        if malformed:
            rec['blockers'].append('model_safetensors_malformed_tensor_records')
            rec['malformed_tensor_records_sample'] = malformed[:10]
        if max_end > rec['data_buffer_bytes']:
            rec['blockers'].append('model_safetensors_offsets_exceed_file_data_buffer')
        elif max_end < int(rec['data_buffer_bytes'] * 0.95):
            rec['warnings'].append('model_safetensors_offsets_do_not_cover_most_data_buffer')
    except Exception as exc:
        rec['blockers'].append('model_safetensors_header_parse_failed')
        rec['parse_error'] = type(exc).__name__ + ': ' + repr(exc)
    return rec


def inspect_snapshot(path: Path, *, model_id: str = DEFAULT_MODEL_ID, revision: str = DEFAULT_REVISION, include_hashes: bool = False) -> dict[str, Any]:
    path = path.expanduser()
    blockers: list[str] = []
    warnings: list[str] = []
    record: dict[str, Any] = {
        'path': str(path),
        'exists': bool(path.exists()),
        'is_dir': bool(path.is_dir()) if path.exists() else False,
        'file_count': 0,
        'present_required_files': [],
        'missing_required_files': REQUIRED_SNAPSHOT_FILES[:],
        'required_file_records': {},
        'complete_required_snapshot': False,
        'integrity_checked_without_transformers': True,
        'model_id': model_id,
        'model_revision': revision,
        'blockers': blockers,
        'warnings': warnings,
    }
    if not path.exists():
        blockers.append('snapshot_dir_missing')
        return record
    if not path.is_dir():
        blockers.append('snapshot_path_not_directory')
        return record
    files = sorted(p for p in path.iterdir() if p.is_file())
    names = {p.name for p in files}
    record['file_count'] = len(files)
    record['bytes_total_top_level_files'] = int(sum(p.stat().st_size for p in files))
    present = [name for name in REQUIRED_SNAPSHOT_FILES if name in names]
    missing = [name for name in REQUIRED_SNAPSHOT_FILES if name not in names]
    record['present_required_files'] = present
    record['missing_required_files'] = missing
    if missing:
        blockers.append('snapshot_missing_required_files')
    for name in present:
        p = path / name
        size = int(p.stat().st_size)
        allocated = _allocated_bytes(p)
        frec: dict[str, Any] = {'bytes': size, 'allocated_bytes': allocated, 'min_bytes': MIN_BYTES.get(name, 1), 'published_size_hint_bytes': PUBLISHED_SIZE_BYTES.get(name), 'size_ok': size >= MIN_BYTES.get(name, 1)}
        if not frec['size_ok']:
            blockers.append(f'snapshot_file_too_small:{name}')
        pub = PUBLISHED_SIZE_BYTES.get(name)
        if pub is not None and MIN_BYTES.get(name, 1) > pub:
            blockers.append(f'snapshot_min_bytes_exceeds_published_size:{name}')
        record['required_file_records'][name] = frec
    for name in ['config.json', 'generation_config.json', 'special_tokens_map.json', 'tokenizer_config.json']:
        if name in names:
            parsed = _parse_json_file(path / name)
            record['required_file_records'].setdefault(name, {})['json_parse_ok'] = parsed.get('ok')
            if not parsed.get('ok'):
                blockers.append(f'snapshot_json_unparseable:{name}')
            elif name == 'config.json':
                data = parsed.get('data') or {}
                selected = {k: data.get(k) for k in sorted(EXPECTED_CONFIG_FIELDS)}
                record['config_selected_fields'] = selected
                for key, expected in EXPECTED_CONFIG_FIELDS.items():
                    if data.get(key) != expected:
                        blockers.append(f'snapshot_config_unexpected_{key}')
                arch = data.get('architectures')
                record['config_architectures'] = arch
                if not (isinstance(arch, list) and 'LlamaForCausalLM' in arch):
                    blockers.append('snapshot_config_architecture_not_llama_for_causal_lm')
    safe = _inspect_safetensors(path / 'model.safetensors')
    record['model_safetensors'] = safe
    record['model_safetensors_hash_requested'] = bool(include_hashes)
    if include_hashes and (path / 'model.safetensors').exists() and (path / 'model.safetensors').is_file():
        digest_record = sha256_file_with_receipt(path / 'model.safetensors', expected_sha256=EXPECTED_MODEL_SAFETENSORS_SHA256)
        sha = str(digest_record.get('sha256') or '')
        safe['sha256'] = sha
        safe['sha256_matches_expected'] = sha == EXPECTED_MODEL_SAFETENSORS_SHA256
        safe['sha256_source'] = digest_record.get('sha256_source')
        safe['digest_receipt_contract'] = digest_record.get('digest_receipt_contract')
        safe['digest_receipt_path'] = digest_record.get('digest_receipt_path')
        safe['digest_receipt_reused'] = digest_record.get('digest_receipt_reused')
        safe['digest_receipt_written'] = digest_record.get('digest_receipt_written')
        safe['digest_receipt_cache_error'] = digest_record.get('digest_receipt_cache_error')
        safe['digest_receipt_write_error'] = digest_record.get('digest_receipt_write_error')
        safe['file_identity'] = digest_record.get('file_identity')
        if not safe['sha256_matches_expected']:
            blockers.append('model_safetensors_sha256_mismatch')
    elif not include_hashes and safe.get('present') and not safe.get('blockers'):
        warnings.append('model_safetensors_sha256_not_checked')
    blockers.extend(str(x) for x in safe.get('blockers', []))
    warnings.extend(str(x) for x in safe.get('warnings', []))
    record['complete_required_snapshot'] = not blockers
    record['blockers'] = sorted(set(blockers))
    record['warnings'] = sorted(set(warnings))
    return record
