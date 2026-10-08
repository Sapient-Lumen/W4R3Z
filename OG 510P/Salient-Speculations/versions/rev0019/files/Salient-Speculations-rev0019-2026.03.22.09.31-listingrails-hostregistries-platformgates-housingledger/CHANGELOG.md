# Changelog

## rev0019 — 2026.03.22.09.31

Added one new canonical branch, broadened the archive into urban housing and platform-mediated lodging governance, and tightened synchronization between the portfolio map and the machine registry.

Added:

- canonical note `025` on listing permission rails, platform verification, and the shift from complaint-driven short-term-rental enforcement toward listing-time legality checks
- new source anchors on Regulation (EU) 2024/1028, the European Agenda for Tourism 2030, New York City's Local Law 18 registration and enforcement materials, NYC's FY2025 registration report, and Spain's rental single-window / registration-number implementation stack

Strengthened:

- the portfolio map now names platform-mediated lodging legality as a twenty-fifth canonical surface
- the pattern language now makes clear that gatekeeping can happen at listing time too, not only at borders, in employment, in healthcare, in payments, or in housing finance
- the research agenda now explicitly asks when registration-number validity and platform-side legality checks become more decisive than after-the-fact inspections for short-term lodging markets

Meta-engineering:

- tightened lint so the `Canon by domain` table in `docs/30-synthesis/portfolio-map.md` must stay synchronized with the registry not only on note number but also on domain label, closing another quiet drift path between human-facing synthesis and machine registry
- regenerated the context pack under the same nine-family taxonomy and updated the followthrough queue plus assumption ledger to reflect the new branch without over-fragmenting the archive
- kept the archive compact by adding one thick urban-lodging note instead of splitting EU registration architecture, national single-window implementation, and city-level platform enforcement into separate notes

Editorial decisions:

- promoted listing permission rails directly into canon because the strongest evidence is no longer merely that cities dislike illegal short-term rentals; it is that registries, platforms, and authorities are increasingly able to stop non-compliant listings before transactions occur
- did not mint a tenth mechanism family; for now `025` is better treated as a strengthening of gatekeepers and permission layers than as a wholly separate branch
- preferred a broad note about platform-mediated lodging admissibility over a narrower note about one city or one national registry, because the deeper pattern is the upstream software governance of occupancy markets


## rev0018 — 2026.03.22.09.12

Added one new canonical branch, broadened the archive into housing-finance governance, and made the registry/context pack explicitly domain- and mechanism-aware.

Added:

- canonical note `024` on insurable collateral, mortgage gatekeeping, and the shift from geography-blind housing finance toward address-level hazard admissibility
- new source anchors on Treasury’s homeowners-insurance dataset and findings, Freddie Mac borrower cost-burden data, OECD’s real-estate and catastrophic-risk framing, Fannie Mae’s flood-insurance origination and servicing requirements, HUD’s flood-insurance authority language, and FHFA’s 2026 insurance-rule rollback

Strengthened:

- the portfolio map now names insurable collateral as a twenty-fourth canonical surface
- the pattern language now makes housing-finance gatekeeping legible as a distinct example of permission layers rather than only a downstream consequence of note `002`
- the research agenda now explicitly asks when property-level hazard and insurability become more decisive than borrower-only qualification for ordinary mortgage access

Meta-engineering:

- added explicit `domain` and `mechanism_family` fields to the speculation registry, making the archive’s machine-readable structure less dependent on inference from titles and paths
- expanded the context-pack generator to emit canon-by-domain and canon-by-mechanism summaries rather than only counts and ids
- tightened lint so every registry item must declare a non-empty domain and a recognised mechanism family, and so `MANIFEST.json` must carry a non-empty summary instead of a null placeholder

Editorial decisions:

- promoted insurable collateral directly into canon because insurance affordability and availability are now clearly feeding back into mortgage eligibility, servicing, and programme design rather than remaining a background cost issue
- did not mint a tenth mechanism family; for now `024` is better treated as a strengthening of the archive’s gatekeeper grammar and as a downstream intensification of territorial repricing in `002`
- preferred one note on housing-finance admissibility over narrower notes on flood insurance, condo master policies, or rural coverage carve-outs alone, because the deeper pattern is the collateral chain becoming hazard-aware


