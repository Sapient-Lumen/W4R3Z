from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    print("rev0152 captured in-place in this archive copy")
    print("Added docs/253-shareable-artifact-carryforward-delta-ledger-and-refresh-notice-interface-spec.md")
    print("Refreshed README.md, docs/00-status.md, docs/20-product-direction.md, docs/30-interface-spec.md, docs/31-daemon-api-spec.md, docs/32-interface-flows.md, docs/40-architecture-decisions.md, docs/50-roadmap.md, and docs/sources.md")
    print(f"Root: {root}")


if __name__ == "__main__":
    main()
