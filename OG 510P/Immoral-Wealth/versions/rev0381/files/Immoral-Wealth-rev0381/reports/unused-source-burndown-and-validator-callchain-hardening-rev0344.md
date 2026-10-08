---
revision_current: rev0355
status: active_report
claim_kind: audit_refactor
---

# Unused-source burndown and validator callchain hardening — rev0355

## What was risky

After source-alias canonicalization, 45 non-alias sources still had no active case lineage. Several were high-value official or dataset anchors, so keeping them unused made the source ledger look richer than the case/evidence layer actually was.

A second risk was validator drift: the rev0343 live-doc alias check existed but was not called from `main()`. Rev0344 repairs that omission and adds a self-audit for recent invariant calls.

## What changed

- Formerly unused non-alias sources before repair: **45**.
- Source bindings added: **45**.
- Active scoreboards touched: **30**.
- Cases touched: **30**.
- Formerly unused non-alias sources after repair: **0**.
- Evidence edges after rebuild: **5407**.

## Substantive effect

The repair binds measurement, tax transparency, workplace power, place finance, household-credit, retirement, land-title, gender/family-property, remedy-access, and score-mediated-exclusion sources to the actual fields and gates they support. No verdicts were relaxed and no new cases, sources, or schema fields were added.

## Validator hardening

The validator now calls the rev0343 alias invariant and adds a rev0344 invariant requiring all target sources to remain active in source/evidence lineage while recent checks remain in the callchain.
