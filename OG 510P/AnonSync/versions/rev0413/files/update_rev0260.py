from pathlib import Path

root = Path('.')

def prepend(path_str, text):
    path = root / path_str
    old = path.read_text(encoding='utf-8')
    path.write_text(text.rstrip() + "

" + old, encoding='utf-8')

new_docs = {
    'docs/731-resilio-incident-object-absence-history-search-and-diagnostic-continuity-fragmentation-evaluation.md': 'created in rev0261',
    'docs/732-diagnostic-incident-page-entry-summary-current-best-explanation-and-gap-budget-interface-spec.md': 'created in rev0261',
    'docs/733-incident-timeline-page-status-history-queue-warning-and-action-unification-interface-spec.md': 'created in rev0261',
    'docs/734-evidence-sufficiency-review-page-route-coverage-proof-strength-and-next-cheapest-question-interface-spec.md': 'created in rev0261',
    'docs/735-diagnostic-conclusion-receipt-page-winning-explanation-alternatives-and-escalation-boundary-interface-spec.md': 'created in rev0261',
}

for path_str, placeholder in new_docs.items():
    path = root / path_str
    if not path.exists():
        path.write_text(placeholder + "
", encoding='utf-8')

print('rev0261 scaffold recorded; apply concrete document payloads from archive if replaying manually.')
