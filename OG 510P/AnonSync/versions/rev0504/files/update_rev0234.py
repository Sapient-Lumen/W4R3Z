from pathlib import Path

ROOT = Path(__file__).resolve().parent
print("rev0234 adds docs 596-600 plus status/scorecard/clone-veto/sources/README updates for network eligibility truth.")
for rel in [
    "docs/596-resilio-mobile-network-eligibility-and-forbidden-network-truth-evaluation.md",
    "docs/597-network-eligibility-page-network-class-seat-policy-share-policy-and-detection-floor-interface-spec.md",
    "docs/598-forbidden-network-review-page-stoppage-class-detection-loss-and-wake-condition-interface-spec.md",
    "docs/599-network-policy-delta-page-seat-wide-vs-share-wide-widening-and-observer-delta-interface-spec.md",
    "docs/600-network-eligibility-receipt-page-policy-basis-detection-floor-and-wake-proof-interface-spec.md",
]:
    print(rel)
