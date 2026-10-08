from pathlib import Path

REVISION = "rev0058"
TIMESTAMP = "2026.03.17.14.01"
CODENAME = "replayproofdeletequarry"

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
    "docs/71-destructive-replay-and-delete-wave-review-spec.md",
]

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print(f"Recorded {REVISION} {TIMESTAMP} {CODENAME}")
    for path in FILES_TOUCHED:
        print(path)
