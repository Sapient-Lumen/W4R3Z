from pathlib import Path

REV = "rev0132"
STAMP = "2026.03.19.17.58"
CODENAME = "clockaliaspausequartz"

def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    expected = [
        "189-clock-authority-drift-budget-and-invalid-time-quarantine-interface-spec.md",
        "190-locked-writer-delay-profile-and-quiescent-commit-interface-spec.md",
        "191-link-node-alias-edge-and-target-boundary-admission-interface-spec.md",
        "192-pause-scheduler-and-destructive-signal-separation-interface-spec.md",
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