## rev0017 — 2026.03.22.08.52

Added one new canonical branch, broadened the archive into natural-resource governance, and de-staled the archive’s re-entry surfaces while tightening revision-receipt discipline.

Added:

- canonical note `023` on resource telemetry, telemetry-conditioned extraction rights, and the shift from self-declared take toward approved meters, electronic monitoring, and standardised submissions
- new source anchors on California’s large-diversion reporting rules, NSW’s non-urban metering stack, the EU fisheries control and vessel-tracking regime, NOAA’s 2026 Alaska monitoring plan, and WCPFC electronic reporting/electronic monitoring guidance

Strengthened:

- the portfolio map now names resource telemetry as a twenty-third canonical surface
- the pattern language now makes observability and gatekeeping legible in common-pool resource governance too, not only in territory, borders, labour, healthcare, payments, or permitting
- the research agenda now explicitly asks which extraction regimes make approved meters, telemetry-capable devices, or electronic monitoring more decisive than licence paper or annual reports

Meta-engineering:

- refactored `README.md` and `START_HERE.md` to remove stale revision-local guidance and point readers back toward the synthesis and changelog surfaces
- tightened lint so `REVISION-RECEIPT.json` must carry a non-empty summary, move-class list, and counterfactual shadow, reducing the chance of packaging a revision without a real rationale
- regenerated the context pack under the same nine-family taxonomy, broadening the domain map without minting a tenth mechanism family too early

Editorial decisions:

- promoted resource telemetry directly into canon because the pattern is now operational across water and fisheries: lawful take increasingly depends on approved instruments, machine-readable submissions, and monitorable flows rather than on licence possession plus sparse retrospective reporting
- did not create a separate `telemetry-conditioned rights` mechanism family yet; for now `023` is better treated as a strengthening of the archive’s gatekeeper and observability grammar
- preferred a note about extraction rights becoming instrumented over narrower notes on water metering or fisheries monitoring alone, because the deeper pattern is cross-domain governance of common-pool take through telemetry-conditioned admissibility


## rev0016 — 2026.03.22.08.34

Added one new canonical branch, broadened the archive into payment-system governance, and tightened release-manifest discipline.

Added:

- canonical note `022` on payee verification, preflight counterparty validation, and the shift from blind account addressing toward machine-mediated payment admissibility
- new source anchors on the EU instant-payments regulation, the EPC Verification Of Payee stack, the UK’s Confirmation of Payee regime, Pay.UK’s operating model, the Federal Reserve Banks’ payee-name-verification service, and 2026 UK enforcement

Strengthened:

- the portfolio map now names payee verification as a twenty-second canonical surface
- the pattern language now makes gatekeepers, status surfaces, and transaction rails legible in payment initiation too, not only in tax, healthcare, labour, borders, or permitting
- the research agenda now explicitly asks which payment corridors make counterparty validation more decisive than the bare account identifier when money is sent

Meta-engineering:

- tightened lint so `RELEASE-MANIFEST.json` must stay aligned with `MANIFEST.json` on revision, timestamp, slug, and expected bundle filename
- regenerated the context pack under the same nine-family taxonomy, deliberately broadening the domain map without minting a tenth mechanism family
- kept the archive compact by adding one thick payments note instead of splitting instant-payment fraud, sanctions-state refresh, payee directories, and enterprise payment controls into separate notes

Editorial decisions:

- promoted payee verification directly into canon because the stack is no longer merely experimental: EU law now requires pre-authorisation payee checks, the EPC has an operational scheme layer, UK implementation is supervised and enforceable, and the Federal Reserve Banks now market payee-name verification as a live risk-mitigation service
- did not create a separate `financial admissibility` mechanism family yet; for now `022` is better treated as a strengthening of the archive’s gatekeeper, transaction-rail, and status grammar
- preferred a note about money movement becoming counterparty-validated over a narrower note on instant payments alone, because the deeper pattern is not speed by itself but payment initiation moving onto governed preflight checks


## rev0015 — 2026.03.22.08.18

Added one new canonical branch, broadened the archive into built-environment governance, and tightened changelog timestamp discipline.

Added:

