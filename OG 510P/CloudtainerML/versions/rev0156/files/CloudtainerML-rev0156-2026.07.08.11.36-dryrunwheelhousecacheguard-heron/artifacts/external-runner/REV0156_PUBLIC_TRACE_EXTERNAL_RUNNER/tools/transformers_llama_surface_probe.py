#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib, importlib.util, inspect, json, platform, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0096'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)


def module_status(name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)  # type: ignore[attr-defined]
    d: dict[str, Any] = {'name': name, 'present': bool(spec is not None)}
    if spec is None:
        return d
    try:
        mod = importlib.import_module(name)
        d['import_ok'] = True
        d['version'] = str(getattr(mod, '__version__', 'unknown'))
    except Exception as exc:
        d['import_ok'] = False
        d['error'] = repr(exc)
    return d


def sig_params(obj: Any) -> list[str]:
    try:
        return list(inspect.signature(obj).parameters)
    except Exception:
        return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--strict', action='store_true', help='return nonzero if the current Transformers/Llama surface is not capture-compatible')
    args = ap.parse_args()
    blockers: list[str] = []
    warnings: list[str] = []
    facts: dict[str, Any] = {'python': platform.python_version(), 'executable': sys.executable}
    modules = {name: module_status(name) for name in ['torch', 'transformers', 'huggingface_hub', 'safetensors']}
    facts['modules'] = modules
    if not modules['transformers'].get('import_ok'):
        blockers.append('transformers_not_importable_runtime_surface_unchecked')
    if not modules['torch'].get('import_ok'):
        blockers.append('torch_not_importable_runtime_surface_unchecked')

    llama: dict[str, Any] = {}
    if not blockers:
        try:
            ml = importlib.import_module('transformers.models.llama.modeling_llama')
            llama['modeling_llama_import_ok'] = True
            eager = getattr(ml, 'eager_attention_forward', None)
            llama['eager_attention_forward_present'] = callable(eager)
            eager_params = sig_params(eager) if callable(eager) else []
            llama['eager_attention_forward_signature'] = eager_params
            required_eager = ['module', 'query', 'key', 'value', 'attention_mask', 'scaling']
            missing_eager = [p for p in required_eager if p not in eager_params]
            if not callable(eager):
                blockers.append('llama_eager_attention_forward_missing')
            elif missing_eager:
                blockers.append('llama_eager_attention_forward_signature_incompatible:' + ','.join(missing_eager))
            LlamaAttention = getattr(ml, 'LlamaAttention', None)
            llama['LlamaAttention_present'] = LlamaAttention is not None
            fwd = getattr(LlamaAttention, 'forward', None) if LlamaAttention is not None else None
            fwd_params = sig_params(fwd) if fwd is not None else []
            llama['LlamaAttention_forward_signature'] = fwd_params
            for p in ['hidden_states', 'position_embeddings', 'attention_mask']:
                if p not in fwd_params:
                    warnings.append('llama_attention_forward_missing_expected_param:' + p)
            if 'cache_position' not in fwd_params:
                warnings.append('llama_attention_forward_cache_position_not_visible')
            if 'past_key_value' not in fwd_params and 'past_key_values' not in fwd_params:
                warnings.append('llama_attention_forward_past_key_value_not_visible')
        except Exception as exc:
            llama['modeling_llama_import_ok'] = False
            llama['modeling_llama_error'] = repr(exc)
            blockers.append('transformers_llama_modeling_import_failed')
        try:
            import transformers  # type: ignore
            ai = getattr(transformers, 'AttentionInterface', None)
            ami = getattr(transformers, 'AttentionMaskInterface', None)
            llama['AttentionInterface_present'] = ai is not None
            llama['AttentionMaskInterface_present'] = ami is not None
            if ai is None:
                warnings.append('AttentionInterface_not_exported_from_transformers')
            if ami is None:
                warnings.append('AttentionMaskInterface_not_exported_from_transformers')
        except Exception as exc:
            warnings.append('attention_interface_probe_failed:' + repr(exc))

    # Version-major warning: the adapter is internal-surface sensitive; v5 may be fine,
    # but must be proven by the signature checks above rather than assumed from docs.
    version = str(modules.get('transformers', {}).get('version', 'missing'))
    if version.startswith('5.'):
        warnings.append('transformers_major_5_detected_internal_surface_must_be_revalidated')

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
        'summary': 'Runtime compatibility probe for the exact HF Llama eager-attention surface used by the public trace capture hook. It catches Transformers-version/API drift before an expensive model download or trace run.',
        'facts': facts,
        'llama_surface': llama,
        'blockers': blockers,
        'warnings': warnings,
        'decision': 'capture_surface_compatible' if not blockers else 'repair_transformers_or_adapter_before_capture',
    }
    (OUT / f'{REVUP}_TRANSFORMERS_LLAMA_SURFACE_PROBE.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    (OUT / f'{REVUP}_TRANSFORMERS_LLAMA_SURFACE_PROBE.md').write_text(
        f'# Transformers Llama surface probe — {REVUP}\n\n'
        f"Status: `{status}`  \nPromotion allowed: `false`\n\n"
        '## Blockers\n\n' + ('\n'.join(f'- `{b}`' for b in blockers) if blockers else '- none') + '\n\n'
        '## Warnings\n\n' + ('\n'.join(f'- `{w}`' for w in warnings) if warnings else '- none') + '\n\n'
        '## Interpretation\n\nThe riskiest remaining software failure is a silent Transformers/Llama internal-surface mismatch. This probe must pass before a public trace can be treated as an executable lane. It does not promote any trace.\n',
        encoding='utf-8'
    )
    print(json.dumps({'status': status, 'blockers': blockers, 'warnings': warnings}, indent=2))
    if args.strict and blockers:
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
