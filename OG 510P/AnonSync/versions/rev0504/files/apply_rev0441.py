from pathlib import Path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    expected = [
        "docs/1786-resilio-remedy-surveillance-relapse-detection-and-refence-fragmentation-evaluation.md",
        "docs/1787-remedy-surveillance-contract-sheet-page-post-discharge-watch-relapse-signals-and-refence-thresholds-interface-spec.md",
        "docs/1788-remedy-surveillance-review-page-is-this-discharged-case-still-being-watched-strongly-enough-to-stay-in-ordinary-life-interface-spec.md",
        "docs/1789-remedy-surveillance-proof-page-relapse-signals-platform-coverage-and-refence-authority-interface-spec.md",
        "docs/1790-remedy-surveillance-timeline-page-discharge-watch-relapse-escalation-and-refence-events-interface-spec.md",
        "docs/1791-remedy-surveillance-lineage-receipt-page-post-discharge-watch-relapse-posture-and-blocked-ordinary-sentences-interface-spec.md",
    ]
    missing = [p for p in expected if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0441 files:\n" + "\n".join(missing))
    print("rev0441 presence check OK")
