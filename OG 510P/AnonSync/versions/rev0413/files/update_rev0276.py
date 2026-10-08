from pathlib import Path

root = Path('.')

new_docs = {
    'docs/806-resilio-dormant-return-reentry-and-stale-claim-fragmentation-evaluation.md': 'created in rev0276',
    'docs/807-re-entry-case-page-dormancy-class-roster-return-and-safe-language-interface-spec.md': 'created in rev0276',
    'docs/808-dormancy-timeline-page-last-good-witness-hide-expiry-and-return-context-interface-spec.md': 'created in rev0276',
    'docs/809-stale-return-review-page-offline-edits-clock-confidence-and-source-reality-interface-spec.md': 'created in rev0276',
    'docs/810-re-entry-receipt-page-dormancy-facts-safe-sentence-and-reopen-boundary-interface-spec.md': 'created in rev0276',
}

for path_str, placeholder in new_docs.items():
    path = root / path_str
    if not path.exists():
        path.write_text(placeholder + "\n", encoding='utf-8')

print('rev0276 scaffold recorded; apply concrete document payloads from archive if replaying manually.')
