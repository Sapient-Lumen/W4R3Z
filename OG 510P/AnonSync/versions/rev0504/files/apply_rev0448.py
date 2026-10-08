from pathlib import Path

REV = "0448"
FILES = [
    "docs/1828-resilio-remedy-hardening-rollout-bounding-and-abort-honesty-fragmentation-evaluation.md",
    "docs/1829-remedy-hardening-rollout-contract-sheet-page-pilot-scope-blast-radius-and-abort-readiness-interface-spec.md",
    "docs/1830-remedy-hardening-rollout-review-page-can-this-approved-change-go-live-with-bounded-blast-radius-and-honest-abort-interface-spec.md",
    "docs/1831-remedy-hardening-rollout-proof-page-pilot-cohort-expansion-ceiling-and-rollback-floor-interface-spec.md",
    "docs/1832-remedy-hardening-rollout-timeline-page-pilot-expand-freeze-abort-and-reseal-events-interface-spec.md",
    "docs/1833-remedy-hardening-rollout-lineage-receipt-page-rollout-scope-abort-honesty-and-blocked-stronger-sentences-interface-spec.md",
]

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    missing = [p for p in FILES if not (root / p).exists()]
    if missing:
        raise SystemExit("Missing expected rev0448 files:\n" + "\n".join(missing))
    print(f"rev{REV} present: {len(FILES)} new docs found")
