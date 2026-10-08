---
id: ss-0183-resolution-metrics-become-publishable-status-signals
revision_promoted: pre-rev0180
title: Resolution Metrics Become Publishable Status Signals
constellation:
- resilience-and-continuity
- model-governance
- managed-legibility
- maintenance-and-repair
- market-and-state-capacity
status: dossier
maturity: S3-enforcement-surface
confidence: medium
time_horizon: mixed
domain:
- energy / grid / flexible load
- logistics / cold chain / physical continuity
- compute / AI / data centers
- simulation / forecasting / counterfactual capacity
- identity / credentials / delegated authority
- procurement / purchasing / offtake
- waste / remediation / decommissioning
- insurance / risk transfer / underwriting
bottleneck_type:
- allocation priority
- queue position
- fallback / graceful degradation
- model credibility
- admissible evidence
- state freshness
- source-of-truth precedence
- appealability / redress
- liability-tail custody
- maintenance capacity
- replayability / reconstructability
- underwritability
- small-actor evidence capacity
enforcement_surface:
- audit / attestation / assurance
- procurement / framework contract
- platform eligibility / ranking
- permit / license
- underwriting / insurance renewal
- lending covenant / credit agreement
artifact_type:
- registry entry
- notice
- state label
- certificate / attestation
- replay bundle
lifecycle_stage:
- publish
- rely
- dispute
- correct
- archive
- retire
primary_actors:
- operator
- utility
- public-agency
- model-provider
- buyer
- auditor
- broker
- source-vendor
- insurer
- supplier
failure_modes:
- stale-state
- nonpropagation
- false-match
adversarial_pressure:
- strategic-delay
- overbroad-disclosure
distributional_effect:
- small-supplier-burden
- incumbent-compliance-advantage
migration_status: inferred-rev0183-minimal
migration_note: Metadata was inferred from title, source references, and local keyword context; review before treating as authoritative.
---
# Dossier: Resolution Metrics Become Publishable Status Signals

## Core claim

The important shift is not merely that institutions count complaints, appeals, grievances, or service failures internally. It is that **more of those counts are being pushed onto public comparison surfaces**. Once upheld rates, response-time clocks, complaint volumes, appeal outcomes, maladministration rates, and service-quality ratings are published in comparable tables, dashboards, or scorecards, repair quality stops being a hidden back-office matter and starts acting like a public status signal.

The stronger version of the thesis is not simply that transparency increases. It is that **resolution metrics become publishable status signals**. Organizations increasingly have to live inside public measures of how often they get things wrong, how quickly they respond, how often outside reviewers disagree with them, how many users complain, and whether their repair systems meet a visible quality threshold. Those signals then begin to affect switching, plan choice, procurement, journalism, supervisory attention, and executive prestige.

## Why this belongs in the archive

The archive now has dossiers on human fallback, exception handling, complaint telemetry, and delegated representation. The missing layer was the **external legibility** of repair quality. Complaint telemetry explains how institutions learn from redress traces. This dossier asks what happens when those traces stop being merely internal signal and become part of a public ranking surface.

Financial regulation already makes this concrete. The CFPB’s Consumer Complaint Database lets anyone view complaint trends, maps, narratives, and company responses, and says all published complaint data is freely available to use, analyze, and build on [S365]. It also states that 98% of complaints sent to companies get timely responses and that complaints are generally published after the company responds or after 15 days, whichever comes first [S365]. The CFPB’s complaint-program guidance adds that companies are generally expected to provide complete, accurate, and timely responses within 15 calendar days, and that the Bureau analyzes complaints, company responses, and consumer feedback to assess whether companies are responding well [S366]. That is not just intake and routing. It is a public performance surface for response quality.

The UK financial stack is even more explicit about comparative visibility. FCA says it publishes complaints data every six months, provides firm-specific and aggregate market-level data, and that firms above reporting thresholds are obligated to publish complaint data on their own websites [S367]. Its firm-level tables are sortable by complaints opened and closed, the share closed within 3 days, the share closed after 3 days but within 8 weeks, and the percentage upheld [S368]. The Financial Ombudsman Service then adds another public comparison layer: it publishes quarterly, half-yearly, and annual data on businesses, and in the first half of 2025 its half-yearly data featured 245 businesses with an overall uphold rate of 32% [S369]. Its annual 2024/25 release shared 305,726 new complaints, a 34% overall uphold rate, product-level breakdowns, downloadable data, and a searchable full dataset [S370]. Together these sources imply that complaints handling is becoming something consumers, journalists, firms, and regulators can compare rather than something each firm narrates for itself.

