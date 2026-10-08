from pathlib import Path

REVISION = "rev0327"
FILES = [
    "docs/1102-resilio-maintenance-health-warning-repair-rung-and-salvage-boundary-fragmentation-evaluation.md",
    "docs/1103-health-warning-contract-sheet-page-pressure-lock-spine-and-repair-class-interface-spec.md",
    "docs/1104-health-triage-review-page-busy-recovering-rescan-only-suspended-and-corrupt-verdict-interface-spec.md",
    "docs/1105-repair-rung-review-page-restart-reconnect-readd-and-salvage-boundary-interface-spec.md",
    "docs/1106-health-proof-page-recovered-degraded-rescan-only-and-support-escalation-ceiling-interface-spec.md",
    "docs/1107-health-lineage-receipt-page-warning-basis-repair-rung-and-state-loss-boundary-interface-spec.md",
]

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print(REVISION)
    for rel in FILES:
        path = root / rel
        print(f"OK\t{rel}\t{path.exists()}")