- canonical note `021` on permit-ready models, machine-checkable submissions, and the shift from narrative plan packets toward model-governed approval
- new source anchors on Singapore’s CORENET X mandate and overview, the U.S. Permitting Technology Action Plan, the U.S. NEPA and permitting data standard, OGC’s CHEK digital-building-permit work, and the EU BUILD UP toolkit for municipalities

Strengthened:

- the portfolio map now names permit-ready models as a twenty-first canonical surface
- the pattern language now makes gatekeepers legible in the built environment too, not only in borders, healthcare, labour, or energy
- the research agenda now explicitly asks which jurisdictions make machine-checkable BIM/GIS submissions more decisive than narrative plan packets for ordinary approvals

Meta-engineering:

- tightened lint so the top `CHANGELOG.md` timestamp must match `MANIFEST.json`, closing another quiet metadata-drift path
- regenerated the context pack under the same nine-family taxonomy, deliberately broadening the domain map without minting a tenth mechanism family
- kept the archive compact by adding one thick built-environment note instead of splitting municipal permitting, infrastructure review, BIM schemas, and automated code checking into separate notes

Editorial decisions:

- promoted permit-ready models directly into canon because the stack is no longer just speculative: Singapore has concrete mandatory timelines, the U.S. federal government is standardising digital permitting architecture, and European municipal tooling now openly targets automated compliance checks and BIM+GIS maturity
- did not create a separate `model-governed approvals` mechanism family yet; for now `021` is better treated as a strengthening of the archive’s gatekeeper and proof grammar
- preferred a note about the admissible object of approval changing over a narrower note on BIM adoption alone, because the deeper pattern is permits moving onto machine-checkable models rather than merely onto nicer portals


## rev0014 — 2026.03.22.08.03

Added one new canonical branch, broadened the archive into labour-market entry governance, and tightened archive-index ordering discipline.

Added:

- canonical note `020` on work-permission rails, pre-start digital clearance, and the shift from copy-based hiring toward machine-readable onboarding
- new source anchors on the UK digital-ID consultation, the UK digital-ID explainer, the right-to-work supplementary code for digital verification services, current Home Office share-code guidance, USCIS’s remote I-9 alternative procedure, the EU posted-workers e-Declaration push, the Council’s digitalisation press line, and the UK’s proposed extension of right-to-work duties into agency, subcontracting, gig, and platform settings

Strengthened:

- the portfolio map now names work-permission rails as a twentieth canonical surface
- the pattern language now makes gatekeepers legible in labour markets too, not only in borders, healthcare, or energy
- the research agenda now explicitly asks when digital work-right checks and posted-worker declarations become more decisive than the signed contract or photocopied document set

Meta-engineering:

- tightened lint so the `ARCHIVE_INDEX.md` canon and quarantine sections must preserve registry order, reducing another quiet drift path between the human-facing index and the machine registry
- regenerated the context pack under the same nine-family taxonomy, deliberately broadening the domain map without minting a tenth mechanism family too early
- kept the archive compact by adding one thick labour note instead of splitting hiring checks, platform compliance, cross-border worker declarations, and contractor/gig verification into separate notes

Editorial decisions:

- promoted work-permission rails directly into canon because the stack is no longer just aspirational: the UK is actively shifting right-to-work checks toward digital-only evidence routes, digital verification-service rules are being formalised, USCIS already ties remote I-9 checking to a governed E-Verify path, and the EU is actively standardising posted-worker e-declarations
- did not create a separate `labour admissibility` mechanism family; for now `020` is better treated as a strengthening of the archive’s gatekeeper grammar
- preferred a note about labour-market entry moving onto compliance rails over a narrower note on digital ID alone, because the deeper pattern spans employers, platforms, staffing intermediaries, cross-border declarations, and first-shift clearance



## rev0013 — 2026.03.22.07.48

Added one new canonical branch, broadened the archive into healthcare reimbursement governance, and slimmed drift-prone re-entry text.

Added:

- canonical note `019` on prior-authorization rails, machine-readable pre-service adjudication, and the shift from treatment-first care toward software-mediated approval
- new source anchors on CMS’s current prior-authorization rule surface, CMS’s API/implementation-guide page, CMS’s live FAQ and metrics guidance, ASTP’s HTI-4 certification timeline, and CMS’s live WISeR rollout

