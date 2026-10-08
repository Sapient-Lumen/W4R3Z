from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_DOCS = [
    "2164-resilio-remedy-hardening-attestation-survivor-self-routing-and-automatic-re-closure-fragmentation-evaluation.md",
    "2165-remedy-hardening-attestation-survivor-reroute-contract-sheet-page-resurfacing-carriers-canonical-route-and-reclosure-budget-interface-spec.md",
    "2166-remedy-hardening-attestation-survivor-reroute-review-page-if-a-late-survivor-is-found-can-the-finder-reach-current-truth-without-operator-help-interface-spec.md",
    "2167-remedy-hardening-attestation-survivor-reroute-proof-page-reroute-evidence-supersession-carrier-and-reclosure-sentence-ceiling-interface-spec.md",
    "2168-remedy-hardening-attestation-survivor-reroute-timeline-page-rediscover-route-open-correct-reclose-and-resurface-again-events-interface-spec.md",
    "2169-remedy-hardening-attestation-survivor-reroute-lineage-receipt-page-self-routing-survivor-verdict-reclosure-path-and-blocked-stronger-sentences-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_DOCS if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0504 docs: {missing}")
    print("rev0504 docs present")
