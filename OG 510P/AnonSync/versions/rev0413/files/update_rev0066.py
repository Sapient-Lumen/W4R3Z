from pathlib import Path

CHANGED_FILES = [
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
    "docs/79-browser-independent-control-integrity-and-auth-repair-spec.md",
    "docs/sources.md",
]

if __name__ == "__main__":
    print("rev0066 touched the following files:")
    for rel in CHANGED_FILES:
        print(f" - {rel}")
