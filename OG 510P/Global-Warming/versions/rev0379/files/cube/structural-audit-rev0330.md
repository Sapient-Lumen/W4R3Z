# Structural audit rev0330

## Focus
CRC/decon/medical-flow processing after protective-action uptake.

## Corrected risk
Prior revisions made alert receipt and action uptake explicit, but the cube could still let a successful public action imply a successful physical reception/monitoring/decon/medical process. Rev0330 inserts station-level proof boundaries and synthetic queue pressure so that bottlenecks become workorders rather than hidden assumptions.

## Canonical query path
`action uptake -> CRC arrival -> station queue -> contamination screening -> decon -> medical split flow -> registry/follow-up -> CAP/retest/verifier -> public claim gate`.

## Non-canonical surfaces
Public CRC guidance, generic population-monitoring guidance, public capacity rows, synthetic queue results, photos, public AAR paragraphs, and preliminary public statements remain context/no-upgrade or reopen signals only.

## Remaining risk
No real/anonymized June 2026 CRC station logs, instrument QA records, registry exports, hospital handoffs, waste/water packets, or CAP/retest results are loaded.
