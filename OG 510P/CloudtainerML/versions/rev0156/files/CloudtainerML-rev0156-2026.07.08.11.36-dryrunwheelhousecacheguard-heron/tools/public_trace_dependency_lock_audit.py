#!/usr/bin/env python3
from __future__ import annotations
import importlib
import importlib.metadata as md
import importlib.util
import inspect
import json
import os
import platform
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0099'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
MAN = ROOT / 'artifacts' / 'run-manifests'
OUT.mkdir(parents=True, exist_ok=True)
MAN.mkdir(parents=True, exist_ok=True)
REQ = ROOT / 'artifacts' / 'runtime' / f'{REVUP}_public_trace_requirements.txt'

MIN_VERSIONS = {
    'torch': '2.4',
    'transformers': '4.34',
    'huggingface_hub': '1.0',
    'safetensors': '0.4',
}
OPTIONAL_FOR_DOWNLOAD = ['accelerate', 'hf_xet']


def version_tuple(text: str) -> tuple[int, ...]:
    nums = re.findall(r'\d+', str(text).split('+', 1)[0])
    return tuple(int(x) for x in nums[:4]) if nums else ()


def ge_version(actual: str, minimum: str) -> bool | None:
    a = version_tuple(actual)
    m = version_tuple(minimum)
    if not a or not m:
        return None
    L = max(len(a), len(m))
    return a + (0,) * (L - len(a)) >= m + (0,) * (L - len(m))


def module_status(name: str, *, import_probe: bool) -> dict[str, Any]:
    """Report module presence/version without importing heavy libraries unless needed.

    Rev0119's first blocker here is often a missing `transformers`; importing
    torch just to rediscover that can cost several seconds or hang on local CUDA
    shutdown. Use `find_spec` + package metadata first, and only import modules
    after the cheap dependency surface is complete.
    """
    spec = importlib.util.find_spec(name)  # type: ignore[attr-defined]
    out: dict[str, Any] = {
        'name': name,
        'present': bool(spec is not None),
        'origin': getattr(spec, 'origin', None) if spec else None,
        'import_probe_attempted': bool(import_probe and spec is not None),
    }
    if spec is None:
        return out
    try:
        out['version'] = md.version(name)
    except Exception:
        out['version_error'] = 'metadata_version_unavailable'
    if not import_probe:
        out['import_ok'] = True
        out['import_ok_inferred_from_spec_only'] = True
        return out
    try:
        importlib.import_module(name)
        out['import_ok'] = True
    except Exception as exc:
        out['import_ok'] = False
        out['import_error'] = repr(exc)
    return out


def hf_capabilities() -> dict[str, Any]:
    caps: dict[str, Any] = {'snapshot_download_importable': False}
    try:
        from huggingface_hub import snapshot_download  # type: ignore
        sig = inspect.signature(snapshot_download)
        params = sig.parameters
        caps['snapshot_download_importable'] = True
        caps['snapshot_download_signature'] = str(sig)
        for p in ['revision', 'allow_patterns', 'local_files_only', 'dry_run', 'etag_timeout']:
            caps[f'supports_{p}'] = p in params
    except Exception as exc:
        caps['error'] = repr(exc)
    return caps


def torch_capabilities(status: dict[str, Any]) -> dict[str, Any]:
    if not status.get('import_ok'):
        return {'torch_import_ok': False}
    out: dict[str, Any] = {'torch_import_ok': True}
    try:
        import torch  # type: ignore
        out['cuda_available'] = bool(torch.cuda.is_available())
        out['cuda_device_count'] = int(torch.cuda.device_count()) if torch.cuda.is_available() else 0
        out['scaled_dot_product_attention_present'] = hasattr(torch.nn.functional, 'scaled_dot_product_attention')
        out['torch_version'] = str(getattr(torch, '__version__', 'unknown'))
    except Exception as exc:
        out['torch_probe_error'] = repr(exc)
    return out


