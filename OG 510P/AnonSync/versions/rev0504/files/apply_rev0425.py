from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    touched = [
        docs / "00-status.md",
        docs / "10-resilio-sync-evaluation.md",
        docs / "11-resilio-borrow-line-and-non-clone-scorecard.md",
        docs / "sources.md",
        docs / "1690-resilio-execution-mandate-agent-scope-and-autopilot-authority-fragmentation-evaluation.md",
        docs / "1691-execution-mandate-contract-sheet-page-human-agent-device-and-autopilot-scope-interface-spec.md",
        docs / "1692-execution-review-page-who-may-carry-out-which-effect-and-under-what-supervision-interface-spec.md",
        docs / "1693-execution-proof-page-which-actor-executed-why-it-counted-and-what-stronger-agency-sentence-stays-blocked-interface-spec.md",
        docs / "1694-execution-timeline-page-assent-mandate-execution-suspension-and-override-events-interface-spec.md",
        docs / "1695-execution-lineage-receipt-page-mandate-scope-actor-kind-freshness-and-blocked-stronger-sentences-interface-spec.md",
    ]
    missing = [str(p) for p in touched if not p.exists()]
    if missing:
        raise SystemExit("Missing expected rev0425 files:\n" + "\n".join(missing))
    print("rev0425 content present:")
    for path in touched:
        print("-", path.relative_to(root))


if __name__ == "__main__":
    main()
