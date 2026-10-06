import pathlib

from gpustorming_contract_lib import ensure_needles, trajectory_problem_phrase

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, 'gpustorming-entanglement', {
    'docs/10-method/operator-tokens-and-bootstrap-grammar.md': [
        'criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant',
        'cross-criterion privilege',
        'objective-conflation privilege',
        'multi-question privilege',
    ],
    'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': [
        'criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant',
        'cross-criterion privilege',
        'objective-conflation privilege',
        'multi-question privilege',
    ],
    'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': [
        '- **entanglement**',
        'multiple criteria, bundled objectives, or multi-question judge prompts',
    ],
    'docs/00-meta/trajectory-map.md': [
        'A parallel entanglement extension',
        'cross-criterion privilege',
        'objective-conflation privilege',
        'multi-question privilege',
        trajectory_problem_phrase('entanglement'),
    ],
    'docs/20-constitution/open-question-registry.md': [
        'criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant',
        'cross-criterion privilege',
        'objective-conflation privilege',
        'multi-question privilege',
    ],
    'docs/50-promptcraft/prompt-pairs.md': [
        'criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant worth checking',
        'cross-criterion privilege',
        'objective-conflation privilege',
        'multi-question privilege',
    ],
    'docs/00-meta/llm-runbook.md': [
        'criterion-isolated, atomic-evaluation, or entanglement-scrubbed variant',
        'cross-criterion privilege',
        'objective-conflation privilege',
        'multi-question privilege',
    ],
    'docs/90-quarantine/wild-speculations-2026-03-08.md': [
        'QWS-0172',
        'criteria-entanglement court, objective-blending scaffold, or rubric-halo controller',
    ],
    'CHANGELOG.md': [
        'criterion-isolated / atomic-evaluation / entanglement-scrubbed guard',
        'check_gpustorming_entanglement_contract.py',
    ],
    'ARCHIVE_INDEX.md': [
        'criterion-isolated, atomic-evaluation, or entanglement-scrubbed control',
    ],
})
print('check_gpustorming_entanglement_contract: OK')
