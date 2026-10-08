# 539 — Nuclear Emergency Preparedness Dose Assessment, Field Monitoring, and PAR/PAD Decision Trace Refactor — Compact Canon

## Purpose

This revision hardens the upstream radiological decision chain for the Beaver Valley public-only emergency-preparedness pilot. Recent revisions made alert originator authority, alert receipt, protective-action uptake, CRC/decon throughput, and hospital first-receiver flow harder to overclaim. The remaining dangerous shortcut was upstream: a protective action can look well executed even when the emergency classification, source term, meteorology, dose model, field measurements, PAG comparison, or protective-action recommendation/protective-action decision trace is not proven.

Rev0332 therefore separates the chain:

`EAL/classification -> plant/status inputs -> source-term/release estimate -> meteorology -> dose model run -> field monitoring -> PAG/decision threshold crosswalk -> PAR/PAD decision trace -> public message -> action uptake -> CRC/decon/first receiver -> CAP/retest/verifier -> public claim gate`

## Claim boundary

No real Beaver Valley, Pennsylvania, West Virginia, Ohio, county, alerting authority, field team, CRC, hospital, healthcare coalition, or facility readiness or unreadiness claim is made. `REAL_BVPS_PUBLIC_ONLY` remains public-context-only.

A model printout, public PAG page, RASCAL product, public ETE table, emergency-classification label, preliminary meeting sentence, exercise schedule, event notice, public AAR paragraph, field-team training course page, or source ID may create a demand, clock, contradiction, cap, or reopen signal. It cannot close local dose-assessment, field-monitoring, or PAR/PAD decision evidence.

## Minimum upstream packet

A credible local or anonymized packet needs, at minimum, timestamped emergency classification, EAL basis, decision authority, plant-parameter snapshot, radiological release/source-term basis, meteorological stream quality and clock sync, dose model run identifier and input manifest, field-monitoring dispatch/reading/custody chain, PAG-threshold comparison, PAR/PAD decision log, offsite consultation record, public-message linkage, change/retraction lineage, counterevidence path, sensitive-annex split, CAP/retest linkage, and independent verifier.

## P0 defects this revision makes visible

- Dose model output without raw inputs, version/configuration, clock, source term, meteorology, and run lineage.
- PAR/PAD without EAL/classification timing, authority, and offsite decision-maker interface.
- Meteorological data without tower/source health, backup source, gap flag, and clock synchronization.
- Source-term estimate without release path, rate basis, isotope assumption, containment/filtration state, and uncertainty flag.
- Field monitoring dispatched but not linked to readings, instrument QA, worker-dose controls, custody, and dose-model reconciliation.
- PAG threshold cited as generic doctrine rather than mapped to local projected dose and decision clock.
- ETE/route context used as if it were the protective-action decision record.
- Public preliminary findings used as readiness closure.
- Counterevidence from field teams, public behavior, hospitals, labs, or plume/meteorology updates not allowed to reopen a decision.

## New query route

`source clock -> source term/met inputs -> dose-model lineage -> field monitoring -> PAG/PAR crosswalk -> contradiction ledger -> validator -> CAP/retest/verifier -> public claim gate`

## Audit/refactor note

Rev0332 also refreshes source canonicalization and source-ID firebreaks so duplicate source IDs and public-source aliases cannot be counted as independent proof of decision quality.
