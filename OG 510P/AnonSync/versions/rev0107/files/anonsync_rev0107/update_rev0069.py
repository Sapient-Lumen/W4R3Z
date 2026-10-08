"""Revision helper for AnonSync rev0069.

This revision centered on safety-critical channel parity and cross-channel review handoff.
The archive was updated in-place during the work session; this helper exists as a concise
manifest of the intended changes rather than as a replayable patch script.
"""

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
    "docs/82-safety-critical-channel-parity-and-surface-capability-spec.md",
    "docs/sources.md",
]

if __name__ == "__main__":
    print("AnonSync rev0069 manifest")
    for path in CHANGED_FILES:
        print(f"- {path}")
