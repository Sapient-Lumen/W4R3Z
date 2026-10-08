# Structural audit — rev0296

Created: 2026-05-30T12:00:00-04:00
Base: rev0295

## Audit focus

Rev0296 audits the benefit-accounting side of the nuclear-positive cube. Prior revisions made nuclear preferred and then added safety, licensing, finance, operations, integrated-energy and fuel-cycle/back-end gates. The remaining risk was that nuclear benefits could be asserted as slogans: low-carbon, firm, safe, land-sparing, health-positive, or reliability-enhancing without a counterfactual.

## Refactor result

The package now includes first-class tables for avoided-emissions accounting, counterfactual dispatch, capacity-value/reliability credit, lifecycle/environmental footprint, fossil-displacement public-health benefit, portfolio comparison, comparative safety and benefit attribution.

## Counts

- Numbered markdown files: 469
- Index rows: 469
- Registered sources: 851
- Service floors: 584
- Nuclear service floors: 169
- Nuclear assurance gates: 100
- Nuclear gate evaluations: 16900
- System-benefit gap rows: 2704
- SQLite import/view errors: 0

## Design decision

Nuclear remains favored by default in relevant clean-firm and system-benefit contexts, but rev0296 prevents automatic maturity upgrade. The cube now requires evidence for what nuclear displaces, which system value it provides, which lifecycle boundary is used, whose public-health burden is reduced, and whether the benefit is double counted.
