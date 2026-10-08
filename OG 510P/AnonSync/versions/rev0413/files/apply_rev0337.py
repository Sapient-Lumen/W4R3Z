from pathlib import Path

NEW_DOCS = [
    "1162-resilio-offer-family-bearer-capability-acceptance-lane-and-landing-residue-fragmentation-evaluation.md",
    "1163-offer-family-contract-sheet-page-key-link-qr-file-send-and-claim-governance-interface-spec.md",
    "1164-bearer-capability-review-page-approval-absence-expiry-usage-ceiling-and-fanout-interface-spec.md",
    "1165-acceptance-lane-review-page-browser-handoff-manual-paste-qr-and-webui-fallback-interface-spec.md",
    "1166-landing-residue-review-page-default-destination-collision-suffix-and-ui-byte-divergence-interface-spec.md",
    "1167-offer-family-lineage-receipt-page-artifact-family-claim-lane-and-landing-survivor-boundary-interface-spec.md",
]

if __name__ == "__main__":
    docs = Path(__file__).parent / "docs"
    missing = [name for name in NEW_DOCS if not (docs / name).exists()]
    if missing:
        raise SystemExit(f"Missing expected rev0337 docs: {missing}")
    print("rev0337 docs present")
