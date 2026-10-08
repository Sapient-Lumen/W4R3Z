from pathlib import Path

REV = "rev0136"
STAMP = "2026.03.19.18.11"
CODENAME = "mobileimportshellquarantine"


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    expected = [
        "205-constrained-seat-path-consent-and-removable-storage-capability-interface-spec.md",
        "206-external-editor-roundtrip-import-copy-and-replacement-review-interface-spec.md",
        "207-shell-extension-loss-and-in-app-capability-equivalence-interface-spec.md",
        "208-suspended-seat-resume-quarantine-and-offline-precedence-interface-spec.md",
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
