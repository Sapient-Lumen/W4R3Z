from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    expected = [
        "docs/1780-resilio-remedy-discharge-quarantine-release-and-ordinary-mutation-fragmentation-evaluation.md",
        "docs/1781-remedy-discharge-contract-sheet-page-quarantine-release-write-rights-and-future-admission-interface-spec.md",
        "docs/1782-remedy-discharge-review-page-is-it-safe-to-release-this-repair-case-back-to-ordinary-mutation-and-admission-policy-interface-spec.md",
        "docs/1783-remedy-discharge-proof-page-release-authority-returner-fences-and-ordinary-lane-restoration-interface-spec.md",
        "docs/1784-remedy-discharge-timeline-page-quarantine-continue-release-rearm-and-reclose-events-interface-spec.md",
        "docs/1785-remedy-discharge-lineage-receipt-page-quarantine-release-normal-lane-restoration-and-blocked-stronger-cure-sentences-interface-spec.md",
    ]
    missing = [p for p in expected if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0440 files:\n" + "\n".join(missing))
    print("rev0440 presence check OK")
