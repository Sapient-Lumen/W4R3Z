from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    docs = root / "docs"
    expected = [
        "2014-resilio-remedy-hardening-attestation-successor-action-authorization-quorum-step-up-and-high-risk-gate-fragmentation-evaluation.md",
        "2015-remedy-hardening-attestation-successor-action-authorization-contract-sheet-page-action-class-quorum-gate-and-step-up-proof-interface-spec.md",
        "2016-remedy-hardening-attestation-successor-action-authorization-review-page-may-this-controller-or-controller-set-perform-this-high-risk-successor-world-action-now-interface-spec.md",
        "2017-remedy-hardening-attestation-successor-action-authorization-proof-page-authorization-chain-quorum-satisfaction-and-step-up-ceiling-interface-spec.md",
        "2018-remedy-hardening-attestation-successor-action-authorization-timeline-page-request-challenge-approve-execute-and-expire-action-gate-events-interface-spec.md",
        "2019-remedy-hardening-attestation-successor-action-authorization-lineage-receipt-page-action-authority-quorum-state-and-blocked-stronger-legitimacy-sentences-interface-spec.md",
    ]
    missing = [name for name in expected if not (docs / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0479 docs: {missing}")
    print("rev0479 docs present")


if __name__ == "__main__":
    main()