Strengthened:

- the portfolio map now names machine-readable pre-service adjudication as a nineteenth canonical surface
- the synthesis now states more clearly that some gatekeepers are not only broad front-door permission layers but episode-specific adjudication loops
- the research agenda now explicitly asks when electronic prior authorization becomes decisive care-access infrastructure and whether adjudication surfaces deserve their own branch later

Meta-engineering:

- slimmed `README.md` and `START_HERE.md` so they point back to the synthesis files instead of carrying increasingly drift-prone repeated family lists
- regenerated the context pack under the same nine-family taxonomy, deliberately keeping the archive from minting a tenth mechanism family too early
- kept the archive tight by adding one thick healthcare note instead of splitting clinical workflow, payer APIs, electronic prior authorization, and review-metrics transparency into separate notes

Editorial decisions:

- promoted prior-authorization rails directly into canon because the stack is no longer just aspirational: CMS has active API and metrics requirements, ASTP has provider-side certification criteria, and CMS has a live 2026 model in which pre-service authorisation affects scheduling and turnaround
- did not create an `adjudication surfaces` family yet; for now `019` is better treated as a strengthening of the archive’s gatekeeper and transaction-rail grammar
- preferred a note about treatment access moving onto payer rails over a narrower note on electronic prior authorization alone, because the deeper pattern is care being pre-adjudicated, not merely digitised


## rev0012 — 2026.03.22.07.31

Added one new canonical branch, broadened the archive into mobility governance, and tightened map-discipline between the synthesis table and the canon registry.

Added:

- canonical note `018` on travel preclearance, upstream mobility permission, and the shift from arrival-first border control toward carrier checks, digital authorisation, and pre-screening
- new source anchors on the UK ETA enforcement regime, the live ETA guidance page, the EU Entry/Exit System launch and phased rollout, ETIAS timing and boarding logic, the EUDI Wallet travel manual, and ICAO’s live Digital Travel Credential publication stack

Strengthened:

- the portfolio map now names travel preclearance as an eighteenth canonical surface
- the synthesis now states more clearly that some permission layers become decisive before a journey begins rather than only at the moment of arrival
- the research agenda now explicitly asks which mobility corridors make upstream authorisation and pre-submitted credentials more decisive than the traditional border booth

Meta-engineering:

- tightened lint so the canon table in `docs/30-synthesis/portfolio-map.md` must stay synchronised with the canonical note numbers in `SPECULATION_REGISTRY.json`
- regenerated the context pack under the same nine-family pattern language, keeping the taxonomy stable while broadening the domain map
- kept the archive tight by adding one thick mobility note instead of spinning out separate notes on ETA systems, EES logging, carrier enforcement, or digital travel credentials

Editorial decisions:

- promoted travel preclearance directly into canon because the move is no longer just conceptual: the UK already enforces digital permission to travel, EES is live, ETIAS has a concrete start window, and EUDI/ICAO stacks now treat digital travel credentials as live implementation work
- did not create a tenth mechanism family yet; for now `018` strengthens the gatekeeper and status branches more than it justifies a new umbrella category
- preferred a note about the upstream relocation of border control over a narrower note on passports-in-wallets, because the deeper pattern spans authorisation, boarding, routing, pre-screening, and arrival completion


## rev0011 — 2026.03.22.07.07

Added one new canonical branch, clarified the archive’s scarcity-governance grammar, and tightened revision-metadata lint.

Added:

- canonical note `017` on large-load classes, differentiated utility service, and the shift from generic grid access toward bespoke governance packages for system-shaping demand
- new source anchors on FERC’s large-load rulemaking, FERC’s PJM tariff intervention, PJM load-growth and large-load process material, Pennsylvania’s model tariff, Virginia’s new large-scale-user class, and New York’s fair-share proceeding
- a ninth mechanism family in the pattern language: **allocation surfaces**

Strengthened:

- the portfolio map now names large-load service classes as a seventeenth canonical surface
- the synthesis now distinguishes a scarce bottleneck from the separate question of what class of service a system-shaping participant may enter under
- the research agenda now explicitly asks which jurisdictions first normalize self-supply, flexibility, minimum-take, or collateral obligations for very large energy users