def main() -> int:
    allow_download = os.environ.get('ALLOW_DOWNLOAD', '0') == '1'
    cheap_modules = {name: module_status(name, import_probe=False) for name in ['torch', 'transformers', 'huggingface_hub', 'safetensors', 'accelerate', 'hf_xet']}
    missing_required = [name for name in MIN_VERSIONS if not cheap_modules[name].get('present')]
    import_probe = not missing_required
    modules = {name: module_status(name, import_probe=import_probe) for name in ['torch', 'transformers', 'huggingface_hub', 'safetensors', 'accelerate', 'hf_xet']}
    blockers: list[str] = []
    warnings: list[str] = []

    py_ok = sys.version_info >= (3, 10)
    if not py_ok:
        blockers.append('python_version_below_3_10')
    for name, minimum in MIN_VERSIONS.items():
        st = modules[name]
        if not st.get('present'):
            blockers.append(f'{name}_not_importable')
            continue
        if import_probe and not st.get('import_ok'):
            blockers.append(f'{name}_import_probe_failed')
            continue
        cmp = ge_version(str(st.get('version', 'unknown')), minimum)
        st['minimum_required'] = minimum
        st['meets_minimum'] = cmp
        if cmp is False:
            blockers.append(f'{name}_version_below_{minimum}')
        elif cmp is None:
            warnings.append(f'{name}_version_unparseable')
    for name in OPTIONAL_FOR_DOWNLOAD:
        if allow_download and not modules[name].get('present'):
            warnings.append(f'{name}_not_importable_download_may_be_slower_or_less_robust')

    caps = hf_capabilities()
    if not caps.get('snapshot_download_importable'):
        blockers.append('snapshot_download_not_importable')
    else:
        for cap in ['supports_revision', 'supports_allow_patterns', 'supports_local_files_only', 'supports_dry_run']:
            if not caps.get(cap):
                blockers.append('huggingface_hub_snapshot_download_missing_' + cap.replace('supports_', ''))
    torch_caps = torch_capabilities(modules['torch']) if import_probe else {'torch_import_ok': False, 'cuda_available': False, 'skipped': 'cheap_dependency_surface_incomplete'}
    if not torch_caps.get('cuda_available'):
        warnings.append('cuda_not_available_named_hardware_timing_still_blocked_here')

    status = 'pass' if not blockers and not warnings else ('pass_with_warnings' if not blockers else 'blocked_here')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev','')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Import-light fail-fast runtime dependency/capability lock for the public TinyLlama trace lane. It separates install/capability blockers from model-source blockers so the next operator repairs the environment instead of editing registries.',
        'python': {'version': platform.python_version(), 'executable': sys.executable, 'meets_python_3_10_plus': py_ok, 'platform': platform.platform()},
        'allow_download': allow_download,
        'requirements_file': REQ.relative_to(ROOT).as_posix() if REQ.exists() else None,
        'missing_required_modules_before_import_probe': missing_required,
        'heavy_import_probe_attempted': import_probe,
        'modules': modules,
        'huggingface_hub_capabilities': caps,
        'torch_capabilities': torch_caps,
        'blockers': blockers,
        'warnings': warnings,
        'next_if_blocked': [
            'create an isolated venv/container',
            f'install -r {REQ.relative_to(ROOT).as_posix()} if policy allows network/package installation',
            'rerun python tools/public_trace_readiness_gate.py --local-only before attempting capture',
        ],
        'online_source_basis': [
            {'url': 'https://huggingface.co/docs/transformers/en/installation', 'fact': 'Transformers installation docs state Python 3.10+ and PyTorch 2.4+ are tested.'},
            {'url': 'https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0', 'fact': 'TinyLlama model card says transformers>=4.34 is needed and the model uses Llama 2 architecture/tokenizer.'},
            {'url': 'https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/_snapshot_download.py', 'fact': 'snapshot_download exposes revision, allow_patterns, local_files_only, and dry_run parameters in current source.'},
        ],
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_DEPENDENCY_LOCK_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_PUBLIC_TRACE_DEPENDENCY_LOCK_AUDIT.md').write_text(
        f'# Public trace dependency lock audit — {REVUP}\n\n'
        f"Status: `{status}`  \nPromotion allowed: `false`\n\n"
        f"Requirements: `{audit['requirements_file']}`\n\n"
        '## Blockers\n\n' + ('\n'.join(f'- `{b}`' for b in blockers) if blockers else '- none') + '\n\n'
        '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in warnings) if warnings else '- none') + '\n\n'
        '## Interpretation\n\nThis probe makes the environment repair lane explicit. A missing `transformers` import is no longer a vague runtime blocker; it is a specific package/capability blocker before any large snapshot operation.\n',
        encoding='utf-8'
    )
    (MAN / f'{REVUP}_TRACE_DEPENDENCY_LOCK.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'blockers': blockers, 'warnings': warnings}, indent=2))
    return 0 if not blockers else 1

if __name__ == '__main__':
    raise SystemExit(main())
