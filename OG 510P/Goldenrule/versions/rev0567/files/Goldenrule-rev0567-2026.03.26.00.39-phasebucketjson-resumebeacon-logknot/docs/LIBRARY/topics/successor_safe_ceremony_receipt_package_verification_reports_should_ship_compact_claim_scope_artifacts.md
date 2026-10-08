# Successor-safe ceremony receipt package verification reports should ship compact claim-scope artifacts

Once the archive already keeps a live package head, status card, and verification report, the next cheap inheritor question is not only "what ran here?" but also "what may I safely say because it ran here?" A compact package claim-scope artifact closes that gap without retaining bulky logs or prose.

A useful claim-scope artifact stays small and machine-checkable:
- authoritative manifest reference and active locator digest
- the live status-card and verification-report inputs it was derived from
- one explicit claim-scope decision
- a short list of allowed claim classes
- a short list of restricted claim classes
- the qualifier text future stewards should carry forward
- the exact follow-up steps needed before broader claims become justified

In this cloudtainer, the practical distinction is already clear: local Python-integrity checks pass, but the Rust lane is still blocked by missing `cargo` / `junest`. Future stewards should not have to infer from that mixed result whether they may talk about contract preservation only, or full engine/runtime verification.

The package head should therefore expose one current claim-scope artifact beside the live status card and verification report. The status card answers whether the package is citable now; the verification report answers what ran; the claim-scope artifact answers which downstream claims that local basis actually supports.