Meta-engineering:

- tightened lint so `MANIFEST.json`, `SPECULATION_REGISTRY.json`, `REVISION-RECEIPT.json`, and `context-pack.json` must stay aligned on revision metadata and meta-claim
- updated `tools/gen_context_pack.py` so the generated context pack derives the archive meta-claim from `docs/30-synthesis/portfolio-map.md` instead of duplicating it by hand
- regenerated the context pack under a nine-family pattern language

Editorial decisions:

- promoted allocation surfaces directly into canon because current power fights are no longer only about scarcity in the abstract but about whether unusually large customers receive ordinary service, special tariffs, self-supply duties, or curtailment-conditioned access
- split **allocation surfaces** from gatekeepers because the decisive question is increasingly not only yes/no admission but the differentiated burden-sharing terms of admission
- did not add a separate quarantine note on housing-finance repricing this round; it still looks like the strongest next second-order extension of the climate-insurance branch, but the large-load class turn was more ripe for canon now

## rev0010 — 2026.03.22.06.39

Added one new canonical branch, sharpened the archive’s runtime-validity grammar, and made context-pack family lists derive from the synthesis file rather than staying hand-maintained.

Added:

- canonical note `016` on status surfaces, live standing checks, and the shift from one-time verification toward runtime admissibility
- new source anchors on EU trusted lists, W3C credential status lists, Peppol metadata discovery and revocability, detergent product-passport customs verification, vLEI role-credential revocation, and EUDI verifier authentication
- an eighth mechanism family in the pattern language: **status surfaces**

Strengthened:

- the portfolio map now names live status as a sixteenth canonical surface
- the synthesis now distinguishes what is proven, what is queried, what relay carries the message, and whether the relevant object is still in force right now
- the research agenda now explicitly asks which sectors first make runtime standing checks an ordinary condition of admissibility

Meta-engineering:

- updated `tools/gen_context_pack.py` so mechanism families are parsed from `docs/30-synthesis/pattern-language.md` instead of being manually duplicated
- tightened lint so bibliography source-anchor IDs must be unique and strictly increasing, reducing another quiet drift vector
- regenerated the context pack under an eight-family pattern language

Editorial decisions:

- promoted status surfaces directly into canon because the same live-standing pattern is now visible across trust services, wallet verification, credential revocation, participant discovery, product-passport customs checks, and organisational-role invalidation
- split **status surfaces** from proof, query, and relay surfaces because the decisive question is not only what can be shown, where evidence comes from, or who carried it, but whether the relevant thing remains valid now
- did not add a separate quarantine note on outage politics or revocation due process; for now those are better tracked as pressure tests and watchpoints on `016`

## rev0009 — 2026.03.22.06.24

Added one new canonical branch, clarified the archive’s trust grammar, and tightened index/registry synchronization.

Added:

- canonical note `015` on relay surfaces, governed intermediary operators, and the shift from bilateral endpoint trust toward certified or registered carriers
- new source anchors on OpenPeppol’s candidate-versus-certified service-provider model, the live certified-provider list, OOTS/eDelivery access points, qualified trust service provider rules and 2026 implementing acts, the EUDI wallet signature flow, and the EU register plus legal status of data intermediation services
- a seventh mechanism family in the pattern language: **relay surfaces**

Strengthened:

- the portfolio map now names governed relay operators as a fifteenth canonical surface
- the synthesis now distinguishes what a system trusts **about a message** from what it trusts **about the operator carrying the message**
- the research agenda now explicitly asks which sectors first make certified relays a real condition of admissibility

Meta-engineering:

- tightened lint so `ARCHIVE_INDEX.md` must stay synchronised with the speculation registry’s note paths, reducing human-facing/machine-facing drift
- regenerated the context pack under a seven-family pattern language
- kept the archive compact by adding one thick canon note rather than a loose cluster on access-point accreditation, QTSPs, data intermediaries, or trust lists separately

Editorial decisions:

