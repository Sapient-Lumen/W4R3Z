from pathlib import Path

NEW_DOCS = [
    "docs/2032-resilio-remedy-hardening-attestation-successor-preview-commit-binding-snapshot-freshness-and-no-surprise-execution-fragmentation-evaluation.md",
    "docs/2033-remedy-hardening-attestation-successor-preview-commit-binding-contract-sheet-page-reviewed-snapshot-freshness-window-and-execute-if-unchanged-interface-spec.md",
    "docs/2034-remedy-hardening-attestation-successor-preview-commit-binding-review-page-is-this-still-the-same-run-we-reviewed-and-may-it-execute-now-interface-spec.md",
    "docs/2035-remedy-hardening-attestation-successor-preview-commit-binding-proof-page-bound-snapshot-drift-invalidators-and-commit-legitimacy-ceiling-interface-spec.md",
    "docs/2036-remedy-hardening-attestation-successor-preview-commit-binding-timeline-page-preview-refresh-bind-expire-invalidate-and-run-events-interface-spec.md",
    "docs/2037-remedy-hardening-attestation-successor-preview-commit-binding-lineage-receipt-page-bound-preview-freshness-window-and-blocked-no-surprise-sentences-interface-spec.md",
]


def main() -> None:
    root = Path(__file__).resolve().parent
    missing = [p for p in NEW_DOCS if not (root / p).exists()]
    if missing:
        raise SystemExit(f"Missing rev0482 docs: {missing}")
    print("rev0482 materials present")


if __name__ == "__main__":
    main()
