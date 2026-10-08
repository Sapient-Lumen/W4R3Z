#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / 'CUBE-META.json').read_text(encoding='utf-8'))
REV = str(META.get('revision', 'rev0000'))
REVUP = REV.upper()
OUT = ROOT / 'artifacts' / 'audit'
OUT.mkdir(parents=True, exist_ok=True)
CAPTURE_REL = 'experiments/public_trace_capture/hf_attention_trace_capture.py'


def assigned_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


def line_of_assignment(tree: ast.AST, name: str) -> list[int]:
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if assigned_name(target) == name:
                    lines.append(int(getattr(node, 'lineno', -1)))
        elif isinstance(node, ast.AnnAssign):
            if assigned_name(node.target) == name:
                lines.append(int(getattr(node, 'lineno', -1)))
        elif isinstance(node, ast.AugAssign):
            if assigned_name(node.target) == name:
                lines.append(int(getattr(node, 'lineno', -1)))
    return sorted(lines)


def first_text_line(src: str, marker: str) -> int:
    for i, line in enumerate(src.splitlines(), 1):
        if marker in line:
            return i
    return -1


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    path = ROOT / CAPTURE_REL
    src = path.read_text(encoding='utf-8', errors='replace')
    tree = ast.parse(src)
    effective_public_lines = line_of_assignment(tree, 'effective_public')
    effective_source_type_lines = line_of_assignment(tree, 'effective_source_type')
    score_bias_line = first_text_line(src, 'score_bias.shape !=')
    rotary_all_lines = line_of_assignment(tree, 'rotary_position_ids_verified')
    phase_contract_lines = line_of_assignment(tree, 'phase_contract_verified')
    rotary_semantic_lines = [line for line in rotary_all_lines if score_bias_line > 0 and line > score_bias_line and (not phase_contract_lines or line < phase_contract_lines[0])]
    score_fidelity_lines = line_of_assignment(tree, 'score_path_fidelity_verified')
    final_fidelity_lines = line_of_assignment(tree, 'fidelity_verified')
    provenance_lines = line_of_assignment(tree, 'provenance_complete')

    if len(effective_public_lines) != 1:
        errors.append(f'effective_public_assignment_count_{len(effective_public_lines)}')
    if len(effective_source_type_lines) != 1:
        errors.append(f'effective_source_type_assignment_count_{len(effective_source_type_lines)}')
    if len(rotary_semantic_lines) != 1:
        errors.append(f'final_rotary_position_ids_verified_assignment_count_{len(rotary_semantic_lines)}')
    if len(phase_contract_lines) != 1:
        errors.append(f'phase_contract_verified_assignment_count_{len(phase_contract_lines)}')
    if len(score_fidelity_lines) != 1:
        errors.append(f'score_path_fidelity_verified_assignment_count_{len(score_fidelity_lines)}')
    if len(final_fidelity_lines) != 1:
        errors.append(f'fidelity_verified_assignment_count_{len(final_fidelity_lines)}')
    if len(provenance_lines) != 1:
        errors.append(f'provenance_complete_assignment_count_{len(provenance_lines)}')

    token_line = first_text_line(src, 'token_provenance_verified = bool(')
    gen_token_line = first_text_line(src, 'generation_token_provenance_verified = bool(')
    gen_det_line = first_text_line(src, 'generation_determinism_gate_verified = bool(')
    if effective_public_lines:
        final_line = effective_public_lines[0]
        for label, line in [
            ('score_bias_shape_check', score_bias_line),
            ('rotary_position_semantics_gate', rotary_semantic_lines[0] if rotary_semantic_lines else -1),
            ('token_provenance_gate', token_line),
            ('generation_token_gate', gen_token_line),
            ('generation_determinism_gate', gen_det_line),
            ('provenance_complete', provenance_lines[0] if provenance_lines else -1),
            ('final_fidelity', final_fidelity_lines[0] if final_fidelity_lines else -1),
        ]:
            if line < 0:
                errors.append(label + '_not_found')
            elif line >= final_line:
                errors.append(label + '_not_before_effective_public')
    if 'effective_public = bool(args.public_pretrained_trace and fidelity_verified and provenance_complete and runtime_provenance_verified)' not in src:
        errors.append('effective_public_formula_changed_or_missing')
    if 'fidelity_verified = bool(score_path_fidelity_verified and token_provenance_verified and generation_token_provenance_verified and generation_determinism_gate_verified)' not in src:
        errors.append('final_fidelity_formula_changed_or_missing')
    if 'score_path_fidelity_verified' not in src:
        errors.append('score_path_fidelity_name_missing')
    if rotary_semantic_lines and phase_contract_lines and rotary_semantic_lines[0] >= phase_contract_lines[0]:
        errors.append('rotary_position_semantics_not_before_phase_contract')
    if phase_contract_lines and effective_public_lines and phase_contract_lines[0] >= effective_public_lines[0]:
        errors.append('phase_contract_not_before_effective_public')
    if 'and rotary_position_ids_verified is True' not in src:
        errors.append('rotary_position_semantic_gate_not_in_final_fidelity_path')
    if src.count('effective_public = bool(') != 1:
        errors.append('effective_public_text_assignment_count_not_one')

    status = 'pass' if not errors else 'fail'
    audit: dict[str, Any] = {
        'revision': REV,
        'revision_number': int(REV.replace('rev', '')),
        'package_name': META.get('package_name'),
        'archive_name': META.get('archive_name'),
        'status': status,
        'promotion_allowed': False,
        'public_pretrained_trace_loaded': False,
        'gpu_fused_kernel_measured': False,
        'summary': 'Audits the public-trace final gate. Promotion must be assigned once, after score-path, rotary-position semantics, token/generated-token provenance, generation determinism, runtime provenance, and digest-authenticated model provenance are all known.',
        'checked_file': CAPTURE_REL,
        'assignment_lines': {
            'rotary_position_ids_verified_all': rotary_all_lines,
            'rotary_position_ids_verified_final_gate': rotary_semantic_lines,
            'phase_contract_verified': phase_contract_lines,
            'score_path_fidelity_verified': score_fidelity_lines,
            'fidelity_verified': final_fidelity_lines,
            'provenance_complete': provenance_lines,
            'effective_public': effective_public_lines,
            'effective_source_type': effective_source_type_lines,
        },
        'critical_gate_lines': {
            'score_bias_shape_check': score_bias_line,
            'token_provenance_verified': token_line,
            'generation_token_provenance_verified': gen_token_line,
            'generation_determinism_gate_verified': gen_det_line,
        },
        'errors': errors,
        'warnings': warnings,
        'decision': 'single_final_promotion_decision_guarded' if not errors else 'repair_capture_decision_flow',
        'why_it_matters': 'The old helper computed promotion-ish booleans before all token/generation gates were known and overwrote them later. Rev0126 additionally closes a latent seam where rotary-position semantic validation was computed after the final public decision, meaning future edits could accidentally read a premature success path.'
    }
    (OUT / f'{REVUP}_PUBLIC_TRACE_CAPTURE_DECISION_REFACTOR_AUDIT.json').write_text(json.dumps(audit, indent=2, sort_keys=False) + '\n', encoding='utf-8')
    lines = [
        f'# Public trace capture decision refactor audit — {REVUP}',
        '',
        f"Status: `{status}`  ",
        'Promotion allowed: `false`',
        '',
        '## Errors',
        '',
    ]
    lines.extend([f'- `{e}`' for e in errors] if errors else ['- none'])
    lines.extend(['', '## Interpretation', '', audit['why_it_matters']])
    (OUT / f'{REVUP}_PUBLIC_TRACE_CAPTURE_DECISION_REFACTOR_AUDIT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': status, 'errors': errors, 'warnings': warnings}, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(main())
