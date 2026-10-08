# 969 — Cloudtainer direct-refresh tranche, second merge packet, and no completion by refresh percentage

## One-line thesis

The archive has now moved past the easiest repair traps: generated surfaces are compact, all source keys have a posture, and route overlap has a packet queue. The riskiest remaining failure is subtler: treating a higher direct-review percentage as completion while the remaining unrefreshed rows are exactly the kinds of live, rights-bearing, or remedy-bearing surfaces that can change underneath a polished catalog.

## Why this matters

Rev0770 reduced catalog-triaged source rows from 201 to 167 and proved that one high-overlap note should not be deleted merely because a newer note covers adjacent ground. That was real progress, but it created a new temptation: announce completion because the dashboard is cleaner.

That would repeat the cube's central failure pattern. A coverage percentage is a row. It is not the lived outcome. It does not say whether an eVisa user can prove status at a boarding gate, whether a compensation claimant can supply the demanded evidence, whether a FATF statement has been superseded after the next plenary, whether an identity-proofing update fixed access for low-document users, whether a public AI register entry describes actual use, or whether an ecological-personhood statute has the operational guardians, land-registration steps, funding, and dispute routes needed to act.

This revision therefore keeps two lanes moving at once:

1. **direct-refresh another high-risk source tranche** rather than adding a broad new docket; and
2. **convert another route-retirement candidate into a preservation decision** rather than letting route similarity become deletion pressure.

## Pattern pack

### 1. Refresh the sources whose staleness would mislead an affected person

The refreshed tranche prioritizes rows where stale evidence would directly distort live claims:

- ecological-personhood statutes and guardian pages, where recognition of a river, mountain, lagoon, or basin can be mistaken for functioning guardianship, funding, land-registration, or enforcement;
- status-proof, identity-proofing, and eVisa rows, where a page can describe a route without proving access at the moment a person needs work, rent, benefits, travel, or tax-refund proof;
- AI and automated-decision rows, where a tool page or commitment record can be mistaken for assurance, outcome quality, appeal sufficiency, or live use;
- redress and refund rows, where scheme pages, feedback reports, and closure notices can be mistaken for money reaching the person;
- global-risk, IHR, and FATF rows, where publication cycles and plenary updates can invalidate yesterday's list; and
- procurement, platform, and financial-review rows, where contracts, roadmaps, and audit pages can be mistaken for implementation readiness.

### 2. Name blocked refreshes as blocked refreshes

A direct-refresh pass is not only successful page opens. Sometimes the official source blocks automated retrieval, requires JavaScript verification, or is best confirmed through an official search result. Those rows now move out of catalog-only posture, but their retrieval result remains honest. That is better than leaving them invisible and better than laundering them as clean live checks.

### 3. Keep source-health coverage and source reliance separate

A source can be directly reviewed and still be insufficient for reliance. A statute can be current but not implemented. A report can be found but outdated. A government page can be live but self-serving. A human-rights or crisis page can be recent but not complete. Direct review tells the maintainer what was inspected; it does not prove the claim.

### 4. Turn merge pressure into preservation decisions

The second merge packet reviews note `811`, the scope-verdict packet note. Its nearest newer surface is note `857`, the claim-ledger note, because both are evidence-routing and public-proof objects. But the preservation finding is again conservative: do not delete `811`.

Why: `857` provides a smaller proof unit for individual claims; `811` provides a bundled applied verdict object for real scope judgments. A future ledger can absorb `811` only if it keeps the verdict fields that make applied judgments portable: settled scope holding, frontier threshold, benchmark class, repair path, public-proof class, review clock, and publication state. Without those fields, claim-ledger discipline would make proof smaller but would lose the applied-judgment object.

### 5. Reduce queue noise without hiding candidates

`tools/build_retirement_candidates.py` now removes merge-reviewed source notes from the raw review-only list, not just from the priority queue. That does not delete the rows. It moves them into the reviewed packet table, where a maintainer sees the preservation decision first. This makes the retirement surface more usable without pretending any note is deletion-ready.

## Direct-refresh tranche

This pass moved another tranche of catalog-triaged rows into direct-review posture. The refreshed sources include New Zealand ecological-personhood legal anchors, ArriveCAN procurement and issue-note materials, EU SIS legal texts, Interoperable Europe implementation material, Login.gov IAL2 and roadmap updates, eVisa and FDP public sources, Horizon and infected-blood redress rows, Haiti crisis sources, IHR materials, Canada AIA tooling, Australia automated-decision transparency commitments, IRS account access, Robodebt/Robodebt-response pages, FATF/Treasury rows, and EU AI Act / GPAI guidance pages.

The result is not a declaration that the remaining catalog rows are safe. It is a narrower queue: source-health now separates complete posture, direct review, official-search/blocked attempts, and catalog-only rows.

## Second merge packet

`MP-002-811-to-857` records that note `811` is **not deletion-ready**.

Protected elements include:

- one-sentence settled scope holding for a real polity, proposal, or case;
- explicit separation between settled doctrine and frontier thresholds;
- benchmark class and material stress modifiers;
- repair/intervention path and review clock;
- outward public-proof class and internal evidence-room boundary;
- status date and packet state; and
- anti-scatter rule: no applied judgment by scattered cross-reference.

The future absorption route is not a similarity decision. It would require an explicit claim-ledger or case-packet schema that preserves those fields and shows source/test parity.

## Audit/refactor shipped

- `metadata/source_health.json` converts the next high-risk catalog-triaged tranche into direct-review posture, with blocked/official-search cases named rather than hidden.
- `metadata/route_merge_packets.json` adds `MP-002-811-to-857`.
- `tools/build_retirement_candidates.py` removes merge-reviewed notes from the raw review-only table as well as the raw priority queue.
- `tools/lint_archive.py` now validates route-merge packet source and target integrity against archive files and metadata note numbers.
- `generated/SOURCE_HEALTH.*` and `generated/RETIREMENT_CANDIDATES.*` expose the resulting queue movement.

## Failure modes

- **refresh-percentage theater** — a higher direct-review share is treated as completion even though the riskiest rows still require periodic review.
- **blocked-page laundering** — a direct open failure is rewritten as a clean successful check.
- **statute-as-implementation** — legal personhood or legal text is treated as proof that guardianship, land registration, funding, or remedy works.
- **register-as-use** — an AI, algorithmic, or transparency page is treated as proof of actual safe operation.
- **redress-row substitution** — scheme pages or feedback summaries are treated as proof that payment reached a specific person.
- **claim-ledger overcompression** — small claim records replace the scope-verdict object needed for applied judgments.
- **review-queue clutter** — reviewed merge packets continue appearing as raw candidates, hiding the next actionable route.

## Operational next move

The next pass should continue direct-refreshing the remaining catalog rows, but the priority should now be sharpened: focus first on rows with live dashboards, periodic list updates, status-proof/identity gates, redress clocks, and official pages that previously blocked automated retrieval. In parallel, write one more merge packet from the priority queue and only then consider an actual absorption patch.

## Rule of thumb

No completion by refresh percentage.
