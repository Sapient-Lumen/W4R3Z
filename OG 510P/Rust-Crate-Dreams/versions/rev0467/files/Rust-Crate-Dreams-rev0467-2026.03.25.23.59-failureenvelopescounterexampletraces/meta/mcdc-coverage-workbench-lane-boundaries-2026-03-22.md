# MC/DC Coverage Workbench Kit — lane boundaries (2026-03-22)

## This lane owns

- decision-authority receipts
- construct-support matrices
- independence-pair reports
- caveat-basis receipts
- evidence-lineage receipts
- campaign-scope receipts
- comparison-basis receipts
- qualification-basis receipts
- profile-compatibility receipts
- campaign-policy receipts
- manual-review-debt reports
- MC/DC support-bundle diffs

## This lane does not own

- compiler instrumentation itself
- LLVM profile merging / reporting itself
- generic line/region/branch dashboards
- full assurance-case authoring
- generic test-run scheduling

## Adjacent proposals to keep separate

- **P-0434 Sanitizer Profile & Evidence Kit** owns sanitizer instrumentation/linkage/symbolization/suppression truth.
- **P-0455 Doctest Extraction & Support Contract Kit** owns docs-example execution/support truth.
- **P-0533 Verification Campaign Workbench Kit** owns cross-lane obligation bundling.
- generic coverage/reporting tools may remain substrate, but should not stand in for decision-authority or independence truth.

## Anti-collapse rule

Do not summarize an MC/DC-facing crate as “coverage support” unless you can keep all of these separate:

1. decision authority,
2. construct support,
3. independence evidence,
4. caveat basis,
5. campaign scope,
6. comparison basis,
7. qualification basis,
8. evidence lineage,
9. profile compatibility,
10. campaign policy,
11. manual-review debt.
