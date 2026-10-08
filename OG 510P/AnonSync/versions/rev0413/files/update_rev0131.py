from pathlib import Path

REV = "rev0131"
STAMP = "2026.03.19.17.14"
CODENAME = "cipherwatchghostbulkhead"

def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    expected = [
        "185-opaque-replica-custody-decrypt-authority-and-recovery-ladder-interface-spec.md",
        "186-change-detection-coverage-watcher-budget-and-rescan-truth-interface-spec.md",
        "187-ghost-announcement-byte-witness-absence-and-source-revival-repair-interface-spec.md",
        "188-service-root-contamination-self-embedding-boundary-and-whole-tree-admission-interface-spec.md",
    ]
    missing = [name for name in expected if not (docs / name).exists()]
    print(f"AnonSync {REV} @ {STAMP} {CODENAME}")
    if missing:
        print("Missing expected docs:")
        for name in missing:
            print(" -", name)
    else:
        print("Expected revision docs present.")
    print("See README.md, docs/00-status.md, and docs/sources.md for the substantive revision summary.")

if __name__ == "__main__":
    main()
