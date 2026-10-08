from pathlib import Path

EXPECTED = [
    "docs/1804-resilio-remedy-reaccreditation-post-uncertainty-and-guard-requalification-fragmentation-evaluation.md",
    "docs/1805-remedy-reaccreditation-contract-sheet-page-requalification-evidence-reentry-ladder-and-sticky-scars-interface-spec.md",
    "docs/1806-remedy-reaccreditation-review-page-is-this-case-honestly-eligible-to-return-from-failsafe-to-guarded-ordinary-life-interface-spec.md",
    "docs/1807-remedy-reaccreditation-proof-page-fresh-evidence-cause-remediation-and-reentry-floor-interface-spec.md",
    "docs/1808-remedy-reaccreditation-timeline-page-decay-refence-repair-reprove-and-rerelease-events-interface-spec.md",
    "docs/1809-remedy-reaccreditation-lineage-receipt-page-requalification-reentry-scope-and-blocked-ordinary-sentences-interface-spec.md",
]

base = Path(__file__).resolve().parent
missing = [p for p in EXPECTED if not (base / p).exists()]
if missing:
    raise SystemExit("Missing rev0444 files: " + ", ".join(missing))
print("rev0444 present")