Healthcare is moving in the same direction. CMS says Medicare Advantage and Part D Star Ratings are published on Medicare Plan Finder to help people with Medicare and caregivers compare plans, and that the ratings affect later quality bonus payments [S371]. The published measure set includes **Complaints about the Plan**, **Plan Makes Timely Decisions about Appeals**, and **Reviewing Appeals Decisions** [S371]. That matters because it turns complaint and appeal performance into visible shopping information and payment-relevant status, not just internal compliance data.

Transport and tax administration show the pattern outside classic ombuds terrain. ORR publishes complaint volumes per 100,000 journeys and complaint-response timeliness, including tables for the share of complaints responded to within 10, 20, and 30 working days by operator [S372]. HMRC’s quarterly performance release publishes complaint receipts and the shares fully upheld, partially upheld, and not upheld at both tier 1 and tier 2 [S373]. Once these numbers are routinely public, the institution’s repair lane becomes comparable in a way that used to require insider access.

Housing and ombuds systems push the thesis even further. The Housing Ombudsman publishes quarterly landlord complaint statistics and an annual review; in 2024/25 it upheld 71% of complaints, decided complaints about 419 landlords, and reported that 120 landlords had 75% or more of the complaints about them upheld [S374]. PHSO likewise publishes annual complaint data in CSV and PDF formats, including complaints received and decisions made at each stage in the process [S375]. These are not merely transparency gestures. They create a world in which institutional reputation can be shaped by public repair metrics as much as by mission statements.

A broader public-administration norm is also visible. GOV.UK says service teams must publish performance data, including mandatory KPIs, and specifically identifies service desks, call centres, user support, and back-end systems as data sources for that publication [S376]. That matters because it normalizes the idea that service quality should be made publicly legible. Complaint and appeal metrics then become one especially consequential subset of a larger publish-and-compare governance style.

Put together, these signals support a broader claim: **repair quality is becoming a publishable dimension of institutional status**. The institution that resolves quickly, is upheld less often by independent reviewers, and improves visibly may increasingly enjoy better public trust, lower regulatory suspicion, stronger procurement prospects, and a reputation for seriousness. The institution that performs poorly on visible resolution metrics may increasingly find that its failure can no longer be hidden behind glossy front-end experience.

## Speculative consequences worth tracking

### 1. Complaint handling becomes part of brand and procurement strategy

Organizations may increasingly market and defend themselves not only through product quality or mission, but through visible repair quality: faster response clocks, lower uphold rates, fewer complaint escalations, and stronger improvement trends.

### 2. Independent redress bodies become de facto rankers

Ombuds services, complaint databases, public dashboards, and regulator scorecards may function like quasi-rating agencies for institutional seriousness. Even when they do not publish a formal league table, the underlying data increasingly allows others to create one.

### 3. Internal incentives shift toward reducing embarrassing public metrics

Senior management may care more about complaint taxonomy, first-response speed, reversals, and remedial follow-through once those measures are likely to become visible to the public, media, procurement teams, or ministers.

### 4. Public metrics may reshape where users switch, who gets audited, and who gets funded

Visible repair metrics may increasingly influence plan selection, contract awards, inspections, ombuds attention, regulator scrutiny, and political interventions, especially in sectors where users cannot directly observe service quality in advance.

### 5. Institutions may optimize for the metric as well as the underlying repair quality

Once resolution metrics become status signals, organizations may game categorization thresholds, discourage complaints, or divert disputes before they count. The metric surface may therefore improve real repair in some places while producing performative compliance in others.

## What could falsify or weaken the thesis

- Published complaint and appeal metrics remain too inconsistent across sectors to become genuinely comparable.
- Users, journalists, procurers, and regulators ignore the published data in practice.
- Complaint volumes are too sensitive to awareness, channel design, or reporting rules to function as credible status signals.
- Firms and agencies become better at suppressing complaints than at fixing underlying failures.
- High-profile scorecards remain confined to a few regulated sectors rather than spreading across healthcare, finance, housing, transport, tax, and public services.

## Research queue

- Which published repair metrics travel best across sectors: uphold rate, response time, appeal reversal, complaint rate, or compensation ordered?
- When do public scorecards improve real repair quality, and when do they mainly induce gaming?
- Which users actually act on visible resolution metrics: consumers, caregivers, watchdogs, journalists, ministers, or procurement officers?
- Do public complaint metrics become more powerful when tied to money, such as bonuses, sanctions, or contract renewals?
- How should publishable repair metrics be risk-adjusted so institutions serving harder cases are not mechanically punished?
