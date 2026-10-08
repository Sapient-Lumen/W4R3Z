# 540 — Nuclear emergency preparedness: ingestion lab, embargo/release, water/milk control refactor

## Purpose

Rev0333 adds a BVPS public-only ingestion-pathway proof spine for food, milk, feed, livestock, drinking water, laboratory surge, embargo/release orders, public advisories, and producer/processor claims. It is designed to stop a dangerous shortcut: treating public guidance, a public fact sheet, a sample list, or a lab name as proof that the food/water system was controlled.

## Main rule

Public guidance, public brochures, PAG pages, FDA food-safety guidance, REMM summaries, sampled-item lists, or public archive entries can create a demand, clock, contradiction, hold, or reopen signal. They cannot close local ingestion-readiness evidence.

## Operational chain

`deposition/field trigger -> producer/water-intake inventory -> sampling plan -> sample custody -> lab receipt/QA/QC -> result interpretation -> embargo/hold/release order -> public advisory -> producer/processor/retailer enforcement -> alternate water/food support -> claims/compensation -> CAP/retest/verifier -> public claim gate`

## Why this was added now

Rev0332 hardened source-term, meteorology, field monitoring, and PAR/PAD decision tracing. The next weak link is the post-plume ingestion branch: milk, water, crops, livestock, feed, processors, distributors, private wells, public water systems, and claims. The cube now requires local/anonymized evidence for each operational handoff.

## Non-claim boundary

`REAL_BVPS_PUBLIC_ONLY` remains public-context-only. Rev0333 does not claim Beaver Valley, Pennsylvania, West Virginia, Ohio, any producer network, any public water system, any laboratory, any processor, any county, or any facility is ready, unready, green, failed, passed, certified, safe, sufficient, or closed.