- promoted relay surfaces directly into canon because the same governed-intermediary pattern is now visible across e-invoicing, once-only evidence exchange, qualified trust services, wallet signatures, and data intermediation law
- split **relay surfaces** from gatekeepers and transaction rails because the deeper question is not only who is allowed to participate or what rail carries the event, but which operators are trusted to carry high-stakes digital messages at all
- did not add a separate quarantine note on vendor concentration; for now that is better tracked as a pressure test and watchpoint on `015`

## rev0008 — 2026.03.22.06.12

Added one new canonical branch, clarified the archive’s mechanism grammar, and tightened deterministic registry ordering.

Added:

- canonical note `014` on authoritative evidence exchange, once-only administration, and the shift from applicant-assembled packets toward source-side retrieval of current evidence
- new source anchors on the Single Digital Gateway’s Article 14 once-only machinery, the 2025–2026 work programme, OOTS operational material and v2.0 design documents, the European Business Wallet proposal, the Commission’s 2026 EU Inc communication, and OECD material on once-only data-sharing infrastructure
- a sixth mechanism family in the pattern language: **query surfaces**

Strengthened:

- note `013` now states its boundary more clearly: authority credentials answer who may act, while `014` asks when systems stop requiring document presentation and instead retrieve evidence from source systems
- the portfolio map now names authoritative-source evidence exchange as a fourteenth canonical surface
- the research agenda now explicitly asks which procedures actually retire upload-heavy packets when source-side retrieval becomes available

Meta-engineering:

- tightened lint so the speculation registry must remain in deterministic numeric order and so note source-anchor lists must preserve registry source order
- regenerated the context pack under a six-family pattern language
- kept the archive compact by adding one thick canon note plus a synthesis repair rather than a cluster of thinner notes on single-window portals, once-only government, registry quality, or evidence brokers separately

Editorial decisions:

- promoted authoritative evidence exchange directly into canon because the move is now visible in live OOTS infrastructure, maintained specifications, active business-wallet legislation, business-lifecycle onboarding pressure, and OECD-recognised once-only administrative practice
- split **query surfaces** from proof surfaces because retrieving current evidence from the source is not the same move as asking a user or object to present a proof
- did not add a separate quarantine note on private-sector registry querying; for now that looks better tracked as a watchpoint and follow-through test on `014`

## rev0007 — 2026.03.22.05.48

Added one new canonical branch, slimmed an overlap, and tightened note-ID drift checks.

Added:

- canonical note `013` on organisational authority credentials, machine-verifiable representation, and the shift from emailed delegation toward reusable proofs of who may bind or act for a firm
- new source anchors on the revised eIDAS framework, OOTS representation work, the European Business Wallet proposal, the Commission’s Business Wallet policy framing, GLEIF’s vLEI, ISO 5009 role codes, and the FSB’s continuing LEI push in cross-border payments
- a new synthesis link inside proof surfaces: some proof systems increasingly answer not just “who are you?” or “is this good compliant?” but “what organisation are you entitled to act for right now?”

Strengthened:

- note `009` now narrows back toward threshold and eligibility proofs rather than authority-to-act, reducing thematic overlap with the new canon note
- the portfolio map now names organisational authority credentials as a thirteenth canonical surface
- the research agenda now explicitly asks where machine-verifiable agency first replaces emailed delegation and portal-role sprawl

Meta-engineering:

- tightened lint so each speculation ID suffix must match the file-number prefix of its note, reducing another form of silent registry/file drift
- regenerated the context pack under the expanded proof-surfaces framing
- kept the archive compact by adding one thick canon note plus a small refactor rather than several narrower notes on business wallets, e-mandates, company-law digitisation, or LEI adoption separately

Editorial decisions:

- promoted authority credentials directly into canon because the move is now visible across enacted eIDAS changes for legal persons and mandates, Commission architecture work on representation, active business-wallet legislation, global vLEI role credentials, and FSB pressure to extend legal-entity identifiers into transactional infrastructure
- did not split organisational authority into a sixth mechanism family yet; for now it remains a high-value subtype of proof surfaces
- preferred a note about machine-verifiable agency over a narrower note on business wallets because the deeper pattern spans payments, filings, procurement, customs, compliance, and future agentic delegation

## rev0006 — 2026.03.22.05.36

Added one new canonical branch and tightened title-drift discipline.

