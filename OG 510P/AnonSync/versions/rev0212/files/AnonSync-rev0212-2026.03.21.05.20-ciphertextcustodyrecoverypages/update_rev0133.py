from pathlib import Path

REV = "rev0133"
STAMP = "2026.03.19.18.24"
CODENAME = "rulemetadatastageharbor"

def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    expected = [
        "193-ignore-rule-agreement-drift-and-visible-rule-ledger-interface-spec.md",
        "194-metadata-stream-policy-xattr-carriage-and-bundle-fidelity-interface-spec.md",
        "195-transfer-staging-partial-artifacts-and-finalize-visibility-interface-spec.md",
        "196-capture-only-ingest-sink-and-retention-floor-interface-spec.md",
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
