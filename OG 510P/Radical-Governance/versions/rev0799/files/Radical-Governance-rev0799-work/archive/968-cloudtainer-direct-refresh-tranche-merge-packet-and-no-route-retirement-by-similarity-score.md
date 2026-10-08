# 968 — Cloudtainer direct-refresh tranche, first merge packet, and no route retirement by similarity score

## One-line thesis

The riskiest unfinished work after rev0769 was not another policy domain. It was the gap between catalog-triaged source posture and actual direct refresh, plus a retirement queue that could still tempt maintainers to treat lexical overlap as safe deletion. This revision refreshes the highest-consequence catalog rows and turns the top retirement candidate into a preservation packet rather than a deletion shortcut.

## Why this matters

Rev0769 honestly separated complete source posture from direct verification. That was necessary, but it left a new operational queue: 201 catalog-triaged source rows still needed direct refresh before they should be used as current evidence. The riskiest rows were not the obscure stable background texts. They were live or implementation-clock surfaces that carry public-service consequences: SIS alert/data and access-rights pages, eVisa evidence, algorithmic-transparency records, HR/pay transition pages, public AI/chatbot evidence, redress clocks, and identity or tax-refund access pages.

The second risk was route retirement. `generated/RETIREMENT_CANDIDATES.*` had become useful enough to identify overlap, but a similarity score is a dangerous object. It can identify where to look; it cannot prove that an old note's case grammar, affected-party tail, source posture, opposition brief, or test value has been preserved.

This pass therefore does two concrete things:

1. direct-refreshes a high-priority tranche of catalog-triaged sources; and
2. adds the first route merge packet, for note `719`, proving why the top candidate is **not** deletion-ready even though it overlaps newer surfaces.

## Pattern pack

- **Direct-refresh before reliance.** Catalog posture can route review, but high-consequence claims should prefer a refreshed official page, official search result, primary text, or clearly dated scrutiny source.
- **Preservation packet before retirement.** A route-overlap score can nominate a merge review, but only a packet can identify which tests, source posture, affected-party tails, opposition briefs, and operational grammar must survive.
- **Queue work without fake closure.** Moving a row from catalog triage to direct review is progress; leaving unresolved rows visible is also progress when the alternative is source-health theater.
- **No deletion by low dependency.** A zero-dependency note may still carry reusable field grammar. Low dependency lowers merge-review cost; it does not establish deletion safety.

## Direct-refresh tranche

The refreshed tranche targets sources that can distort live claims if stale:

- **SIS and border/database waists.** The European Commission SIS overview, alerts/data page, access-rights page, EDPS SIS page, eu-LISA SIS page, and EUR-Lex SIS return-alert regulation now carry direct-review posture. These sources can show the system frame, alert/data categories, access rights, oversight lane, and legal text; they still do not prove a particular national alert is lawful, timely, corrected, or contestable.
- **eVisa and status-proof surfaces.** The House of Commons Library briefing, parliamentary evidence, GOV.UK eVisa account-creation data, and methodology note now carry direct-review posture. These sources can show migration/status-proof risk and operational statistics; they still do not prove that a person can work, rent, travel, claim benefits, or board transport at the moment of need.
- **AI and staff-copilot records.** FCDO Correspondence Triage, DBT Redbox, DBT AI governance/Redbox narrative, GOV.UK Chat engineering, and the civil-service AI productivity trial now carry direct-review posture. These sources can show tool description, phase, human review claims, productivity claims, or implementation narrative; they do not prove accuracy, proportionality, service quality, or appeal sufficiency.
- **Platform and supplier dependency surfaces.** Canada HR/pay transformation, FedRAMP, GOV.UK One Login, Login.gov rules, NHS FDP information governance, Hansard FDP debate, EMSA THETIS, and FATF mutual-evaluation materials now carry direct-review posture. These sources can show a program, register, standard, inspection database, privacy/IG frame, or scrutiny surface; they do not prove readiness, exit capability, user continuity, or repaired public power.
- **Redress and deadline clocks.** IBCA support-payment transition, infected-blood compensation updates, Post Office Horizon redress costs, TAS ERC backlog/claim-period material, and tax identity-verification material now carry direct-review posture. These sources can show scheme route, deadline, cost, backlog, or burden; they do not prove money reached a specific person.

The point is not to make every refreshed source authoritative. The point is to reduce the number of high-consequence rows where the archive only knew the catalog role but had not directly refreshed the page or official search result.

## First merge packet

The top retirement priority candidate was note `719`, which defines case packets for lane-typed government fields: case object, intake, triage, state model, clocks, notice, lineage, and the rule against government by unofficial casework. The nearest newer surfaces were `857` claim ledgers and `858` the applied Interoperable Europe case.

The merge packet reaches a deliberately conservative holding:

**Do not delete `719`.**

Why: `858` applies a procedural digital-waist case to interoperability assessments, and `857` makes claim evidence more granular, but neither fully preserves `719` as a reusable field-level case constitution across housing, permits, care, and other live service fields. The protected elements remain operationally useful: receipt versus acknowledgement versus activation, wrong-door and incompleteness states, typed closure states, clock pause/resume rules, predecessor-successor lineage, and ordinary-service rework versus challenge/appeal boundaries.

So the retirement queue made progress, but not by deleting. It converted a route-mass suspicion into a preservation instruction: `719` can be absorbed later only if a future route explicitly preserves those protected elements and records source/test parity.

## Audit/refactor shipped

- `metadata/source_health.json` moves the directly refreshed tranche out of catalog-backfill status and marks the review method honestly.
- `tools/build_retirement_candidates.py` now reads `metadata/route_merge_packets.json` and separates merge-reviewed candidates from raw priority candidates.
- `generated/RETIREMENT_CANDIDATES.*` now reports a reviewed merge packet as a distinct state: not deletion-ready, not ignored, and not left as a vague overlap row.
- `metadata/route_merge_packets.json` records the first preservation packet, `MP-001-719-to-857-858`.

## Failure modes blocked

- **Freshness laundering:** saying a current-looking register row proves the operating service works.
- **Direct-review theater:** counting catalog posture as if it were a direct page or official-search refresh.
- **Similarity-score deletion:** letting lexical/tag overlap retire a note without preserving its protected operational grammar.
- **Merge avoidance:** keeping every route forever because deletion is risky, instead of writing bounded preservation packets.
- **Redress-row substitution:** treating scheme pages, cost tables, or claim-period notices as proof that affected people received money.
- **Status-proof substitution:** treating eVisa or SIS source availability as proof that a person can exercise a right at the point of need.

## Operational next move

The next pass should continue direct-refreshing catalog-triaged rows, but should also write another merge packet from the zero-dependency queue. The best maintenance path is now a two-lane rhythm: refresh the most volatile/high-consequence source rows, and convert one route-overlap candidate at a time into a preservation decision.

## Rule of thumb

No route retirement by similarity score.