Added:

- canonical note `012` on title rails, electronic transferable records, and the shift from paper possession toward software-governed control of legally effective originals
- new source anchors on UNCITRAL’s MLETR and enactment status page, the UK Electronic Trade Documents Act, the 2025 UN Convention on Negotiable Cargo Documents, the 2024 UNCITRAL–UNIDROIT Model Law on Warehouse Receipts, Singapore’s MLETR adoption, and DCSA’s interoperable eBL milestone
- a new synthesis link inside proof surfaces: some digital records do not merely prove a fact but allocate control over a right

Strengthened:

- the portfolio map now names digitally controlled originals as a twelfth canonical surface
- the proof-surfaces synthesis now distinguishes evidence-bearing records from legally operative originals whose control substitutes for possession
- the research agenda now asks where title rails become routine commercial infrastructure

Meta-engineering:

- tightened lint so every registry note must have a top-level heading that matches its file number and registry title, reducing silent drift between filenames, headings, and registry entries
- regenerated the context pack under the updated portfolio map
- kept the archive compact by adding one thick canon note instead of several narrower notes on eBLs, warehouse receipts, trade finance, or digital title conflicts

Editorial decisions:

- promoted title rails directly into canon because the move is now live across model law, enacted national legislation, a 2025 UN convention, warehouse-receipt law reform, and interoperable industry transactions
- did not split out a sixth mechanism family yet; for now the archive treats title rails as the strongest current proof-surface subtype rather than inflating the taxonomy too early
- preferred a note about legally effective originals over a narrower note on shipping paperwork, because the deeper pattern spans transport, warehousing, collateral, and trade finance

## rev0005 — 2026.03.22.05.17

Added one new canonical branch and tightened the archive’s predictive discipline.

Added:

- canonical note `011` on transaction rails, e-invoicing, and the shift from after-the-fact accounting toward born-reportable transactions
- new source anchors on OECD’s digital continuous transactional reporting work, OECD evidence on API-heavy tax embedding, EU public-procurement eInvoicing infrastructure, the adopted ViDA timetable, the Commission’s eInvoicing building blocks programme, and the March 2026 consultation on revising the eInvoicing Directive
- a fifth mechanism family in the pattern language: **transaction rails**

Strengthened:

- the portfolio map now names transaction rails as an eleventh canonical surface
- the synthesis now distinguishes between proving a transaction after the fact and generating it natively on standardised rails
- the research agenda now asks when eInvoicing becomes shared infrastructure for customs, finance, procurement, or sustainability reporting

Meta-engineering:

- tightened lint so canonical notes must contain at least three numbered prediction bullets, not merely a predictions heading
- regenerated the context pack under the five-family pattern language
- kept the archive compact by adding one thick canon note rather than several thinner notes on ERP lock-in, tax APIs, or trade-finance reuse

Editorial decisions:

- promoted transaction rails directly into canon because the move is already live across OECD tax-administration strategy, EU procurement infrastructure, the adopted ViDA regime, and the Commission’s explicit reuse plans for customs and sustainability workflows
- did not add a separate quarantine note on software-vendor dependency; that risk seems real, but it is better tracked first as a pressure test on `011`
- preferred a new mechanism family over treating eInvoicing as just another proof-surface anecdote

## rev0004 — 2026.03.22.05.08

Added one new canonical branch and tightened the archive’s watchability discipline.

Added:

- canonical note `010` on object passports, machine-readable goods, and the shift from paperwork toward queryable product-level admissibility
- new source anchors on the ESPR digital product passport regime, the 2025–2030 Commission working plan, toy-safety passport enforcement, UNECE’s passport specification, e-commerce supervision, and the batteries regulation
- a new cross-note watchpoint section on products, trade, and object passports

Strengthened:

- the portfolio map now names machine-readable product passports as a tenth canonical surface
- the proof-surfaces synthesis now explicitly covers goods as well as persons, media, and performance
- the research agenda now asks where product passports become real trade or market-access infrastructure

Meta-engineering:

- tightened lint so each note must carry at least three watchpoint bullets, making the archive’s watchability rule enforceable instead of merely aspirational
- regenerated the context pack under the expanded proof-surfaces framing
- kept the archive small by adding one thick canon note instead of a diffuse cluster on traceability, customs, and circularity

