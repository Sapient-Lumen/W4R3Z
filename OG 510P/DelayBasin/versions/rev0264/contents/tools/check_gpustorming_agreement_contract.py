import pathlib

from gpustorming_contract_lib import ensure_needles

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, 'gpustorming-agreement', {
    'docs/10-method/operator-tokens-and-bootstrap-grammar.md': [
        'agreement-neutralized, endorsement-scrubbed, or alignment-pressure-scrubbed variant',
        'agreement privilege',
        'endorsement privilege',
        'alignment-pressure privilege',
    ],
    'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': [
        'agreement-neutralized, endorsement-scrubbed, or alignment-pressure-scrubbed variant',
        'agreement privilege',
        'endorsement privilege',
        'alignment-pressure privilege',
    ],
    'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': [
        'agreement',
        'agreement-seeking wording',
        'endorsement invitations',
        'favorable-label defaults',
    ],
    'docs/00-meta/trajectory-map.md': [
        'agreement privilege',
        'endorsement privilege',
        'alignment-pressure privilege',
        'agreement-seeking wording',
    ],
    'docs/20-constitution/open-question-registry.md': [
        'agreement-neutralized/endorsement-scrubbed/alignment-pressure-scrubbed variant',
        'agreement privilege',
        'alignment-pressure privilege',
    ],
    'docs/50-promptcraft/prompt-pairs.md': [
        'agreement-neutralized, endorsement-scrubbed, or alignment-pressure-scrubbed variant worth checking',
        'agreement privilege',
    ],
    'docs/00-meta/llm-runbook.md': [
        'agreement-neutralized, endorsement-scrubbed, or alignment-pressure-scrubbed variant',
        'agreement privilege',
    ],
    'docs/90-quarantine/wild-speculations-2026-03-08.md': [
        'QWS-0169',
        'endorsement court',
        'assent-pressure scaffold',
        'alignment-pressure controller',
    ],
    'CHANGELOG.md': [
        'agreement-neutralized / endorsement-scrubbed / alignment-pressure-scrubbed guard',
        'check_gpustorming_agreement_contract.py',
    ],
})

print('check_gpustorming_agreement_contract: OK')
