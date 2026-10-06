import pathlib

from gpustorming_contract_lib import ensure_needles, trajectory_problem_phrase

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, 'gpustorming-verbosity', {
    'docs/10-method/operator-tokens-and-bootstrap-grammar.md': [
        'length-balanced, verbosity-scrubbed, or style-neutralized variant',
        'verbosity privilege',
        'style-fluency privilege',
    ],
    'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': [
        'length-balanced, verbosity-scrubbed, or style-neutralized variant',
        'verbosity privilege',
        'style-fluency privilege',
    ],
    'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': [
        '- **verbosity**',
        'answer length, completeness-looking detail, chain-of-thought reveal, or polished style',
    ],
    'docs/00-meta/trajectory-map.md': [
        'verbosity privilege',
        'style-fluency privilege',
        'A parallel verbosity extension',
        trajectory_problem_phrase('verbosity'),
    ],
    'docs/20-constitution/open-question-registry.md': [
        'length-balanced/verbosity-scrubbed/style-neutralized variant',
        'verbosity privilege',
        'style-fluency privilege',
    ],
    'docs/50-promptcraft/prompt-pairs.md': [
        'length-balanced, verbosity-scrubbed, or style-neutralized variant worth checking',
        'verbosity privilege',
        'style-fluency privilege',
    ],
    'docs/00-meta/llm-runbook.md': [
        'length-balanced, verbosity-scrubbed, or style-neutralized variant',
        'verbosity privilege',
        'style-fluency privilege',
    ],
    'docs/90-quarantine/wild-speculations-2026-03-08.md': [
        'QWS-0171',
        'style court / rich-content scaffold / model-style controller',
    ],
    'CHANGELOG.md': [
        'length-balanced / verbosity-scrubbed / style-neutralized guard',
        'check_gpustorming_verbosity_contract.py',
    ],
    'ARCHIVE_INDEX.md': [
        'length-balanced, verbosity-scrubbed, or style-neutralized control',
    ],
})
print('check_gpustorming_verbosity_contract: OK')
