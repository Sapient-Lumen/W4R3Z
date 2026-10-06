import pathlib

from gpustorming_contract_lib import ensure_needles

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = {
    ROOT / 'docs/10-method/operator-tokens-and-bootstrap-grammar.md': [
        'overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed variant',
        'exact-match privilege',
        'reference-echo privilege',
    ],
    ROOT / 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': [
        'overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed variant',
        'exact-match privilege',
        'reference-echo privilege',
    ],
    ROOT / 'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': [
        '- **overlap**',
        'reference-echo scaffolds',
    ],
    ROOT / 'docs/20-constitution/open-question-registry.md': [
        'overlap-neutralized/paraphrase-balanced/reference-echo-scrubbed variant',
        'reference-echo privilege',
    ],
    ROOT / 'docs/00-meta/trajectory-map.md': [
        'reference-echo scaffolds',
        'A parallel overlap extension',
    ],
    ROOT / 'docs/50-promptcraft/prompt-pairs.md': [
        'overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed variant worth checking',
        'reference-echo privilege',
    ],
    ROOT / 'docs/00-meta/llm-runbook.md': [
        'overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed variant',
        'reference-echo privilege',
    ],
    ROOT / 'docs/90-quarantine/wild-speculations-2026-03-08.md': [
        'QWS-0170',
        'echo court / canon-echo scaffold / reference-similarity controller',
    ],
    ROOT / 'CHANGELOG.md': [
        'overlap-neutralized / paraphrase-balanced / reference-echo-scrubbed guard',
    ],
    ROOT / 'ARCHIVE_INDEX.md': [
        'overlap-neutralized, paraphrase-balanced, or reference-echo-scrubbed control',
    ],
}
for path, needles in FILES.items():
    ensure_needles(path, needles)
print('check_gpustorming_overlap_contract: OK')
