from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
REQUIRED = [
    "1852-resilio-remedy-hardening-attestation-integrity-and-tamper-evidence-fragmentation-evaluation.md",
    "1853-remedy-hardening-attestation-integrity-contract-sheet-page-seal-custody-and-claim-ceiling-interface-spec.md",
    "1854-remedy-hardening-attestation-integrity-review-page-is-the-verifier-bundle-still-tamper-evident-after-export-and-handoff-interface-spec.md",
    "1855-remedy-hardening-attestation-integrity-proof-page-seal-basis-custody-lineage-and-verifier-floor-interface-spec.md",
    "1856-remedy-hardening-attestation-integrity-timeline-page-seal-custody-check-and-tamper-challenge-events-interface-spec.md",
    "1857-remedy-hardening-attestation-integrity-lineage-receipt-page-seal-custody-verifier-readiness-and-blocked-stronger-sentences-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in REQUIRED if not (DOCS / name).exists()]
    if missing:
        raise SystemExit("Missing expected rev0452 docs: " + ", ".join(missing))
    print("rev0452 docs present and accounted for")
