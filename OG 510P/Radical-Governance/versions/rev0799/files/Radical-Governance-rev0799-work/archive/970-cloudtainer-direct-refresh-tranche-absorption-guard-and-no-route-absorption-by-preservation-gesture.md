# 970 — Cloudtainer direct-refresh tranche, absorption guard, and no route absorption by preservation gesture

## One-line thesis

The riskiest remaining work is now concentrated in two places: live or consequence-bearing source rows that still depend on catalog posture, and route-retirement candidates that can be reviewed forever without ever producing an absorption-ready successor. This revision keeps direct-refresh work moving while adding a stronger merge-packet guard: a preservation packet must say what a future absorption patch would have to preserve, not merely why deletion is unsafe.

## Why this matters

Rev0771 moved source-health direct review above eighty percent and added a second merge packet. That was useful, but it also created a new maintenance trap. The archive can now look mature by showing high direct-review coverage, zero generated-surface warnings, and multiple merge-reviewed candidates, while the hardest rows and routes remain unfinished.

That would be a softer version of the same failure the cube studies everywhere else. A completed percentage is not continuity. A merge packet is not absorption. A source found in a catalog is not current reliance. A redress page is not payment. A status page is not point-of-need access. A statute is not implementation. A transport case is not the whole service-home doctrine.

This pass therefore keeps three work lanes tied together:

1. refresh the next highest-risk source-health tranche;
2. convert the next route-retirement candidate into a preservation decision; and
3. make merge packets carry explicit absorption requirements so future maintainers can either write a real absorption patch or leave the older route alone.

## Pattern pack

### 1. Prioritize source rows where stale evidence would mislead a user, claimant, operator, or reviewer

The refreshed tranche starts with rows whose staleness can change the practical answer to a live question:

- Medicaid renewal and unwinding strategies, where an official bulletin or policy deck may still matter but cannot prove that a state completed a person's renewal correctly;
- Detroit and LAHSA fiscal/audit materials, where resolutions and audits can show governance action or failure but not whether services reached residents;
- Taranaki, Atrato, Mar Menor, Ganga/Yamuna, and OECD water-governance materials, where legal or governance recognition can be mistaken for functioning guardianship, monitoring, funding, or enforcement;
- Universal Credit, appointee, representative, IRS authorization, Medicare/Marketplace appeal, and One Login status pages, where the public row is a route, not a guarantee that a claimant can act through it;
- Paris MoU, FATF, IHR, UN, and port-state-control materials, where list or legal-text currentness matters because periodic updates change reliance; and
- Post Office, Robodebt, FDP, GOV.UK Chat, ICO, NHS, HMRC, and GOV.UK materials, where program pages and decision notices can be mistaken for repaired money, safe data use, or working access.

### 2. Treat direct refresh as a queue movement, not a reliance license

A source moved out of catalog triage is not automatically strong. The archive should preserve blocked and partial refresh states. A direct PDF open, official search result, or indexed page proves a route was found; it does not prove page-level facts, implementation, or lived remedy unless the relevant claim explicitly binds to the right excerpt, date, and user outcome.

That is why this revision marks several PDF or official-search rows as needing follow-up capture rather than laundering them into clean reliance. It is better to reduce catalog-only posture honestly than to claim full source fitness.

### 3. Merge packets should name the absorption test

A merge packet that only says "do not delete" can become another registry object. It reduces deletion risk but does not reduce route mass. The next useful step is to make every packet answer a harder question: **what would a real absorption patch have to preserve?**

That is now an explicit field in `metadata/route_merge_packets.json`. The field does not authorize deletion. It creates a checklist for future absorption work: protected fields, successor route, source/test parity, redirect path, and the distinction between generic doctrine and applied example.

### 4. Service-home doctrine is not absorbed by a transport case

The third merge packet reviews note `615` against note `849`. The overlap is real: both concern shared territorial power, service delivery, metropolitan authority, fiscal risk, and oversight. But the absorption is not real.

Note `849` is a useful London transport case. Note `615` is a general service-home rule for shared territorial government: authority/operator/regulator separation, territorial service maps, commissioning or direct-operation instruments, operator-chain disclosure, near-to-person front doors, complaint handoffs, and failure-takeover duties.

