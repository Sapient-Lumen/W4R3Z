from pathlib import Path

REV = "rev0134"
STAMP = "2026.03.19.17.52"
CODENAME = "progressrepairdepartureanvil"


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    expected = [
        "197-hidden-work-phase-ledger-and-honest-progress-interface-spec.md",
        "198-preseed-reuse-dedup-proof-and-local-block-witness-interface-spec.md",
        "199-integrity-rebuild-reindex-and-subject-repair-ladder-interface-spec.md",
        "200-disconnect-remove-and-placeholder-eviction-contract-interface-spec.md",
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
