from pathlib import Path


NEW_DOCS = [
    "docs/2026-resilio-remedy-hardening-attestation-successor-action-envelope-preflight-preview-and-fail-closed-containment-fragmentation-evaluation.md",
    "docs/2027-remedy-hardening-attestation-successor-action-envelope-contract-sheet-page-target-slice-predicted-effects-and-runtime-guardrails-interface-spec.md",
    "docs/2028-remedy-hardening-attestation-successor-action-envelope-review-page-will-this-execution-stay-inside-the-reviewed-scope-if-it-starts-now-interface-spec.md",
    "docs/2029-remedy-hardening-attestation-successor-action-envelope-proof-page-preflight-diff-expected-effects-and-runtime-ceiling-interface-spec.md",
    "docs/2030-remedy-hardening-attestation-successor-action-envelope-timeline-page-preview-approve-arm-execute-trip-and-abort-events-interface-spec.md",
    "docs/2031-remedy-hardening-attestation-successor-action-envelope-lineage-receipt-page-reviewed-scope-tripped-guardrails-and-blocked-stronger-containment-sentences-interface-spec.md",
]


def main() -> None:
    root = Path(__file__).resolve().parent
    missing = [p for p in NEW_DOCS if not (root / p).exists()]
    if missing:
        raise SystemExit(f"Missing rev0481 docs: {missing}")
    print("rev0481 materials present")


if __name__ == "__main__":
    main()