Editorial decisions:

- promoted object passports directly into canon because the move is already live in framework law, sector rollout plans, batteries, toy safety, customs, and international standards work
- kept geolocation-heavy trade compliance in quarantine because it still looks like one important subtype of the broader goods-passport turn, not yet the whole story
- preferred a cross-domain goods-governance note over a narrower sustainability or circularity note

## rev0003 — 2026.03.22.05.04

Strengthened the archive’s internal grammar while adding one new canonical branch.

Added:

- canonical note `009` on threshold credentials, selective disclosure, and the shift from document copies toward wallet-mediated proof
- new source anchors on W3C verifiable credentials, the EU Digital Identity framework, EU wallet service-provider and age-verification use cases, NIST mDL work, NIST’s digital identity model, and the UK’s age-assurance regime
- a new watchpoint section on identity, access, and threshold proofs

Strengthened:

- the portfolio synthesis now treats **proof surfaces** as the more useful umbrella term, replacing the narrower phrase **verification surfaces**
- the research agenda now explicitly tracks recovery, exclusion, and over-requesting risk for wallet-mediated proof systems
- the assumption ledger now records the bet that threshold credentials belong in the same rising-control-surface family as provenance and certification

Meta-engineering:

- tightened lint so each registry note must carry a matching `**Status:**` line and a `## Source anchors` section whose source IDs match the registry entry
- regenerated the context pack under the updated proof-surfaces framing
- kept the archive small by adding a single canon note rather than a cluster of thinner identity notes

Editorial decisions:

- promoted threshold credentials directly into canon because the move is already institutionally real across standards, wallets, online safety, and regulated onboarding
- did not yet add a separate quarantine note on identity exclusion; that risk is important, but better treated first as a follow-through pressure test on `009`
- preferred synthesis repair over thematic sprawl

## rev0002 — 2026.03.22.04.55

Tightened the archive while adding one new canonical branch and one new quarantined extension.

Added:

- canonical note `008` on remote sensing, persistent observation, and the shift from self-reporting toward ambient audit
- quarantined extension `904` on plot-level geolocation becoming a condition of market access in more trade regimes
- `docs/30-synthesis/pattern-language.md` to compress the archive into four recurring mechanism families
- new source anchors on provenance adoption, drone governance, remote sensing, disaster geospatial assessment, catastrophic-risk finance, and geolocation-based trade compliance

Strengthened:

- note `005` now carries two source anchors rather than one
- note `006` now carries two source anchors rather than one
- note `002` and quarantine note `902` now draw on the 2026 OECD catastrophic-risk report

Meta-engineering:

- repaired the archive’s internal inconsistency between the canon rubric and actual source counts
- updated lint to check that canonical notes have at least two source anchors and that registry source IDs resolve in the bibliography
- refined the portfolio meta-claim to include **observability layers**

Editorial decisions:

- promoted observability into the canon rather than letting it remain implicit inside climate, land-use, and disaster notes
- kept the new trade-geolocation move in quarantine because the generalization is important but still under-demonstrated
- preferred structural repair and portfolio compression over adding many thin notes

## rev0001 — 2026.03.22.00.44

Initial archive release.

Added:

- a compact constitutional shell (`README`, `START_HERE`, charter, archive policy, rubric, canon/quarantine method)
- a first broad portfolio map across infrastructure, climate, demography, biology, media, warfare, and education
- seven canonical salient-speculation notes
- three quarantined extensions
- a bibliography grounded primarily in official or institutional sources
- machine-readable continuity surfaces: `MANIFEST.json`, `SPECULATION_REGISTRY.json`, `ASSUMPTION-LEDGER.json`, `FOLLOWTHROUGH-QUEUE.json`, `context-pack.json`, `REVISION-RECEIPT.json`
- lightweight tooling for lint, context-pack generation, and release packaging

Editorial decisions:

- preferred breadth over depth for the first revision
- preferred mechanism sketches and watchpoints over rhetorical flourish
- preserved a quarantine lane instead of over-promoting bolder moves
- kept the archive intentionally small enough to reopen in one sitting
