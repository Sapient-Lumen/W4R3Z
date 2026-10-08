# Successor-safe ceremony receipt package claim scopes should ship compact reliance cards

Once the archive already keeps a live package head, status card, verification report, and claim-scope artifact, the next cheap inheritor question is no longer just "what is current?" or "what ran?" but "what may I safely rely on right now?" A compact package reliance card closes that gap without retaining bulky reports or prose.

A useful package reliance card stays small and machine-checkable:
- authoritative manifest reference and active locator digest
- the live status-card, verification-report, and claim-scope inputs it was derived from
- one explicit reliance decision
- the current citable/not-citable result
- the allowed and restricted claim classes that should bound reuse
- the qualifiers that must travel with downstream use
- the exact steps that would justify broader reliance later

In this cloudtainer, the practical distinction is already sharp: the package remains citable for non-runtime statements, the local Python-integrity lane is green, and the Rust lane is still blocked by missing `cargo` / `junest`. Future stewards should not have to reconcile three neighboring artifacts by hand just to determine whether they may rely on identity, citation posture, and freshness claims while withholding runtime claims.

The package head and package catalog should therefore expose one current reliance card beside the live status card, verification report, and claim scope. The status card answers whether the package is citable now; the verification report answers what ran; the claim scope answers which claims remain in or out of scope; the reliance card answers what a downstream steward may safely rely on right now from that combined posture.