A London transport packet cannot retire the generic service-home doctrine unless the successor route preserves that grammar for other shared services too: water, waste, emergency communications, specialist social services, administrative access, and regional infrastructure.

### 5. Keep route reduction tied to actual absorption patches

The archive should eventually shrink. But shrinking should come from successful absorption, not deletion pressure. A note becomes retireable only after:

- a successor route is named;
- protected elements are preserved there;
- source and test coverage are carried forward;
- generated audit surfaces reflect the move;
- the old route has a clear redirect or lineage note; and
- the protected affected-party, opposition, and operational tails survive.

Until then, the safer status is **merge-reviewed, keep until absorption patch**.

## Direct-refresh tranche

This revision moves another high-priority tranche of catalog-triaged source rows into direct-review or explicit follow-up-capture posture. The tranche includes Medicaid unwinding guidance, Detroit budget-resolution material, LAHSA audit routes, Taranaki land-registration guidance, Universal Credit official statistics, IHR text and Joint External Evaluation material, OECD and ecological-personhood rows, FATF and Paris MoU rows, IRS and GOV.UK representative-access rows, NHS FDP and ICO rows, Post Office and Robodebt redress rows, and GOV.UK Chat / HMRC / flood and river-basin governance rows.

Several rows remain intentionally cautious. PDF rows, blocked pages, and official-search-indexed documents can move out of catalog-only posture while still saying they need page-level capture for exact quotation or reliance. That is forward motion without pretending that source work is done.

## Third merge packet

`MP-003-615-to-849` records that note `615` is **not deletion-ready**.

Protected elements include:

- generic authority / operator / regulator / commissioner separation;
- territorial service map showing local, shared, direct-operated, and state/national lanes;
- lawful commissioning, franchising, direct-operation, or shared-service instruments;
- public front doors and complaint handoffs near enough for ordinary people to use;
- common operator-chain service constitution for contractors, concessionaires, and municipal operators;
- continuity, reserve-capacity, failure-takeover, and substitution duties; and
- upgrade trigger from loose shared-service cooperation to real service government.

A future absorption patch must create or designate a successor route that preserves that generic service-home grammar. Note `849` can remain a London transport instance, but it cannot by itself carry the generic rule.

## Audit/refactor shipped

- `metadata/source_health.json` moves another priority tranche out of catalog-only posture and marks PDF/official-search cases honestly.
- `metadata/route_merge_packets.json` adds `MP-003-615-to-849` and adds `absorption_requirements` to route-merge packets.
- `tools/lint_archive.py` now requires every route-merge packet to include non-empty absorption requirements.
- `tools/build_retirement_candidates.py` exposes absorption-requirement counts in the generated retirement audit, so preservation packets become operational work items rather than narrative holds.
- `generated/SOURCE_HEALTH.*` and `generated/RETIREMENT_CANDIDATES.*` expose the narrowed direct-refresh queue and the expanded merge-reviewed table.

## Failure modes blocked

- **percentage completion** — direct-review coverage is high enough to look complete while the remaining rows are exactly the rows that need careful reliance boundaries.
- **PDF laundering** — a located PDF becomes a claimed fact without page-level capture, date, and excerpt discipline.
- **service-home overcompression** — a strong applied transport case is allowed to absorb generic shared-service governance.
- **merge-packet bureaucracy** — preservation packets accumulate without ever naming what an absorption patch would require.
- **route-retirement theater** — a note is declared merged because it has a similar neighbor, not because protected grammar moved.
- **continuity-by-source-row** — an official page is treated as proof that a claimant, resident, patient, operator, or ship can obtain the promised outcome.

## Operational next move

The next pass should either direct-refresh another tranche of the remaining catalog rows or write an actual absorption patch for one reviewed packet. The highest-value absorption patch is likely not deletion; it is a successor module that can show where one protected grammar now lives. Until that exists, route mass is a maintenance cost, but premature retirement is a worse evidentiary failure.

## Rule of thumb

No route absorption by preservation gesture.
