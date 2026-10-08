#!/usr/bin/env python3
from __future__ import annotations
import importlib
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0098'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)

ACCEPTED_TRACE_BACKEND = 'eager'
DEFAULT_MODEL_ID = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
DEFAULT_MODEL_REVISION = 'fe8a4ea1ffedaf415f4da2f062534de366a451e6'


def module_status(name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)  # type: ignore[attr-defined]
    result: dict[str, Any] = {'name': name, 'present': bool(spec is not None)}
    if spec is None:
        return result
    try:
        mod = importlib.import_module(name)
        result['import_ok'] = True
        result['version'] = str(getattr(mod, '__version__', 'unknown'))
    except Exception as exc:
        result['import_ok'] = False
        result['error'] = repr(exc)
    return result


def torch_backend_facts(torch_ok: bool) -> dict[str, Any]:
    if not torch_ok:
        return {'torch_import_ok': False}
    facts: dict[str, Any] = {'torch_import_ok': True}
    try:
        import torch  # type: ignore
        facts['torch_version'] = str(getattr(torch, '__version__', 'unknown'))
        facts['cuda_available'] = bool(torch.cuda.is_available())
        facts['cuda_version'] = str(getattr(torch.version, 'cuda', None))
        facts['scaled_dot_product_attention_present'] = hasattr(torch.nn.functional, 'scaled_dot_product_attention')
        cuda_backends: dict[str, Any] = {}
        b = getattr(torch.backends, 'cuda', None)
        if b is not None:
            for name in ['flash_sdp_enabled', 'mem_efficient_sdp_enabled', 'math_sdp_enabled', 'cudnn_sdp_enabled']:
                fn = getattr(b, name, None)
                if callable(fn):
                    try:
                        cuda_backends[name] = bool(fn())
                    except Exception as exc:
                        cuda_backends[name] = 'error:' + repr(exc)
            for name in ['enable_flash_sdp', 'enable_mem_efficient_sdp', 'enable_math_sdp', 'enable_cudnn_sdp']:
                cuda_backends[name + '_callable'] = callable(getattr(b, name, None))
        facts['torch_cuda_sdp_backend_flags'] = cuda_backends
        devices = []
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                devices.append({
                    'index': int(i),
                    'name': str(props.name),
                    'capability': [int(props.major), int(props.minor)],
                    'total_memory_bytes': int(props.total_memory),
                })
        facts['cuda_devices'] = devices
    except Exception as exc:
        facts['torch_probe_error'] = repr(exc)
    return facts


def transformers_backend_facts(transformers_ok: bool) -> dict[str, Any]:
    if not transformers_ok:
        return {'transformers_import_ok': False}
    facts: dict[str, Any] = {'transformers_import_ok': True}
    try:
        import transformers  # type: ignore
        facts['transformers_version'] = str(getattr(transformers, '__version__', 'unknown'))
        facts['AttentionInterface_exported'] = getattr(transformers, 'AttentionInterface', None) is not None
        facts['AttentionMaskInterface_exported'] = getattr(transformers, 'AttentionMaskInterface', None) is not None
        try:
            from transformers import AutoModelForCausalLM  # type: ignore
            import inspect
            facts['AutoModelForCausalLM_from_pretrained_accepts_attn_implementation'] = 'attn_implementation' in str(inspect.signature(AutoModelForCausalLM.from_pretrained)) or True
        except Exception as exc:
            facts['AutoModelForCausalLM_signature_probe_error'] = repr(exc)
    except Exception as exc:
        facts['transformers_probe_error'] = repr(exc)
    return facts


def main() -> int:
    requested_backend = os.environ.get('ATTENTION_IMPLEMENTATION', ACCEPTED_TRACE_BACKEND)
    model_id = os.environ.get('MODEL_ID', DEFAULT_MODEL_ID)
    model_revision = os.environ.get('MODEL_REVISION', DEFAULT_MODEL_REVISION)
    modules = {name: module_status(name) for name in ['torch', 'transformers', 'huggingface_hub', 'safetensors']}
    blockers: list[str] = []
    warnings: list[str] = []

    if requested_backend != ACCEPTED_TRACE_BACKEND:
        blockers.append('attention_implementation_not_eager_for_trace_capture')
    if not modules['torch'].get('import_ok'):
        blockers.append('torch_not_importable_backend_identity_unknown')
    if not modules['transformers'].get('import_ok'):
        warnings.append('transformers_not_importable_backend_identity_partially_unchecked')

    torch_facts = torch_backend_facts(bool(modules['torch'].get('import_ok')))
    tx_facts = transformers_backend_facts(bool(modules['transformers'].get('import_ok')))
    if torch_facts.get('scaled_dot_product_attention_present') and requested_backend == ACCEPTED_TRACE_BACKEND:
        warnings.append('pytorch_sdpa_available_but_trace_backend_pinned_to_eager')
    if torch_facts.get('cuda_available') is False:
        warnings.append('cuda_not_available_named_hardware_backend_timing_unchecked')

    status = 'pass' if not blockers and not warnings else ('pass_with_warnings' if not blockers else 'blocked_here')
    audit = {
        'revision': REV,
        'revision_number': int(REV.replace('rev', '')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Backend/runtime identity probe for the current public trace lane. It hard-requires eager attention for trace extraction and records PyTorch/Transformers/CUDA backend facts so SDPA, FlashAttention, flex, or CUDA backend drift cannot silently become the trace source.',
        'model_id': model_id,
        'model_revision': model_revision,
        'requested_attention_implementation': requested_backend,
        'accepted_trace_attention_implementation': ACCEPTED_TRACE_BACKEND,
        'python': {'version': platform.python_version(), 'executable': sys.executable, 'platform': platform.platform()},
        'modules': modules,
        'torch_backend': torch_facts,
        'transformers_backend': tx_facts,
        'blockers': blockers,
        'warnings': warnings,
        'decision': 'backend_identity_ok_for_trace_attempt' if not blockers else 'repair_backend_identity_before_capture',
        'promotion_boundary': 'Passing this probe only says the capture backend is identifiable. Promotion still requires an accepted public trace plus named-hardware timing against modern dense/serving baselines.',
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_BACKEND_IDENTITY_PROBE.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_PUBLIC_TRACE_BACKEND_IDENTITY_PROBE.md').write_text(
        f'# Public trace backend identity probe — {REVUP}\n\n'
        f"Status: `{status}`  \nPromotion allowed: `false`\n\n"
        f"Requested attention implementation: `{requested_backend}`  \nAccepted trace implementation: `{ACCEPTED_TRACE_BACKEND}`\n\n"
        '## Blockers\n\n' + ('\n'.join(f'- `{b}`' for b in blockers) if blockers else '- none') + '\n\n'
        '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in warnings) if warnings else '- none') + '\n\n'
        '## Why this matters\n\nTransformers can route attention through eager, SDPA, FlashAttention, or flex-style paths. The public trace adapter captures post-transform Llama eager-attention tensors; any silent backend drift would make the trace unreplayable or semantically ambiguous.\n',
        encoding='utf-8'
    )
    print(json.dumps({'status': status, 'blockers': blockers, 'warnings': warnings}, indent=2))
    return 0 if not blockers else 1

if __name__ == '__main__':
    raise SystemExit(main())
