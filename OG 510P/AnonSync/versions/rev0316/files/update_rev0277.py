from pathlib import Path

root = Path('.')

new_docs = {
    'docs/811-resilio-local-pause-and-cohort-quiet-agreement-fragmentation-evaluation.md': 'created in rev0277',
    'docs/812-quiet-cohort-page-target-seats-local-posture-and-coverage-interface-spec.md': 'created in rev0277',
    'docs/813-quiet-agreement-review-page-counterpart-proof-residual-movers-and-safe-language-interface-spec.md': 'created in rev0277',
    'docs/814-quiet-window-request-page-intent-window-token-and-counterpart-acknowledgement-interface-spec.md': 'created in rev0277',
    'docs/815-quiet-cohort-receipt-page-covered-seats-achieved-stillness-and-reopen-boundary-interface-spec.md': 'created in rev0277',
}

for path_str, placeholder in new_docs.items():
    path = root / path_str
    if not path.exists():
        path.write_text(placeholder + "\n", encoding='utf-8')

print('rev0277 scaffold recorded; apply concrete document payloads from archive if replaying manually.')
