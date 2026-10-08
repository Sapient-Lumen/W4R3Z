from pathlib import Path

root = Path('.')

new_docs = {
    'docs/741-resilio-freeform-incident-brief-timestamp-narrative-and-reproduction-fragmentation-evaluation.md': 'created in rev0263',
    'docs/742-incident-brief-page-problem-statement-time-anchors-and-affected-subjects-interface-spec.md': 'created in rev0263',
    'docs/743-symptom-bookmark-page-observed-event-anchor-and-later-capture-alignment-interface-spec.md': 'created in rev0263',
    'docs/744-coordinated-capture-run-page-steps-participants-dwell-and-success-window-interface-spec.md': 'created in rev0263',
    'docs/745-capture-brief-receipt-page-claimed-symptom-run-outcome-and-usable-evidence-window-interface-spec.md': 'created in rev0263',
}

for path_str, placeholder in new_docs.items():
    path = root / path_str
    if not path.exists():
        path.write_text(placeholder + "
", encoding='utf-8')

print('rev0263 scaffold recorded; apply concrete document payloads from archive if replaying manually.')
