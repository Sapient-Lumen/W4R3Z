from pathlib import Path

REV = "rev0135"
STAMP = "2026.03.19.17.57"
CODENAME = "budgetidentitycohorttripwire"


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    expected = [
        "201-storage-budget-scope-staging-headroom-and-actual-drive-truth-interface-spec.md",
        "202-identity-root-health-folder-list-salvage-and-relink-ladder-interface-spec.md",
        "203-host-ownership-claim-dual-instance-collision-and-safe-branching-interface-spec.md",
        "204-release-cohort-compatibility-control-plane-migration-and-link-gate-interface-spec.md",
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
