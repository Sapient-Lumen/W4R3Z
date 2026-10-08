from pathlib import Path

REVISION = "rev0054"
TIMESTAMP = "2026.03.17.12.29"
CODENAME = "joinproofscopequarry"

FILES_TOUCHED = [
    "README.md",
    "docs/00-status.md",
    "docs/10-resilio-sync-evaluation.md",
    "docs/30-interface-spec.md",
    "docs/31-daemon-api-spec.md",
    "docs/32-interface-flows.md",
    "docs/38-operator-workbench-interface-spec.md",
    "docs/39-interface-pattern-language.md",
    "docs/40-architecture-decisions.md",
    "docs/50-roadmap.md",
    "docs/64-critical-open-questions.md",
    "docs/66-claim-and-adoption-intake-interface-spec.md",
    "docs/67-link-and-constellation-join-interface-spec.md",
    "docs/sources.md",
]

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print(f"Recorded {REVISION} {TIMESTAMP} {CODENAME}")
    for path in FILES_TOUCHED:
        print(path)
