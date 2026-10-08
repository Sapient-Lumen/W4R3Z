
### Audit continuity anchors

- rev0059: MulliganKeepRecord remains the typed record for bottoming cards after keeping.
- rev0041 roadmap update: sacrifice-as-cost remains a cost component that must preserve rollback ordering.

# rev0191 roadmap delta — discard costs before wider registry

Completed now: discard-as-cost is no longer only a generic discard plus zone move. The paid-action spine carries a typed `DiscardCostPaymentRecord` through declaration, placement, committed transaction, and `PaidActionTransactionJournal.v6`.

Highest-risk next work: consolidate sacrifice/discard/tap/counter/life costs into a reusable staged nonmana cost-plan kernel. The current rev0191 seam is intentionally vertical and tested; the remaining risk is code duplication as more payment kinds join the same all-or-nothing transaction boundary.

Avoid: broad card-count import without semantic status gates. Parsed text, known keywords, implemented costs, transaction coverage, and fuzz coverage should stay separate signals.
