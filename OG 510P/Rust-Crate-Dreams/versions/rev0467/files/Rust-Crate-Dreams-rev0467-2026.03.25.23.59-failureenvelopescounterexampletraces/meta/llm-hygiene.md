
## Added 2026-03-25 (467) — failure-envelope hygiene before synthesis

Future passes should not write “disproved”, “broken”, “unsafe to use”, or “no longer supported” until they first ask:
- what exact scenario failed,
- which witness is decisive,
- what smaller claim still survives,
- what guarantee is withdrawn,
- and what cheapest honest replay or rerun could clear the failure.

Before summarizing a lane as falsification-ready, create or point to:
1. a failure envelope,
2. a counterexample trace,
3. a degraded-claim note,
4. a withdrawn-guarantee note,
5. a repair-hint slice,
6. and a refutation / supersession bridge.

Do not silently flatten:
- one tuple failure into total ecosystem failure,
- hosted-vs-local mismatch into runtime breakage,
- unresolved challenge into full refutation,
- or repaired cases into “nothing happened.”

## Added 2026-03-25 (466) — assurance-case hygiene before synthesis

Future passes should not write “trustworthy”, “ready”, “supported”, or “recommended” until they first ask:
- what exact claim is being made,
- which witnesses are decisive,
- what warrant turns those witnesses into the claim,
- what open challenges and non-claims remain,
- and whether the case is inherited, downgraded, reset, or superseded.

Before summarizing a lane as assurance-ready, create or point to:
1. a claim catalog,
2. an assurance case,
3. a witness bundle,
4. a challenge register,
5. a non-claim note,
6. and an inheritance / supersession bridge.

Do not silently flatten:
- witnesses into claims,
- policy verdicts into justification,
- inherited cases into fresh cases,
- or unresolved challenges into “good enough.”

## Added 2026-03-25 (465) — delta-program hygiene before synthesis

Future passes should not write “cheap to update”, “easy to keep current”, or “only a small rerun is needed” until they first ask:
- what class of change occurred,
- what prior conclusions still carry forward,
- what the minimum honest rerun slice is,
- what forces confidence reset,
- and how supersession is represented.

Before summarizing a lane as cheaply updatable, create or point to:
1. a change-intake object,
2. a change classification,
3. a carry-forward decision,
4. a supersession diff,
5. and a confidence-reset record.

Do not silently flatten:
- “something changed” into one review meaning,
- carry-forward into full approval,
- policy-only edits into evidence refresh,
- or unknown change classes into optimistic reruns.

## Added 2026-03-25 (464) — renewal-program hygiene before synthesis

Future passes should not write “maintainable”, “continuously trusted”, or “easy to keep current” until they first ask:
- what the renewal unit is,
- which triggers are time-based versus event-based,
- what the cheapest honest rerun slice is,
- who owns escalation,
- and how stale / superseded / retired states are represented.

Before summarizing a lane as sustainably maintainable, create or point to:
1. a renewal program,
2. a freshness budget,
3. a renewal ticket or queue object,
4. a stewardship summary,
5. and a supersession / retirement record.

Do not silently flatten:
- “reviewed once” into “stays reviewed”,
- cheap freshness checks into full reapproval,
- grace into active standing,
- or superseded into disappeared.


## Added 2026-03-25 (463) — review-packet hygiene before synthesis

Future passes should not write “this crate is ready for adoption” until they first ask:
- what exact packet another reviewer reads,
- which evidence slice is decisive,
- where signoff history lives,
- how overrides expire,
- and when the packet goes stale.

Before summarizing a top-lane implementation shape, create or point to:
1. a review packet,
2. a maintenance summary,
3. a signoff ledger,
4. an override register,
5. and a reapproval plan.

Do not silently flatten:
- raw receipts into reviewed packets,
- policy verdicts into human signoff,
- active overrides into invisible local state,
- or stale packets into current truth.


## Added 2026-03-25 (461) — evidence-interchange hygiene before synthesis

Future passes should not write “the crate exports JSON” or “the crate integrates with other tools” until they first ask:
- what reviewed bundle is being exchanged,
- what raw receipt stream sits beneath it,
- what profile vocabulary is in force,
- what verifier checks compatibility,
- and what schema/version policy governs reuse.

Before summarizing a top-lane exchange posture, create or point to:
1. a profile manifest,
2. a reviewed exchange bundle,
3. a raw receipt stream,
4. a verifier result,
5. and a compatibility policy.

Do not silently flatten:
- crate-local JSON into a cross-tool contract,
- raw receipts into reviewed bundles,
- profile names into actual qualification,
- or bundle parsing into semantic compatibility.


## Added 2026-03-25 (460) — conformance-claim hygiene before synthesis

Future passes should not write “supported”, “works on”, “debuggable”, or “ready” until they first ask:
- which support dimension is being claimed,
- which evidence tier the claim is at,
- which profile or matrix the claim covers,
- which basis generated the claim,
- and what the archive explicitly refuses or leaves unknown.

Before summarizing a top-lane support posture, create or point to:
1. a tier vocabulary,
2. a claim envelope,
3. a raw receipt stream,
4. a human support summary,
5. and a recheck plan.

Do not silently flatten:
- declared into built,
- built into replayed,
- replayed into exercised,
- or any of those into domain qualification language.

## Added 2026-03-25 (459) — package-topology hygiene before synthesis

Future passes should not write “this should be a crate” until they first ask:
- who runs it from a CLI,
- who embeds it as a library,
- who reviews its packet/schema types,
- what substrate churn should stay behind adapters,
- and what corpus defends the meaning.

Before summarizing a top-lane implementation shape, create or point to:
1. a package-family plan,
2. a schema boundary,
3. an adapter boundary,
4. and a corpus boundary.

Do not silently flatten:
- CLI workflows into core semantics,
- packet types into CLI implementation details,
- docs.rs / crates.io / Cargo import quirks into stable packet meaning,
- or scenario corpora into afterthought examples.


## 2026-03-25 product-blueprint / state-file reminder

When the archive is revisited:

1. read `archive-state.json` and `llms.txt` before sampling older files;
2. do not describe a top lane as practically build-worthy until you can state its `0.1`, `0.3`, and `1.0` meanings separately;
3. do not treat a machine-readable report as if it were already an acceptance packet for another team;
4. do not imply handoff-grade maturity unless packet semantics and supersession rules are both explicit;
5. prefer leaving behind one tighter product blueprint or schema family over writing another broad narrative of ecosystem desire.

Also:
- use `templates/product-blueprint-card.template.md` when a pass changes what a top lane should look like in practice;
- and update `archive-state.json` whenever the current frontier stack or current practical queue changes.

## 2026-03-25 promise-bundle / llms.txt reminder

When the archive is revisited:

1. read `llms.txt` first if the reader is a machine agent or LLM;
2. do not describe a crate as “worthy” until you can state its **promise bundle** or **support envelope** in one compact block;
3. do not treat raw machine-readable artifacts as if they already formed a downstream product offer;
4. do not reopen a broad sector lane unless it beats the current control-plane frontier on receiver value, bounded first release, and handoff durability;
5. distinguish **facts**, **inferences**, and **open questions** explicitly in every materially new pass.

Also:
- use `templates/promise-bundle-card.template.md` when a pass changes what a lane should provide another team;
- and update the latest machine-facing navigation hints whenever the frontier interpretation changes.

## 2026-03-25 operating-surface / scenario-corpus reminder

When the archive is revisited:

1. do not describe a crate as “practically ready” until you can say **who runs it, when it reruns, and what artifact the rerun emits**;
2. do not treat a clean artifact family as if it already proved a **supportable operating loop**;
3. do not upgrade a claim without naming at least one **scenario corpus** that exercises both success and refusal behavior;
4. do not let broad synthesis or polished wording outrun the imported evidence, especially on support or operations claims;
5. prefer deepening `meta/frontier-operating-surface-2026-03-25.md` and `meta/scenario-corpus-and-recheck-discipline-2026-03-25.md` over another wide ecosystem narrative when context is already broad.

Also:
- use `templates/operating-model-card.template.md` when a pass changes how a lane should work in practice;
- and update the memory spine whenever operating model, scenario corpus, or practical build order changes.

## 2026-03-25 continuity-ring / claim-upgrade reminder

When the archive is revisited:

1. do not describe a crate as “worthy” until you can say how its value survives **rechecks, drift, and handoff over time**;
2. do not treat a visible ecosystem surface as if it were already a **crate-authored support promise**;
3. do not upgrade a claim without naming whether it moved from observed surface, to inference, to imported contract, to composite crate contract;
4. do not reopen a broad umbrella lane unless it beats the current frontier on **continuity value**, not just novelty;
5. prefer deepening `meta/frontier-continuity-ring-2026-03-25.md` and `meta/frontier-receiver-value-planes-2026-03-25.md` over another wide ecosystem narrative when context is already broad.

Also:
- use `templates/continuity-contract-card.template.md` when a pass changes how a lane should survive time and drift;
- and update the memory spine whenever claim level, practical build order, or continuity scope changes.

## 2026-03-25 adoption-contract / source-basis reminder

When the archive is revisited:

1. do not describe a crate as “worthy” until you can name its **receiver**, **repeated workflow**, **portable artifact family**, **first useful release**, and **refusal boundary**;
2. do not materially rerank the frontier without leaving behind a **source-basis note** that distinguishes fact, inference, and open question;
3. do not cite community ecosystem hubs as if they were official status authorities;
4. do not reopen a broad umbrella lane unless it beats the current frontier on adoption-contract completeness, not just excitement;
5. prefer deepening `meta/frontier-mvp-stack-2026-03-25.md` over another territory narrative when context is already broad.

Also:
- use `templates/source-basis-note.template.md` when a pass changes reasoning materially;
- and update the memory spine whenever source-basis, worthiness bar, or build order changes.

## 2026-03-25 delivery-card / buildability reminder

When the archive is revisited:

1. do **not** rank only by “how important the problem sounds”;
2. do **not** rank only by “what seems easy to spec”;
3. separate **need** from **buildability now**;
4. if a pass changes the frontier, leave behind at least one practical artifact (delivery card, plan, schema, scenario, or checklist);
5. before promoting a proposal, answer explicitly what the crate provides other people in its first useful release.

Also:
- do not widen sector coverage at the cost of narrowing the practical front;
- do not reopen the generic “web stack”, “GUI savior”, “ML umbrella”, or “enterprise platform” lanes unless a sharper seam escaped the existing frontier;
- use `templates/frontier-delivery-card.template.md` and `templates/archive-pass-checklist.template.md` when a pass risks becoming too narrative.

## Added 2026-03-25 (452) — territory-scan hygiene before synthesis

Future passes should not write “Rust is missing X” until they first ask:
- is X a real artifact seam, decision seam, boundary seam, or evidence seam?
- does the sector already have a strong umbrella/community center?
- would the first useful release be narrow and honest?
- and did the scan actually beat the current control-plane frontier?

Before promoting a new top-level lane, create or point to:
1. a territory comparison,
2. a worthiness test,
3. and an elimination/defer list.

Do not silently flatten:
- sector fragmentation into proof that a new umbrella crate should exist,
- community energy into evidence that the right missing contribution is broad,
- or a compelling use case into a maintainable crate plan.

## Added 2026-03-24 (451) — gap and closure hygiene before synthesis

Future passes should not write “more evidence is needed” until they first ask:
- which exact gate is still unsatisfied,
- which packet exposed that gap,
- whether the gap is automatable, manual-artifact, manual-judgment, or blocked-upstream,
- what smallest bounded campaign is in scope,
- and what would count as partial closure versus full closure.

Before summarizing a stronger posture, create or point to:
1. an `evidence-gap.report` or equivalent artifact,
2. an `evidence-campaign.plan` or equivalent bounded plan,
3. and a `gap-closure.receipt` or equivalent movement record if anything changed.

Do not silently flatten:
- a named gap into a solved gap,
- a campaign plan into campaign success,
- docs.rs download or queue state into offline readiness,
- Security-tab or Trusted Publishing visibility into task fit,
- or one closed gap into full stage completion.

## Added 2026-03-24 (450) — stage and exit hygiene before synthesis

Future passes should not write “this crate is ready for enterprise/offline/safety use” until they first ask:
- which decision-program stage is actually in scope,
- which earlier basis and packets are being inherited,
- which new evidence is genuinely new for this stage,
- what exceptions or unresolved gaps remain,
- and what exit posture is being claimed.

Before summarizing a stronger posture, create or point to:
1. a `decision-program.runbook` or equivalent stage map,
2. a `profile-progression.report` or equivalent progression artifact,
3. and an explicit exit status.

Do not silently flatten:
- exploratory profile passes into enterprise-offline readiness,
- docs.rs or Security-tab visibility into stage-complete evidence,
- carried exceptions into satisfied gates,
- or later stage gates into retroactive truth about the earlier basis.

## Added 2026-03-24 (448) — exception-budget hygiene before synthesis

Future passes should not write “we can keep this for now” until they first ask:
- what exact packet or decision is being excepted,
- who owns the exception,
- what scope the exception applies to,
- what evidence or witness supports it,
- and when the exception expires or is removed.

Before summarizing a temporary allowance, create or point to:
1. a `policy-exception.receipt` or equivalent artifact,
2. an expiry/removal trigger or ticket,
3. and an explicit support ceiling.

Do not silently flatten:
- Cargo Vet exemptions into general support truth,
- cargo-deny ignores into ecosystem-wide safety clearance,
- semver overrides into “not actually breaking”,
- or docs.rs partial support into universal incompatibility or compatibility.

## Added 2026-03-24 (447) — disagreement-ledger hygiene before synthesis

Future passes should not write “the new evidence says X” until they first ask:
- what older packet or basis does X disagree with,
- whether the disagreement is route-based, time-based, scope-based, or policy-based,
- and whether the pass is actually adjudicating, revalidating, or transitioning.

Before summarizing a changed answer, create or point to:
1. a disagreement ledger or equivalent conflict list,
2. an adjudication artifact,
3. and a carry-forward artifact.

Do not silently flatten:
- `latest` docs routes into frozen basis,
- registry/index and `cargo metadata` into one generic dependency fact,
- cached build-script observations into fresh execution,
- or improved trust posture into automatic task-fit promotion.

## Added 2026-03-23 (445) — trigger class before refresh

Future passes should not say merely “fresh research changed the answer.”
They should first classify what opened review:
- new release,
- advisory / trust signal,
- docs or support-surface shift,
- Cargo/toolchain substrate change,
- local incident,
- or manual architectural recheck.

Then keep these artifacts separate:
1. **trigger intake**,
2. **recheck ticket**,
3. **revalidation packet**,
4. **transition packet**.

Do not silently compress those into one fresh conclusion.

## 2026-03-23 addendum — frozen packets must not be silently rewritten

When extending this archive, keep these distinctions explicit:
- initial compare packet,
- frozen basis lock,
- later refresh / revalidation packet,
- later transition packet.

Do not rewrite an old decision as if it always contained later facts.
Append a new artifact that points back to the old basis.

When in doubt, prefer:
- `same_choice_stands_reviewed`,
- `manual_review_required`,
- or `new_compare_required`

over a vague merged narrative.

## Added 2026-03-24 (443) — basis-witness hygiene

Before saying a crate or packet is “grounded”, state:
- which witness surfaces were actually consulted,
- whether the basis was registry, packaged-state, docs.rs hosted surfaces, build JSON, or repository prose,
- which target filters or freeze windows were in scope,
- and what remains manual-review-only.

Do **not** let future passes:
- cite floating `latest` pages as if they were a replayable basis,
- blur packaged-state witnesses with casual repository browsing,
- or treat trusted publishing / security surfaces as if they settled task fit.

When deepening top lanes, prefer adding:
- `basis-lock.manifest.json`,
- witness receipts,
- and answer-boundary notes
before adding another ranking layer or abstraction story.

## Added 2026-03-24 (442) — future passes must ask what packet family a crate emits and how the front-door stack fits together

Before promoting or widening a proposal, read:
1. `entries/2026-03-24-442.md`
2. `meta/frontier-salience-2026-03-24-233.md`
3. `meta/front-door-stack-pathfinder-knowledge-pack-2026-03-24.md`
4. `meta/packet-family-schema-discipline-2026-03-24.md`
5. `meta/crate-knowledge-pack-review-bundle-plan-2026-03-24.md`

Then apply these filters:
1. **packet-kind test** — is this output a receipt, report, manifest, matrix, pack, import, lock, or note, and does that choice stay honest?
2. **front-door coupling test** — if the proposal touches crate choice or support packets, should it actually deepen the `P-0509 + P-0536` pair instead?
3. **schema-evolution test** — what downstream consumer breaks if this packet changes shape, and how is that handled?
4. **browse-vs-replay test** — are floating latest-view routes being confused with pinned replay basis?
5. **manual-review test** — what classes still require refusal or manual review even after the packet is emitted?

Default bias after this pass:
- prefer packet-family clarity over bigger feature lists;
- prefer the front-door stack over a new ranking/search layer;
- prefer pinned review packets over assistant rhetoric.

## Added 2026-03-24 (441) — future passes must ask who receives the packet and what first adopter loop proves value

Before promoting or widening a proposal, read:
1. `entries/2026-03-24-441.md`
2. `meta/epic-crate-receiver-persona-map-2026-03-24.md`
3. `meta/epic-crate-first-adopter-programs-2026-03-24.md`
4. `meta/cargo-vendor-source-parity-product-plan-2026-03-24.md`
5. `meta/frontier-salience-2026-03-24-232.md`

Then apply these filters:
1. **receiver test** — which humans and which machines receive the packet?
2. **pilot test** — what narrow first-adopter loop proves the crate is useful?
3. **restricted-delivery boundary test** — if offline/mirror/vendor ideas appear, are mirror verification, transfer, and source parity still kept separate?
4. **anti-abstraction test** — is the value a boring reviewable artifact rather than a smart-sounding wrapper?
5. **non-claim test** — what must the crate still refuse to claim after a successful pilot?

Default bias after this pass:
- prefer receiver-facing packets over broader rhetoric;
- prefer pilotable `0.1` loops over larger speculative roadmaps;
- prefer sharpening restricted-delivery truth over inventing another generic supply-chain crate.

## Added 2026-03-24 (440) — future passes must ask for supportive surfaces and adoption tier before promoting a crate

Before promoting or widening a proposal, read:
1. `entries/2026-03-24-440.md`
2. `meta/supportive-crate-surface-principles-2026-03-24.md`
3. `meta/hard-domain-adoption-ladder-2026-03-24.md`
4. `meta/epic-crate-first-release-bundles-2026-03-24.md`
5. `meta/frontier-salience-2026-03-24-231.md`

Then apply these filters:
1. **supportive-surface test** — what are the orientation, evidence, review, machine, and drift/refusal surfaces?
2. **bundle test** — what exact first-release bundle would another engineer receive on day one?
3. **adoption-tier test** — is this only explore-level, or does it honestly serve team-default, shipping, offline, or regulated use too?
4. **pathfinder/knowledge substitution test** — should this be a pathfinder scenario or knowledge pack instead of a new frontier lane?
5. **anti-handwave test** — are the claims specific enough for a skeptical reviewer to verify later?

Default bias after this pass:
- prefer **supportive surfaces** over broader rhetoric;
- prefer **small first-release bundles** over sprawling feature lists;
- prefer **scenario packs** over new sector lanes when the control-plane frontier can still absorb the need.

## Added 2026-03-23 (439): future broad passes must run sector ideas through the receiver-value and substitution tests

When a future pass gets excited by a new domain or subculture, apply these checks before creating or promoting a lane:

1. **receiver-value test** — what packet does another person get?
2. **substitution test** — could the same value be captured by pathfinder, debuggability, docs/build truth, dependency transition, toolchain support, native deps, or crate knowledge packs?
3. **watchlist test** — is this a real future theme but still better kept below the top frontier for now?
4. **refusal-boundary test** — what must the crate refuse to claim?

Default bias after this pass:
- widen the map,
- but keep promotion hard.

## Added 2026-03-23 (437): future passes should add delivery cards before promoting a crate

When a future pass wants to promote a proposal, it should first be able to name:

1. **users** — who receives value,
2. **promise** — the boring answer the crate gives them,
3. **`0.1` outputs** — concrete files/reports/commands,
4. **workflow replacement** — what repeated pain this removes,
5. **refusal boundary** — what the crate must not pretend to prove.

If a proposal cannot yet survive that delivery-card test, prefer deepening over promotion.

## Added 2026-03-23 (437): future build/native passes must keep explanation, fixture drift, and native contract separate

When the archive touches the native-build stack again, do not collapse these into one fake “native tooling” story:

1. **buildscript explanation** — what happened in a run and what mattered,
2. **fixture drift** — whether emitted behavior changed under controlled scenarios,
3. **native contract / provenance** — what support was promised, what backend resolved, and what override/vendoring/ABI assumptions were active.

A pass may truthfully improve one of those without improving the others.


## Added 2026-03-23 (436) — contribution-bar and refresh-loop hygiene

Future passes should assume:
- a proposal is not strong just because it sounds broad; it must export a durable artifact seam for other people;
- repo passes should explicitly choose whether they are deepening, reranking, or appending;
- when current official sources make an existing lane more implementation-ready, deepen that lane before creating more proposal sprawl;
- “assistant / search / ranking” ideas should be demoted unless they come with decision receipts, claim ceilings, and portable bundles.

## Added 2026-03-23 (435): broad scans must use the demand matrix before appending another sector lane

Before opening a new domain-specific proposal, read:
1. `entries/2026-03-23-435.md`
2. `meta/control-plane-demand-matrix-2026-03-23.md`
3. `meta/frontier-salience-2026-03-23-226.md`
4. `meta/crate-ecosystem-pathfinder-lane-catalog-plan-2026-03-23.md`
5. `meta/debuggability-support-capability-stack-plan-2026-03-23.md`

Then apply these filters:
1. **use-case-family test** — which real Rust audience is this for: newcomer CLI, async service, GUI/game, embedded, kernel-adjacent, safety-critical, Wasm/component, mixed-language, data/numerics, or build/platform tooling?
2. **horizontal-seam test** — is the sharper missing seam still crate choice, dependency transition, target/support truth, debuggability, machine-usable knowledge, concurrency/runtime truth, stewardship, or build/test evidence?
3. **artifact test** — what exact receipts / reports / manifests would the new lane export that the control-plane lanes do not already cover?
4. **template test** — could the value be captured more cleanly by adding a pathfinder lane template or a debug/target/support capability report instead?
5. **anti-sector-inflation test** — is this really a new missing crate, or just a real use case that still points back to the same control-plane gaps?

Default bias after this pass:
- prefer **deepen the horizontal lanes** over **append another sector lane**;
- prefer **named task templates** and **capability stacks** over another vague prose proposal;
- prefer **artifacts another team can inspect later** over another smart-sounding wrapper idea.

## Added 2026-03-23 (434): broad passes must preserve band structure and source-grounded prose

Before a broad refresh, read:
1. `entries/2026-03-23-434.md`
2. `meta/epic-crate-territory-map-2026-03-23-225.md`
3. `meta/archive-operator-stack-2026-03-23.md`
4. `meta/frontier-salience-2026-03-23-224.md`
5. `meta/archive-memory-anchor-2026-03-22.md`

Then apply these filters:
1. **band test** — is this a control-plane epic, adoption amplifier, sector lab, or moonshot?
2. **promotion test** — does it really beat a current control-plane lane on ecosystem leverage?
3. **artifact test** — what exact receipts / reports / manifests would it export?
4. **substance test** — are the claims grounded in current sources, not generic ecosystem vibes?
5. **anti-LLM-blur test** — is the prose specific enough that a skeptical maintainer would trust it?

Reminder: the March 2026 Rust challenges post now includes a retraction note about an earlier LLM-written draft and explicitly records discomfort with generic, low-substance phrasing. Treat that as an archive-quality lesson, not a side note.

## Added 2026-03-23 (433): broad refreshes must begin with the frontier anchor, not with idea generation

When a future model opens this archive and is tempted to brainstorm more “missing crates,” it should first read:

1. `entries/2026-03-23-433.md`
2. `meta/frontier-salience-2026-03-23-224.md`
3. `meta/archive-memory-anchor-2026-03-22.md`

Then it should apply this filter before adding anything new:

1. **top-frontier test** — does the new idea obviously outrank at least one current top-ten lane on ecosystem-wide pain?
2. **artifact test** — does it export a new review artifact / bundle / receipt type, rather than just a nicer wrapper?
3. **seam test** — does it create a reusable support-contract seam other crates could import?
4. **substitution test** — could the value be captured more cleanly by deepening an existing proposal instead?
5. **anti-novelty test** — is this just another narrow protocol/client/parser/integration idea wearing strategic language?

Default bias after this pass:
- prefer **deepen / merge / eliminate** over **append**;
- prefer **horizontal support layers** over narrow product ideas;
- prefer crates that help other people choose, trust, prove, explain, or migrate over crates that simply expose one more API.

## Added 2026-03-23 (432): concurrency-contract work must keep observer cursor and progress isolation separate

When a pass deepens **P-0538** again, do not let the archive collapse these into one fake “multi-receiver channel semantics” story:

1. **delivery audience** — who may observe a unit at all;
2. **consumption claim** — whether one observer taking a unit excludes others;
3. **observer cursor** — whether each observer advances its own frontier or observers compete for one shared frontier;
4. **observer progress isolation** — whether one observer’s slowness only hurts itself or changes other observers’ truth;
5. **order/gap visibility** — what sequence is promised and what skipped/collapsed units are visible.

A pass may truthfully show many receivers, single-delivery competition, or lag counters while still lacking an honest answer about cursor ownership or observer-local progress fate.

## Added 2026-03-23 (429): concurrency-contract work must keep order, memory, and gap visibility separate

When future revisions touch **P-0538** again, do not let the archive collapse these into one fake “channel ordering” story:

1. **delivery memory** — what, if anything, is retained: one permit, latest value, bounded queue, bounded broadcast history, no buffer;
2. **delivery order** — what sequence a receiver is actually promised: single-consumer FIFO, per-receiver FIFO, latest-snapshot-only, coalesced wake, selection-level random/bias;
3. **gap visibility** — whether missed or collapsed units are counted, cursor-rebased, silent, or only manually reviewable;
4. **audience / claim semantics** — who can observe a unit and whether one observer taking it excludes others;
5. **acceptance / observation evidence** — what producer-visible success means and what later proof exists, if any.

A pass may truthfully show bounded memory, current receivers, and successful sends while still lacking an honest answer about whether any meaningful ordered sequence exists or whether missed units are visible at all.

## Added 2026-03-23 (425): compile-iteration passes must keep coverage scope, claim ceilings, and route truth separate

When future revisions touch **P-0537** again, do not let the archive collapse these into one fake “hot reload is supported” story:

1. **coverage scope** — what surfaces, routes, crates, functions, or exports are actually under the live-update regime;
2. **coverage ceiling** — what support claims are explicitly out of bounds because coverage is tip-crate-only, annotation-only, wrapper-only, launch-time-only, or target-bound;
3. **activation / generation / drain** — what code became reachable, what generation is claimed, and whether older work is gone;
4. **live-update outcome / degraded mode** — what happened on a particular attempt and what posture the process is in now;
5. **restart fallback** — what deterministic recovery path exists if the session must be abandoned.

A pass may truthfully show a visible update, a new generation witness, and a healthy process while still lacking an honest answer about what the live-update regime actually covered.

## Added 2026-03-23 (424): compile-iteration passes must keep eligibility, outcome, degraded mode, and fallback separate

When future revisions touch **P-0537** again, do not let the archive collapse these into one fake “the reload worked” story:

1. **patch eligibility** — whether the edit class is theoretically compatible with a live-update route;
2. **live-update outcome** — what actually happened on this attempt;
3. **degraded iteration mode** — what operating posture the process is in now;
4. **restart fallback** — what deterministic recovery path exists if the session must be abandoned;
5. **activation / generation / retirement / drain** — what code became reachable, what generation is claimed, and whether old work is gone.

A pass may truthfully show a patch-eligible edit, a completed build, an activation boundary, and a restart plan while still lacking an honest answer about whether the current attempt applied or whether the process is still safe to keep iterating in place.

## Added 2026-03-23 (423): compile-iteration passes must keep activation, generation, retirement, and drain separate

When future revisions touch **P-0537** again, do not let the archive collapse these into one fake “the new code fully took over” story:

1. **activation boundary** — when fresh code becomes reachable on some route;
2. **generation witness** — what evidence identifies the code epoch of that route or library;
3. **retirement boundary** — when older code is expected to stop being reachable for that route class;
4. **old-generation drain** — whether pre-reload work was actually observed drained or only partially rewound;
5. **mixed-generation risk** — whether old and new generations may coexist across routes.

A pass may truthfully show a completed reload, a visible UI update, and a latest-generation witness while still lacking an honest answer about retirement or drain completeness.


## Added 2026-03-23 (422): compile-iteration passes must keep activation, generation witnesses, and mixed-generation risk separate

When future revisions touch **P-0537** again, do not let the archive collapse these into one fake “the new build is live” story:

1. **activation boundary** — when fresh code becomes reachable on a route;
2. **generation witness** — what evidence identifies the code epoch of that route or library;
3. **stale-code residency** — what old code can still remain reachable;
4. **mixed-generation risk** — whether old and new generations may coexist across routes;
5. **state continuity** — what survived, re-instanced, migrated, or reset.

A pass may truthfully show a completed reload, a visible UI update, and preserved state while still lacking an honest answer about homogeneous execution generation.

## Added 2026-03-23 (421): compile-iteration passes must keep patch route, continuity, activation, and stale-code residency separate

When future revisions touch **P-0537** again, do not let the archive collapse these into one fake “reload worked” story:

1. **patch / reload route** — what mechanism ran: surface reload, hotpatch, relink, rebuild, restart;
2. **state continuity** — what state survived, reset, migrated, or was out of scope;
3. **activation boundary** — when fresh code actually becomes active on relevant call paths;
4. **stale-code residency** — what old code may still remain reachable through stored routes or identity-sensitive systems;
5. **restart fallback** — what deterministic recovery path remains when takeover honesty fails.

A pass may truthfully show a fast path, some preserved state, and a visible reload while still lacking honest activation or stale-code answers.

## Added 2026-03-23 (419): concurrency-contract work must keep locality, liveness, and legality separate

When a pass deepens **P-0538** again, do not let the archive collapse these into one fake “works in async” story:

1. **execution-context legality** — whether the call is allowed, panics, blocks, or deadlocks in a context;
2. **mobility / affinity** — whether work is movable across threads or bound to a thread / local context / CPU placement;
3. **driver-liveness** — what must keep running for tasks, timers, I/O, or local queues to make progress;
4. **fairness / progress class** — FIFO, eventual fairness, writer-priority, unspecified;
5. **wait-cancellation / recovery posture** — what cancellation or panic changes.

Do not let any of the following stand in for an honest answer by themselves:
- “the future is `!Send`,”
- “`spawn_local` exists,”
- “a runtime handle exists,”
- “the code is inside Tokio,”
- or “the executor supports local tasks.”

The sharper move is to publish one `mobility-affinity.report`, one `driver-liveness.report`, and bundle/doctor rules that keep locality, liveness, and legality explicitly separate.

## Added 2026-03-23 (418): pathfinder work must keep exclusion class, re-entry, and replacement separate

When a pass deepens **P-0509** again, do not let the archive collapse these into one fake “best crate” story:

1. **runner-up not chosen** — eligible candidate that lost on trade-offs;
2. **hard exclusion** — candidate that failed a declared constraint or policy gate;
3. **candidate re-entry** — what change would permit reconsideration later;
4. **starter-set replacement** — whether the frozen winner should actually be superseded.

Do not let any of the following masquerade as re-entry authority by themselves:

- higher crates.io search placement,
- more downloads or popularity rhetoric,
- SLOC visibility changes,
- prettier docs.rs/readme surfaces,
- or “cargo add picked it”.

The sharper move is to publish one `candidate-elimination.receipt`, one `candidate-reentry.policy`, and doctor rules that keep exclusion, re-entry, and replacement explicitly separate.

## Added 2026-03-23 (414): crate-knowledge passes must keep item witnesses, opaque IDs, and locators separate

When future revisions touch **P-0536** or adjacent docs/search/assistant-facing lanes, do not let the archive collapse these into one fake “the claim points at the right API item” story:

1. **opaque JSON IDs** — raw rustdoc JSON item IDs that are valid only within a single blob;
2. **item witnesses** — crate/version/target/path/kind/source-span context for the conceptual item;
3. **citation locators** — the current review surfaces or fallback routes that can be cited;
4. **identity fidelity** — whether witness reuse is exact, rechecked, approximate, or manual-review-only;
5. **claim traces** — which excerpts/materials justified the exported statement.

A bundle can contain all of those truths and still fail to prove stable item identity across versions or targets.

## Added 2026-03-23 (413): crate-knowledge passes must keep citation locators, citation capability, and claim traces separate

When future revisions touch **P-0536** or adjacent docs/search/assistant-facing lanes, do not let the archive collapse these into one fake “the pack is grounded and citable” story:

1. **material basis** — what exact hosted/local/versioned materials were imported;
2. **claim traces** — which exported claims map back to which excerpts/materials;
3. **citation locators** — what exact pinned, target-aware URL/path should be cited;
4. **citation capability** — which query classes can cite at item/page/package level and which still require manual review;
5. **answerability** — what the compact pack can answer at all.

Do not let any of the following stand in for an honest answer:
- “the docs are on docs.rs,”
- “the pack has claim traces,”
- “we used the latest docs page,”
- “the item exists in rustdoc JSON,”
- or “the assistant can answer that.”

A bundle can contain all of those truths and still fail to say what URL should actually be cited or whether the answer class is citation-ready.

## 2026-03-23 concurrency-contract cancellation/recovery addendum

When the archive next touches concurrency-support work, prefer deepening **P-0538** around:

1. queue-withdrawal versus true cancel-safe classes,
2. value/message/seen-state preservation,
3. panic-recovery posture,
4. advisory poisoning versus no-poisoning,
5. and experimental/nightly claim ceilings.

Do not let future passes rephrase those into generic channel semantics, generic runtime support, generic lock docs, or generic “concurrency safe” marketing.

## 2026-03-23 concurrency-contract addendum

When the archive next touches concurrency-support work, prefer deepening **P-0538** around:

1. reentrancy scope,
2. progress/fairness class,
3. wait-cancellation behavior,
4. execution-context boundaries,
5. and portable support bundles.

Do not let future passes rephrase those into generic async help, generic channel semantics, generic runtime choice, or generic “concurrency safe” marketing.

Keep these distinctions explicit:
- FIFO fairness is not reentrancy.
- Eventual fairness is not FIFO.
- Cancellation safety is not “nothing changes when cancelled.”
- Queue-place loss is not message loss.
- Seen-state preservation is not the same thing as queue withdrawal.
- No poisoning is not fairness.
- Context legality is not the same thing as progress/fairness.

## Added 2026-03-23 (409): rustdoc JSON passes must keep source route, format windows, normalization loss, and downstream support scope separate

When future revisions touch **P-0051** or nearby machine-docs lanes, do not let the archive collapse these into one fake “rustdoc JSON support” story:

1. **source route** — local nightly generation, docs.rs import, rustup `rust-docs-json`, or manual file import;
2. **format-window support** — whether the consumer actually supports the observed `format_version`;
3. **normalization quality** — what the stable IR preserves, downgrades, omits, or leaves unresolved;
4. **downstream support scope** — which semver/docs/search/assistant questions are still safe above the current IR;
5. **claim ceiling** — where manual review is still required.

Do not let any of the following stand in for an honest answer:
- “the file parsed”,
- “docs.rs had a JSON endpoint”,
- “the crate exposes rustdoc JSON”,
- or “the normalized graph loaded”.

A bundle can contain all of those facts and still fail to say what route was used, what versions are supported, or what was lost.

## Added 2026-03-23 (401): publish-receipt passes must keep local bytes, identity, registry capability, protection scope, and visibility separate

When future revisions touch **P-0477** or nearby publish/registry lanes, do not let the archive collapse these into one fake “publish succeeded safely” story:

1. **local bytes** — what exact package artifact or digest was observed;
2. **publish identity** — manual, token, or trusted-publisher route plus its explicit evidence;
3. **registry capability** — what this registry lane actually exposes (`pubtime`, TP-only posture, docs coupling, notifications, advisory surface);
4. **protection scope** — which mitigations, audits, advisory channels, and client-version windows were really in scope;
5. **publication visibility** — uploaded, index-visible, Cargo-ready, docs-pending, docs-visible, or still partial.

Do not let any of the following stand in for an honest answer:
- “the crate was published,”
- “trusted publishing was used,”
- “crates.io blocks that,”
- “the index entry exists,”
- or “there was a public advisory.”

A bundle can contain all of those facts and still fail to say what registry lane was in play or what protections genuinely applied there.

## Added 2026-03-23 (400): workspace-boundary passes must keep ancestor discovery, config layering, and invocation mode separate

When future revisions touch **P-0506** or nearby Cargo workspace/config lanes, do not let the archive collapse these into one fake “Cargo saw the wrong workspace” story:

1. **ancestor discovery** — which parent manifests/config candidates existed and where probing stopped;
2. **config layering** — file layers, include edges, env overrides, CLI overrides, and path bases;
3. **invocation mode** — cwd auto-discovery, `--manifest-path`, manifest-command mode, and single-file package mode;
4. **membership diagnosis** — root/member/excluded/ambiguous package classification;
5. **advice** — workaround, repo cleanup, or upstream design gap.

Do not let any of the following stand in for an honest answer:
- “Cargo found a parent manifest,”
- “there was a config file,”
- “we used `--manifest-path`,”
- “the script was just `foo.rs`,”
- or “the error message mentions workspace discovery.”

A bundle can contain all of those facts and still fail to say which ancestor candidates were in play, how config precedence worked, or whether workspace auto-discovery was even available in that invocation mode.


## Added 2026-03-23 (399): crate-knowledge passes must keep machine-facing pack structure, query-support scope, refusal zones, and claim traces separate

When future revisions touch **P-0536** or adjacent docs/search/assistant-facing lanes, do not let the archive collapse these into one fake “the assistant slice understands the crate” story:

1. **machine-facing pack structure** — what sections, exclusions, and linked artifacts the compact export actually contains;
2. **query-support scope** — which classes are `supported`, `partial`, `manual_review_required`, or `refused`;
3. **refusal/manual-review zones** — which question families must not be answered from the pack alone;
4. **claim traces** — which exported claims map back to which excerpt IDs and source-material IDs;
5. **material/export basis** — what exact materials and policy produced the slice.

Do not let any of the following stand in for an honest answer:
- “we emitted assistant context,”
- “the docs are on docs.rs,”
- “rustdoc JSON exists,”
- “the pack is compact,”
- or “the summary looks right.”

A bundle can have all of those truths and still fail to say what it can answer or how its claims are grounded.


## Added 2026-03-23 (397): safety-contract passes must keep authority, consumer coverage, and semantic lanes separate

When future revisions touch **P-0453** or nearby safety-contract / verification lanes, do not let the archive collapse these into one fake “contracts are supported” story:

1. **authority** — where each clause came from and how it was extracted,
2. **consumer coverage** — which tools or modes actually consumed which clauses,
3. **semantic lane** — runtime checks, bounded model checking, deductive verification, refinement typing, separation logic, or manual review,
4. **runtime/proof receipts** — what evidence was actually produced in that lane,
5. **bundle truth** — what one portable handoff really contains.

Do not let any of the following stand in for an honest answer:
- “the compiler has contracts now”,
- “Kani passed”,
- “verify-rust-std accepts multiple tools”,
- “the function has requires/ensures”,
- or “runtime checks were green”.

A bundle can contain all of those facts and still fail to say which clauses were consumed by which tools or what semantic caveats still fence the result.

## Added 2026-03-23 (396): async runtime assurance passes must keep deployment topology, capability matrices, and surface guards separate

When future revisions touch **P-0532** or nearby async/runtime lanes, do not let the archive collapse these into one fake “async runtime support everywhere” story:

1. **runtime family** — Tokio-style hosted runtime, Embassy-style embedded executor, RTIC-style interrupt-priority scheduler, or mixed/custom lane;
2. **service topology** — where spawning, time, I/O, process, signal, and blocking services actually come from;
3. **deployment topology** — which host, CI, simulator, console, and target lanes exist;
4. **capability availability** — which capabilities are supported, unsupported, or guarded in each lane;
5. **surface guards** — what cfg/feature/runtime-context/provider guard fences each claim;
6. **bridge debt** — what an adapter actually bridges and what provider/context dependence still remains.

Do not let any of the following stand in for an honest answer:
- “the crate uses Tokio”,
- “the examples run on PC”,
- “Embassy has a std example”,
- “Windows ctrl-c worked once”,
- or “the docs mention signals”.

A bundle can contain all of those facts and still fail to say which capabilities are available in which lane or what guards fence the claim.

## Added 2026-03-23 (395): async runtime assurance passes must keep runtime family, service topology, capability routes, and bridge debt separate

When future revisions touch **P-0532** or nearby async/runtime lanes, do not let the archive collapse these into one fake “async runtime support” story:

1. **runtime family** — Tokio-style hosted runtime, Embassy-style embedded executor, RTIC-style interrupt-priority scheduler, or mixed/custom lane;
2. **service topology** — where spawning, time, I/O, process, signal, and blocking services actually come from;
3. **capability route** — what builder flag, runtime context, HAL feature, dispatcher setup, or adapter is required for one claimed capability;
4. **bridge debt** — what an adapter actually bridges and what provider/context dependence still remains;
5. **evidence class** — docs only, docs plus metrics, docs plus target measurement, imported assurance artifact, or manual review.

Do not let any of the following stand in for an honest answer:
- “the crate uses Tokio”,
- “we added async-compat”,
- “the executor is embedded-friendly”,
- “it worked in host integration tests”,
- or “the runtime is documented”.

A bundle can have all of those facts and still fail to say which async services are present, what made them available, or what bridge debt remains.

## Added 2026-03-22 (393): pathfinder import basis must stay distinct from visibility and choice

When a proposal touches **crate pathfinder / starter-set** work, future revisions must state explicitly whether the product is primarily about:

1. a **candidate-basis receipt**,
2. a **support-visibility report**,
3. a **decision-pack / starter-set choice**,
4. a **watch/revisit policy**,
5. or an adjacent **health / trust / docs parity / toolchain-support** import.

Future revisions must also keep these truths visibly separate whenever possible:

- Cargo could find or add the package,
- crates.io exposes a Security tab or Trusted Publishing posture,
- docs.rs makes a target/features story publicly visible,
- imported health/trust receipts look strong,
- and the crate is actually the right starter-set choice for the task.

Do **not** let the archive silently convert “this crate is visible and well-surfaced” into “this is the correct default”.
A good pathfinder crate may use visible registry/docs/tooling surfaces to improve reviewability and still conclude `manual_review_required` when task fit remains unresolved.

## Added 2026-03-22 (391): compile-iteration passes must keep watch routes, link speedups, patchability, state continuity, and restart fallback separate

When future revisions touch **P-0537** or adjacent iteration/DX lanes, do not let the archive collapse these into one fake “hot reload works” story:

1. **watch / trigger route** — what noticed the edit and which command lane fired;
2. **compile/link acceleration** — what only made rebuild or relink faster;
3. **reload surface** — what was really updated: markup, assets, functions, symbols, or nothing live;
4. **patch eligibility** — whether this edit class is live-updateable, relink-only, restart-only, or manual review;
5. **state continuity** — what state survives, resets, migrates, or becomes invalid;
6. **restart fallback** — what deterministic path remains when live update is not safe.

Do not let any of the following stand in for an honest answer:
- “the watcher reran instantly,”
- “we switched to LLD or Wild,”
- “the framework has hot reload,”
- “the process stayed up,”
- or “the loop feels much faster.”

A workflow can have all of those truths and still leave patch safety, state continuity, or restart truth unresolved.

## Added 2026-03-22 (391b): broad rerank passes should emit one map, one rank, and at most one new lane

When a pass is explicitly about the whole archive rather than one subsystem, future revisions should prefer this package of outputs:

1. one broad territory map,
2. one ranked frontier snapshot,
3. and at most one genuinely new proposal lane.

Do not let broad passes degenerate into “add three more proposals because many things are still missing.”
In a mature archive, the harder and better move is usually ranking, synthesis, lane-boundary cleanup, or one carefully chosen new seam.

## Added 2026-03-22 (382): trusted publishing requires registry-state imports, workflow-route receipts, and authorization drift

When future revisions touch **P-0175** or adjacent release/auth lanes, do not let the archive collapse these into one fake “trusted publishing is configured” story:

1. **registry trust state** — what crates.io is actually configured to trust for the package set;
2. **workflow-route identity** — what direct/reusable/config route actually ran;
3. **claim basis** — issuer, audience, subject, environment, and route claims;
4. **trigger and publish mode** — whether the event is allowed and whether TP-only/mixed/manual posture matches;
5. **authorization drift** — what changed between two release paths.

Do not let any of the following stand in for an honest answer:
- “the repo has a publish workflow,”
- “the job minted an OIDC token,”
- “`id-token: write` is present,”
- “the run rehearsed successfully,”
- or “the release still uses the same provider.”

A release path can have all of those truths and still leave imported registry state, actual route identity, or authorization drift unresolved.

## Added 2026-03-22 (380): feature support requires scope honesty, hosted-doc posture, and portable bundles

When future revisions touch **P-0528** or adjacent feature/docs/support lanes, do not let the archive collapse these into one fake “the crate supports these features” story:

1. **public surface** — which names are contract versus hidden dependency plumbing;
2. **profile support** — which named combinations are observed, sampled, unsupported, or recipe-only;
3. **observation scope** — which command/workspace/target context the evidence came from;
4. **hosted-doc posture** — what docs.rs or equivalent public docs are actually showing users;
5. **portable bundle shape** — what one review bundle another engineer can archive and inspect.

Do not let any of the following stand in for an honest answer:
- “the `[features]` table is documented,”
- “docs.rs built with `all-features`,”
- “one workspace build passed,”
- or “CI runs `--all-features`.”

## Added 2026-03-22 (379): crate-knowledge passes must keep material basis, export policy, excerpt lineage, and compact packs separate

When future revisions touch **P-0536** or adjacent docs/search/assistant-facing lanes, do not let the archive collapse these into one fake “the crate knowledge export is trustworthy” story:

1. **material basis** — what exact hosted/local/versioned/floating materials fed the pack;
2. **export policy** — what source classes, redaction rules, and pinning rules shaped the slice;
3. **excerpt lineage** — what exact fragments entered the compact export;
4. **portable pack shape** — what the bundle actually contains versus what it only references.

Do not let any of the following stand in for an honest answer:
- “docs.rs has a latest URL,”
- “rustdoc JSON exists,”
- “the README was included,”
- “we emitted assistant context,”
- or “the support slice is small.”

A crate can have all of those truths and still leave exact materials, export policy, excerpt lineage, or public/machine handoff honesty unresolved.

## Added 2026-03-22 (376): toolchain/target passes must keep imported authority, local support class, public docs surface, and bundle shape separate

When future revisions touch **P-0484** or adjacent toolchain/target lanes, do not let the archive collapse these into one fake “supports target X” story:

1. **imported upstream authority** — which facts came from Rust-project policy, rustup, docs.rs, or Cargo docs;
2. **local support class** — what the project itself promises after interpreting those facts;
3. **public docs surface** — what docs.rs is actually exposing, and whether defaults were implicit;
4. **route/topology/support evidence** — what was really exercised and how artifacts were found;
5. **portable bundle shape** — what one reviewer should actually receive.

Do not let any of the following stand in for an honest answer:
- “it is Tier 2,”
- “rustup ships a host for it,”
- “docs.rs shows the target by default,”
- “the target was installed,”
- or “CI produced an artifact.”

A crate can have all of those truths and still leave imported-authority meaning, project-local promise, hosted public surface, or bundle completeness unresolved.

## Added 2026-03-22 (375): debuggability passes must keep posture, backend observations, source materials, handoff, and portable bundles separate

When future revisions touch **P-0486** or adjacent debugging lanes, do not let the archive collapse these into one fake “the build is debuggable” story:

1. **broad support posture** — `interactive_debugger`, `backtrace_only`, `crash_symbolication_only`, or weaker;
2. **exact backend observation** — which debugger family / version / capability lane was actually checked;
3. **artifact handoff** — which sidecars and visualizer assets are required for the promise;
4. **source material** — what lookup materials exist after trimming/remapping and whether they are safe to share;
5. **portable bundle truth** — what the exported handoff actually contains versus what it only references.

Do not let any of the following stand in for an honest answer:
- “the PDB exists,”
- “NatVis is embedded,”
- “the debugger opened the binary once,”
- “trim-paths is enabled,”
- or “the release bundle has the executable.”

A build can have all of those truths and still leave portable support posture, cross-backend evidence, source-lookup material, or review handoff honesty unresolved.


## Added 2026-03-22 (374): MSRV passes must keep workspace promises, policy activation, command families, authoring floors, and split drift separate

When future revisions touch **P-0036** or adjacent Cargo/MSRV lanes, do not let the archive collapse these into one fake “the repo supports Rust X” story:

1. **effective workspace promise** — what each member or lane actually promises;
2. **policy activation** — whether the intended resolver/MSRV policy was truly active;
3. **command-family floor** — whether `build`, `metadata`, `doc`, `update`, `generate-lockfile`, or `package` hold at the same floor;
4. **lockfile-authoring floor** — whether reading/updating/writing lockfiles requires something newer;
5. **policy-split drift** — whether only one member or command-family promise changed.

Do not let any of the following stand in for an honest answer:
- “`rust-version = X` is set,”
- “`cargo build` passed,”
- “resolver v3 exists in one member,”
- “the committed lockfile still works,”
- or “`cargo-msrv verify` is green.”

A crate can have all of those truths and still leave workspace promise shape, activation truth, command-family divergence, authoring-floor drift, or member-granularity change unresolved.

## Added 2026-03-22 (371): unsafe-review passes must keep authority imports, obligation drift, comparison scope, and callback boundaries separate

When future revisions touch **P-0120** or adjacent unsafe-review lanes, do not let the archive collapse these into one fake “unsafe evidence improved” story:

1. **authority import** — what was imported from docs, contract attributes, std contracts, upstream manifests, or manual local manifests;
2. **obligation drift** — what semantic unsafe obligations changed versus what merely moved sites;
3. **comparison scope** — whether two witness runs are honestly comparable at all;
4. **callback/FFI boundary** — what foreign behavior stayed partially out of scope.

Do not let any of the following stand in for an honest answer:
- “Miri still passes,”
- “contract attributes were imported,”
- “the unsafe block count went down,”
- “the diff only moved helpers,”
- or “the callback harness is green.”

A crate can have all of those truths and still leave imported-authority exactness, semantic obligation drift, witness comparability, or callback-boundary honesty unresolved.

## Added 2026-03-22 (369): crate-knowledge passes must keep authority, sources, examples, hosted presence, and slices separate

When future revisions touch **P-0536** or adjacent docs/search/assistant-facing lanes, do not let the archive collapse these into one fake “crate knowledge is handled” story:

1. **API authority** — what public items were named by rustdoc/cargo and with what exactness class;
2. **docs-source provenance** — which README/book/rustdoc/docs.rs pages were authoritative, imported, or inferred;
3. **example lineage** — which examples are official, runnable, compile-only, illustrative, generated, or manual-review-only;
4. **hosted presence** — what docs.rs actually hosted and on which target/default posture;
5. **slice policy** — what a support/search/assistant slice included, excluded, and why.

Do not let any of the following stand in for an honest answer:
- “rustdoc JSON exists,”
- “docs.rs is green,”
- “the README has examples,”
- “`cargo test --doc` passed,”
- or “we built an assistant index.”

A crate can have all of those truths and still leave actual authority, example status, hosted reality, or export/slice policy unresolved.

## Added 2026-03-22 (366): Cargo contention passes must keep root authority, actor lanes, wait windows, blocker exactness, and mitigation cost separate

When future revisions touch **P-0490** or adjacent Cargo/IDE blocking lanes, do not let the archive collapse these into one fake “Cargo lock contention is handled” story:

1. **root authority** — where each root path claim came from;
2. **actor command lane** — what the actor actually ran;
3. **wait window** — what time-bounded wait was directly observed;
4. **blocker-identity exactness** — whether a blocker was directly observed, session-supported, inferred, or unknown;
5. **mitigation cost** — what the workaround buys and costs.

Do not let any of the following stand in for an honest answer:
- “use a separate target dir,”
- “rust-analyzer was running,”
- “a Cargo session overlapped the incident,”
- “build-dir-layout v2 is enabled,”
- or “the build eventually finished.”

A crate can have all of those truths and still leave actual root authority, command scope, blocker certainty, or mitigation trade-offs unresolved.

## Added 2026-03-22 (365): public-dependency passes must keep intent, effect, routes, provenance, gaps, and migration separate

When future revisions touch **P-0431** or adjacent public-API lanes, do not let the archive collapse these into one fake “public dependencies are handled” story:

1. **manifest intent** — what Cargo declarations say;
2. **effective boundary** — what is actually public today;
3. **exposure route** — how the dependency escaped;
4. **evidence provenance** — which parts came from Cargo/rustc versus rustdoc-based inference;
5. **workspace gap** — where current Cargo behavior blocks a cleaner declaration;
6. **migration posture** — what the safest next move is.

Do not let any of the following stand in for an honest answer:
- “the lint fired,”
- “`public = true` is set,”
- “`cargo-public-api` found external items,”
- “the dependency is doc-hidden,”
- or “we can wrap it later.”

A crate can have all of those truths and still leave actual boundary effect, scope limits, evidence authority, or migration risk unresolved.

## Added 2026-03-22 (349): delegated build-time passes must keep topology, outputs, overrides, bridges, and drift separate

When future revisions touch **P-0508** or adjacent build-time delegation lanes, do not let the archive collapse these into one fake “delegated build scripts are supported” story:

1. **unit topology** — what build units exist and in what order;
2. **output lane** — which metadata/env/generated files/artifacts each unit owns;
3. **override authority** — whether live execution, config override, or delegate-package policy was authoritative;
4. **bridge posture** — whether any artifact handoff is stable, nightly-only, or manual-review-only;
5. **drift** — what changed across revisions or toolchains.

Do not let any of the following stand in for an honest answer:
- “the crate has multiple build scripts”,
- “the build succeeded”,
- “a `links` override exists”,
- “Cargo emitted metadata”,
- or “we plan to use metabuild later”.

A crate can have all of those truths and still leave output ownership, authority route, bridge ceiling, or review drift unresolved.

## Added 2026-03-22 (348): in-place-init passes must keep placement, constructor lanes, address commit, cleanup, and drift separate

When future revisions touch **P-0447** or adjacent pinning/construction lanes, do not let the archive collapse these into one fake “supports pinned/in-place initialization” story:

1. **placement topology** — where bytes were first written and where final storage lives;
2. **constructor lane** — by-value Rust, `pin-init`, out-pointer, `moveit`, Crubit `Ctor`, or provisional future-language lane;
3. **address commit** — when movement becomes forbidden;
4. **failure cleanup** — what can fail, what may be partially initialized, and who owns rollback;
5. **drift** — what changed across revisions.

Do not let any of the following stand in for an honest answer:
- “the API returns `Pin<_>`,”
- “the crate uses `MaybeUninit`,”
- “the type is constructed on the heap,”
- “the constructor is fallible,”
- or “future language support will solve this.”

A crate can have all of those truths and still leave placement, constructor semantics, address-commit boundaries, or cleanup posture unresolved.

## Added 2026-03-22 (347): lint-policy passes must keep authority, scope, channels, waivers, and drift separate

When future revisions touch **P-0459** or adjacent lint-facing lanes, do not let the archive collapse these into one fake “strict linting is enabled” story:

1. **policy authority** — where the effective lint level came from;
2. **checked scope** — what packages / features / targets / tests / private items were actually checked;
3. **diagnostic channel** — whether a finding came from stable rustc/Clippy or nightly Cargo linting;
4. **waiver truth** — which exceptions are explicit, owned, and time-bounded;
5. **drift** — what widened, narrowed, or reclassified across revisions.

Do not let any of the following stand in for an honest answer:
- “the workspace uses `[lints]`,”
- “`cargo clippy` passed,”
- “the root manifest forbids `unsafe_code`,”
- “the waiver is documented,”
- or “nightly found extra warnings.”

A crate can have all of those truths and still leave authority source, checked scope, channel provenance, or waiver ownership unresolved.

## Added 2026-03-22 (346): unsafe-field planning must keep authority, mutation, constructors, witness scope, and drift separate

When future revisions touch **P-0460** or adjacent unsafe-review lanes, do not let the archive collapse these into one fake “unsafe invariants documented” story:

1. **field authority** — where the invariant claim came from;
2. **mutation lane** — which safe/unsafe/generated paths can change the field;
3. **constructor trust** — which paths are trusted to establish the invariant;
4. **witness scope** — what tests/Miri/contracts/manual review actually touched;
5. **drift** — what widened or narrowed across revisions.

Do not let any of the following stand in for an honest answer:
- “the field is private”,
- “safety comments exist”,
- “Miri passed”,
- “the constructor validates input”,
- or “future unsafe fields will solve this”.

A crate can have all of those and still leave authority source, safe mutator scope, constructor trust, or witness boundaries unresolved.

## Added 2026-03-22 (345): documentation-example support must keep manifest, rewrites, execution mode, hosted parity, and coverage separate

When future revisions touch **P-0455** or adjacent docs-facing lanes, do not let the archive collapse these into one fake “docs are tested” story:

1. **manifest truth** — what rustdoc extracted and from where;
2. **rewrite lineage** — what harness/setup/adapters were injected after extraction;
3. **execution mode** — standalone, merged, wrapper-executed, compile-only, ignored, or render-only;
4. **hosted/build parity** — what docs.rs rendered or failed to render;
5. **coverage/debt** — what public API or examples remain under-documented.

Do not let any of the following stand in for an honest answer:
- “docs.rs is green”,
- “`cargo test --doc` passed”,
- “we use `#[cfg(doc)]`”,
- “the example is visible in the docs”,
- or “coverage improved”.

A crate can have all of those and still leave extraction provenance, rewrite honesty, support class, or drift unresolved.

## Added 2026-03-22 (341): dependency lifecycle planning must keep trust, floors, seams, and exits separate

When future revisions touch **P-0535** or adjacent dependency-planning lanes, do not let the archive collapse these into one fake “dependency policy” story:

1. **criticality lane** — where third-party crates are allowed to live;
2. **imported trust/support signal** — advisories, trusted publishing, SLOC, or pubtime context;
3. **toolchain/version floor** — MSRV and lockfile posture;
4. **abstraction seam** — the actual trait/process/FFI/protocol boundary that makes replacement plausible;
5. **transition posture** — pin, contain, fork, vendor, internalize, replace, or manual review.

Do not let any of the following stand in for an honest dependency-lifecycle answer:

- “the crate has no known advisories”,
- “the lockfile is pinned”,
- “we can replace it later”,
- “we forked it”,
- or “there are only a few dependencies”.

A crate can look trustworthy and still sit in the wrong lane, a lockfile can be stable and still hide direct core coupling, and a fork can still be a lifecycle dead end without a named exit path.

## Added 2026-03-22 (383): dependency lifecycle planning must keep override authority, freshness, and exception status separate

When future revisions touch **P-0535** after the initial seam/exception pass, do not let the archive collapse these into one fake “transition plan is in place” story:

1. **override authority** — where the route is declared and who can see it;
2. **source posture** — registry, mirror, vendor subset, fork, or path checkout;
3. **shared reviewability** — checked-in, generated-shared, local-only, CI-only, or manual-only;
4. **imported signal freshness** — whether contextual trust/support facts are still current enough to lean on;
5. **exception reevaluation** — whether the waiver is still active, nearing review, expired, or exit-ready.

Do not let any of the following stand in for an honest lifecycle-transition answer:

- “there is a local `[patch]`,”
- “the dependency is vendored,”
- “the crate had good imported signals last quarter,”
- “an exception was approved once,”
- or “the bundle still exists.”

A local patch may be useful and still not be shared policy, a vendored mirror may still imply zero fork progress, and a typed waiver may still be stale without fresh supporting context.


## Added 2026-03-23 (416): dependency lifecycle planning must keep override authority, selection anchors, and clean-resolve risk separate

When future revisions touch **P-0535** after the override/freshness pass, do not let the archive collapse these into one fake “the transition is durable” story:

1. **override authority** — where the route is declared and who can see it;
2. **selection anchor** — what currently makes the realized route hold (`Cargo.lock`, root patch, local config patch, source replacement, git rev pin, manual step, ...);
3. **sharedness** — whether another maintainer gets the same route from the repo alone;
4. **clean-resolve risk** — what changes if the lockfile is refreshed, the patch disappears, the registry state moves, or `rust-version` context changes;
5. **lifecycle posture** — whether the dependency is actually becoming more contained, more replaceable, or more sticky over time.

Do not let any of the following stand in for an honest lifecycle-transition durability answer:

- “CI is green right now,”
- “the version is in Cargo.lock,”
- “we have a local `[patch]`,”
- “the crate is yanked but our release still works,”
- or “we vendored it.”

A green lockfile may only reflect yesterday’s selection, a local patch may not be shared team policy, a yanked version may still be locked today while future selection is exposed, and a vendor mirror may imply containment without implying transition progress.

## Added 2026-03-22 — support-evidence anti-amnesia guardrails

When working in the toolchain/target lane, do not summarize a project as “supports target X” unless you have checked:

1. override lineage,
2. support class,
3. exercise scope,
4. external prerequisites,
5. **artifact route**, and
6. **host-target topology**.

Specific anti-amnesia rule: never infer that a target lane was fully exercised just because a CI script found a file under `target/` or because docs.rs published a page.

## Added 2026-03-22 (339): interop passes must keep layout authority and error channels explicit

When future revisions touch **P-0121** or neighboring interop/shipkit lanes, do not stop at “supports bindings” or “has FFI.”
Read `meta/cross-language-interop-frontier-2026-03-22.md` and `meta/archive-memory-anchor-2026-03-22.md` first.

Future interop passes should explicitly ask at least six questions:

1. what ownership crosses the boundary,
2. what unwind posture exists,
3. how callbacks execute and tear down,
4. which binding surfaces are actually checked,
5. what representation really crosses and who defines it,
6. how errors / exceptions / panics cross.

Do not let any of these stand in for an honest answer:

- “uses UniFFI”
- “has a C ABI”
- “supports C++”
- “returns Result”
- “bindings are generated”
- “works in Swift/Kotlin/Python/Wasm”

Those are ingredients, not a boundary contract.

## Added 2026-03-22 (338): broad archive refreshes must rerank before they proliferate

When doing a broad “what is Rust still missing?” pass, do **not** jump straight to adding another proposal.
Read `meta/epic-crate-rubric-2026-03-22.md` and `meta/archive-refresh-checklist-2026-03-22.md` first.

Future broad scans should usually do one of three things:

1. deepen an already-strong frontier,
2. rerank and synthesize the frontier,
3. or add exactly one sharply-bounded new lane with explicit artifacts.

Do not let the archive degrade into:

- overlapping micro-proposals,
- score-only ideas without receipts or assumption ledgers,
- or giant “one dashboard for everything” fantasies.


## Added 2026-03-21 (334): crash symbolication work must stay contract-shaped

When revising **P-0101 Crash Artifact & Symbolication Workbench Kit**, do not stop at “Rust already has crash crates.”
Future passes should explicitly ask whether the missing value is the support contract above them:

- **capture-basis receipt**,
- **module-identity receipt**,
- **symbol-route receipt**,
- **analysis-coverage report**,
- **report-determinism receipt**,
- **share-safety receipt**,
- and one compact **crash-bundle manifest**.

Do not confuse:
- a minidump with a replayable crash bundle,
- a function name with a verified symbol route,
- a code-id fallback with a high-confidence debug-id match,
- or “safe share” marketing with a real redaction/inclusion receipt.

## Added 2026-03-21 (333): task supervision must keep topology, triggers, reset, timeout, and bundles separate

When future revisions touch **P-0095** or adjacent supervision ideas, do not let the archive collapse these into one fake “supports supervised tasks” story:

1. **supervision topology** — static/dynamic membership, ordering basis, and restart blast radius;
2. **restart policy** — restart class, trigger classes, backoff, and meltdown windows;
3. **health / readiness basis** — stable-start criteria, liveness basis, and unresponsive-task action;
4. **state reset basis** — template clone, fresh factory, shared external state, or persisted rehydrate;
5. **shutdown escalation** — stop signal, graceful phase, timeout aftermath, and blocking-work posture;
6. **failure bundle** — the receipts and attachments exported for support/review.

Do not let any of the following stand in for an honest supervision answer:

- “uses `JoinSet`”,
- “supports graceful shutdown”,
- “restarts failed tasks”,
- “uses actor supervision”,
- or “has health checks”.

A service can have all of those and still leave blast radius, reset semantics, timeout aftermath, or review artifacts unresolved.

## Added 2026-03-21 (332): OpenAPI 3.1 / JSON Schema toolchain anti-flattening note

When working on **P-0224**, do **not** say only that a crate or fixture "supports OpenAPI 3.1".
Force yourself to classify at least five things separately:

1. **dialect identity** — is the Schema Object posture labeled as the OpenAPI 3.1 dialect or falsely flattened into plain draft-2020-12?
2. **ref-resolution route** — what entry document, base URI, fetch mode, and cache/mirror route produced the graph?
3. **bundle / projection policy** — is this for review, codegen, docs, or gateway import, and what was flattened or rewritten?
4. **compatibility profile** — which downstream consumer profile was actually checked?
5. **semantic-diff authority** — are change facts descriptive only, or tied to a named policy/verdict?

Resist these failure modes:
- treating structural validity as full consumer compatibility,
- treating a flattened generator projection as the authoritative review artifact,
- treating remote ref fetches as invisible implementation detail,
- treating descriptive diffs as self-justifying breaking-change verdicts,
- or treating 3.0.x tolerance as proof of lossless 3.1 fidelity.

Prefer the artifact vocabulary introduced in `fixtures/openapi31-jsonschema-toolchain-kit/` before inventing another vague support-bundle shape.

## Added 2026-03-21 (330): trusted publishing must keep provider scope, claim basis, trigger policy, publish mode, and rehearsal result separate

When future revisions touch **P-0175** or adjacent publish/security lanes, do not let the archive collapse these into one fake “trusted publishing configured” story:

1. **provider scope** — GitHub Actions, GitLab.com, self-hosted/manual-review provider, or future provider;
2. **claim basis** — issuer, audience, repository/project, workflow route, reusable-workflow route, ref, and environment identity;
3. **trigger policy** — eligible, blocked, unsupported, or manual-review-only;
4. **publish mode** — trusted-publishing-only, mixed transition, token fallback, or manual publish;
5. **rehearsal result** — observed pass, blocked, partial, or manual-review-only.

Do not let any of the following stand in for an honest trusted-publishing answer:

- “OIDC is enabled”,
- “the workflow filename matched”,
- “GitLab supports ID tokens”,
- “the crate uses trusted publishing”,
- or “the release passed in CI once”.

A release path can contain all of those truths and still remain blocked on trigger policy, host scope, reusable-workflow route identity, or mixed-mode migration review.

## Added 2026-03-21 (328): async replay support must keep schedule, time, coverage, effects, and fidelity separate

When future revisions touch **P-0073** or adjacent async-replay lanes, do not let the archive collapse these into one fake “supports async replay” story:

1. **schedule basis** — exhaustive model, recorded schedule, seeded scheduler, live trace only, or manual review;
2. **time basis** — wall clock, paused Tokio time, synthetic timeline, imported timestamps, or manual review;
3. **instrumentation coverage** — task/resource/span coverage, lineage propagation, and blind spots;
4. **effect boundary** — which nondeterministic effect classes were captured, stubbed, seeded, or left live;
5. **replay fidelity** — inspection only, timeline reconstruction, narrow effect replay, deterministic local replay, minimized schedule repro, or manual review.

Do not let any of the following stand in for an honest async-replay answer:

- “uses `tokio-console`”,
- “has `tracing` spans”,
- “runs with paused time”,
- “has a seed”,
- or “can replay the stream”.

A bundle can be helpful and still leave schedule authority, effect capture, or fidelity unresolved.


## Added 2026-03-21 (327): native plugin support must keep surface, negotiation, lifecycle, and compatibility witness separate

When future revisions touch **P-0081** or adjacent native-plugin lanes, do not let the archive collapse these into one fake “supports native plugins” story:

1. **ABI surface** — root-module / symbol authority, boundary style, and extensibility posture;
2. **capability negotiation** — required vs optional APIs, negotiation route, and downgrade policy;
3. **lifecycle posture** — load mode, unload truth, reload route, and state persistence;
4. **compatibility witness** — target/version/layout checks, diagnostics coverage, and mismatch evidence.

Do not let any of the following stand in for an honest native-plugin answer:

- “uses `abi_stable`”,
- “can `dlopen` plugins”,
- “supports hot reload”,
- “works across Rust versions”,
- or “loaded successfully in CI once”.

A plugin boundary can be explicit and still leave lifecycle, downgrade behavior, or compatibility proof unresolved.

## Added 2026-03-21 (325): Wasm plugin support must keep interface, grants, budgets, and lifecycle separate

When future revisions touch Wasm plugin work, do not let the archive collapse these into one fake “supports plugins” story:

1. **plugin interface** — WIT package/world identity, host-function surface, and compatibility class;
2. **capability grant** — filesystem, network, host-function, WASI, and config posture;
3. **execution budget** — fuel, epochs, timeout-only control, memory caps, and pool/store limits;
4. **instance lifecycle** — fresh-per-call, pooled reuse, long-lived state, teardown basis, and concurrency posture;
5. **distribution/provenance route** — package name, OCI route, digest, or manual/local-only posture.

Do not let any of the following stand in for an honest plugin-support answer:

- “it builds with cargo component”,
- “it uses Wasmtime”,
- “it is sandboxed”,
- “it has a timeout”,
- or “it is safe because it is WebAssembly”.

A component build can still be experimental, a timeout can still be non-deterministic, and a pool can still reuse stateful instances.

## Added 2026-03-21 (error support is a contract lane, not a renderer lane)

When future revisions notice that Rust already has strong error-handling substrate — such as `thiserror`, `anyhow`, `miette`, `error-stack`, `snafu`, or improved `std::error` context hooks — do not stop at “the ecosystem has error crates already.”

Future revisions must explicitly ask whether the real missing crate is one of these middle layers:

1. an **error-identity contract**,
2. an **audience-mode receipt**,
3. a **remediation-surface report**,
4. or a **sensitivity-posture receipt** for exported reports.

Do not confuse:
- a pretty report with a stable machine/public contract,
- help text with authoritative remediation,
- source chains/backtraces with safe-to-share detail,
- or `derive(Error)` ergonomics with downstream compatibility promises.

A worthy crate contribution may be the thing that makes a project's **error posture legible** without pretending to solve all error handling.

## Added 2026-03-21 (320): async runtime support must keep runtime family, allocation posture, shutdown behavior, and evidence basis separate

When future revisions touch async runtime work, do not let the archive collapse these into one fake “supports async runtime” story:

1. **runtime family** — hosted I/O runtime, cooperative embedded executor, interrupt-priority scheduler, or custom/manual-review runtime;
2. **allocation posture** — heap required, heap optional, static task allocation, shared stack, or mixed/manual-review;
3. **shutdown behavior** — when async tasks stop, what happens to blocking work, what timeout means, and what resources fail after drop;
4. **preemption/timer authority** — cooperative only, priority preemptive, integrated timer queue, hardware timer queue, or external/manual-review;
5. **qualification basis** — documentation only, metrics/instrumentation, on-target measurement, imported assurance artifact, or manual review.

Do not let any of the following stand in for an honest runtime-support answer:

- “uses Tokio”,
- “runs on embedded”,
- “no_std-friendly”,
- “supports graceful shutdown”,
- or “safe for regulated use”.

A runtime choice can be explicit and still leave shutdown aftermath, allocation posture, or evidence basis unresolved.


## Added 2026-03-21 (315): crate health must keep broad status separate from actual maintenance coverage

When future revisions touch crate-health work, do not let the archive collapse these into one fake “maintained crate” story:

1. **broad health profile** — active, reactive, critical-fixes-only, sunset, or manual-review posture;
2. **support horizon** — which versions or change classes are still in scope;
3. **succession posture** — backup, org, transfer, or successor truth;
4. **maintenance coverage** — which invisible work classes are actually covered right now;
5. **imported signals** — security tabs, trusted publishing, SLOC, release dates, or other registry/repo context.

Do not let any of the following stand in for an honest duty-map answer:

- “the crate published last month”,
- “the crate has trusted publishing”,
- “the crate has no known advisories”,
- “the maintainer says it is passively maintained”,
- or “there is a backup maintainer”.

A crate can be honest about support horizon while still leaving CI breakage, docs upkeep, review bandwidth, or security response ownerless.


## Added 2026-03-21 (313): resource support must keep local bounds, sharing scope, and aggregate totals separate

When future revisions touch resource-support work, do not let the archive collapse these into one fake “bounded resource” story:

1. **local bound** — the number attached to one queue, pool, cache, connection, or permit gate;
2. **budget topology** — where that bound lives (`per_instance`, `shared_clone_family`, `per_host`, `per_connection`, `per_runtime`, `process_global`, or topology-dependent);
3. **sharing behavior** — whether cloning another handle shares the same waiting room or silently multiplies it;
4. **aggregate-bound posture** — whether the crate can honestly state a process-wide total at all.

Do not let any of the following stand in for an honest topology answer:

- “the client is cheap to clone”,
- “the pool max is 10”,
- “the server concurrency limit is 32”,
- or “the cache is bounded”.

A per-host pool, per-connection limit, shared-clone-family queue, and independently constructed instance budget are materially different support surfaces even when each is truthfully called bounded.


## Added 2026-03-20 (310): request execution support must keep replay basis, budgets, admission, and topology separate

When future revisions work on **P-0530** or adjacent resilience ideas, do not flatten these four questions into one vague “supports retries” story:

1. **why replay is safe**,
2. **what the attempt budget and time budget really are**,
3. **how admission behaves under load**,
4. **whether attempts are serial or parallel**.

Do not confuse:
- safe-method folklore with explicit idempotency basis,
- per-attempt timeout with overall deadline or retry budget,
- rate limiting with buffering or load shedding,
- or hedged parallel attempts with serial retry.

The sharper move is usually to publish one compact contract for replay basis, attempt budgets, admission path, and attempt topology before inventing another resilience helper.


## 2026-03-20 ffi-boundary reminder

Do not let the archive flatten **P-0121 FFI Boundary & Bindings Conformance Kit** into a generic “Rust has FFI/bindings support” story.
When live bridge and generator substrate is present, keep **ownership-transfer truth**, **unwind-posture truth**, **callback-execution truth**, and **binding-coverage truth** separate.

Do not confuse:
- a borrowed call-only input with an explicit-free output buffer,
- `extern "C"` panic containment with an explicit unwind-capable ABI,
- a continuation/future poll-cancel-free lifecycle with an ordinary sync callback,
- or generated bindings with directly checked bindings.

## 2026-03-20 package-review reminder

Do not let the archive flatten **P-0470 Cargo Package Review Kit** into a generic “we reviewed the tarball” story.
When live Cargo packaging substrate is present, keep **packaged-surface truth**, **archive-authority truth**, **extraction-mutation truth**, **manifest-normalization truth**, and **path-lineage truth** separate.

Do not confuse:
- an authored `Cargo.toml` with generated packaged `Cargo.toml`,
- a retained raw `.crate` with an extracted verification tree,
- `.cargo-ok` or unpack-time mtime changes with archive-byte drift,
- or Cargo’s best-effort VCS snapshot with authority over reviewed package bytes.


## 2026-03-20 open-table-format reminder

Do not let the archive flatten **P-0028 open-table-format-kit** into a generic “Rust supports multiple lakehouse formats” story.
When live Iceberg / Delta / Hudi / DataFusion substrate is present, keep **table-surface truth**, **capability-profile truth**, **storage/catalog wiring truth**, and **integration-coupling truth** separate.

Do not confuse:
- a live catalog-backed provider with a pinned snapshot provider,
- underlying storage support with binding/path wiring,
- one format’s write matrix with another format’s read-focused surface,
- or successful provider registration with a low-coupling integration story.

## 2026-03-20 lifecycle-phase reminder

Do not let the archive flatten **P-0520 Crate Lifecycle Surface Pack Kit** into a generic “graceful timeout support” story.
When live async/task/framework substrate is present, keep **shutdown-phase truth** and **timeout-aftermath truth** separate from barrier and escape-path truth.

Do not confuse:
- a named barrier completing with the whole system becoming quiescent,
- `timeout` returning with the task being cancelled,
- runtime wait abandonment with cleanup completion,
- or surviving blocking work with a harmless implementation detail.

## 2026-03-20 lifecycle-barrier reminder

Do not let the archive flatten **P-0520 Crate Lifecycle Surface Pack Kit** into a generic “graceful shutdown support” story.
When live async/task/framework substrate is present, keep **stop-verb truth**, **shutdown-barrier truth**, **escape-path truth**, **blocking-work caveats**, and **teardown evidence** separate.

Do not confuse:
- sending a stop signal with barrier completion,
- listener shutdown with full protocol/work completion,
- timeout on a `JoinHandle` with task cancellation,
- tracked-task completion with completion of all spawned or upgraded work,
- or a framework graceful-shutdown future with the whole user-visible stop story.

## 2026-03-20 text-input reminder

Do not let the archive flatten **P-0027 text-input-kit** into a generic “Rust GUI text support” story.
When live native IME issues, hidden-input fallbacks, EditContext experimentation, and AccessKit text vocabulary are all present, keep **transaction truth**, **edit-path truth**, **selection-geometry truth**, and **accessibility-mirror truth** separate.

Do not confuse:
- committed text with inline provisional rendering,
- hidden-input fallback with first-class canvas editing,
- candidate-window presence with precise geometry sync,
- or a visible text surface with an accessible text surface.

## 2026-03-20 trust-lens reminder

Do not let the archive flatten **P-0017 Trust Lens** into a single numeric reputation system.
When live registry, advisory, audit, and effect-analysis signals are present, prefer explicit artifacts for **identity risk**, **signal-basis provenance**, **assumption registers**, and **review debt** before adding more “confidence” language.


## Added 2026-03-20 (crate health is a contract lane, not a score lane)

When future revisions notice that the Rust ecosystem has gained richer registry-side support and trust surfaces — such as **security tabs**, **trusted publishing**, **mutable registry metadata discussions**, or more visible **report/support flows** — do not stop at “the registry now shows more information.”

Future revisions must explicitly ask whether the real missing crate is one of these middle layers:

1. a **maintenance-window contract**,
2. a **succession / backup map**,
3. a **support-intent receipt**,
4. or a **health-check report** that keeps imported signals separate from maintainer promises.

Do not confuse:
- recent publish activity with active support,
- trusted publishing with maintainer responsiveness,
- security-tab visibility with a support horizon,
- or pathfinder ranking with stewardship truth.

A worthy crate contribution may be the thing that makes a dependency’s **survivability legible** without pretending to automate the whole social problem.


## Added 2026-03-20 (287): compact public surfaces do not prove exhaustiveness

When **P-0514** is in play, do not let a pack sound exhaustive merely because:

- the exported files are exact,
- the visible summary is traceable,
- and any private material was redacted carefully.

The sharper move is to ask whether any **known-but-not-exported** hazards, receipts, or local-only context exist and to require one **omission register** whenever that absence matters to public interpretation.

---
## Added 2026-03-20 (286): exact citations do not erase authorship buckets

When **P-0514** is in play, do not let a lane sound like one homogeneous source of truth merely because:

- every claim has evidence refs,
- the public summary is traceable,
- or the pack records review provenance somewhere else.

The sharper move is to ask which surfaced bytes are **Cargo-native generated**, **maintainer-authored**, **reviewer-authored**, or **archive-derived** and to keep those trust surfaces explicit.

---
## Added 2026-03-20 (285): release-pair upgrade packs must keep baseline identity separate from exact command truth

Do not let future passes assume that exact package/feature/target/config/session metadata automatically means the checked subject was a clean published baseline.

The sharper move is to ask for one **baseline-state receipt** that says whether the lane was checked from a pinned published release, a reconstructible package extract, a mutable workspace, or an already partially migrated tree, and to downgrade summary/export posture when that baseline is not clean enough for release-pair claims.

---
## 2026-03-20 upgrade-pack refinement — do not infer replayability from posture labels or native origin alone

When **P-0514** is in play, do not let a lane sound replayable merely because:

- the import came from a native Cargo report lane,
- the capture context says `direct_replayable` or `native_storage_replayable`,
- or a copied attachment looks close enough to the native surface.

The sharper move is to ask for one **replay bridge** that says whether a reviewer reruns a command, rerenders from native storage by id, opens a copied attachment, compares manually, or cannot honestly replay the evidence at all.

---
---
## 2026-03-20 upgrade-pack refinement — do not infer single-session certainty from several well-structured receipts

When **P-0514** is in play, do not let a lane sound like one coherent review moment merely because:

- every imported receipt has a capture context,
- native session ids exist somewhere in the import surfaces,
- or the public summary can cite all the relevant evidence refs.

The sharper move is to ask whether those receipts belong to one session family or whether the pack is joining several sessions and therefore owes the reader a visible mixed-session disclosure.

---
## 2026-03-20 upgrade-pack refinement — do not infer public-shareable posture from clean-looking exported files

When **P-0514** is in play, do not upgrade a lane from private/internal to candidate-public or frozen-public merely because:

- the exported summary looks clean,
- the publication-surface manifest is exact,
- or the pack now carries durable public cues.

The sharper move is to ask whether the bundle can also show **how** any required sanitization happened.
If redaction mattered at all, prefer one explicit `redaction.receipt.json` over vague notes about cleanup or “safe for external sharing”.

## Added 2026-03-19 (264): authority-surface packs must keep origin, fallback order, and refusal posture separate

When future revisions sharpen **P-0519** or any adjacent sandbox/capability idea, do not let the archive collapse these three claims into one fake “sandbox-ready” story:

1. **where the power originates** — caller input, injected handle, host-supplied capability, ambient discovery, OS entropy, root-crate backend choice, or manual review;
2. **what fallback order exists** — which route is preferred before the crate widens into more authority;
3. **what denial does** — hard error, degraded mode, silent fallback, retry, or manual review.

Do not let future passes quietly rephrase authority-surface packs as “better cap-std docs”, “better static scans”, or “better sandboxing”. The archive now has a distinct lane for the receiver-facing authority contract, and within that lane it must keep **origin**, **fallback order**, and **refusal posture** explicit.

## Added 2026-03-19 (262): performance-envelope packs must keep metric authority, execution intent, workload lineage, and profile identity separate

When working on **P-0517** or adjacent lanes, do not flatten these four questions into one vague “performance claim”:

1. **which metric rules**,
2. **what kind of run produced the evidence**,
3. **what workload lineage the scenario rests on**,
4. **which profile / harness / environment story actually generated the result**.

Do not let future passes quietly rephrase performance-envelope packs as “better benchmark outputs”, “better CI perf checks”, or “better charts”. The archive now has a distinct lane for the receiver-facing performance contract, and within that lane it must keep **metric authority**, **execution intent**, **workload lineage**, and **profile identity** separate.

## Added 2026-03-19 (260): persistence-surface packs must not blur publication target, metadata retention, and durable publication

When future revisions sharpen **P-0522** or any adjacent durable-state idea, do not let the archive collapse these three claims into one fake “safe save” story:

1. **what object changed** — destination path replaced, symlink replaced, canonical target modified, or manual-review-required;
2. **what identity survived** — permissions, ownership, timestamps, ACLs, xattrs, SELinux context, and similar metadata classes;
3. **what durability boundary was reached** — visible replacement, data sync, metadata sync, transaction commit, remote ack, or manual review.

The existence of temp-file replacement, async file wrappers, or a crash-safe backend is not enough by itself.
Future revisions must keep publication target, identity retention, compatibility authority, and recovery witness as separate review objects.

## Added 2026-03-19 (256): diagnosis-support deepening before adjacent support sprawl

When **P-0525** is already in the archive and the live ecosystem has moved underneath it, prefer adding:

1. **symptom-identity detail**,
2. **first-inspection order**,
3. **instrumentation-compatibility receipts**,
4. **safe capture / bundle-safety examples**,
5. and **release-diffable troubleshooting artifacts**

before inventing another neighboring crate.

Do not mistake any of the following for proof that a new lane exists:

- a missing Tokio Console compatibility receipt,
- a missing support-capture example,
- a missing symptom alias/root-cause distinction,
- a missing triage-order proof artifact,
- or a missing safety verdict for environment/config capture.

The sharper move may still be to deepen the already-promoted diagnosis lane rather than opening another vague debugging-support proposal.

When sharpening **P-0483**, prefer adding product-plan detail, joined release-review artifacts, waiver-expiry rules, and scenario fixtures before inventing another neighboring API analyzer. Keep semver evidence (**P-0244**), public/private dependency boundary work (**P-0431**), and item-level cfg availability (**P-0451**) separate from the joined release verdict.

## Added 2026-03-19 (249): foreign-package frontier saturation must trigger a product-engineering rebalance

When the last several revisions have all strengthened **foreign-package / ship-contract** proposals, future passes must explicitly ask whether the archive is under-investing in:

1. **end-user product engineering** (GUI, accessibility, text, testing),
2. **supportiveness above substrate** (doctor, diff, gate, bundle layers),
3. or other cross-domain receiver-facing lanes that have real substrate but still weak workflows.

Do not let a productive packaging frontier quietly crowd out equally strategic product-level opportunities just because packaging docs are easier for an LLM to keep extending.
A good rebalance candidate often looks like: real substrate exists, multiple ecosystems have partial adoption, and what is still missing is a **reviewable contract/workflow** rather than another abstraction layer.

In the current archive, **P-0087 UI Accessibility Doctor Kit** is exactly such a rebalance candidate.

## Added 2026-03-18 (241): Wasm-component shipping work must separate lineage, world truth, and closure

When a proposal touches **Rust-built Wasm components**, future revisions must state explicitly whether the missing value is primarily about:

1. **target/tooling lineage**,
2. **WIT/package/world version truth**,
3. **composition closure and dependency satisfaction**,
4. **generic runnable surface** such as `wasi:cli/run` or `--invoke`,
5. **custom-host-required posture**,
6. or **broader runtime/portability/performance work** that belongs in adjacent lanes.

Do **not** let the archive silently collapse “`cargo build --target=wasm32-wasip2` worked”, “`cargo-component` produced a component”, “WAC composed something”, and “this bundle is closed and runnable for another team” into one vague component-support claim.

When sharpening **P-0206**, prefer adding product-plan detail, tooling-lineage artifacts, world-lock artifacts, and composition-closure artifacts before inventing another neighboring Wasm crate.

## Added 2026-03-18 (239): Android shipping work must separate build substrate, packaging truth, and policy readiness

When a proposal touches **Rust-on-Android shipping**, future revisions must state explicitly whether the missing value is primarily about:

1. **target / NDK plumbing**,
2. **binding generation**,
3. **library packaging and distribution shape**,
4. **load-readiness / collision diagnosis**,
5. **release-policy readiness** such as page-size requirements,
6. or **final app-graph behavior** that still requires imported context.

Do **not** let the archive silently collapse “`cargo-ndk` works”, “UniFFI generated Kotlin”, “an AAR was assembled”, and “the native library is safely shippable in modern Android releases” into one vague Android-support claim.

When sharpening **P-0168**, prefer adding product-plan detail, ABI-coverage artifacts, load-doctor artifacts, and page-size-compat artifacts before inventing another neighboring mobile crate.

## Added 2026-03-17 (232): guidance-pack productization before support-portal creep

When a recently promoted compile-time support lane still lacks a believable `0.1` build shape, prefer adding a **product-plan note**, **guidance-authority artifacts**, **recovery-origin artifacts**, and **recipe-fidelity artifacts** before proposing another neighboring crate.

In particular, future passes should not mistake any of the following for proof that a *new lane* exists:

1. a missing exact-vs-advisory guidance vocabulary,
2. a missing provenance artifact for recovery hints,
3. a missing fidelity artifact for the supposed smallest-good-path recipe,
4. a missing adapter split for `trybuild`, `ui_test`, rustdoc `compile_fail`, `miette`, or proc-macro helpers,
5. or a missing doctor warning for docs-only guidance.

Do not let the archive spin out a second or third neighboring crate when the sharper move is to make the already-promoted guidance lane more buildable and more falsifiable.

## Added 2026-03-17 (memory observability): keep scope, fidelity, backend capability, and gates separate

When planning or revising memory-observability crates, future passes must explicitly separate:

1. **capture scope** — which phase or window was actually profiled,
2. **backend capability** — allocator interception, heap dump, stats-only, or imported profile evidence,
3. **symbolization fidelity** — how trustworthy callsite attribution is,
4. **regression gate** — which metric can actually fail CI or block release review.

Do not flatten these into one vague “memory profile” claim.
A stats-only capture, a partially-symbolized heap profile, and a scoped profile that misses the interesting background phase are **not** equivalent evidence.

Also keep this lane separate from:
- crate-authored resource/capacity contracts,
- performance-envelope metric-authority work,
- generic observability signal design,
- allocator choice/tuning crates,
- and hosted profiler products.

## Added 2026-03-17 (224): task-first pathfinder scoring must stay distinct from popularity and blessing

When a proposal touches **crate pathfinder / starter-set** work, future revisions must state explicitly whether the product is primarily about:

1. a **task profile and role-coverage artifact**,
2. an **evidence-weight / veto policy**,
3. a **health/trust import**,
4. a **façade crate / curated starter pack output**,
5. or a **governance / blessing / stdlib-expansion** argument.

Future revisions must also keep these decision inputs visibly separate whenever possible:

- **hard vetoes**,
- **task fit**,
- **role coverage**,
- **interop / lock-in fit**,
- **teaching fit**,
- **adoption signal**,
- **health/trust imports**,
- **migration friction**,
- and **uncertainty**.

Do **not** let the archive silently convert “what should this team use for this task?” into “what is the best crate, full stop?”
A good pathfinder crate may use adoption signal as an advisory tie-breaker and still conclude `manual_review_required` when the trade-off is genuinely unresolved.

## Added 2026-03-17 (236): persistence-surface deepening must separate authority, atomicity, and witnesses

When a promoted durable-bytes lane is being refined further, future passes should ask three separate questions explicitly:

1. **What authority backs the compatibility promise?**
2. **What exact atomicity scope is being claimed?**
3. **Was recovery/repair merely declared, or actually witnessed?**

Do not let future passes quietly flatten any of the following into one fake “durable write” story:

- a stable external wire specification,
- a schema snapshot kept under version control,
- revision-history metadata,
- best-effort Serde shape stability,
- no-intermediate-state overwrite semantics,
- same-mount destination replacement,
- fully durable local publication,
- automatic crash recovery,
- and explicit repair tooling.

The sharper move is usually to deepen **P-0522** with clearer compatibility-authority, atomicity-scope, and recovery-witness artifacts rather than inventing yet another neighboring persistence crate.

## Added 2026-03-17 (217): persistence-surface productization before substrate sprawl

When a recently promoted persisted-state support lane still lacks a believable `0.1` build shape, prefer adding a **product-plan note**, **contract-level policy artifacts**, **write-path artifacts**, and **failure-model artifacts** before proposing another neighboring crate.

In particular, future passes should not mistake any of the following for proof that a *new lane* exists:

1. a missing public-vs-cache vocabulary,
2. a missing write-path / temp-file-replace / transaction-commit artifact,
3. a missing failure-model coverage artifact,
4. a missing adapter split for serde / Postcard / `revision` / redb / file-write helpers,
5. or a missing doctor warning for overclaimed durability.

Do not let the archive spin out a second or third neighboring crate when the sharper move is to make the already-promoted persistence lane more buildable and more falsifiable.

## Added 2026-03-17 (213): diagnosis-surface productization before platform creep

When a recently promoted troubleshooting-support lane still lacks a believable `0.1` build shape, prefer adding a **product-plan note**, **symptom taxonomy**, **triage-order artifacts**, and **capture-policy artifacts** before proposing another neighboring crate.

In particular, future passes should not mistake any of the following for proof that a *new lane* exists:

1. a missing symptom vocabulary,
2. a missing triage-order artifact,
3. a missing capture-policy / redaction artifact,
4. a missing adapter split for `miette` / `tracing` / tokio-console / tokio-metrics,
5. or a missing conservative bundle workflow.

Do not let the archive spin out a second or third neighboring crate when the sharper move is to make the already-promoted lane more buildable and more falsifiable.

## Added 2026-03-17 (212): deepen promoted lanes before inventing adjacent ones

When a recently promoted supportiveness lane still lacks a believable `0.1` build shape, prefer adding a **product-plan note** and a few concrete artifacts before proposing yet another adjacent crate.

In particular, future passes should not mistake any of the following for proof that a *new lane* exists:

1. a missing normalization vocabulary,
2. a missing adapter split,
3. a missing command surface,
4. a missing proving-ground scenario family,
5. or a missing adoption staircase for the current proposal.

Do not let the archive spin out a second or third neighboring crate when the sharper move is to make the already-promoted lane more buildable and more falsifiable.

## Added 2026-03-17 (211): crate diagnosis-surface layering discipline

When a proposal touches **crate troubleshooting / diagnosis support**, future revisions must state explicitly whether the missing value is primarily about:

1. **failure-path / compile-time guidance**,
2. **runtime failure handoff**,
3. **observability signal contracts**,
4. **debugger / symbol / visualizer posture**,
5. **receiver-facing diagnosis-surface contracts** (symptom catalogs, self-checks, signal maps, remediation classes, capture bundles, diffs),
6. **downstream testing support**,
7. or a **full incident/support platform**.

Do not let the archive silently collapse “this crate emits traces”, “this crate debugs well in LLDB”, “this crate has an issue template”, and “this crate publishes an official troubleshooting contract” into one vague debugging-support story. The strongest missing crates here are often **contract layers above substrate and below platforms**.

When a pass promotes a new lane in this neighborhood, it should also list at least **two adjacent lanes it considered but did not promote**, so archive memory keeps the boundary sharp.

## Added 2026-03-17 (215): debug-support layering discipline

When a proposal touches **debug support**, future revisions must state explicitly whether the missing value is primarily about:

1. **broad debuggability support contracts** (posture, sidecars, summaries, diffs),
2. **source lookup / path hygiene diagnosis**,
3. **visualizer compatibility**,
4. **runtime troubleshooting / symptom triage**,
5. **crash collection or symbolication backends**,
6. or a **full debugger / IDE integration layer**.

Do not let the archive silently collapse “the build has symbols somewhere”, “the debugger can find sources”, “NatVis or GDB scripts exist”, and “this crate publishes an honest debug-support contract” into one vague debugging story. The strongest missing crates here are often **contract layers above substrate and below platforms**.

When a pass promotes a new lane in this neighborhood, it should also list at least **two adjacent lanes it considered but did not promote**, so archive memory keeps the boundary sharp.

## Added 2026-03-17 (210): crate example-surface layering discipline

When a proposal touches **crate example / adoption support**, future revisions must state explicitly whether the missing value is primarily about:

1. **task-first crate choice** (which crate should I use?),
2. **failure-path / compile-time guidance** (why did I fail and how do I recover?),
3. **configuration/setup support** (which feature/profile/env recipe should I choose?),
4. **downstream testing support** (which fixtures/fakes/scenario corpora should I use in tests?),
5. **docs rendering / docs.rs parity / hosting**,
6. **tutorial publishing platforms**,
7. or **receiver-facing example-surface contracts** (what is the smallest officially supported path to first success, what prerequisites does it have, and what counts as success?).

Do not let the archive silently collapse “the README has examples”, “the docs.rs build works”, “there is a tutorial”, and “this crate publishes an official quickstart contract” into one vague learning-support story. The strongest missing crates here are often **contract layers above docs substrate and below platforms**.

When a pass promotes a new lane in this neighborhood, it should also list at least **two adjacent lanes it considered but did not promote**, so archive memory keeps the boundary sharp.

## Added 2026-03-17 (206): crate lifecycle-surface layering discipline

When a proposal touches **crate lifecycle support**, future revisions must state explicitly whether the missing value is primarily about:

1. **runtime failure handoff** (post-failure support bundles, crash receipts, redaction),
2. **observability / telemetry** (signals, cost, privacy, stability),
3. **authority / ambient powers** (host touchpoints, determinism posture, sandboxability),
4. **receiver-facing lifecycle-surface contracts** (background work, cancel semantics, shutdown obligations, drain recipes, diffs),
5. **structured-concurrency or cancellation substrate** (task groups, propagation, join/abort building blocks),
6. or a **full graceful-shutdown/runtime orchestration framework** (top-level service supervision, signal handling, subsystem trees).

Do not let the archive silently collapse “this crate spawns background work”, “this task can be cancelled cleanly”, and “this runtime can orchestrate shutdown” into one vague lifecycle story. The strongest missing crates here are often **contract layers above primitives and below frameworks**.

When sharpening **P-0520** further, require explicit answers to three separate questions: **what starts the work**, **what stop verbs really do**, and **what evidence proves cleanup completed**. Do not let “supports graceful shutdown” stand in for activation boundaries, detach-on-drop truth, or teardown evidence.

## Added 2026-03-17 (205): crate authority-surface layering discipline

When a proposal touches **crate authority support**, future revisions must state explicitly whether the missing value is primarily about:

1. **compile-time sandbox policy** (build scripts, proc-macros, Cargo execution surfaces),
2. **capability-based runtime substrate** (`cap-std`, explicit handle APIs, host wiring),
3. **static authority scanning** (import heuristics, syscall guesses, lints),
4. **receiver-facing authority-surface contracts** (ambient powers, injection points, determinism modes, recipes, diffs),
5. or a **full sandbox/runtime host platform** (containers, seccomp/Landlock/AppContainer orchestration, policy platforms).

Do not let the archive silently collapse “this crate can be used with capabilities”, “this crate touches ambient state”, and “this org can sandbox it” into one vague authority story. The strongest missing crates here are often **contract layers above substrate and below platforms**.

## Added 2026-03-17 (204): crate observability-surface layering discipline

When a proposal touches **crate observability support**, future revisions must state explicitly whether the missing value is primarily about:

1. **telemetry plumbing** (subscribers, exporters, env/config wiring),
2. **schema governance** (semantic conventions, field naming, linting),
3. **redaction / privacy policy tooling**,
4. **receiver-facing observability-surface contracts** (named signals, stability, cost, sensitivity, recipes, diffs),
5. or a **full observability platform** (collector/backend/dashboard governance).

Do not let the archive silently collapse “this crate emits telemetry”, “this crate’s signals are stable enough to rely on”, and “this org can govern telemetry at scale” into one vague observability story. The strongest missing crates here are often **contract layers above plumbing and below platforms**.

# LLM hygiene & “amnesia resistors”

Goal: make it hard for an assistant (or a human) to accidentally:
- duplicate prior work,
- drift into vague/fictional claims,
- lose key constraints over time.

## Grounding rules
1. **Every proposal must have at least 3 external sources** (URLs) that justify:
   - the pain exists,
   - why existing crates/tools are insufficient,
   - why now (timeliness).
2. Separate **claims** from **speculation**:
   - Claims: must have sources.
   - Speculation: clearly labeled and framed as hypotheses to test.
3. Record a **“Last verified”** date for any ecosystem facts likely to change.

## Reality-check checklist (required before “draft” → “prototyping”)
- [ ] Prior art scan done (crates.io + GitHub + forum threads)
- [ ] “Why this crate, not a cargo subcommand / book / RFC?” answered
- [ ] Minimal dependency strategy described
- [ ] Security model documented (esp. parsing, crypto, network, plugins)
- [ ] Maintenance plan (bus factor, succession plan, triage policy)

## Anti-hallucination repo mechanics
- Add a CI job that fails if:
  - a proposal lacks a `Sources` section,
  - any URL is dead (link checker),
  - front matter is missing required fields.
- Keep a `meta/known-existing.md` file listing “common false gaps” (areas that *feel* missing but already have strong crates),
  updated whenever someone discovers a duplicate.

## Prompts / interaction pattern (recommended)
- When adding a new proposal, the assistant should output:
  1) a short summary,
  2) the exact file path to create,
  3) the full markdown for the file,
  4) the sources list.

## Memory anchors
- `INDEX.md` is the authoritative map.
- Each entry in `entries/` is immutable after 7 days; later corrections go into a new entry with a link back.


## Proposal checklist (required)
For every new `proposals/*.md` entry, include:
- **Persona / who it’s for** (library author, app developer, embedded engineer, etc.)
- **MVP surface** (minimal types + functions + feature flags)
- **Compatibility story** (what it interoperates with; what it intentionally doesn’t)
- **Conformance & fixtures** (what can be tested deterministically; golden files)
- **Path to boring stability** (what must be proven before 1.0; deprecation strategy)
- **Explicit non-goals** (so scope doesn’t explode)

## Web source quality (avoid “citation spam”)
Prefer sources in roughly this order:
1) **Primary docs / crates / repos** (docs.rs, crates.io, official project docs, RFCs, issue trackers)
2) **Foundation / standards bodies** (e.g., OpenTelemetry, Bytecode Alliance, kernel docs)
3) **Well-regarded technical blogs** that contain concrete details (limited)
Deprioritize: SEO blogs, thin summaries, AI-generated posts, and “listicle” pages unless they add unique evidence.

When you must cite a lower-signal source (e.g., a community thread), pair it with at least one primary source that anchors the core claim.



## Added 2026-03-06 (74): standards with conformance surfaces

When a proposal depends on a standards body that already publishes a **test suite, certification process, or validator surface**, record that surface explicitly in the proposal and research ledger. Do not cite only the base specification and then “forget” that the real operational seam is conformance.



## Added 2026-03-06 (75): bridge standards and validator wrapping

When a proposal sits at a boundary between **two standards** (for example JATS → Crossref, BagIt → OCFL, OpenDRIVE ↔ OpenSCENARIO) or between a standard and an **official checker/validator**, record that seam explicitly. Future passes should state whether the Rust crate is meant to:

1. normalize and wrap official validators,
2. add semantic diffs/replay above them,
3. or replace none of them and stay adapter-first.

Do not let the archive silently drift from “evidence/workbench” into “full platform rewrite” just because adjacent tooling exists.



## Added 2026-03-06 (76): drafts versus stable standards

When a proposal spans both a **stable standard** and an **active draft or evolving companion spec** (for example EPUB 3.3 with OPDS 2.0 drafts), future revisions must:

1. pin the stable and draft surfaces separately,
2. say explicitly which parts are validator-backed today,
3. and avoid silently upgrading draft behavior into “core guaranteed support” without new evidence.

Do not let the archive blur the line between “officially standardized and testable now” and “promising but still moving.”


## Added 2026-03-06 (77): crosswalks and multi-surface standards

When a proposal spans **multiple metadata surfaces or protocol layers that are meant to describe the same thing** (for example htsget + refget + Crypt4GH, xAPI + cmi5, or DataCite + CodeMeta + CFF), future revisions must state explicitly:

1. what the shared semantic core is,
2. what is merely a transport/serialization/profile overlay,
3. and where information can be lost or inferred during translation.

Do not let the archive silently blur “same meaning across surfaces” into “same bytes or same schema”. The missing crate is often the **semantic reconciliation and evidence layer**, not yet another parser.


## Added 2026-03-06 (78): validator-first ecosystems and loss accounting

When a proposal lives in an ecosystem that already has an **official validator, conformance tool, or reference renderer/converter** (for example OpenUSD, CityJSON, CF, or notation formats), future revisions must state explicitly:

1. whether the Rust crate wraps that tool or merely imports its outputs,
2. what the crate adds above it (semantic diffs, replay, redaction, lockfiles, loss accounting),
3. and which kinds of information can be **preserved, inferred, or lost** during format conversion.

Do not let the archive silently drift into “new parser/engine” framing when the sharper value is **validator normalization and explainable loss reporting**.


## Added 2026-03-06 (79): layered container/index/transport ecosystems

When a proposal spans a **primary payload format**, a **secondary index or metadata layer**, and a **package or transport surface** (for example WARC + CDXJ + WACZ, miniSEED + StationXML + SeedLink, or MCAP + rosbag2 conversion semantics), future revisions must state explicitly:

1. which layer is the canonical source of truth,
2. which layers are derivative or lossy views,
3. what kinds of semantic drift can occur between them,
4. and which layer the evidence bundle is primarily trying to make reproducible.

Do not let the archive silently flatten “one ecosystem with several linked layers” into “one format”. Many of the best missing crates in this repo are really **boundary workbenches** that make layered correctness portable.


## Added 2026-03-06 (80): base specs versus overlays and capability packs

When a proposal depends on a **stable base specification** plus one or more **overlay layers** (for example market-practice packs, WMO table versions, coordinate conventions, or editor/client capability quirks), future revisions must state explicitly:

1. which layer is the normative base surface,
2. which layers are overlays or profile packs,
3. which findings belong to the base spec versus the overlay,
4. and which exact versions are pinned in the bundle or lockfile.

Do not let the archive silently flatten “standard + overlays + tool behavior” into one undifferentiated thing. Many of the best missing crates here are really **overlay-aware evidence workbenches**.

## Added 2026-03-06 (81): data-model stacks, host subsets, and mixed-stability standards

When a proposal spans a **data model**, a **query or validation surface**, and one or more **host/profile/compatibility overlays** (for example RDF + SPARQL + SHACL, OData protocol + CSDL + payloads, Iceberg REST + Delta feature packs, or Ion + PartiQL host subsets), future revisions must state explicitly:

1. which layer defines the underlying semantic model,
2. which layer is query, validation, or transport behavior over that model,
3. which parts are stable versus still-moving draft surfaces,
4. and which host/profile/capability assumptions are pinned in locks or bundles.

Do not let the archive silently collapse “same ecosystem” into “same semantics”. Many of the best missing crates in this repo are really **semantic-boundary workbenches** that make model/query/profile drift visible and portable.


## Added 2026-03-06 (82): release/profile seams and linked-package boundaries

When a proposal spans a **base standard**, one or more **profile/release overlays**, and a **transport, package, or cross-document linkage layer** (for example ONNX IR + opsets + backends, LwM2M core + object versions + bootstrap flows, HL7 message profiles + MLLP ACK behavior, EDIFACT syntax + directory releases + partner overlays, or OSCAL model families + linked-package identifiers), future revisions must state explicitly:

1. which layer defines the core data model or message semantics,
2. which layer is a release/profile/partner overlay,
3. which layer is transport, packaging, or cross-document linkage behavior,
4. and which exact versions are pinned in the lockfile or bundle.

Do not let the archive silently collapse “same ecosystem” into “same contract”. Many of the best missing crates here are really **release-aware boundary workbenches** that make model/profile/linkage drift portable and explainable.

## Added 2026-03-06 (83): filename highlight parity and codename receipts

When an archive zip filename includes **highlight codenames or topical hints** (for example `sarif`, `onnx`, `oscal`, or similar), each highlighted term must map to at least one of the following within the same pass:

1. a newly added proposal,
2. a materially revised proposal,
3. or an entry note that explicitly explains why the term was considered but not promoted.

Do not let archive filenames drift into accidental fiction. The zip name is part of the archive’s memory surface; future humans and LLMs will infer intent from it whether or not they should.


## Added 2026-03-16 (177): release-surface layering discipline

When a proposal touches **public API release tooling**, future revisions must state explicitly whether the crate is primarily about:

1. **SemVer breakage evidence** (old/new snapshots, witness plans, witness results, judgment receipts),
2. **public dependency boundary truth** (why a dependency is public/private/ambiguous, manifest migration plans, workspace limitations),
3. or a **joined release-review bundle** that imports those lower-level artifacts.

Do not let the archive silently collapse semver witnesses, public-dependency migration, docs/readiness review, and publish gating into one fake “public API tool”. The strongest missing crates here are increasingly **layered coordination artifacts**, not one giant cargo subcommand.


## Added 2026-03-06 (84): substrate versus missing coordination artifact

When a proposal targets a domain where Rust already has **meaningful substrate** (for example an official SDK, protocol bindings, parsers, or early production crates), future revisions must state explicitly:

1. what Rust substrate already exists,
2. what normative or conformance surface exists outside Rust,
3. and what the still-missing crate would add above those pieces (lockfiles, replay, evidence bundles, semantic diffs, validator normalization, or profile packs).

Do not let the archive silently drift into “Rust has nothing here” framing when the sharper and more honest claim is “Rust has pieces, but it still lacks a boring default coordination artifact.”


## Added 2026-03-06 — moving registries/tables and loss surfaces

When a proposal depends on a **core format plus an adjacent registry, table, or usage catalog** (for example HID Usage Tables or profile/version registries), pin the exact revision/date and do not lazily say “the spec” as if one document settled interoperability.

For any format/interchange proposal, explicitly state the **loss surface**:
- what can be preserved exactly,
- what can only be normalized,
- what can silently drift,
- and what may be impossible to round-trip.

Anti-pattern to avoid: “supports format A and format B” with no statement about CRS drift, quantization metadata, usage-table revision, station profile, tokenizer/config sidecars, or similar boundary semantics.


## Added 2026-03-06 (86): stable targets, drafts, and canonical-source discipline

When a proposal lives in an ecosystem with both a **current stable target** and one or more **active drafts / future releases / roadmap items** (for example OCPI 2.3.0 versus 3.0 draft work, or currently deployed AT sync behavior versus ongoing sync updates), future revisions must state explicitly:

1. which version is the **stable MVP target**,
2. which versions are informative future overlays or drafts,
3. and whether a cited source is **normative**, **operational guidance**, or merely **ecosystem commentary**.

Also distinguish **canonical sources** from deprecated or convenience sources:

- official specifications,
- official guidance / validator docs / test-tool docs,
- maintained Rust substrate,
- blogs, webinars, changelog decks, or deprecated ecosystem indexes.

Do not let the archive silently smuggle roadmap chatter or community lore into the same epistemic bucket as the actual contract surface. This repo is partly a memory system for future humans and LLMs; it must preserve which claims were normative, operational, or merely directional.


## Added 2026-03-06 (87): standards maturity, substrate maturity, and living vendor overlays

When a proposal sits in an ecosystem with a **mature standard surface** but only **thin or uneven Rust substrate** (for example FDC3), future revisions must state explicitly:

1. how mature the standard or reference ecosystem is,
2. how mature the Rust substrate is,
3. and which of those two facts is driving the feasibility score.

Also, when a proposal spans a **living standard plus vendor-specific overlays or fallback protocols** (for example WebDriver BiDi with CDP fallbacks), future revisions must state explicitly:

1. which surface is normative,
2. which surface is optional or fallback-only,
3. and which surface is vendor-specific evidence rather than portable contract.

Do not let the archive blur “the standard is mature” into “Rust can adopt this cheaply,” and do not flatten “standard + fallback + vendor domains” into one pretend-homogeneous protocol surface.


## Added 2026-03-06 (84): official SDKs versus coordination-layer crates

When a proposal targets a protocol or ecosystem that already has an **official SDK or reference implementation** (for example MCP), future revisions must state explicitly:

1. whether the missing Rust crate is trying to be another implementation,
2. a conformance/validation layer above the implementation,
3. or an evidence/replay/policy layer above both.

Do not let the archive silently treat “official SDK exists” as either proof that the area is solved or proof that a second SDK is needed. The sharper missing crate is often the **coordination layer** above real substrate.


## Added 2026-03-19 (MCP security docs, experimental extensions, and deployment-guard lanes)

When a proposal targets an ecosystem like **MCP** that now has both **official security/auth guidance** and one or more **experimental extension repositories**, future revisions must state explicitly:

1. which security behaviors are normative in the spec/docs,
2. which hooks or middleware shapes are only experimental,
3. which parts belong to a deployment guard / review crate,
4. and which parts belong to transcript/conformance or host/product UX instead.

Do not let the archive flatten “official security guidance exists”, “experimental interceptor repo exists”, and “Rust should build a deployment guard crate” into one fake already-solved lane.


## Added 2026-03-06 (85): base specs versus profiles, patterns, and house conventions

When a proposal spans a **normative base specification** plus one or more **profiles, patterns, or community conventions** (for example WoT profiles, Frictionless patterns, or SigmaHQ rule conventions), future revisions must state explicitly:

1. which layer is normative and validator-backed,
2. which layer is profile or pattern guidance,
3. which layer is local/house convention,
4. and which of those layers are pinned in the lockfile or bundle.

Do not let the archive silently flatten “widely used practice” into “core standard”. Many good crates here are really **profile/pattern workbenches** that need sharper boundaries than parsers do.


## Added 2026-03-06 (89): quasi-standards, capability matrices, and living overlay catalogs

When a proposal lives in an ecosystem where the “standard surface” is really a mix of a **formal core spec** plus **living compatibility tables, browser/vendor behavior, certification tooling, profile packs, or regional overlays**, future revisions must state explicitly:

1. which parts are the formal normative core,
2. which parts are living compatibility/capability data,
3. which parts are certification or ecosystem workflow overlays,
4. and which exact revisions are pinned in the lockfile or bundle.

Do not let the archive lazily compress “one ecosystem” into “one frozen standard.” In many of these domains, the real missing Rust crate is a **capability-matrix and evidence artifact**, not merely another parser or binding layer.



## Added 2026-03-06 (90): normative cores, companion transforms, and de-facto sidecars

When a proposal spans a **normative core standard** plus one or more **companion transform/workflow specs, drafts, or de-facto sidecars** (for example OpenAPI + Overlay + Arazzo, OpenPGP + WKD + Autocrypt, or MDF/A2L with DBC), future revisions must state explicitly:

1. which layer is the formal normative core,
2. which layer is a companion transform/workflow or discovery surface,
3. which layer is draft, convention, or de-facto sidecar,
4. and which exact revisions are pinned in the lockfile or bundle.

Also state the **loss surface** whenever crossing those boundaries:
- what is preserved exactly,
- what is normalized,
- what is dropped,
- and what is merely inferred or guessed.

Do not let the archive lazily compress “same ecosystem” into “same contract.” Many worthy crates here are really **interpretation-proof workbenches** whose value lies in making companion layers, sidecars, and loss visible.

## Added 2026-03-06 (91): persisted state versus live grants, sessions, and request-scoped overlays

When a proposal spans a **persisted model/state layer** plus one or more **live, request-scoped, session-scoped, or host-mediated overlays** (for example OpenFGA persisted tuples versus contextual tuples, XDG portal capabilities versus live Request/Session objects, or EV charging profile assumptions versus per-session certificate and negotiation state), future revisions must state explicitly:

1. which data is durable and version-pinnable,
2. which data is per-request, per-session, or host-mediated,
3. which parts can be replayed faithfully,
4. and which parts can only be summarized or redacted in evidence bundles.

Also watch for families that share one marketing label but really contain multiple materially different contract layers (for example ODF package/schema/formula, or point-cloud source-model versus export-target constraints).

Do not let the archive silently flatten **persisted policy**, **ephemeral runtime grants**, and **conversion-loss surfaces** into one pretend-homogeneous protocol. Many of the best missing crates here are really **boundary receipts** that make those distinctions portable and explicit.


## Added 2026-03-06 (92): mature external contracts, thin Rust substrate, and multi-layer profile collections

When a proposal lives in an ecosystem where the **external standards/profile surface is already mature** but the **Rust substrate is thin, partial, or uneven**, future revisions must state explicitly:

1. whether the proposed crate depends on mature Rust substrate,
2. whether it is intentionally a **coordination artifact above non-Rust reference ecosystems**,
3. and whether feasibility is driven by a small core schema rather than broad implementation coverage.

Also, when one ecosystem label actually hides a **profile collection or contract stack** (for example Workflow Run vs Provenance Run Crate, generic CloudEvents vs CESQL vs domain families, or Exif vs XMP vs IPTC mapping packs), future revisions must state explicitly:

1. which layer is the normative core,
2. which layer is profile/collection/guidance,
3. which layer is merely a mapping pack, capability matrix, or filter overlay,
4. and which exact revisions are pinned in the lockfile or bundle.

Do not let the archive silently slide from “Rust has few native crates here” to “therefore the opportunity must be a full reimplementation.” Some of the best proposals are **small, high-trust coordination layers** above mature external contracts.

## Added 2026-03-06 (93): boundary receipts for interpretation state, transport state, resolver state, and allocation state

When a proposal lives in an ecosystem where the real failures happen at the boundary between a **payload/artifact** and the **state required to interpret it correctly** (for example profile + symbolization state, sample file + RF metadata, JSON payload + remote `@context`, barcode payload + resolver behavior, or raw billing export + allocation policy), future revisions must state explicitly:

1. what the primary artifact is,
2. what interpretation state sits beside it,
3. which parts of that state are normative versus local/runtime-specific,
4. and which exact pieces are pinned in the lockfile or bundle.

Also state the **boundary receipt** the crate is meant to produce:
- transport receipt,
- context receipt,
- resolver replay,
- allocation receipt,
- symbolization receipt,
- or another similarly narrow artifact.

Do not let the archive lazily jump from “people use this standard/tool today” to “the only remaining opportunity is a full Rust-native implementation.” In many important domains, the missing crate is a **small interpretation-proof artifact layer** that makes runtime state portable and reviewable.


## Added 2026-03-06 (94): syntax is not the whole contract; account for environments, expansion stages, target profiles, and protocol timelines

When a proposal lives in an ecosystem where the external surface looks like “a language or format,” future revisions must check whether the real interoperability contract also depends on one or more of:

1. a **type/environment schema** (for example CEL variables/functions/opaque types),
2. an **authoring/expansion stage** (for example xacro before URDF/SDF normalization),
3. a **target profile or lowering constraint pack** (for example OpenQASM source versus QIR target profiles),
4. a **deliverable/application overlay** (for example IMF package versus OPL/deliverable policy),
5. or a **timeline transcript of protocol events** (for example A2A task/status/event sequences).

Future revisions must state explicitly:
- which layer is the normative syntax/core,
- which layer is environment/profile/overlay state,
- which layer is expansion or lowering history,
- and which exact pieces are pinned in the lockfile or bundle.

Do not let the archive compress “we can parse it” into “we can interoperate with it.” Many worthy crates here are really **environment-proof, lowering-proof, or transcript-proof artifact layers** rather than standalone parsers or SDKs.


## Added 2026-03-07 (95): do not forget Rust’s own seams

When the archive has spent multiple passes productively exploring **external standards, protocols, and file formats**, future revisions must explicitly check whether the more neglected opportunity now lives at one of Rust’s own ecosystem seams, for example:

1. **spec text ↔ executable witnesses**,  
2. **workspace diffs ↔ affected build/test plans**,  
3. **public compiler APIs ↔ reusable fixtures, capability matrices, and evidence bundles**.

Do not let the archive silently drift into the belief that “worthy crate” mostly means “interop wrapper for an outside standard.” Some of the most strategic missing crates are the ones that make Rust itself more **specifiable, explainable, and toolable**.

Also, when official Rust surveys or project goals create new substrate or identify a recurring pain point, prefer asking whether a **small coordination artifact** is missing:
- a witness format,
- a planner receipt,
- a lockfile,
- a capability matrix,
- or a replay/evidence bundle.

Do not jump straight from “the problem is important” to “the answer must be a giant new framework.”


## Added 2026-03-07 (96): when official Rust substrate appears, ask what boring ecosystem default is still missing

When future revisions notice that the Rust project itself has created or is creating meaningful substrate — for example around **sysroot rebuilding**, **public/private dependencies**, **Cargo plumbing phases**, or **safety-critical coverage** — do not stop at “great, upstream is handling it.”

Future revisions must check explicitly whether the real missing crate is now one of the following:

1. a **recipe + lock + receipt** layer,
2. a **migration/explanation** layer,
3. a **phase-schema / interop / drift-receipt** layer,
4. or a **caveat-aware evidence bundle**.

Do not assume that once upstream owns the low-level mechanism, there is no longer room for an epic crate contribution. Very often the highest-leverage remaining contribution is the one that turns new substrate into a **boring, reviewable default** for ordinary maintainers.

Also do not overcorrect in the other direction:
- do not repackage upstream work as a giant replacement framework,
- do not promise maturity that the toolchain does not yet have,
- and do not erase caveats, migration pain, or schema drift from the proposal.



## Added 2026-03-07 (97): when a feature exists, check whether workflow maturity is still missing

When future revisions see that Rust has gained or is gaining a real capability — for example a **sanitizer mode**, a **single-file package shape**, a **shared-cache/build-dir mechanism**, or an **alternative codegen backend** — do not stop at “the feature exists now.”

Future revisions must explicitly ask whether ordinary users still lack one of the following:

1. a **profile** that captures the intended mode of use,
2. a **receipt** that records what actually happened,
3. a **lease or retention policy** for shared artifacts,
4. a **doctor/explainer** for inferred or surprising behavior,
5. or a **fallback matrix** that makes partial support usable instead of mysterious.

Do not confuse:
- raw flags with workflows,
- package shape with reproducibility,
- cache knobs with coordination,
- or backend availability with actionable project policy.

A worthy crate contribution may be the thing that turns an upstream feature into a **boring, reviewable team habit**.

Also do not overclaim maturity:
- keep caveats, inference, fallback, and partial support visible,
- do not silently normalize unsupported states into success,
- and do not pretend internal Cargo/compiler surfaces are stable if they are not.



## Added 2026-03-07 (98): when Rust is exploring a language feature, look for the bridge or witness crate—not just the feature itself

When future revisions notice that the Rust project is actively exploring a language/runtime/compiler feature—such as **smarter rebuild logic**, **reflection/comptime**, **field projections / reborrow traits**, or **Rust/C++ interop mapping**—do not collapse the choice into only two options:

1. “wait for upstream language work,” or
2. “build a giant replacement framework now.”

Future revisions must explicitly check whether the real missing crate is one of these middle layers:

1. a **witness** that records a conservative claim and why it was made,
2. a **bridge** that lets today's ecosystem survive the transition to future substrate,
3. a **semantics testkit** with fixtures and receipts around tricky invariants,
4. or a **boundary evidence kit** for mixed-language / mixed-toolchain seams.

Do not confuse:
- an official roadmap item with a finished workflow for ordinary users,
- an existing implementation helper with a shared evidence standard,
- or a language experiment with an ecosystem migration story.

A worthy crate contribution may be the thing that makes a future Rust capability **legible before it is fully boring**.

Also keep the archive honest:
- do not present speculative language directions as settled,
- do not promise exact correspondence with future compiler behavior,
- and do not erase uncertainty just because a witness or bridge artifact exists.


## Added 2026-03-07 (99): when Rust introduces a new transition surface, look for the ledger, planner, or waiver crate

When future revisions notice that Rust is not merely adding a feature, but opening a **transition surface** — for example:

1. a new compiler mode or solver that changes outcomes,
2. a new package-naming or namespace regime,
3. a “towards stable” systems profile such as Rust-for-Linux,
4. or a growing compile-time capability such as const traits —

future revisions must explicitly check whether the real missing crate is one of these middle layers:

1. a **drift witness**,
2. a **migration planner**,
3. a **readiness profile + waiver bundle**,
4. or a **capability ledger**.

Do not confuse:
- an accepted RFC with a usable migration workflow,
- official docs and tracking issues with a shared artifact story,
- a compiler/language goal with a maintainer-facing receipt,
- or public-API extraction with capability planning.

A worthy crate contribution may be the thing that turns transition-state into a **reviewable ledger**.

Also keep the archive honest:
- do not present implementation work as fully stable if it is not,
- do not erase waivers, caveats, or version-policy constraints,
- and do not assume that because an upstream team owns the mechanism, the ecosystem no longer needs a small coordination artifact.



## Added 2026-03-07 (100): when upstream Rust is still choosing a language path, look for adoption kits and migration ledgers

When future revisions notice that the Rust project is actively choosing among language or compiler paths — for example around **borrow-check precision**, **in-place initialization**, **ergonomic ref-counting**, or **trait hierarchy evolution** — do not collapse the space into only two options:

1. “wait until stabilization”, or
2. “build the final framework now.”

Future revisions must explicitly check whether the real missing crate is one of these middle layers:

1. a **transition witness** that compares old and new behavior conservatively,
2. an **adoption kit** that records address-stability, fallibility, or capture semantics,
3. a **migration ledger** that helps teams map today’s code to tomorrow’s language direction,
4. or a **hierarchy planner** that makes semver and impl-closure consequences reviewable.

Do not confuse:
- an upstream goal with an ordinary maintainer workflow,
- a substrate crate with a migration artifact,
- or active design discussion with proof that nothing ecosystem-level can be built yet.

A worthy crate contribution may be the thing that turns language-design pressure into a **reviewable adoption story** before stabilization.

Also keep the archive honest:
- do not present proposed language directions as settled,
- do not erase ambiguity about future syntax or semantics,
- and do not imply that because a prototype exists, migration is already boring.


## Added 2026-03-07 (101): when Rust turns information into first-class metadata, look for the receipt crate

When future revisions notice that Rust is making some previously implicit surface **first-class or machine-readable** — for example:

1. compilation behavior across serial vs parallel front-end modes,
2. item availability across features/targets/docs contexts,
3. crate customization points via externally implementable items,
4. or safety specifications via contract attributes —

future revisions must explicitly ask whether the real missing crate is one of these middle layers:

1. a **parity lab**,
2. an **availability ledger**,
3. an **adoption/migration kit**,
4. or a **consumer/extraction receipt layer**.

Do not confuse:
- a compiler-team benchmark system with a maintainer-facing adoption workflow,
- visible rustdoc banners with a release-review artifact,
- an accepted language direction with a boring crate-author migration story,
- or a verification tool with a shared contract-consumption substrate.

A worthy crate contribution may be the thing that turns newly exposed Rust metadata into a **reviewable team habit**.

Also keep the archive honest:
- do not present experimental substrate as fully settled,
- do not erase toolchain/version assumptions from receipts,
- and do not let “the compiler can expose this now” collapse into “the ecosystem no longer needs a crate.”



## Added 2026-03-07 (102): raw toolchain surfaces versus boring maintainer workflows

When official Rust work introduces a **flag, unstable mode, JSON output, dep-info surface, or formal-model repository**, future revisions must ask a second question explicitly:

1. can ordinary maintainers review and exchange this as a compact artifact,
2. can external orchestrators consume it without reverse-engineering the toolchain,
3. and can humans tell which assumptions were injected, waived, or left unknown?

Do not let the archive silently equate “rustc/rustdoc/Cargo can now expose something” with “the ecosystem already has a boring default workflow around it.” The missing crate may be the **coherence profile, rewrite receipt, counterexample bundle, or handshake manifest** that makes the raw surface usable.



## Added 2026-03-07 (103): do not mistake a guide, proc macro, or config knob for a maintainer workflow

When future revisions notice that Rust already has:

1. an official migration guide,
2. a proc-macro bridge or helper crate,
3. a configuration file or env-var convention,
4. or a compatibility lint group,

future revisions must explicitly ask a second question:

1. can maintainers rehearse the transition without committing to it,
2. can reviewers see waivers, caveats, and manual-review zones as structured data,
3. can teams compare two recipes or postures without reverse-engineering CI output,
4. and can that evidence be exchanged outside one repository or one local script?

Do not let the archive silently equate “there is already a macro / guide / config file” with “the workflow is already boring.” The missing crate may be the **dispatch-recipe receipt, waiver bundle, field-invariant ledger, or edition rehearsal witness** that makes the raw mechanism usable by ordinary teams.



## Added 2026-03-07 (104): do not mistake a prototype, unstable mode, or goal page for a maintainer workflow

When future revisions notice that Rust already has:

1. a research prototype,
2. an unstable feature or experiment,
3. an accepted project goal with a proof-of-concept,
4. or a fast-moving external tool around an official Rust direction,

future revisions must explicitly ask a second question:

1. can ordinary teams decide whether to adopt it without reverse-engineering research notes,
2. can they record where it falls back or becomes unsound,
3. can they compare two runs or two versions as structured data,
4. and can they hand the result to another human or upstream maintainer as a compact artifact?

Do not let the archive silently equate “there is already a prototype / unstable flag / project-goal page” with “the ecosystem no longer needs a crate.” The missing crate may be the **soundness ledger, schema lock, readiness audit, or finding bundle** that turns experimentation into an ordinary team workflow.

## Added 2026-03-07 (105): do not mistake a binding generator or packaging helper for a boring ship contract

When future revisions notice that Rust already has:

1. a binding generator,
2. a package builder,
3. a cross-compilation helper,
4. or official platform distribution docs,

future revisions must explicitly ask a second question:

1. can maintainers pin the compatibility promise as structured data,
2. can reviewers inspect the platform/interpreter/slice matrix without rerunning CI,
3. can downstream consumers verify origin, checksum, privacy, or ABI posture from one compact artifact,
4. and can the workflow distinguish adjacent-but-different contracts like `abi3` versus free-threaded Python, or generated Swift bindings versus a shipped Apple SDK bundle?

Do not let the archive silently equate “there is already a generator / packager / helper crate” with “the workflow is already boring.” The missing crate may be the **wheel-policy receipt, slice manifest, checksum/origin bundle, or release contract layer** above that substrate.


## Added 2026-03-07 (106): do not mistake tree output, timing HTML, debug logs, or plumbing commands for a boring explanation workflow

When future revisions notice that Cargo already has:

1. a tree view,
2. a timing report,
3. a debug or fingerprint log mode,
4. or a newer plumbing command,

future revisions must explicitly ask a second question:

1. can an ordinary maintainer hand another human one compact artifact that answers **why** a feature, version choice, duplicate build, or rebuild happened,
2. can CI and editor tooling consume the same explanation without scraping human-oriented output,
3. can the artifact separate directly observed Cargo facts from conservative inference,
4. and can two runs or two resolutions be compared without reverse-engineering logs and HTML by hand?

Do not let the archive silently equate “Cargo can show *some* of this somewhere” with “the workflow is already boring.” The missing crate may be the **resolver why-bundle, fingerprint-delta receipt, duplicate-build explainer, or rebuild witness** that turns raw Cargo substrate into an ordinary team habit.


## Added 2026-03-07 (107): do not mistake a file list, VCS snapshot, JSON stream, or unstable output directory for a boring handoff workflow

When future revisions notice that Cargo already has:

1. `cargo package --list`,
2. `.cargo_vcs_info.json`,
3. `--message-format=json`,
4. or an unstable output convenience like `--artifact-dir`,

future revisions must explicitly ask a second question:

1. can a maintainer hand another human one compact artifact that says **what source bundle is being published** and **why its shape changed**,
2. can CI, packagers, or external build systems consume a stable manifest of **what outputs were produced** without rescraping logs,
3. can the workflow distinguish best-effort VCS context from real provenance,
4. and can two package or artifact surfaces be compared without manually unpacking tarballs and target directories?

Do not let the archive silently equate “Cargo can list files / emit JSON / copy outputs somewhere” with “the review or handoff workflow is already boring.” The missing crate may be the **packreview bundle, artifact handoff manifest, sidecar receipt, or publish-surface diff** that turns raw Cargo substrate into an ordinary team habit.


## Added 2026-03-07 (108): do not mistake an official helper that catches many issues for a boring parity workflow

When future revisions notice that an official site or project now provides:

1. documented environment details,
2. a recommended helper command or plugin,
3. builder/reproduction instructions,
4. or explicit configuration knobs for hosted behavior,

future revisions must explicitly ask a second question:

1. can a maintainer capture **what was tried** as one compact artifact,
2. can they compare local preflight facts against hosted facts without rereading many docs pages,
3. can they attach the result to CI, release review, or upstream issue reports,
4. and does the workflow stay honest when the official helper itself says it is only an approximation?

Do not let the archive silently equate “there is now an official helper or reproduction guide” with “the workflow is already boring.” The missing crate may be the **parity receipt, limit report, drift bundle, or issue handoff artifact** above that substrate.

## Added 2026-03-07 (109): do not mistake stable policy tables for a boring rollout workflow

When future revisions notice that Cargo or Rust now has:

1. a stable manifest/config table,
2. workspace inheritance for that table,
3. an emerging nightly extension of that table,
4. or project-team discussion about broader semantics,

future revisions must explicitly ask a second question:

1. can a team see the **effective inherited policy** package-by-package,
2. can they stage the rollout from advisory to blocking without reading many manifests and CI logs by hand,
3. can waivers be owned, expired, and diffed as structured data,
4. and can stable and nightly policy surfaces coexist without pretending they are equally mature?

Do not let the archive silently equate “there is a stable config surface now” with “the adoption workflow is already boring.” The missing crate may be the **inheritance matrix, waiver ledger, rollout diff, or policy receipt** above that substrate.


## Added 2026-03-07 (110): do not mistake Cargo config substrate for a boring support workflow

When future revisions notice that Cargo already has:

1. hierarchical config probing,
2. include graphs,
3. environment-variable and `--config` overrides,
4. or an official `cargo config` inspection command,

future revisions must explicitly ask a second question:

1. can a maintainer hand another human one compact artifact that shows the **effective config** and **where each winning value came from**,
2. can that artifact be safely attached to CI or support tickets without leaking credentials, provider arguments, or sensitive paths,
3. can path-root and include-graph surprises be explained without manually rereading Cargo docs,
4. and can two runs be compared without hand-merging many config files and env vars?

Do not let the archive silently equate “Cargo documents configuration well” or “nightly can print config values” with “configuration debugging is already boring.” The missing crate may be the **effective-config receipt, origin trace, include graph, or redacted support bundle** above that substrate.

## Added 2026-03-07 (111): do not mistake mergeable docs substrate for a boring handoff workflow

When future revisions notice that rustdoc or Cargo now has:

1. `doc.parts` or similar mergeable cross-crate docs substrate,
2. merge/finalize/include flags,
3. parallel or split documentation build support,
4. or explicit motivation around large workspaces and non-Cargo build systems,

future revisions must explicitly ask a second question:

1. can a maintainer hand another human one compact artifact that says **which parts were produced and which were merged**,
2. can CI or external build systems verify toolchain compatibility and completeness without scraping directories by hand,
3. can final docs-surface drift be compared without reverse-engineering `target/doc`,
4. and does the workflow stay honest about unstable rustdoc internals and mixed-version incompatibility?

Do not let the archive silently equate “rustdoc has mergeable-info flags now” with “cross-crate docs handoff is already boring.” The missing crate may be the **`doc.parts` manifest, compatibility report, finalize receipt, or split-pipeline handoff bundle** above that substrate.


## Added 2026-03-07 (110): do not mistake raw docs metrics or registry metadata for a boring maintainer workflow

When future revisions notice that Rust now has:

1. rustdoc coverage JSON,
2. rustdoc JSON types,
3. package checksums in the registry index,
4. trusted publishing, trusted-publishing-only mode, or `pubtime`,

future revisions must explicitly ask a second question:

1. can a maintainer hand another human one compact artifact that says **which public docs regressed** and **why that regression matters**,
2. can a maintainer hand another human one compact artifact that says **what local package was reviewed**, **what the registry observed**, and **how the release was authorized**,
3. can two docs or release events be compared without re-reading raw tool output, CI logs, and index entries by hand,
4. and can the artifact stay honest about what was measured versus inferred?

Do not let the archive silently equate “rustdoc emits coverage JSON” with “docs review is already boring.”
Do not let the archive silently equate “the registry has checksums and trusted publishing” with “post-publish release history is already boring.”

The missing crate may be the **docs-review bundle** or the **publish-receipt join layer** that turns those raw signals into an ordinary maintainer habit.


## Added 2026-03-07 (112): do not mistake built-in warning reports or raw sidecars for a boring workflow contract

When future revisions notice that Cargo already has:

1. a dedicated report surface for future incompatibilities,
2. config knobs around when those reports are shown,
3. machine-readable primary-artifact output,
4. or sidecar-producing features such as SBOM precursor emission,

future revisions must explicitly ask a second question:

1. can a maintainer hand another human one compact artifact that says **who owns each unresolved future-incompat finding**,
2. can waivers expire, diff, and survive beyond one terminal run,
3. can a maintainer hand another tool one compact artifact that says **which companion files belong to which primary artifact**,
4. and can sidecar schema drift be reviewed without rediscovering filename conventions by hand?

Do not let the archive silently equate “Cargo can print a future-incompat report” with “dependency-risk triage is already boring.”
Do not let the archive silently equate “Cargo emits SBOM precursor files” with “artifact sidecar handoff is already boring.”

The missing crate may be the **future-incompat ledger** or the **artifact sidecar contract** that turns those raw signals into an ordinary maintainer habit.


## Added 2026-03-07 (112): do not mistake built-in cache GC or stable doctest runners for a boring maintainer workflow

When future revisions notice that Cargo has gained or stabilized a maintenance surface — for example **global-cache garbage collection** — do not stop at “Cargo can already clean caches now.” Ask instead:

1. can a team see a **normalized inventory** of what exists,
2. can it compute a **dry-run plan** before deletion,
3. can it record **exemptions and policy** in versioned form,
4. can it diff cleanup behavior across toolchain or environment changes,
5. and can the result travel as a compact support artifact rather than a shell transcript?

Do not let the archive silently equate “Cargo has GC” or “a third-party cleaner exists” with “Cargo-home storage governance is already boring.” The missing crate may be the **cache inventory, GC plan, exemption ledger, or cleanup receipt** above that substrate.

Likewise, when future revisions notice that rustdoc/Cargo gained execution substrate — for example stable **`--test-runtool`** hooks, target-specific doctest ignores, or cross-target doctest execution — do not stop at “special-environment docs tests are solved now.” Ask instead:

1. can maintainers declare a **runner profile** rather than encode shell folklore,
2. can they review a **target matrix** of run/compile-only/ignore expectations,
3. can they audit `ignore-*` annotations for drift,
4. can they capture one **execution receipt** with runner/toolchain context,
5. and can they diff policy/results across releases?

Do not let the archive silently equate “stable runner flags exist” with “cross-target docs maintenance is already boring.” The missing crate may be the **runner profile, ignore audit, target matrix, or doctest receipt** above that substrate.


## Added 2026-03-07 (113): do not mistake real shipkits or analyzers for a boring review workflow

When future revisions notice that Rust already has strong artifact builders or analyzers — for example:

1. PyO3 + maturin for Python wheels,
2. UniFFI + XCFramework/SwiftPM packaging for Apple SDKs,
3. `cargo-semver-checks` for semver analysis,
4. `cargo-public-api` for public-surface diffs,
5. rustdoc coverage JSON and public/private dependency work,

future revisions must explicitly ask a second question:

1. can a maintainer hand another human one compact artifact that says **what promise this release makes to consumers** and **how that promise drifted**,
2. can a maintainer hand another human one compact artifact that says **what public contract they are shipping** and **whether it matches their semver/docs/dependency story**,
3. can waivers, intended breaks, and manual-review zones survive beyond one CI log,
4. and can downstream consumers understand impact without re-reading raw build or analysis output?

Do not let the archive silently equate “artifacts can be built” with “foreign-SDK release review is already boring.”
Do not let the archive silently equate “an analyzer exists” with “public-surface release review is already boring.”

The missing crate may be the **release-promise drift bundle** or the **public-API readiness bundle** that turns those raw capabilities into an ordinary maintainer habit.


## Added 2026-03-07 (114): do not mistake support knobs or individual verifiers for a boring team workflow

When future revisions notice that Rust already has explicit support substrate — for example:

1. `rust-toolchain.toml` and rustup override rules,
2. installable profiles, components, and targets,
3. docs.rs target/feature/rustdoc metadata,
4. target-tier documentation expectations,

future revisions must explicitly ask a second question:

1. can a maintainer hand another human one compact artifact that says **what toolchain/target/docs contract the repo actually supports**,
2. can contributors tell which components or targets are **required versus optional**,
3. can support drift be reviewed without diffing CI YAML, docs.rs metadata, and toolchain files by hand,
4. and can the artifact stay honest about `ci_verified`, `docs_only`, `compile_only`, or `manual_setup_required` states?

Do not let the archive silently equate “toolchain files exist” with “support policy is already boring.” The missing crate may be the **toolchain/target support contract** above those knobs.

Likewise, when future revisions notice that Rust already has several meaningful verification tools — for example Miri, Kani, Creusot, Prusti, Flux, Verus, or runtime instrumentation around UB/sanitizer-era work — do not stop at “verification tools already exist.” Ask instead:

1. can a maintainer hand another human one compact artifact that says **which obligations were covered by which lane**,
2. can assumptions, trusted functions, stubs, axioms, and waivers survive beyond one CI log,
3. can proof, dynamic evidence, unsupported status, partial correctness, and manual review remain visibly distinct,
4. can the campaign explain **why it is green, yellow, or red** instead of only dumping raw tool outcomes,
5. and can two verification campaigns be compared without hiding tool-version, scope, or trust-surface drift?

Do not let the archive silently equate “many verifiers exist” with “verification campaigns are already boring.” The missing crate may be the **verification campaign workbench** above those tools, with explicit lane semantics and policy gates.


## Added 2026-03-07 (115): debugger substrate versus debuggability contract

When a proposal touches Rust debugging, future revisions must state explicitly:

1. which parts are **compiler/build knobs** (`debug`, `split-debuginfo`, `strip`, `trim-paths`),
2. which parts are **artifact layout facts** (embedded debuginfo, `pdb`, `dSYM`, `dwp`, `dwo`),
3. which parts are **debugger-UX extras** (visualizers, pretty-printers, batch scripts),
4. and what support posture the resulting build actually offers (`interactive debugger`, `backtrace only`, `symbolication only`, or `manual review`).

Do not let the archive silently equate “Rust exposes debuginfo knobs” or “debugger visualizers exist” with “debugging support is already boring.” The missing crate may be the **support contract and symbol receipt** above those pieces.

## Added 2026-03-07 (115): producer-side release promises versus consumer-side diagnosis

When a proposal touches Rust-built foreign SDKs, future revisions must state explicitly:

1. which concerns are **producer-side release promises** (supported wheel tags, slices, checksums, privacy posture),
2. which concerns are **consumer-side environment facts** (interpreter/platform/ABI/target tuple),
3. which mismatches are hard **spec incompatibilities** versus softer **ecosystem-policy or review requirements**,
4. and whether the proposal is trying to help the producer, the consumer, or both.

Do not let the archive silently collapse **release-promise drift** and **downstream intake diagnosis** into one undifferentiated tool. They are adjacent, but they are different workflow seams.


## Amnesia resistors — lower-bound witnesses and build-dir transitions

1. Do **not** let future passes equate “Cargo has `direct-minimal-versions`” or “Cargo has `implicit_minimum_version_req`” with “maintainers already have a boring lower-bound workflow.” The missing crate may still be the **policy / blame / waiver / diff witness** above those pieces.
2. Do **not** let future passes equate “`build.build-dir` is stable” or “`-Zbuild-dir-new-layout` exists” with “Cargo-adjacent tools already have a safe migration story.” The missing crate may still be the **consumer audit / path contract / transition receipt** above that evolving layout.
3. When a proposal touches Cargo internals, explicitly ask whether the sharper missing value is:
   - a final-artifact handoff,
   - a shared-cache/lease policy,
   - a live rebuild explanation,
   - or a build-dir consumer transition story.
   Do not silently collapse those into one undifferentiated Cargo-tools blob.


## Amnesia resistors — live contention witnesses and visualizer compatibility

1. Do **not** let future passes equate “Cargo has locks” or “rust-analyzer has a target-dir workaround” with “developers already have a boring answer to what is blocking them right now.” The missing crate may still be the **lock-wait / collision / mitigation witness** above those pieces.
2. Do **not** let future passes equate “`build-dir-new-layout` exists” with “contention diagnosis is solved.” A future Cargo layout can improve locking without giving maintainers one compact artifact for current wait chains.
3. When a proposal touches Cargo performance, explicitly ask whether the sharper missing value is:
   - rebuild causality,
   - cache governance / GC,
   - build-dir consumer migration,
   - or a live lock-contention witness.
   Do not silently collapse those into one generic Cargo-tools blob.
4. Do **not** let future passes equate “`#[debugger_visualizer]` is stable” with “debugger visualizer compatibility is already boring.” The missing crate may still be the **backend matrix / render-golden / drift receipt** for those assets.
5. When a proposal touches debugging, explicitly ask whether it is about:
   - formatter-pack UX,
   - broad debuggability support posture,
   - or visualizer-asset compatibility.
   Do not silently collapse those into one vague debugger-tools bucket.



## Amnesia resistors — registry-auth diagnosis and source-path hygiene

1. Do **not** let future passes equate “Cargo has credential providers” or “authenticated sparse registries exist” with “registry-auth support is already boring.” The missing crate may still be the **provider-chain / operation-stage / redacted diagnosis receipt** above that substrate.
2. Do **not** let future passes equate “trusted publishing exists” with “Cargo auth failures are mostly solved.” Publish identity is only one stage; login, index access, download, search, and publish can still fail for different reasons and need a compact shared diagnosis artifact.
3. When a proposal touches Cargo registries, explicitly ask whether the sharper missing value is:
   - a registry implementation or reference server,
   - trusted-publishing enablement,
   - post-publish provenance and release receipts,
   - or **client-side registry-auth diagnosis**.
   Do not silently collapse those into one generic registry-tools blob.
4. Do **not** let future passes equate `--remap-path-prefix`, trim-paths, or installable `rust-src` / `rustc-dev` components with “debugger source lookup is already boring.” The missing crate may still be the **path-hygiene / virtual-source / component-hint receipt** above those pieces.
5. When a proposal touches debugging, explicitly ask whether it is about:
   - broad debuggability support posture,
   - visualizer compatibility,
   - symbol-sidecar handling,
   - or **source-path and source-lookup contracts**.
   Do not silently collapse those into one vague debugger-tools bucket.



## Amnesia resistors — tool-only compile surfaces and artifact-dependency adoption

1. Do **not** let future passes equate “Cargo has `--compile-time-deps`” with “editor and wrapper workflows are already boring.” The missing crate may still be the **tool-build / parity / fallback receipt** above that mechanism.
2. Do **not** let future passes equate “RFC 3477 says `cargo build` is the guarantee boundary” with “there is no workflow seam left.” That policy boundary is exactly why maintainers may still need a compact artifact explaining what a tool-only workflow did and when it must fall back.
3. When a proposal touches Cargo/IDE workflow friction, explicitly ask whether the sharper missing value is:
   - a live lock-contention witness,
   - a rebuild-causality explanation,
   - a build-dir consumer transition,
   - or a **tool-only compile-surface / parity / fallback** artifact.
   Do not silently collapse those into one generic Cargo-devtools bucket.
4. Do **not** let future passes treat `rust-analyzer.cargo.targetDir` as if it fully explains root policy. `target-dir` isolation, `build-dir` isolation, and live lock-contention are adjacent but distinct truths.
5. If a future pass imports Cargo build-analysis sessions into **P-0494**, it must keep that as **optional supporting evidence**. An imported session link does not silently upgrade a tool-facing run into the stronger `cargo build` guarantee line.
6. Do **not** let future passes equate Cargo artifact-dependency RFCs or unstable `bindeps` docs with “artifact consumption is already boring.” The missing crate may still be the **artifact contract / target matrix / env-var / stable fallback** layer above that substrate.
7. When a proposal touches Cargo artifacts, explicitly ask whether it is about:
   - final-artifact handoff,
   - sidecar attachment,
   - external toolchain orchestration,
   - or **artifact-dependency adoption**.
   Do not silently collapse those into one vague artifact-tools blob.



## Amnesia resistors — vendored-source parity and CPU support contracts

1. Do **not** let future passes equate “Cargo has `cargo vendor`” or “source replacement exists” with “vendored or source-replaced dependency workflows are already boring.” The missing crate may still be the **source-origin / registry-equivalence / offline-readiness** artifact above that substrate.
2. Do **not** let future passes equate “a workspace builds with vendored sources once” with “its offline or hermetic claim is honest.” Patch overlays, git/path dependencies, and layered source config can still make the support story much messier.
3. When a proposal touches Cargo dependency sources, explicitly ask whether the sharper missing value is:
   - a mirror or registry,
   - a reproducible package/publish review bundle,
   - an air-gap transfer/mirroring toolkit,
   - or a **vendored/source-parity and offline-honesty receipt**.
   Do not silently collapse those into one generic supply-chain blob.
4. Do **not** let future passes equate `target-cpu`, `target-feature`, or runtime feature detection with “hardware support promises are already boring.” The missing crate may still be the **baseline / dispatch / fallback / illegal-instruction-risk** artifact above those mechanisms.
5. When a proposal touches CPU tuning or SIMD-adjacent work, explicitly ask whether it is about:
   - whole-program ABI coherence,
   - toolchain/target support policy,
   - release-promise drift for foreign SDKs,
   - or a **CPU baseline and runtime-dispatch support contract**.
   Do not silently collapse those into one vague performance-tools bucket.

## Amnesia resistors — foreign package ecosystems beyond Python and Apple

1. Do **not** let future passes equate “a good binding generator exists” with “the package-manager-specific release contract is already boring.” Node/npm and NuGet both show that the missing crate may still be the **runtime/RID contract, artifact manifest, loader receipt, and support-risk bundle** above binding generation.
2. When a proposal touches a foreign ecosystem, explicitly ask whether the sharper missing value is:
   - raw binding generation,
   - producer-side package/release contracts,
   - consumer-side intake diagnosis,
   - or cross-release drift review.
   Do not silently collapse those into one vague “interop tools” bucket.
3. Keep **ABI substrate**, **artifact layout rules**, **loader/probing behavior**, and **support promises** visibly separate. A mature foreign ecosystem can have strong answers to the first two while still lacking a boring maintainer workflow for the last two.



## Added 2026-03-08 (122): modern JVM native access is part of the shipping contract

When future revisions consider Rust→JVM native shipping, do **not** stop at “`jni-rs` exists” or “Maven classifiers can carry native artifacts.”

Modern Java makes native loading a more explicit **restricted/native-access** surface, so future passes must keep at least these facts visible:

1. the **classifier / OS / arch / libc matrix**,
2. the **library base name** the Java side expects,
3. the **loader strategy** (`System.loadLibrary`, `System.load`, resource extraction, or manual install),
4. the **native-access / restricted-method posture**, and
5. whether the package is really a **desktop/server JVM ship contract** or is actually Android/AAR territory already covered elsewhere.

Do not let the archive silently collapse **JNI binding generation** into **boring package-manager-specific shipping**. Those are different seams.


## Added 2026-03-08 (123): RubyGems authoring substrate is not the same as a boring gem release contract

When future revisions consider Rust→Ruby packaging, do **not** stop at “`rb-sys` exists”, “`magnus` exists”, or “rake-compiler can build native gems.”

Those are only substrate.

- Do **not** let future passes equate `rb-sys`, `magnus`, or oxidize-rb authoring substrate with “Rust-backed Ruby gem shipping is already boring.” The sharper seam may still be the **platform matrix / gemspec receipt / Bundler support contract** above those pieces.
- When a proposal touches Ruby packaging, explicitly ask whether the missing value is:
  - authoring substrate,
  - fat-gem release contracts,
  - source-build fallback honesty,
  - Bundler lock/platform support receipts,
  - publish-identity posture,
  - or downstream diagnosis.
  Do not silently collapse those into one generic “Ruby integration toolkit.”
- Future passes must keep at least these facts visible:
  1. the **Ruby implementation support posture** (MRI, JRuby, TruffleRuby, fallback-only, or unsupported),
  2. the **gem platform / binary-gem matrix** that was actually shipped,
  3. the **source-build versus precompiled-binary posture**,
  4. the **extension filename / require-path / packaged load-location contract**, and
  5. the **RubyGems build/rebuild and publish-identity facts** that make support honesty reviewable.
- Do **not** let future passes treat “the gem installed once on my machine” as evidence of a boring release contract. The archive cares about **publishable support truth**, not one happy-path installation.

Do not let the archive silently collapse **Rust-side extension authoring** into **boring RubyGems-native shipping**. Those are different seams.


## Added 2026-03-08 (124): Hex / BEAM native package contracts

When a proposal targets Rust-backed Hex packages or BEAM NIF distribution, future revisions must record separately:

1. the **Hex package tarball** facts (package metadata, file inclusion, checksum, size posture),
2. the **precompiled NIF matrix** and checked-in checksum discipline,
3. the **loader behavior** (`erlang:load_nif`, `priv` path expectations, or `rustler_precompiled` module config),
4. the **OTP / Elixir support window**,
5. and the **source-build fallback** story.

Do not collapse “precompiled NIFs exist” into “the support contract is solved”. The missing crate is often the boring **receipt that joins Hex, RustlerPrecompiled, and loader truth into one reviewable bundle**.

## Added 2026-03-08 (125): frontier saturation means upgrade top proposals, not just add more count

When the frontier has already identified a small set of **top-ranked adjacent proposals** (for example the Cargo explainability stack), future revisions should prefer one of these moves before adding another proposal:

1. add fixture/schema stubs,
2. write an explicit incubation-order note,
3. harmonize receipt vocabulary across adjacent proposals,
4. or tighten the roadmap around which one should plausibly ship first.

Do not let the archive drift into “research means proposal count goes up.” In a mature archive, some of the best work is to turn the strongest ideas into **more buildable contracts** rather than adding another entry to the pile.


## Added 2026-03-08 (126): debug substrate is not yet a boring debug support contract

When future revisions touch debugging, do **not** stop at “Cargo profiles exist”, “`#[debugger_visualizer]` exists”, or “`rust-src` can be installed.” Those are substrate, not the whole workflow.

Future passes should explicitly ask whether the sharper missing value is:

1. a **broad debuggability support contract** (support posture, symbol layout, drift),
2. a **source-path and source-component diagnosis bundle** (`trim-paths`, remaps, `rust-src`, `rustc-dev`),
3. or an **embedded visualizer compatibility matrix**.

Do not silently collapse those into one vague debugger-tools bucket, and do not default back to “invent a better debugger” framing when the archive has already found the stronger seam.


## Added 2026-03-08 (127): build.rs substrate is not yet a boring native-build workflow

When future revisions touch `build.rs`, `-sys` crates, or native dependency probing, do **not** stop at “Cargo documents build scripts,” “`cargo::error` exists,” or “`system-deps` exists.” Those are substrate, not the whole workflow.

Future passes should explicitly ask whether the sharper missing value is:

1. a **build-script report / policy layer** (concise summaries, typed diagnostics, workspace gates),
2. a **hermetic build-script test harness** (fixtures, fake tools, normalized directives),
3. or a **declarative native dependency contract** (backend attempts, doctor UX, support truth).

Do not silently collapse those into one vague “improve build scripts” bucket, and do not default to another thin `pkg-config` wrapper when the archive has already identified stronger seams above the raw probing substrate.
Also do not silently assume every `build-script-executed` JSON message came from a live run; Cargo may surface cached build-script results, so report-oriented crates should carry capture-origin semantics instead of overclaiming freshness.

## Added 2026-03-08 (128): once a stack exists, add example bundles before adding another proposal

When a frontier already has a good stack shape, future passes should prefer:

1. one small **example bundle** that shows what another person would actually receive,
2. one or two missing schema files that close obvious artifact gaps,
3. and one implementation brief that pins down crate splits / CLI / API surfaces.

Do not keep “planning” at the level of renamed bullets once the archive already knows the likely crate family.


## Added 2026-03-08 (129): layer on upstream Cargo before inventing a parallel tooling universe

When future revisions sharpen a Cargo-adjacent frontier, first ask which **official Cargo surfaces already exist** (`cargo metadata`, `--message-format=json`, config overrides, unstable tracking surfaces, package metadata, etc.).

Do not default to writing crate proposals as though Cargo exposes nothing machine-readable and every useful tool must invent a new protocol from scratch.

For the current native-build frontier in particular:

1. treat build-script JSON/event substrate as real substrate,
2. treat `target.<triple>.<links>` override/handoff as a first-class workflow,
3. treat `metabuild` / `multiple-build-scripts` as a reason not to overfit to one handwritten `build.rs` file,
4. and prefer **receipts, summaries, fixture harnesses, and migration-friendly contracts** over Cargo replacement fantasies.


## Added 2026-03-08 (130): new upstream `cargo report` surfaces do not erase the missing support-layer crate

When future revisions touch Cargo build performance, rebuild explainability, or tool/workflow parity, do **not** stop at “Cargo now has `-Zbuild-analysis` and `cargo report`.” Those are substrate, not the whole support workflow.

Future passes should explicitly ask whether the sharper missing value is:

1. a **stable session-import / rebuild-bundle layer** above evolving nightly Cargo reports,
2. a **resolver / graph-choice cause-chain layer** that reuses the same receipt vocabulary,
3. or a **tool-invocation parity layer** that compares tool-only and fuller-build sessions honestly.

Do not let the archive swing from “Cargo exposes nothing” to “Cargo solved it.” The interesting middle is often the crate that freezes unstable upstream signals into one boring support artifact.

## Added 2026-03-08 (131): do not collapse support bundles and historical warehouses

When a future pass touches Cargo explainability, explicitly decide whether the missing thing is:

1. a **support bundle for one run or two runs** (P-0469), or
2. a **historical imported-session warehouse and regression adjudicator** (P-0035).

Those are adjacent, but they are not the same crate.

A good smell for **P-0469**: the question sounds like "why did this rebuild today?"

A good smell for **P-0035**: the question sounds like "when did this start regressing, how often, and compared to which baseline series?"

If a pass cannot answer that distinction, it should sharpen the layer boundary before it proposes another Cargo-performance crate.

## Added 2026-03-21 (196): comparison-window truth is not the same as series compatibility

When future revisions touch **P-0035 cargo-build-insights**, they must state explicitly:

1. why a baseline/head or rolling window was selected,
2. who that window is for (PR review, release review, rolling branch health, or local experiment),
3. whether the selected sessions were comparable enough to stand as one lane,
4. and whether any redaction/export posture changed the bundle's review audience.

Do **not** let the archive silently collapse these into one fake “regression result.”
A good smell for **P-0035** is a bundle that names both the **comparison window** and the **series-compatibility judgment** separately.


## Amnesia resistors — cargo tool-workflow stack

1. Do **not** collapse **P-0494** (tool-build parity / fallback), **P-0490** (live lock contention), and **P-0489** (build-dir consumer transition). They are adjacent, not interchangeable.
2. If a future pass says “Cargo IDE/tooling still hurts,” force it to name which of the following is missing:
   - what the tool-facing workflow actually built,
   - who blocked whom on which cache root,
   - or which consumer still scrapes Cargo internals.
3. Prefer shared vocabulary (`workflow_role`, `target_dir_policy`, `manual_review_required`) over inventing a fresh jargon layer for each proposal.


## Added 2026-03-08 (133): Cargo graph substrate versus explanation artifacts

When a future pass touches Cargo graph / feature / resolver ideas, it must state explicitly whether the proposed crate is primarily:

1. a **graph-query substrate**,
2. a **build or feature simulation layer**,
3. or a **receiver-facing explanation / receipt artifact**.

If official Cargo docs and existing crates already cover (1) or (2), do not present the idea as if those layers were missing. Name the new value above them: cause chains, version-choice receipts, duplicate-build grouping, redaction, diff reports, or support-grade bundles.


## Added 2026-03-08 (134): live lock contention should stay receipt-first, not profiler-first

When a future pass touches Cargo/rust-analyzer blocking, do **not** default to building a profiler, scheduler, or process-killer.

For this frontier, first ask whether the missing value is still just:

1. one **cache-root manifest**,
2. one **lock-wait receipt**,
3. one **collision diagnosis**,
4. and one **mitigation plan**.

If yes, keep the proposal receipt-first.
Do not overfit to unstable internal lock details or act as though PID-perfect attribution is required for the crate to be useful.

A good smell for **P-0490**: “Which root was blocked, how strong is the evidence, and what trade-off should we choose next?”

A bad smell: “Maybe the missing crate is a daemon that orchestrates all local Cargo-like activity.”


## Added 2026-03-08 (135): build-dir transition should stay adapter-first, not pseudo-API-first

When a future pass touches build-dir migration, do **not** default to “maybe the missing crate is a new stable API for all Cargo internals.”

For this frontier, first ask whether the missing value is still just:

1. one **consumer inventory**,
2. one **layout snapshot**,
3. one **consumer audit**,
4. one **path contract**,
5. one **adapter plan**,
6. and one **transition receipt**.

If yes, keep the proposal migration-first.
Do not overfit to unstable path details or pretend that every intermediate artifact already has an honest stable replacement.

A good smell for **P-0489**: “Which consumer is relying on Cargo internals, what safer surface exists, and what should we rehearse before upgrading?”

A bad smell: “Maybe the missing crate is Cargo’s new public filesystem API, plus automatic rewrites for every downstream helper.”

## Added 2026-03-21 (319): adapter names are not adapter viability

When a future pass touches **P-0489**, do **not** stop at “the adapter is `use_cargo_bin_exe`” or “the adapter is `use_out_dir_contract`."

For this frontier, keep separate:

1. the **consumer failure-mode lane**,
2. the **named adapter suggestion**,
3. the **authority / availability class** for that adapter,
4. any **Cargo-version floor** or nightly-only restriction,
5. and any **fallback or dual-layout support** still required during migration.

A good smell for the next pass: “Is this adapter documented in the caller's actual Cargo window, or are we borrowing a point fix without preserving its scope?”

A bad smell: “We named an adapter, therefore the migration is safe.”


## Added 2026-03-08 (138): visualizer lanes versus broad debugger support

When a proposal touches **debugger visualizers** or embedded debugger assets, future revisions must state explicitly:

1. which backend lanes are documented by Rust itself,
2. which lanes are blocked by debugger trust/autoload policy rather than broken assets,
3. and which lanes are external/manual routes rather than embedded support.

Do not let the archive silently collapse **visualizer conformance** into a vague “better debugging” bucket. The sharper missing crate is often the **compatibility receipt**, not another debugger platform.

## Added 2026-03-08 (139): embedding is not activation, and activation is not compatibility

When a proposal touches embedded debugger assets or other tool-loaded sidecar behavior, future revisions must state separately:

1. whether the asset is present,
2. whether the tool will actually activate/load it under current trust or config rules,
3. and whether the resulting behavior counts as supported, external-only, or manual-review-only.

Do not let the archive silently treat **embedded**, **auto-loaded**, and **works across backends** as the same claim. Many worthy crates live exactly in that gap.

## Added 2026-03-08 (84): safety-critical evidence stacks and assurance-case boundaries

When a proposal touches **safety-critical**, **qualification**, **certification**, or **assurance-case** language, future revisions must state explicitly:

1. whether the crate is an **evidence producer** (coverage, lints, contracts, unsafe checks),
2. whether it is a **bundle/receipt substrate**,
3. or whether it is an **assurance-case assembly/export layer** above those artifacts.

Do not let the archive silently blur:

- a raw checker into an assurance case,
- a GSN/SACM editor into the real missing Rust-native value,
- or an assurance workbench into a full certification platform.

If an ecosystem already has assurance-case standards or editors, record them in `meta/known-existing.md`. The missing Rust value may be the **import, provenance, diff, and review-pack layer** above them rather than another generic editor.

## Added 2026-03-08 (141): linker lanes are not the same thing as toolchain support or cross wrappers

When a proposal touches **linkers**, **cross-compilation**, **`lld` adoption**, **Zig-backed linking**, **Windows SDK packaging**, or **containerized build lanes**, future revisions must state explicitly:

1. whether the missing value is a **new execution lane or wrapper**,
2. a **support contract for which lane is intended**,
3. a **doctor/receipt layer for one observed link attempt**,
4. or a **diff layer for switching lanes deliberately**.

Do not let the archive silently collapse:

- broader target/toolchain support posture,
- native dependency or SDK probing,
- and linker-lane diagnosis

into one fuzzy “cross-platform build doctor” story.

If credible lane-specific tools already exist, treat them as substrate and ask whether the sharper missing value has moved upward into **lane contracts, failure receipts, and switch-risk bundles**.

## Added 2026-03-08 (142): host/target config scope is not the same thing as linker lanes or tool-only builds

When a proposal touches **build scripts**, **proc macros**, **rustdoc flags**, **`RUSTFLAGS`**, **`RUSTDOCFLAGS`**, **`host-config`**, or **`target-applies-to-host`**, future revisions must state explicitly:

1. whether the missing value is a **broad toolchain/target support posture**,
2. a **tool-only / editor-oriented compile-surface parity** bundle,
3. a **linker-lane contract / doctor / diff** layer,
4. or a **host/target config scope contract and diagnosis** layer.

Do not let the archive silently collapse:

- build-script/proc-macro scope rules,
- linker-lane choice,
- docs-builder rustdoc quirks,
- and compile-time-deps parity

into one fuzzy “Cargo build doctor” story.

If Cargo’s docs already expose explicit scoping rules or nightly scope controls, treat those as substrate and ask whether the sharper missing value has moved upward into **scope manifests, observation receipts, and drift reports**.


## Added 2026-03-08 (143): rebuild explanation must preserve evidence lanes

When a future pass touches **P-0469**, it must preserve the distinction between:

1. **imported Cargo report facts**,
2. **live-captured workflow facts**,
3. and **optional fingerprint-overlay facts**.

Do not flatten those into one certainty tone.

A good 0.1 bundle can say:
- “Cargo reported this unit rebuilt,”
- “the command role changed from `check` to `build`,”
- and “wrapper drift was also observed,”

without pretending those facts are all the same kind of evidence.

If a pass starts inventing a dashboard, warehouse, or all-purpose build doctor around P-0469, it should first restate why that work is not actually:
- **P-0035** (historical warehousing),
- **P-0490** (live lock contention),
- **P-0494** (tool-workflow parity),
- or **P-0468** (resolver / graph cause chains).


## Added 2026-03-08 (144): host/target scope is not just cross-build folklore

When a proposal touches `RUSTFLAGS`, `build.rustflags`, `build.rustdocflags`, `--target`, `[host]`, or docs-builder-like workflows, future revisions must state explicitly:

1. which artifact kinds are built for the host,
2. which artifact kinds are built for the target,
3. whether the claim is about **intended policy**, **observed application**, or **conservative diagnosis**,
4. and whether same-triple command shapes could still represent different support lanes.

Do not let the archive flatten “host and target triples are the same” into “nothing meaningful changed.” In this frontier, command shape and scope behavior are often the real contract surface.


## Added 2026-03-08 (145): resolver explanation must preserve exactness boundaries

When a future pass touches **P-0468**, it must say explicitly:

1. which command/member/target selection was captured,
2. whether the explanation is being presented as **exact for the selected command**, **close approximation**, or **manual-review-required**,
3. whether MSRV influence is being reported as a documented heuristic versus a directly emitted Cargo fact,
4. and whether any claim depends on unstable `--unit-graph` or third-party simulation.

Do not let the archive silently flatten:

- `cargo tree` investigative views,
- `cargo metadata` graph context,
- `--unit-graph` low-level structure,
- mixed-workspace MSRV heuristics,
- and workspace-selection-sensitive feature states

into one fake “exact Cargo truth” story.

A worthy P-0468 bundle is allowed to say:
- “this is the selected-scope feature state,”
- “this version choice is consistent with Cargo’s documented MSRV heuristics,”
- and “manual review is still required for the counterfactual member-only build.”

That honesty is part of the product.


## Added 2026-03-08 (146): native dependency mode policy is not the same thing as generic probing

When future revisions touch `vendored` features, `system-deps`, `*_BUILD_INTERNAL`, `*_NO_PKG_CONFIG`, or distro/air-gap policy, they must state explicitly whether the missing value is:

1. a **build-script report / policy layer**,
2. a **hermetic build-script test harness**,
3. a **declarative native dependency contract**,
4. or a **mode/policy bundle** for system vs vendored vs override behavior.

Do not let the archive silently collapse:

- feature-unified vendoring,
- env-forced internal builds,
- config override / handoff,
- and generic pkg-config probing

into one fuzzy “native deps are hard” story.

If current substrate already has real controls, treat those as substrate and ask whether the sharper missing value has moved upward into **mode locks, policy reports, and backend-attempt truth**.

## Added 2026-03-08 (147): vendored source parity must preserve source identity and coverage truth

When future revisions touch **P-0496**, they must state explicitly:

1. which **logical source IDs** are being discussed,
2. which **physical roots** those source IDs resolved onto,
3. whether the claim is about **identity**, **coverage**, or **parity**,
4. and whether the result is being presented as **exact**, **conservative**, or **manual-review-required**.

Do not let the archive silently flatten:

- “all sources collapsed onto one `vendor/` directory”,
- “the workspace built once with vendored sources”,
- “offline is enabled”,
- and “the source-replacement assumption says code is the same”

into one fake “offline support is solved” story.

A worthy P-0496 bundle is allowed to say:
- “these two logical source ids share one physical vendor root”,
- “the vendored boundary is incomplete because a path dependency remains external”,
- and “manual review is still required for a git-workspace replacement case”.

That honesty is part of the product.



## Added 2026-03-08 (148): lock contention must preserve root-sharing and wrapper-context boundaries

When future revisions touch **P-0490**, they must state explicitly:

1. which root class is being discussed (`target_dir`, `build_dir`, `package_cache`, or `index_cache`),
2. whether the claim is about **sharing topology**, **observed waiting**, or **wrapper/cache-mode context**,
3. whether the diagnosis is being presented as **observed**, **strong inference**, or **manual-review-required**,
4. and whether a mitigation isolates the right lane or merely changes a neighboring one.

Do not let the archive silently flatten:

- “set a different target dir”,
- “changed build-dir”,
- “Cargo cache was locked”,
- and “wrapper behavior changed artifact hashing”

into one fake “Cargo lock issue” story.

A worthy P-0490 bundle is allowed to say:
- “build-dir lanes were isolated but target-dir remained shared”,
- “the package cache was the serialized lane, not the build root”,
- and “wrapper context made cache reuse expectations different even on one shared root”.

That honesty is part of the product.


## Added 2026-03-08 (149)
1. Do **not** let future passes treat a successful tool-facing run as equivalent to the wrong baseline. If the run is package-scoped, label-scoped, target-filtered, or policy-only, that must be frozen in a `comparison-baseline.lock`.
2. Do **not** normalize away override-command provenance. Relative wrappers, paired build-script overrides, `{label}` interpolation, and rust-analyzer wrapper defaults are part of the support truth for **P-0494**.


## Added 2026-03-08 (150)
1. Do **not** let future passes treat `allTargets`, `check.workspace`, `{label}`, and invocation strategy as minor editor settings. For **P-0494**, they are part of the support truth because they change which package scope, target classes, and proc-macro lanes were actually covered.
2. Do **not** normalize startup leakage away. If first-run diagnostics are wider than configured package scope, preserve that as conservative or `manual_review_required` output.


## Added 2026-03-08 (151): resolver explanation must preserve lane and platform boundaries

When a future pass touches **P-0468**, it must say explicitly:

1. whether a feature claim is about a **normal**, **build/proc-macro**, or **dev** lane,
2. whether target-specific clauses were actually in scope for the selected build or only visible in an all-target graph export,
3. whether `cargo metadata` used `--filter-platform`,
4. and whether the surface is being treated as **exact**, **conservative**, or **manual-review-required**.

Do not let the archive silently flatten:

- resolver v2 lane-split rules,
- `cargo tree`’s merged investigative views,
- `cargo metadata` all-target exports,
- unstable `--unit-graph` imports,
- and real proc-macro/build-vs-normal counterexamples

into one fake “exact feature truth” story.

A worthy P-0468 bundle is allowed to say:
- “the displayed feature set is merged in the investigative surface,”
- “this target-specific clause was out of scope for the selected target,”
- and “manual review is still required for the proc-macro helper lane.”

That honesty is part of the product.


## Added 2026-03-08 (152): resolver explanation must preserve feature-unification policy and participant scope

When a future pass touches **P-0468**, it must say explicitly:

1. what the active `resolver.feature-unification` mode is,
2. which packages were selected,
3. which packages participated in feature unification,
4. whether another package influenced the answer,
5. and whether the answer is exact, conservative, or manual-review-required.

Do not let the archive silently flatten:

- selected-package scope,
- participating-package scope,
- `selected` vs `workspace` vs `package` policy,
- workspace-selection-sensitive issue reports,
- and duplicate-build preference under package mode

into one vague “feature selection changed” story.

A worthy P-0468 bundle is allowed to say:
- “the selected command named one package but workspace mode let another member contribute feature pressure,”
- “package mode preferred duplicate builds instead of one merged feature set,”
- and “manual review is still required because the investigative surface does not preserve package-mode truth exactly.”

That honesty is part of the product.

## Added 2026-03-08 (153): resolver explanation must preserve feature intent and suppression truth

When a future pass touches **P-0468**, it must say explicitly:

1. what the explanation subject is (`-p`, `--bin`, workspace root, or equivalent),
2. which feature requests were positive versus negative,
3. whether the subject asked for `default-features = false` or `--no-default-features`,
4. whether another selected or participating package still kept a feature active,
5. and whether the answer is exact, conservative, or manual-review-required.

Do not let the archive silently flatten:

- positive feature requests,
- negative feature intent,
- subject scope,
- workspace pressure from another package,
- and investigative surfaces that blur the subject

into one fake “this package requested this feature” story.

A worthy P-0468 bundle is allowed to say:
- “the subject explicitly asked for defaults to stay off, but another selected package kept them on,”
- “the explanation subject was `--bin B`, not the whole workspace,”
- and “manual review is still required because the investigative surface merges subject scope.”

That honesty is part of the product.

## Added 2026-03-08 (154): resolver explanation must preserve workspace-inheritance and manifest-origin truth

When a future pass touches **P-0468**, it must say explicitly:

1. whether the dependency policy came from `[workspace.dependencies]`, a member manifest, or both,
2. whether default features were disabled, neutralized, or re-enabled,
3. whether a target-specific inherited edge materially changed the answer,
4. whether the explanation is about manifest origin or feature-unification pressure,
5. and whether the answer is exact, conservative, or manual-review-required.

Do not let the archive silently flatten:

- workspace-root dependency declarations,
- member-level inherited dependency declarations,
- target-specific inherited edges,
- docs/behavior mismatches around `default-features`,
- and release-note or issue-style evidence

into one fake “the member manifest requested this exact dependency policy” story.

A worthy P-0468 bundle is allowed to say:
- “the workspace root disabled defaults, but the member inherited dependency re-enabled them,”
- “the subject depended on a target-specific inherited edge, so the effective policy remains manual-review-required,”
- and “the explanation is conservative because current docs and observed inheritance behavior do not line up cleanly enough to claim more.”

That honesty is part of the product.


## Added 2026-03-08 (155): resolver explanation must preserve feature origin and activation preconditions

When a future pass touches **P-0468**, it must say explicitly:

1. whether a feature-like name is explicit, implicit, hidden by `dep:`, or not actually a public manifest feature,
2. whether a dependency-feature clause activates the optional dependency directly,
3. whether a dependency-feature clause only forwards a dependency feature if some other path already activated that dependency,
4. whether the explanation came from manifest scanning, Cargo investigative surfaces, or conservative reconstruction,
5. and whether the answer is exact, conservative, or manual-review-required.

Do not let the archive silently flatten:

- implicit optional-dependency aliases,
- explicit named features,
- `dep:`-hidden internal dependencies,
- `pkg/feat` strong forwarding,
- `pkg?/feat` weak forwarding,
- and feature-like cfg names that do not correspond cleanly to public manifest features

into one fake “this feature was enabled” story.

A worthy P-0468 bundle is allowed to say:
- “the dependency was activated, but its public implicit feature alias was intentionally suppressed,”
- “this clause only forwarded a dependency feature if another path already enabled the optional dependency,”
- and “manual review is still required because the downstream surface preserved a feature-like name without enough author-intent context.”

That honesty is part of the product.


## Added 2026-03-08 (156): resolver explanation must preserve dependency identity and rename surfaces

When a future pass touches **P-0468**, it must say explicitly:

1. what the local dependency key is,
2. what the original package name is,
3. which token a human would actually use in manifest feature references,
4. how renamed dependencies appear in `cargo metadata` versus registry-index / publish surfaces,
5. whether workspace inheritance blocked or ignored a requested rename,
6. and whether the answer is exact, conservative, or manual-review-required.

Do not let the archive silently flatten:

- local dependency keys,
- original package names,
- `cargo metadata`'s `name` / `rename` fields,
- registry-index `name` / `package` fields,
- publish-surface alias fields,
- and inherited dependency declarations that ignored `package = ...`

into one fake “this dependency has a name” story.

A worthy P-0468 bundle is allowed to say:
- “the optional dependency points at package `foo`, but the relevant manifest feature token is the renamed key `bar`,”
- “this member tried to rename an inherited workspace dependency, but current Cargo behavior leaves that intent ineffective,”
- and “manual review is still required because the registry/publish surface and the local manifest do not describe the rename in the same field vocabulary.”

That honesty is part of the product.


## Added 2026-03-09 (88): frontier monoculture resistance

When the last several passes all strengthen one proposal family or one subsystem frontier, future revisions must periodically do a **broad salience checkpoint** before adding more proposal count.

That checkpoint should ask explicitly:

1. is the archive still ranking the strongest opportunities across the whole ecosystem,
2. which proposals are true **portfolio multipliers**,
3. and whether the repo is silently drifting into one-family monoculture because that frontier is easier for an LLM to keep extending.

Do not let “the current hottest frontier” become “the whole map.”
A healthy archive should periodically rebalance toward the strongest cross-cutting, product-level, and coordination-artifact opportunities.


## Added 2026-03-09 (158): repo citation hygiene versus UI citation markup

When writing archive files, do **not** paste ChatGPT UI citation markup such as `cite…` into repository markdown.

Future revisions must keep repo citations in ordinary archive-friendly forms:

1. raw source URLs in `Sources`,
2. ordinary markdown links where useful,
3. or compact prose references tied to those URLs.

Tool/UI citation syntax is an interface artifact, not durable archive content.


## Added 2026-03-09 (159): moving substrate versus correctness-lab crates

When a proposal targets a domain with both:

1. a real standard or normative surface, and
2. multiple active Rust backends, SDKs, or runner surfaces,

future revisions must state explicitly whether the missing crate is:

- another backend,
- or a **correctness lab** above those backends (scenario DSL, corpus, normalized outputs, repro bundles, diffs, and diagnosis).

Do not let backend churn automatically turn into “Rust needs one more engine.” Often the sharper missing crate is the comparison and review layer above moving substrate.


## Added 2026-03-09 (160): suite contracts versus assurance arguments

When a proposal mentions **conformance**, **interop**, **certification**, or **assurance**, future revisions must state explicitly:

1. what the stable **suite/case/result** contract is,
2. what the portable **bundle/evidence** artifact is,
3. and whether there is a separate **assurance/review** layer above those artifacts.

Do not let the archive silently collapse harness design, bundle substrate, and assurance-case work into one vague “testing/certification platform”. A passing conformance run may become evidence; it is not automatically the whole assurance argument.


## Added 2026-03-09 (161): reproducibility evidence must preserve recipe, verdict, and triage boundaries

When a future pass touches **P-0242**, it must say explicitly:

1. what the **build recipe** artifact is,
2. what the **rebuild verdict** artifact is,
3. what the **diff triage** artifact is,
4. whether semantic normalization was applied,
5. and whether any attestation/publication layer is local, optional, or external.

Do not let the archive silently flatten:

- official build recipe,
- third-party rebuilder recipe,
- exact reproduction,
- semantic reproduction after normalization,
- raw diffoscope output,
- and published attestations

into one fake “reproducibility result”.

A worthy P-0242 bundle is allowed to say:
- “this rebuilt semantically but not bit-for-bit because archive compression drifted,”
- “the compared subjects were not equivalent because target/profile/feature scope diverged,”
- and “manual review is still required because the triage report could not reduce the drift to a safe known cause.”

That honesty is part of the product.


## Added 2026-03-09 (162): evidence bundles must preserve substrate, attestation, profile, and publication boundaries

When a future pass touches **P-0256** or proposes another bundle-first crate, it must say explicitly:

1. what the **core bundle substrate** owns,
2. which **attestation/signature lanes** are embedded or referenced,
3. what the **profile contract** adds above the core,
4. and whether any **publication/transparency** lane is local, optional, external, or entirely out of scope.

Do not let the archive silently flatten:

- deterministic packing rules,
- redaction receipts,
- DSSE or COSE payloads,
- Sigstore verification material,
- domain-specific report semantics,
- and OCI / SCITT / public-log publication

into one fake “signed bundle format”.

A worthy P-0256 bundle is allowed to say:
- “this bundle verified locally but external trust-root retrieval is caller policy,”
- “this profile carries a DSSE envelope and a Sigstore bundle without re-specifying their semantics,”
- and “this export is intentionally shareable-redacted and unsigned because the workflow is support handoff rather than publication.”

That honesty is part of the product.



## Added 2026-03-09 (163): assurance cases must preserve evidence, status, and export boundaries

When a future pass touches **P-0503** or another assurance-case proposal, it must say explicitly:

1. what the imported **evidence sources** are,
2. what the internal **claim/status** model is,
3. what the **review-pack / diff** artifact is,
4. and whether any **GSN / SACM / editor / regulator** lane is export-only, optional, external, or entirely out of scope.

Do not let the archive silently flatten:

- evidence producers,
- bundle substrate,
- assurance-case assembly,
- standards-shaped exports,
- and organization-specific certification workflows

into one fake “safety certification platform”.

A worthy P-0503 pack is allowed to say:
- “the GSN export exists but the internal status is still `blocked`,"
- “this pack imported conformance and verification evidence without pretending either is the whole assurance argument,"
- and “manual review is still required because one top-level assumption remains unresolved.”

That honesty is part of the product.


## Added 2026-03-09 (88): local-first engine/store/transport/membership layering

When a proposal targets **local-first**, **offline-first**, or **collaborative sync** workflows, future revisions must state explicitly:

1. which layer is **document / CRDT engine** semantics,
2. which layer is **durable local storage / compaction** semantics,
3. which layer is **transport / peer synchronization** behavior,
4. which layer is **membership / encrypted-group / revocation** behavior,
5. and which artifacts are meant for **support, diffing, and incident diagnosis**.

Do not let the archive silently collapse “sync works” into one fake claim that also covers authorization, revocation, or supportability. In this frontier, the missing crate is often the **coordination artifact above real substrate**, not another engine.


## Added 2026-03-21 (323): local-first durable sync versus presence versus history retention

When a proposal touches **local-first**, **collaborative sync**, or **CRDT-backed app state**, future revisions must state explicitly:

1. what is **durable synced document state**,
2. what is **ephemeral presence / awareness / cursor / peer metadata**,
3. what is **history/branch/time-travel reach**,
4. what survives **compaction / shallow snapshot / export**,
5. and what support bundles may honestly export from each class.

Do not let the archive silently collapse “supports collaboration” into one fake claim that covers durable state, live presence, and historical comparison equally. Current substrate now proves those are often different truths.


## Added 2026-03-09 (86): accessibility authoring versus interop-lab boundaries

When a proposal touches **accessibility**, future revisions must state explicitly which layer it owns:

1. authoring semantics inside the toolkit/app,
2. platform exposure capture (AT-SPI / UIA / NSAccessibility or equivalent),
3. standards-informed policy packs and scenario expectations,
4. or support/repro bundle export.

Do not let the archive silently collapse **authoring guidance**, **platform capture**, **policy evaluation**, and **compliance workflow** into one vague “a11y crate”. In this repo, **P-0087** and **P-0202** are intentionally adjacent but not identical.


## Added 2026-03-09 (166): authoring-side accessibility versus observer-side capture

When a proposal touches **accessibility**, future revisions must state explicitly whether the crate is meant to:

1. help a toolkit/app **emit and gate** coherent semantics,
2. **capture and diff** what a platform accessibility backend actually exposed,
3. or compare **expected authoring-side semantics** against **observed platform truth**.

Do not let the archive silently collapse semantic authoring, CI gating, platform capture, backend capability gaps, and compliance language into one fake “a11y crate”. The missing value is often the boundary and evidence workflow, not another GUI abstraction.


## Added 2026-03-09 (167): bootstrap tokens, endpoint handles, and support-bundle redaction

When a proposal involves **bootstrap convenience material** (tickets, invite links, endpoint handles, QR payloads, or similar), future revisions must state explicitly:

1. whether that material is only for **bootstrapping** or also participates in durable identity,
2. whether it can become stale, reusable, or capability-like,
3. and how support bundles redact it while still preserving enough receiver-facing truth for diagnosis.

Do not let the archive silently collapse "how peers initially find each other" into "who is authorized, durable, and reviewable over time". In local-first and peer-to-peer systems, that confusion is one of the fastest ways to produce insecure or non-supportable crate plans.


## Added 2026-03-09 (168): async determinism stack boundaries and stale UI citation cleanup

When revising proposals in the async/determinism cluster, do not let one pass silently collapse:

1. permutation testing,
2. deterministic simulation,
3. hardship/profile suites,
4. replay debugger workflows, and
5. rollback/state-hashing determinism

into one fake “deterministic async crate”.

Also, when a legacy proposal in that cluster still contains ChatGPT UI citation markup, treat cleaning that markup as part of the archive maintenance work rather than leaving it to future revisions.


## Added 2026-03-09 (169): text correctness requires separate provenance lanes

When a proposal touches **text layout, shaping, bidi, segmentation, or font fallback**, future revisions must pin and report at least these surfaces separately:

1. **Unicode data / test revision**,
2. **shaping engine**,
3. **layout engine / measurement policy**,
4. **font universe and fallback order**,
5. and whether any **render/pixel artifacts** are authoritative or merely advisory.

Do not let the archive silently flatten “text output changed” into one fake cause. Many text regressions are really boundary bugs between these layers, and future humans or LLMs need the repo to preserve that distinction.


## Added 2026-03-09 (170): text profile truth must stay separate from case truth

When a proposal or fixture touches **text layout** and it can plausibly vary by CSS-like policy, toolkit policy, editor policy, or backend discretion, future revisions must preserve at least these artifact boundaries:

1. **layout case** (what was requested),
2. **layout profile** (which Unicode/CSS/toolkit/editor policy lane was claimed),
3. **backend capability receipt** (what the runner could really support),
4. **decision-origin receipt** (where major choices actually came from),
5. and **font-resolution receipt** (what fonts actually resolved at runtime).

Do not let the archive imply that a changed wrap or cursor boundary automatically proves a backend regression. In this frontier, many “regressions” are really profile drift, backend-default discretion, or changed runtime font universes.


## Added 2026-03-09 (171): protocol semantics, automation lanes, and certification lanes

When a proposal spans a **normative auth/web protocol**, one or more **browser or automation lanes**, and one or more **real-device or certification/conformance surfaces** (for example WebAuthn + WebDriver virtual authenticators + physical-device imports + FIDO conformance), future revisions must state explicitly:

1. which layer defines the normative protocol semantics,
2. which layer is browser or automation substrate,
3. which layer is real-device or imported evidence,
4. which layer is external certification or conformance evidence,
5. and which artifact records **comparability truth** between them.

Do not let the archive silently collapse “same protocol” into “same evidence lane”. Many of the best missing crates in this repo are really **lane-honesty workbenches** that make unstable automation, imported device evidence, and certification facts legible instead of implied.


## Added 2026-03-16 (172): async bridge crates are not the same as migration workflows

When a proposal sits in an area where Rust already has both **active upstream language work** and **bridge crates used in production** (for example `async-trait`, `trait-variant`, `dynosaur`, and future native async dyn support), future revisions must state explicitly:

1. which parts are **upstream milestones**,
2. which parts are **today’s bridge recipes**,
3. which parts are **public-promise differences** versus mere implementation differences,
4. and which artifacts a maintainer would use for **migration review**.

Do not let the archive silently collapse “there are several bridge crates” into “the missing crate is another bridge crate”. In these transition-heavy frontiers, the sharper missing value is often the **migration receipt and comparison bundle**.


## Added 2026-03-16 (173): general sanitizer workflows and aliasing-specific evidence must stay separate

When a proposal touches sanitizers, runtime safety tooling, or unsafe-code evidence, future revisions must state explicitly whether the crate owns:

1. a **general sanitizer profile/report workflow**,
2. a **BorrowSanitizer-specific aliasing/provenance lane**,
3. a **debuggability/support-posture contract**,
4. or a **higher-level verification/assurance import layer**.

Do not let the archive silently flatten symbolized reports, aliasing findings, Miri comparisons, debug-symbol support, and assurance imports into one fake “sanitizer result”. The missing crates here are usually **lane-honest evidence artifacts**, not one giant safety bucket.


## Added 2026-03-16 (174): build-dir transition lanes must stay separate

When a proposal touches Cargo layout migration, build-dir rehearsals, or path-sensitive helper scripts, future revisions must state explicitly whether the case is about:

1. **bin-path inference from test lanes**,
2. **target-dir recovery from `OUT_DIR` or helper binaries**,
3. **user-requested artifact lookup**,
4. or **broad build-dir / target-dir topology migration**.

Do not let the archive silently collapse those into one vague “Cargo path issue”. The right adapter, neighboring crate, and honest confidence level differ a lot across those lanes.

## Added 2026-03-16 (175): MSRV evidence lanes must stay separate

When a proposal touches MSRV, toolchain support, or older-compiler adoption, future revisions must state explicitly whether the crate owns:

1. a **declared support policy** lane,
2. a **resolver-policy / version-selection** lane,
3. an **active build floor** lane,
4. a **metadata / tooling floor** lane,
5. an **inactive target-edge** lane,
6. or a **workspace support-promise** lane.

Do not let the archive silently flatten those into one fake “minimum Rust version”. In this frontier, the missing crate is usually the **receipt / blame / policy-diff layer**, not a magical universal MSRV number.


## Added 2026-03-16 (176): workspace membership, parent probing, and config probing must stay separate

When a proposal touches Cargo workspace discovery, nested repos, or `.cargo/config.toml` behavior, future revisions must state explicitly whether the case is about:

1. **workspace membership**,
2. **parent-manifest discovery**,
3. **parent-config probing**,
4. **current-working-directory effects**,
5. **`--manifest-path` invocation splits**,
6. or **project-specific settings that do not yet have a manifest home**.

Do not let the archive silently collapse those into one vague “Cargo workspace bug”. The missing value here is often the **boundary trace and diagnosis bundle** rather than another broad workspace utility.

## Added 2026-03-16 (177): project support contracts and docs.rs parity must stay separate

When a proposal touches Rust toolchains, docs.rs behavior, or contributor setup, future revisions must state explicitly whether the crate owns:

1. a **project support contract** lane,
2. a **docs.rs parity / issue-bundle** lane,
3. a **linker / external-toolchain diagnosis** lane,
4. a **workspace/config boundary** lane,
5. or a **single-file package portability** lane.

Do not let the archive silently flatten rustup profile drift, docs.rs default-target drift, `#[cfg(docsrs)]` behavior, missing external linkers, and workspace discovery into one vague “support issue”. The missing value is usually the **right support artifact for the right lane**, not one giant helper crate.


## Added 2026-03-16 (178): cargo script portability is not the same as workspace discovery or source parity

When a proposal touches **single-file packages** or cargo script, future revisions must state explicitly whether the crate owns:

1. **frontmatter / inferred-manifest truth**,
2. **target-dir and lockfile placement for single-file packages**,
3. **workspace auto-discovery posture**,
4. **parent config influence**,
5. or **source-parity / offline download truth**.

Do not let the archive silently collapse those into one vague “Cargo script support” result. The sharper missing crate is often the **portability receipt and export plan**, not another general Cargo helper.

## Added 2026-03-16 (179): verified mirrors and local source parity must stay separate

When a proposal touches **mirrors**, **vendoring**, or **offline Cargo**, future revisions must state explicitly whether the crate owns:

1. **external mirror verification / trust distribution**,
2. **workspace-local source identity and coverage truth**,
3. **artifact transfer into constrained environments**,
4. or **intentional graph mutation via patch/path overrides**.

Do not let the archive silently flatten a verified mirror into a fake proof that the workspace’s actual source story is clean. The missing value is often the **source-parity lock and mirror-honesty report**, not another generic supply-chain crate.


## Added 2026-03-16 (178): keep publish-surface rehearsal, release receipts, auth diagnosis, attestations, and malware notification distinct

When future revisions touch crates.io / Cargo publishing work, they must state explicitly:

1. whether the crate owns **pre-publish trusted-publishing rehearsal**, **post-publish release receipts**, **registry auth-stage diagnosis**, or **artifact provenance/attestation**,
2. whether crates.io-specific enrichments like **trusted-publishing-only mode**, blocked triggers, **`pubtime`**, or **publish notifications** are core semantics or merely imported facts,
3. and whether malware / RustSec / public-notification behavior is only **context** rather than the crate’s own job.

Do **not** let future passes collapse:

- trusted-publishing rehearsal,
- joined release receipts,
- registry-auth diagnosis,
- provenance attestations,
- and malicious-crate communication

into one fake “publish security crate”.


## Fix orchestration boundary rule (2026-03-16)

Do not let the archive silently collapse **generic lint-fix campaigns**, **edition migration witnesses**, **future-incompat ledgers**, and **Cargo plumbing phase receipts** into one fake “migration” crate.

If a pass touches `cargo fix`, ask first whether the missing value is:

1. a **campaign / batching / per-pass receipt** crate,
2. an **edition-specific rehearsal witness**,
3. a **future-incompat ownership + waiver** crate, or
4. a **phase-input / reread-versus-consumed Cargo plumbing** crate.

The missing crate may be the **fix-campaign ledger**, the **target-batch plan**, the **manual-review queue**, or the **phase-input intent receipt** that makes the raw mechanism usable by ordinary teams.


For build-time Cargo follow-on work specifically, also consult `meta/build-script-delegation-lanes-2026-03-16.md` so buildscript UX, fixture testing, export handoff, artifact-dependency adoption, delegated reusable units, and host/target execution scope do not get collapsed into one fake build-script modernization result.


## Added 2026-03-16 (181): workspace tool manifests, install policy, rustup toolchains, and cache policy must stay separate

When future revisions touch **Rust tools that are themselves shipped as crates**, they must state explicitly whether the missing crate owns:

1. a **workspace tool manifest / lock / runner receipt** layer,
2. an **install policy / cooldown / waiver / install receipt** layer,
3. a **rustup compiler/toolchain support** contract,
4. a **Cargo home cache retention / GC** policy layer,
5. or a **publish-surface identity / release receipt** layer.

Do **not** let future passes collapse:

- workspace-scoped tool dependencies,
- install-stage policy and `pubtime` age gates,
- rustup compiler/channel/components/targets,
- Cargo-home cleanup rules,
- and publish-surface identity

into one fake “tool setup crate”. The strongest missing crates here are increasingly **layered coordination artifacts** above official Cargo, crates.io, and rustup substrate.


## Added 2026-03-16 (182): `rustc_public` publication, tool compatibility, semantics, and spec work must stay separate

When future revisions touch **`rustc_public`** or public compiler interfaces, they must state explicitly whether the missing crate owns:

1. **official `rustc_public` publication / versioning / bridge release engineering**,
2. **tool compatibility locks, analyzer fixtures, capability matrices, and analysis receipts**,
3. **formal semantics / counterexample exchange**,
4. **Rust specification witnesses**,
5. or a future **syntax / macro-expansion evidence** lane.

Do **not** let future passes collapse:

- compiler-team publication work for `rustc_public`,
- `rustc_private` migration pain,
- tool-facing compatibility bundles,
- formality / MiniRust counterexamples,
- and spec-witness artifacts

into one fake “public compiler tooling crate”. The strongest missing crate here is increasingly the **fixture-first compatibility and evidence layer** above `rustc_public`, not another compiler-interface implementation.


## Added 2026-03-16 (184): resolver explanation must preserve evidence-source and exactness truth in machine-readable artifacts

When a future pass touches **P-0468**, it must say explicitly:

1. which artifact is the capture lock,
2. which conclusions came from `cargo metadata`, `cargo tree`, unstable imports, or conservative reconstruction,
3. whether the report is about lockfile-generation pressure or actual compile-time feature pressure,
4. whether the answer is exact, approximate, or manual-review-required,
5. and which schema/example pair another tool author could implement against.

Do not let the archive silently flatten:

- official resolver semantics,
- investigative surfaces that are only *pretty close*,
- unstable richer inputs,
- conservative reconstruction,
- and wishful “the tool should probably know” guesses

into one fake machine-truth story.

A worthy P-0468 bundle is allowed to say:
- “the version-choice story is exact enough for review but the feature-cause story is still conservative,”
- “workspace mode let another member influence the answer even though the question named one package,”
- and “this scenario stays manual-review-required until a richer Cargo surface is imported.”

That honesty is part of the product.


## Added 2026-03-16 (185): future-incompat crates must preserve capture truth, owner truth, and release truth separately

When a future pass touches **P-0478**, it must say explicitly:

1. whether the bundle came from a live `--future-incompat-report` capture, a recalled `cargo report` id, or a latest-cached recall,
2. which artifact owns normalized finding memory,
3. which artifact owns owner / waiver / release-gate policy,
4. whether a change is truly new versus `reclassified_by_toolchain`,
5. and whether package filtering or other post-hoc narrowing changed exactness.

Do not let the archive silently flatten:

- Cargo's built-in report detection and display,
- persisted report recall,
- owner maps and waiver expiry,
- release-branch gate policy,
- build-analysis warehousing,
- and fix / remediation execution

into one fake “future incompatibility platform”.

A worthy P-0478 bundle is allowed to say:
- “the report is exact as captured but ownership is still missing,”
- “this waiver was valid on main and expired for the release branch,”
- and “the finding surface changed under a newer toolchain, so manual review is still required.”

That honesty is part of the product.


## Added 2026-03-16 (186): Cargo SBOM work must preserve precursor truth, transform truth, and neighbor-lane truth separately

When a future pass touches **P-0125** or nearby Cargo SBOM proposals, it must say explicitly:

1. whether the crate owns **Cargo precursor capture**, **general sidecar attachment**, **publish identity / trusted publishing**, **public-API release truth**, or **policy / provenance / distribution**,
2. which artifact records how precursor files were captured and matched to promoted artifacts,
3. which output owns the normalized build graph,
4. which receipt says what was projected exactly versus normalized or dropped during format emission,
5. and whether any ambiguous artifact association or format loss still forces `manual_review_required`.

Do not let the archive silently flatten:

- Cargo's raw `*.cargo-sbom.json` precursor feature,
- `CARGO_SBOM_PATH` or sidecar scanning,
- general sidecar attachment rules,
- trusted-publishing or post-publish receipts,
- SemVer / public-dependency release reviews,
- and higher-level provenance or policy systems

into one fake “SBOM platform”.

A worthy P-0125 bundle is allowed to say:
- “the component graph is exact but artifact association is still ambiguous,”
- “the CycloneDX projection normalized this field and dropped that one,”
- and “this output is usable for review but not yet for ship-grade automated policy.”

That honesty is part of the product.


## Added 2026-03-16 (187): artifact-sidecar crates must preserve artifact truth, schema truth, and shipping truth separately

When a future pass touches **P-0479** or nearby artifact-sidecar proposals, it must say explicitly:

1. whether the crate owns **artifact handoff**, **artifact↔sidecar association**, **SBOM precursor capture**, **publish identity**, or **debug/support promises**,
2. which artifact carries the ship/local/manual-review policy,
3. whether each sidecar mapping came from `compiler-artifact` messages, `artifact-dir` structure, env hints, or manual mapping,
4. which artifact records schema/stability facts for each sidecar family,
5. and whether a missing or ambiguous sidecar still forces `manual_review_required`.

Do not let the archive silently flatten:

- produced-output manifests,
- sidecar association receipts,
- SBOM precursor capture and transform-loss artifacts,
- publish identity / post-publish receipts,
- and debugger or docs.rs support promises

into one fake “artifact metadata” story.

A worthy P-0479 bundle is allowed to say:
- “the artifact handoff is exact but the sidecar association is still conservative,”
- “the sidecar exists but is analysis-only and should not ship,”
- and “schema drift is reviewable even though the primary artifact itself did not change.”

That honesty is part of the product.


## Added 2026-03-16 (188): artifact-handoff crates must preserve produced-output truth, origin truth, and session truth separately

When a future pass touches **P-0471** or nearby artifact-handoff proposals, it must say explicitly:

1. whether the crate owns **produced-artifact handoff**, **sidecar association**, **build-dir migration**, **artifact-production substrate**, **historical session storage**, or **publish identity**,
2. which artifact facts came directly from `compiler-artifact` or `build-finished` messages,
3. which facts depended on `--artifact-dir`, build-script metadata, filesystem reconstruction, or imported build-analysis sessions,
4. which file in the bundle carries origin and exactness truth,
5. and where `manual_review_required` remains the honest answer.

Do not let the archive silently flatten:

- produced-artifact manifests,
- copied-output convenience,
- build-dir transition receipts,
- build-script artifact-production substrate,
- historical build-analysis sessions,
- and publish-surface identity

into one fake “artifact output” story.

A worthy P-0471 bundle is allowed to say:
- “the manifest is exact from Cargo messages even though copied-output help was unavailable,”
- “the build-script-created artifact is still manual-review-required,”
- and “this bundle is session-linked, but the session store is not itself the product.”

That honesty is part of the product.


## Added 2026-03-16 (189): rebuild-explanation crates must preserve source truth, exactness truth, and lane truth

When future revisions touch Cargo rebuild explainability, do **not** stop at “Cargo has `-Zbuild-analysis` and `cargo report` now.”

Future passes must state explicitly:

1. whether the crate is about **today’s rebuild mystery**, **historical session warehousing**, **lock contention**, **tool-surface parity**, or **input completeness / signatures**,
2. which claims are **imported verbatim**, **normalized from observed facts**, **conservative inference**, or **manual-review required**,
3. and which facts came from imported `cargo report` output versus live capture versus optional overlays.

Do not let the archive silently equate “Cargo can list sessions and show rebuild reasons” with “the support workflow is already boring.”
The missing crate may still be the **session-freeze bundle**, **exactness ledger**, or **rebuild support artifact** that turns unstable upstream surfaces into ordinary maintainer habit.


## Added 2026-03-16 (190): imported-session warehouse versus per-run support discipline

When a proposal touches **Cargo build-analysis history**, future revisions must state explicitly whether the crate is primarily about:

1. **upstream session recording / native Cargo report UX**,
2. **per-run support bundles** (what rebuilt today and why),
3. **historical imported-session warehousing and trend adjudication**,
4. **tool-workflow parity / compile-time-deps drift**,
5. or **lock/contention / waiting witnesses**.

Do not let the archive silently collapse all five into one fake “build performance” crate. The worthy missing crates here are increasingly layered coordination artifacts with different time horizons, different exactness contracts, and different review audiences.


## Added 2026-03-16 (191): keep package review, workspace package-set rehearsal, publish identity, and post-publish receipts distinct

When future revisions touch **Cargo packaging** or **pre-publish review**, they must state explicitly:

1. whether the crate owns the **source-bundle review** layer above `cargo package`,
2. whether it owns **workspace package-set rehearsal** facts,
3. whether it owns **trusted-publishing / release-identity** posture,
4. whether it owns **post-publish registry confirmation**,
5. and whether it is making any **provenance / attestation** claims.

Do **not** let future passes flatten these into one fake “publish security” crate.

Receiver-facing phrasing to prefer:

- “this bundle records what Cargo packaged and what reviewers inspected before publication,”
- “this report freezes the reviewed workspace candidate set, not the later auth flow,”
- “the VCS snapshot is best effort and not provenance,”
- and “copy-in behavior for external license/readme files is review posture, not a signed origin claim.”


## Added 2026-03-16 (192): target-dir isolation is not the whole tool-workflow root story

When future revisions touch **P-0494** or nearby Cargo/editor workflow ideas, they must state explicitly:

1. whether `target-dir` was shared or isolated,
2. whether `build-dir` was shared or isolated,
3. whether any imported Cargo build-analysis session is exact evidence or merely supporting context,
4. and whether the result is about **tool-surface parity**, **live contention**, **layout transition**, or **historical build analysis**.

Do **not** let the archive silently equate “rust-analyzer uses its own target directory” with “the workflow root story is solved.”
That may reduce one class of contention while leaving `build-dir`, wrapper assumptions, or build-dir-layout transition risks completely separate.


## Added 2026-03-16 (193): lock-contention bundles may import sessions, but must not pretend sessions prove blockers

When a future pass touches **P-0490 Cargo Lock Contention Witness Kit**, it must preserve three separate claim classes:

1. **observed wait facts**,
2. **shared-root topology facts**,
3. **optional imported build-analysis session context**.

Good smell:
- “Cargo reported a wait on this root.”
- “These tool roles shared or isolated these roots.”
- “This session overlapped the witness window, but blocker identity remains manual-review-only.”

Bad smell:
- “The imported Cargo session proves rust-analyzer held the lock.”
- “Changing target-dir fully explains the contention story.”
- “Any session link should live inside rebuild/build-history crates, never here.”

The worthy P-0490 bundle is allowed to attach a session.
It is **not** allowed to smuggle blocker certainty through that attachment.


## Added 2026-03-16 (194): build-std recipe capture must stay separate from adjacent sysroot lanes

When a proposal touches `build-std`, sysroot rebuilding, or std-aware Cargo workflows, future revisions must state explicitly whether the crate owns:

1. a **stage-aware sysroot recipe / lock / receipt bundle**,
2. an **ABI-coherence / whole-program flag contract**,
3. a **sanitizer or runtime-instrumentation evidence lane**,
4. a **source-path / source-availability / debugger-support lane**,
5. or a **tool-surface parity / editor-workflow diagnosis lane**.

Do not let the archive silently flatten manual `-Z build-std`, explicit std dependencies, target-modifier experimentation, future auto-rebuild policy, ABI claims, source lookup, and editor parity into one fake “std-aware crate”. The missing crate here is usually a **recipe/lock/receipt/diff substrate with explicit stage posture**, not a giant sysroot bucket.

## Added 2026-03-16 (195): crate-decision lanes and starter-set honesty

When a proposal touches **crate discovery, starter sets, or ecosystem curation**, future revisions must state explicitly whether the crate is primarily about:

1. a **task-first decision pack**,
2. a **per-crate health import**,
3. a **trust/risk import**,
4. a **dependency-minimal façade crate**,
5. or a **governance / blessing / stdlib-expansion** argument.

Future revisions must also pin the **task profile** being optimized for (for example: CLI baseline, async service, `no_std` embedded, Wasm browser client) and must record the main **interop/lock-in surfaces** that shaped the recommendation.

Do not let the archive silently convert “which crate should I use for this task?” into “which crate is best, full stop?”
A good pathfinder crate may rank candidates and still emit `manual_review_required` when the evidence is thin or the trade-offs are role-dependent.

## Added 2026-03-16 (196): crate capability contracts must stay distinct from decision packs and slice tools

When a proposal touches **crate support claims, interop posture, or producer-side metadata**, future revisions must state explicitly whether the crate owns:

1. a **producer-side capability contract**,
2. a **task-first decision pack**,
3. an **item-level availability ledger**,
4. a **whole-project toolchain/target support contract**,
5. a **health/trust import**,
6. or a **public-API / semver / MSRV / dependency-policy slice tool**.

Future revisions must also preserve three claim classes separately whenever possible:

- **declared** facts,
- **observed** facts,
- **inferred** facts.

Do **not** let the archive silently equate `keywords`, `categories`, docs.rs metadata, rustdoc JSON, `rust-version`, or slice tools like `cargo-msrv` / `cargo-public-api` / `cargo-deny` / `cargo-semver-checks` with “crate support truth is already solved.”
The missing crate may still be the **joined producer-side contract** above those pieces.


## Added 2026-03-16 (197): shared ecosystem interop profiles must stay distinct from capability contracts and semver slices

When a proposal touches **library interop, shared building blocks, or ecosystem boundary contracts**, future revisions must state explicitly whether the crate owns:

1. a **shared ecosystem interop profile pack**,
2. a **producer-side capability contract**,
3. a **task-first decision pack**,
4. a **trait-evolution / customization-point migration planner**,
5. a **public-API / semver slice tool**,
6. or a **domain-specific conformance kit**.

Future revisions must also keep **static conformance**, **behavioral probes**, and **pairwise compatibility** visibly separate whenever possible.

Do **not** let the archive silently equate shared building blocks like `http`, `tower-service`, `futures-core`, or Serde with “library interop is already solved”.
The missing crate may still be the **joined shared profile contract** above those building blocks.

## Added 2026-03-17 (230): shared interop profiles need profile-class, obligation, and pair-fidelity honesty

When a pass sharpens **shared ecosystem interop profiles**, future revisions must state explicitly whether the main review object is about:

1. **what class of profile is being claimed**,
2. **which boundary obligations are required or forbidden**,
3. **how provider/consumer pairs were actually checked**,
4. **which adapters are assumed versus observed**,
5. or **which migration hazards narrowed the shared boundary**.

Do **not** let future passes flatten those into one vague “these crates are compatible” result. Shared interop profiles are a distinct lane from producer-side capability contracts, semver/public-API tools, framework-specific docs, and domain conformance suites.

## Added 2026-03-16 (198): crate guidance/supportiveness lanes

When a pass proposes a crate in the ecosystem-supportiveness area, it must state explicitly whether the missing value is about:

1. **which crate to choose**,
2. **what a crate claims to support**,
3. **what shared interop profile a crate fits**,
4. **what guidance a crate gives when users hit common failure paths**,
5. or **how diagnostics/docs are rendered or browsed**.

Do not let future passes silently flatten these into one vague “better DX” result. Receiver-facing guidance packs are a distinct lane from metadata contracts, interop profiles, crate selection, renderer crates, and docs portals.

## Added 2026-03-16 (199): runtime handoff versus compile-time guidance

When a pass proposes a crate in the supportiveness area, it must state explicitly whether the missing value is about:

1. **compile-time / early-failure guidance**,
2. **runtime failure handoff / support bundles**,
3. **generic report rendering**,
4. **tracing / observability**,
5. or **domain-specific incident capture**.

Do not let future passes quietly rephrase runtime handoff as “better diagnostics” or rephrase compile-time guidance as “incident support”. The archive now has distinct lanes for both.


## Added 2026-03-16 (200): release-to-release upgrade packs must stay distinct from semver evidence and release automation

When a pass proposes a crate in the release-support area, it must state explicitly whether the missing value is about:

1. **SemVer/public-API evidence**,
2. **release-to-release upgrade packs**,
3. **compile-time guidance**,
4. **runtime handoff**,
5. **release automation / changelog tooling**,
6. or **domain-specific migration kits**.

Do not let future passes quietly rephrase upgrade packs as “better changelogs”, “better semver checks”, or “better diagnostics”. The archive now has a distinct lane for the receiver-facing migration artifact.


## Added 2026-03-16 (201): successor / off-ramp packs must stay distinct from health metadata, advisory detection, and upgrade packs

When a pass proposes a crate in the ecosystem-supportiveness or maintenance area, it must state explicitly whether the missing value is about:

1. **crate health / governance posture**,
2. **task-first crate choice**,
3. **compile-time guidance**,
4. **runtime handoff**,
5. **release-to-release upgrade packs**,
6. **successor / deprecation / off-ramp packs**,
7. **advisory / ban / outdated detection**,
8. or **publish/yank / ownership mechanics**.

Do not let future passes quietly rephrase off-ramp packs as “better advisories”, “better deprecation notes”, or “better maintenance metadata”. The archive now has a distinct lane for the receiver-facing exit artifact.


## Added 2026-03-16 (202): configuration-scenario packs must stay distinct from crate choice, config provenance, and feature testing

When a pass proposes a crate in the ecosystem-supportiveness or setup area, it must state explicitly whether the missing value is about:

1. **task-first crate choice**,
2. **producer-side support / interop claims**,
3. **shared interop profiles**,
4. **crate configuration scenarios**,
5. **compile-time guidance**,
6. **runtime handoff**,
7. **upgrade/off-ramp support**,
8. **generic Cargo config provenance**,
9. or **feature-matrix testing / feature documentation**.

Do not let future passes quietly rephrase configuration-scenario packs as “better feature docs”, “better README setup”, or “better Cargo config explanation”. The archive now has a distinct lane for the receiver-facing setup artifact.

### Added 2026-03-17 (227): configuration-scenario productization must keep policy, provenance, and fidelity explicit

When a pass deepens **P-0516**, it must state explicitly:

1. which scenarios are `recommended_default`, `minimal_supported`, `backend_choice_required`, `docs_only`, or `manual_review_required`,
2. where important setup facts came from (manifest, docs.rs metadata, observed checks, maintainer policy, or manual review),
3. and how much of the advertised matrix was actually observed versus merely declared.

Do not let future passes quietly flatten configuration-scenario work into “the README has instructions”, “docs.rs built with all features”, or “a powerset tool passed, so support is honest.”


## Added 2026-03-17 (203): performance-envelope packs must stay distinct from setup scenarios, benchmark tools, and perf services

When a pass proposes a crate in the ecosystem-supportiveness or performance area, it must state explicitly whether the missing value is about:

1. **task-first crate choice**,
2. **support / interop claims**,
3. **shared interop profiles**,
4. **configuration/setup scenarios**,
5. **performance-envelope contracts**,
6. **compile-time guidance**,
7. **runtime handoff**,
8. **upgrade/off-ramp support**,
9. **generic benchmark / profiling tools**,
10. or **hosted CI perf services**.

Do not let future passes quietly rephrase performance-envelope packs as “better benchmark runners”, “better profiling”, or “better setup docs with charts”. The archive now has a distinct lane for the receiver-facing performance artifact.


## Added 2026-03-17 (207): crate supportiveness resource boundaries

When a proposal touches **capacity, backlog, pool size, memory bounds, or overload posture** in the crate-supportiveness frontier, future revisions must state explicitly whether the missing value is primarily about:

1. **setup/configuration scenarios**,
2. **performance envelopes**,
3. **observability surfaces**,
4. **authority / ambient powers**,
5. **lifecycle / shutdown truth**,
6. or **receiver-facing resource-surface contracts**.

Do not let the archive silently collapse “how much can accumulate, what is bounded, and what happens at saturation” into generic performance work, generic metrics work, or generic async docs. The strongest missing crate here is a **resource contract layer**, not just more tuning advice.


## Added 2026-03-17 (208): persistence-surface packs must stay distinct from upgrade packs, serializer/storage substrate, and domain schema workbenches

When a proposal touches **persisted bytes or durable state**, future revisions must state explicitly whether the crate is primarily about:

1. **release-to-release code/config migration**,
2. **receiver-facing persisted-state compatibility, durability, recovery, and migration artifacts**,
3. **generic serializer / storage-engine substrate**,
4. or a **domain-specific schema/protocol workbench**.

Do not let future passes quietly rephrase persistence-surface packs as “better serde docs”, “better upgrade notes”, or “better storage-engine docs”. The archive now has a distinct lane for the receiver-facing durable-bytes artifact.


## Added 2026-03-17 (209): crate test-surface packs must stay distinct from generic test frameworks and domain conformance labs

When a proposal touches **fixtures, mocks, fake services, paused clocks, property strategies, snapshots, or integration environments**, future revisions must state explicitly whether the crate is primarily about:

1. **generic testing substrate**,
2. **runtime/setup support surfaces**,
3. **domain-specific conformance/evidence workbenches**,
4. or **receiver-facing test-surface contracts**.

Do not let future passes quietly rephrase crate test-surface packs as “another mock crate”, “better examples”, or “a nicer test harness”. The archive now has a distinct lane for the receiver-facing downstream-testing artifact.


## Added 2026-03-17 (214): toolchain/target support truth needs three explicit layers

When a proposal touches **toolchains**, **targets**, **docs.rs posture**, or **cross-compilation setup**, future revisions must state explicitly whether the crate owns:

1. a **support-class policy** layer,
2. an **evidence provenance** layer,
3. an **external-prerequisite / runner / linker** layer,
4. a **docs.rs parity / replay** lane,
5. an **item-level cfg/API availability** lane,
6. or an **MSRV-only** lane.

Do not let the archive silently flatten these into one vague “supported targets” result. The missing value is often the **reviewable contract that says what class of support is claimed, what evidence backs it, and what non-Rust prerequisites still apply**, not another installer or another generic doctor tool.

## Added 2026-03-17 (216): docs.rs parity needs explicit fidelity and drift-cause vocabulary

When a proposal touches **docs.rs**, **rustdoc CI**, or **local-vs-hosted documentation failures**, future revisions must state explicitly whether the crate owns:

1. a **metadata normalization** layer,
2. a **local preflight fidelity** layer,
3. a **hosted-build import** layer,
4. a **sandbox-limit / policy interpretation** layer,
5. a **drift-cause explanation** layer,
6. or a **different docs product** such as hosting, coverage review, or rustdoc-JSON analytics.

Do not let the archive silently flatten “`cargo docs-rs` passed”, “the docs.rs builder passed”, “the hosted build summary exists”, “rustdoc JSON is downloadable”, and “the HTML docs rendered correctly” into one vague “docs.rs parity” claim. The missing value is often the **reviewable fidelity and drift-cause artifact**, not another docs runner.



## Added 2026-03-17 (218): crate test-surface follow-on work must separate support level, environment requirements, and scenario witnesses

When a proposal touches **fixture catalogs, fake backends, paused clocks, integration topologies, or named test scenarios** inside the P-0523 lane, future revisions must state explicitly whether the missing value is primarily about:

1. **support-level policy**,
2. **environment requirements / host capabilities**,
3. **scenario witnesses that tie named cases to real fixtures and seams**,
4. **generic test execution substrate**,
5. or a **new adjacent lane entirely**.

Do not let future passes quietly rephrase missing support-level vocabulary, Docker/loopback/paused-time prerequisites, or unwitnessed scenario claims as proof that the archive needs “another testing crate”. The sharper move is usually to deepen **P-0523**.


## Added 2026-03-17 (219): observability contracts versus telemetry plumbing

When a proposal already has a decent **signal catalog / cost / redaction** shape but still lacks:

1. explicit **stability-class meaning**,
2. explicit **activation-recipe truth** (filters, layers, runtime requirements, exporter bridges),
3. or explicit **semantic-convention / schema posture**,

the next move is usually to sharpen the **existing observability-surface lane**, not to invent a new telemetry proposal.

Do not let the archive drift from “crate-authored observability contract” into:
- another subscriber/exporter idea,
- another dashboard/config platform,
- or a vague semconv-lint lane.

If the missing question is “can other people trust, activate, and carry these signals across releases?”, that is still **P-0518** until proven otherwise.


## Added 2026-03-20 (307): observability route truth must not masquerade as delivery/completeness truth

When a proposal already has a decent **signal catalog / activation / route / redaction** shape but still lacks:

1. explicit **delivery-posture truth** (blocking, backpressure-buffered, lossy-buffered, batch-flush, periodic reader, sampled),
2. explicit **completeness-class meaning** (`attempted_all_events`, `best_effort_buffered`, `representative_sample`, `aggregated_window`, `exit_sensitive`),
3. or explicit **exit/flush dependence** for honest support summaries,

the next move is usually to sharpen the **existing observability-surface lane**, not to invent another tracing/exporter/collector crate.

Do not let the archive drift from “crate-authored observability contract” into:
- another subscriber/appender idea,
- another vendor/backend platform,
- or a vague “better telemetry delivery” implementation lane.

If the missing question is “what kind of delivery/completeness claim may another team honestly rely on from this signal route?”, that is still **P-0518** until proven otherwise.


## Added 2026-03-17 (220): cfg availability follow-on work must separate class, origin, and fidelity

When a proposal touches **conditional API availability**, **rustdoc markers**, **docs.rs-only documentation slices**, or **feature/target matrices**, future revisions must state explicitly whether the missing value is primarily about:

1. **availability-class policy**,
2. **origin receipts** (`cfg`, `doc(cfg)`, `auto_cfg`, `cfg(doc)`, docs.rs cfg, custom cfg, inference),
3. **matrix fidelity** (direct observation versus docs-only / hosted-import / inference),
4. **whole-project support truth**,
5. **docs.rs parity / hosted-build replay**,
6. or a **generic public-API / SemVer / rustdoc-JSON slice tool**.

Do not let future passes quietly rephrase item-level conditional API truth as “better docs”, “better docs.rs support”, or “another public API diff”. The sharper move is often to deepen **P-0451**.


## Added 2026-03-17 (223): performance-envelope packs must keep metric authority, environment fidelity, and noise class separate

When a proposal touches **benchmarks, profiles, CI perf imports, or performance claims**, future revisions must state explicitly whether the missing value is primarily about:

1. **named workload selection**,
2. **metric authority**,
3. **environment fidelity**,
4. **noise / confidence class**,
5. **generic benchmark or profiling substrate**,
6. or **hosted regression services**.

Do not let future passes quietly rephrase performance-envelope packs as “better benchmark outputs”, “better profiler integration”, or “better perf dashboards”. The archive now has a distinct lane for the receiver-facing performance contract, and within that lane it must keep **which number rules**, **how honest the environment was**, and **how trustworthy the result is** separate.


## Added 2026-03-17 (225): authority-surface follow-on work must separate budgets, injection boundaries, and profile witnesses

When a proposal touches **ambient powers, offline claims, determinism, capability handles, or sandbox-ready posture**, future revisions must state explicitly whether the missing value is primarily about:

1. **authority-budget policy** (required vs optional vs forbidden),
2. **injection-boundary truth** (ambient-only vs explicit-handle vs host-supplied),
3. **profile witnesses** under restricted recipes,
4. **compile-time sandbox policy**,
5. **capability-oriented substrate**,
6. **generic static authority scanning**,
7. or a **full sandbox/runtime host platform**.

Do not let future passes quietly rephrase crate authority contracts as “better sandboxing”, “better capability docs”, or “another security scanner”. The archive now has a distinct lane for the receiver-facing authority artifact, and within that lane it must keep **what powers are budgeted**, **where the boundary is explicit**, and **which claims were actually witnessed** separate.


### Added 2026-03-17 (228): upgrade-pack productization must keep hazard class, fixup capability, and lane fidelity separate

When a pass deepens **P-0514**, it must state explicitly:

1. what class of hazard is being claimed (`machine_fix_available`, `manifest_edit_required`, `behavior_check_required`, etc.),
2. what fix capability was actually observed and where it applies (source only, manifest/config, docs, or workspace scope),
3. and how much of the named `from -> to` lane was really checked across features, targets, runtimes, and package subsets.

Do not let future passes quietly flatten upgrade-pack work into “the changelog mentions it”, “cargo fix succeeded”, or “SemVer checks passed so migration is fine.”


## Added 2026-03-17 (229): capability-contract product plans must keep claim class, obligations, and fidelity separate

When a pass sharpens **producer-side support / interop contracts**, future revisions must state explicitly whether the main review object is about:

1. **claim class** (`declared`, `observed`, `inferred`, `manual_review_required`),
2. **support obligations** (`build.rs`, `links`, proc macros, docs.rs overlays, target overlays, MSRV, workspace inheritance),
3. **profile fidelity** (how complete the support story really is),
4. **shared ecosystem interop profiles**,
5. **task-first crate choice**,
6. **item-level availability**,
7. or **whole-project support policy**.

Do **not** let future passes silently flatten those into one fake “supported crate” verdict.
A producer-side capability contract is strongest when it makes claim class, adoption obligations, and profile completeness separately reviewable.

## Added 2026-03-17 (231): runtime handoff productization requires exactness, share-safety, and fidelity honesty

When a pass deepens **P-0513**, it must say explicitly whether the new value is about:

1. **capture exactness**,
2. **share safety / redaction**,
3. **handoff fidelity / completeness**,
4. **error-path versus panic-path boundaries**,
5. or **recovery-step linkage**.

Do not let future passes quietly flatten those into one fake “better crash report” result. A runtime handoff pack is not just a renderer, not just a panic hook, and not just a log bundle.


## Support-surface boundary reminder

Before proposing or editing a crate in the supportiveness cluster, check `meta/crate-support-surface-boundaries-2026-03-17.md`.
Do not flatten compile-time guidance, runtime handoff, observability, example surfaces, and diagnosis into one generic “better DX” lane.


Do not let the archive silently collapse “the README has a quickstart”, “rustdoc scraped an example”, “a maintainer says it works”, and “this crate publishes a witnessed official first-success path” into one vague adoption story. For **P-0524**, keep prerequisite origin, success witness, and scenario coverage as separate review objects.
Also keep **environment class**, **docs/example linkage**, and **normalization boundaries** explicit; a loopback quickstart, a credentialed-service walkthrough, and a board-only demo are not the same support promise even if all three have code samples.

## Added 2026-03-17 (235): cfg-availability passes must keep slice witness, gate normalization, and re-export lineage separate

When a pass deepens **P-0451**, it must say explicitly whether the new value is about:

1. **slice witness** (which target/feature/docs profile was actually observed and how),
2. **gate normalization** (how raw `cfg` / `doc(cfg)` / `doc(auto_cfg)` / docs.rs overlays were simplified for people),
3. **re-export lineage** (whether a public path inherits its effective gate from another path),
4. **availability class**,
5. **origin**,
6. or **fidelity**.

Do not let future passes quietly flatten “the docs showed a badge”, “docs.rs rendered the page”, “the hosted rustdoc JSON contains the item”, and “downstream users can rely on this item in that slice” into one fake availability story.


## Added 2026-03-17 (237): toolchain/target support passes must keep override lineage, component availability, and exercise scope separate

When a pass deepens **P-0484**, it must say explicitly whether the new value is about:

1. **override lineage** (which selector actually won),
2. **component availability** (requested vs effective vs unavailable),
3. **exercise scope** (`compile`, `docs`, `run`, `test`, `bench`, `host_build_script`, `host_proc_macro`),
4. **support class**,
5. **evidence provenance**,
6. or **external prerequisites**.

Do not let future passes quietly flatten the repository pin, the effective rustup selector, the installed components, and the actually exercised scopes into one fake support story.


## Added 2026-03-18 (238): pathfinder follow-on work must keep evidence origin, freshness windows, and starter-set scope separate

When a pass deepens **P-0509**, it must say explicitly whether the new value is about:

1. **evidence origin** (registry metadata vs crate-authored docs vs official Rust policy vs imported receipts vs local observation vs inference),
2. **freshness windows** (cooldown, recent-review, or steady-state treatment for new publishes or changed signals),
3. **starter-set scope** (teaching, production, org-policy, target-specific, or still manual-review territory),
4. **role coverage**,
5. **decision-axis weighting**,
6. or **manual-review boundaries**.

Do not let future passes quietly flatten crates.io security/publishing signals, docs.rs visibility, download counts, fresh publishes, and scoped starter-set answers into one fake “best crate” verdict.


## Added 2026-03-18 (240): Python-extension shipping passes must keep ABI class, thread-support declaration, and variant horizon separate

When a pass deepens **P-0466**, it must say explicitly whether the new value is about:

1. **ABI target class** (`version_specific`, `abi3`, split free-threaded, `abi3t` horizon),
2. **thread-support declaration** (`gil_used`, free-threaded safety claim, manual-review hotspots),
3. **variant horizon** (classic tags only, `abi3t` planned, wheel-variant monitoring, or implemented future surfaces),
4. **repair/publication evidence**,
5. **interpreter matrix coverage**,
6. or **downstream install guidance**.

Do not let future passes quietly flatten “build succeeded”, “wheel loads on a free-threaded interpreter”, “module declares GIL-disabled safety”, and “accepted packaging PEPs exist” into one fake “Python support” story.


## Added 2026-03-18 (242): Node-API shipping passes must keep prebuild coverage, loader route, and publish identity separate

When a pass deepens **P-0498**, it must say explicitly whether the new value is about:

1. **prebuild coverage** (`fully_prebuilt`, partial matrix, source-build escape hatch, or named unsupported tuple),
2. **loader route** (`node-addons`, native-first, `default`, local-build, or WASM fallback posture),
3. **publish identity** (trusted publisher, provenance expectation, token/manual release, or mixed release posture),
4. **runtime claim boundary** (Node-only versus Bun/Deno aspirations),
5. **Node-API floor**,
6. or **downstream intake guidance**.

Do not let future passes quietly flatten “package published”, “prebuild shipped”, “there is a fallback route”, and “trusted publishing/provenance is present” into one fake “Node support” result.


For Apple XCFramework / SwiftPM follow-on work specifically, also consult `meta/apple-xcframework-swiftpm-shipkit-product-plan-2026-03-18.md` so slice coverage, wrapper/checksum alignment, signature/origin posture, and privacy-manifest review do not get collapsed into one fake “the SDK ships for Apple” story.


## Added 2026-03-18 (244): NuGet native-package layering discipline

When a proposal touches **Rust-built native packages for .NET / NuGet**, future revisions must state explicitly whether the missing value is primarily about:

1. **binding generation** (`csbindgen`, handwritten bindings, source generators),
2. **package asset coverage** (`runtimes/<rid>/native`, portable-RID truth, native filename/layout),
3. **loader-route truth** (default probing, `SetDllImportResolver`, isolated `AssemblyLoadContext`, plugin hosts),
4. **deployment posture** (ordinary runtime, single-file, Native AOT, Unity/plugin host nuances),
5. **producer-side release contracts** (RID coverage reports, loader-route receipts, deployment-posture receipts),
6. **consumer-side doctoring** (why did this one app fail to load the package?),
7. or a **full .NET build / publishing platform**.

Do not let the archive silently collapse “bindings were generated”, “the package restored”, “a DLL loaded once”, and “Native AOT is mentioned in docs” into one vague .NET-support story. The strongest missing crates here are often **contract layers above substrate and below platforms**.

When sharpening **P-0499** further, require explicit answers to three separate questions: **what RID assets really shipped**, **what loader route is actually required**, and **what deployment modes are honestly supported**.

## Added 2026-03-18 (Hex deepening)

When future revisions touch **P-0502 Hex Native NIF ShipKit**, they must keep at least these facts visibly separate:

1. the **checksum file existing somewhere**,
2. the **checksum file actually being included in the published Hex tarball**,
3. the **minimum NIF version / OTP window** the release is configured for,
4. the **precompiled-target matrix** that really exists,
5. and the **trigger that forces a local build** on uncovered targets or prerelease/dev flows.

Do **not** let future passes treat “the checksum file is in git” as equivalent to “the Hex package is installable without Rust”.
Do **not** let “OTP 22+” become a vague folklore claim when the configured NIF floor may imply a narrower window.

## Added 2026-03-18 (246): JAR/JNI shipping passes must keep classifier dialect, native-access posture, and loader residency separate

When a pass deepens **P-0500**, it must say explicitly whether the new value is about:

1. **classifier dialect** (`os.detected.classifier` alignment, custom classifier schemes, or manual mapping requirements),
2. **native-access posture** (named-module enablement, `ALL-UNNAMED`, missing declaration, or manual review),
3. **loader residency** (`java.library.path`, absolute-path load, extraction-first load, or manual installation),
4. **symbol contract**,
5. **publication receipt**,
6. or **downstream intake guidance**.

Do not let future passes quietly flatten “attached artifacts published”, “the JVM loaded locally”, “runtime flags exist”, and “downstream consumers can intake the package boringly” into one fake JVM-support story.


## Added 2026-03-18 (247): R-package shipping passes must keep registration posture, DLL load contracts, and install posture separate

When a pass deepens **P-0526**, it must say explicitly whether the new value is about:

1. **registration posture** (registered routines, `useDynLib(..., .registration = TRUE)` alignment, wrapper/export drift, or manual review),
2. **DLL load contract** (`useDynLib`, `.onLoad` + `library.dynam`, package/lib name drift, installed `libs/` expectations),
3. **install posture** (CRAN-binary expectation, source-build/toolchain requirement, mixed posture, staged-install/manual-review boundary),
4. **wrapper surface**,
5. **build-toolchain receipt**,
6. or **downstream intake guidance**.

Do not let future passes quietly flatten “wrappers were generated”, “the package compiled once”, “CRAN may have binaries somewhere”, and “the package loaded on one machine” into one fake “R support” story.


## Added 2026-03-18 (248): RubyGems shipping passes must keep platform coverage, resolver routes, and extension residency separate

When a pass deepens **P-0501**, it must say explicitly whether the new value is about:

1. **platform coverage** (binary-gem matrix, source-build fallback, fat-gem gaps, or manual review),
2. **resolver route** (Gemfile `platforms:`, Ruby-engine claims, lockfile platform targets, `force_ruby_platform`, or cache-route assumptions),
3. **extension residency** (copied `lib/` artifacts, require stubs, shared-library basename/path alignment, or manual review),
4. **publish identity**,
5. **rebuild parity**,
6. or **downstream intake guidance**.

Do not let future passes quietly flatten “Bundler can scaffold Rust”, “the gem built once in CI”, “a platform gem exists somewhere”, “the require stub works on one machine”, and “trusted publishing is configured” into one fake “Ruby support” story.

## Added 2026-03-19 (173): text input needs separate event, selection, layout, and accessibility lanes

When a proposal or fixture touches **text input, IME/composition, cursor movement, selection, or editor-like replacement behavior**, future revisions must keep at least these surfaces separate:

1. **event ingress / adapter behavior**,
2. **IME transaction semantics**,
3. **document + selection semantics**,
4. **layout/shaping dependency surfaces**,
5. **accessibility export semantics**,
6. and **replay / capture / regression tooling**.

Do not let the archive silently collapse “typing changed” into one fake cause. In this frontier, many failures are really boundary bugs between backend event truth, transaction semantics, selection policy, layout policy, and accessibility export.


## Added 2026-03-19 (littlefs adoption lane hygiene)

When future revisions touch embedded flash/filesystem work, do **not** stop at “a pure-Rust littlefs crate now exists.” Ask whether the missing value is primarily:

1. raw engine correctness,
2. storage-adapter truth,
3. compatibility witnesses,
4. power-cut evidence,
5. host-side image tooling,
6. or an application-layer persistence product.

Do not let the archive silently collapse all six into one fake “embedded filesystem crate.”



## Added 2026-03-19 (desktop shipkit lane hygiene)

When future revisions touch desktop release/distribution work, do **not** stop at “the app was packaged successfully.” Ask whether the missing value is primarily:

1. packaging output,
2. signing/notarization identity,
3. update-channel topology,
4. crash-symbol handoff,
5. support-bundle export,
6. or backend crash-reporting/telemetry.

Do not let the archive silently collapse all six into one fake “desktop shipping support” story.


## Added 2026-03-19 (253): off-ramp productization must keep successor intent, stopgap horizon, and recipe witness separate

Do not let future passes say that a deprecation note, RustSec advisory, or redirect crate already solves the sunset story.
When touching **P-0515**, keep these distinct:

1. what is being sunset,
2. whether the current answer is a real successor or only a temporary stopgap,
3. what migration path was actually checked,
4. and where manual review still begins.

Do **not** collapse these back into vague “maintenance status”, “security status”, or “rename support”.


## Added 2026-03-19 (258): lifecycle-claim discipline refresh

When a pass sharpens **P-0520** or any nearby lifecycle/shutdown idea, future revisions must keep five questions separate:

1. what starts the work,
2. what stop verbs really do,
3. where blocking work weakens the stop claim,
4. what evidence proves cleanup completed,
5. what the supported drain recipe actually is.

Do **not** let “supports graceful shutdown” stand in for activation boundaries, detach-on-drop truth, `spawn_blocking` caveats, or teardown evidence.

When importing substrate from Tokio or adjacent crates, do not flatten these distinct facts:
- `JoinHandle` drop detaches work;
- `JoinSet` drop aborts tracked tasks, while `detach_all` keeps them running and `shutdown()` aborts then waits;
- `TaskTracker::wait()` has stronger completion meaning than merely requesting cancellation;
- `write_all` is not the same cancel/retry story as `write`, `flush`, or `shutdown`;
- shutdown frameworks and structured-concurrency crates are substrate, not the support contract itself.


## Added 2026-03-19 (259): resource-surface claim discipline refresh

When a pass sharpens **P-0521** or any nearby resource/capacity idea, future revisions must keep five questions separate:

1. what admits work first,
2. who owns the waiting room,
3. what can shrink effective capacity later,
4. what callers experience at the boundary,
5. what evidence really supports the claim.

Do **not** let “there is a queue”, “there is a pool limit”, or “there are metrics” stand in for admission order, backlog ownership, or acquire fate.

When importing substrate from Tokio, Tower, SQLx, Deadpool, or adjacent crates, do not flatten these distinct facts:
- unbounded buffering is not the same thing as a bounded queue with backpressure;
- a concurrency limit is not the same thing as owning backlog;
- a constructor-time permit count is not the same thing as runtime-effective capacity;
- pool size does not by itself tell callers whether they wait, time out, or wake closed.


## Added 2026-03-19 (261): test-surface claim discipline refresh

When a pass sharpens **P-0523** or any nearby testing-support idea, future revisions must keep four questions separate:

1. what fixtures/recipes are actually supported,
2. what topology and host capabilities the scenario really needs,
3. where the scenario witness came from,
4. what normalization/redaction/sorting rules are stabilizing the output.

Do **not** let “the crate has tests”, “CI passed”, “there is a wiremock example”, or “a replay artifact exists” stand in for a downstream testing contract.

When importing substrate from Tokio, nextest, `assert_cmd`, `wiremock`, `testcontainers`, `trybuild`, or `insta`, do not flatten these distinct facts:
- paused time is not the same thing as a fully deterministic async scenario;
- imported portable replay is not the same thing as a supported local recipe;
- compile-fail coverage is not the same thing as runtime/integration support;
- snapshot stability is not the same thing as semantic proof.

## Added 2026-03-19 (263): observability route truth versus mere signal existence

When planning or revising **crate observability-support** proposals, future passes must explicitly separate:

1. **signal existence** (there is `tracing` instrumentation in code),
2. **activation truth** (what features, filters, layers, env vars, cfgs, or runtimes are really required),
3. **bridge-route truth** (which route actually carries a signal to fmt/log output, console, traces, metrics, or logs),
4. **schema/query posture** (which semantic-convention and schema-URL commitments are being made),
5. **sensitivity boundaries** (which fields are safe, payload-derived, hashed, dropped, or manual-review territory),
6. and **backend governance** (collector/retention/org policy).

Do not let the archive flatten “the crate emits telemetry”, “the operator can see it through the documented route”, and “the field is safe to ship” into one fake observability story. The strongest missing crates here are usually **contract layers above plumbing and below platforms**.


## Added 2026-03-19 (265): guidance lane hygiene

When future revisions touch compile-time / early-failure support work, do **not** stop at “the crate has better diagnostics.” Ask whether the missing value is primarily:

1. message-stability truth,
2. guidance-channel truth,
3. environment-sensitivity truth,
4. recovery-origin truth,
5. recipe-witness truth,
6. or broad diagnosis/runtime handoff after the crate is already running.

Do not let the archive silently collapse all six into one fake “better errors” crate.

When importing substrate from the diagnostic namespace, rustdoc, `trybuild`, `ui_test`, `miette`, or proc-macro helpers, do not flatten these distinct facts:
- a `compile_fail` doctest proving failure is not the same thing as an exact-message contract;
- a nightly doctest error-code check is not the same thing as full stderr stability;
- a green `trybuild` snapshot can still be sensitive to `rust-src` and toolchain rendering;
- a proc-macro helper path is not the same thing as panic-free guidance in every misuse lane;
- a `miette` code/help/url surface is not the same thing as a witnessed recovery recipe.

## Added 2026-03-19 (266): pathfinder work must keep rank, freeze readiness, lock-in cost, and scope split separate

When future revisions sharpen **P-0509** or any adjacent crate-choice lane, do not let the archive collapse these four claims into one fake “best crate” story:

1. **what ranks well for the task right now**,
2. **what is actually ready to freeze as a starter set**,
3. **what lock-in cost the choice buys**, and
4. **whether teaching, production, or org-policy scopes legitimately diverge**.

More Cargo/crates.io/docs.rs signal is not proof that the selection problem is solved.
It is evidence that the pathfinder lane is now more buildable.
Future passes should keep **starter-set readiness**, **lock-in cost**, and **scope split** explicit rather than drifting back into popularity scores, blessing lists, or façade-crate wishcasting.


### Added 2026-03-19 (267): upgrade-pack work must keep hazard authority, package scope, and follow-through coverage separate

When a pass deepens **P-0514**, it must state explicitly:

1. where each hazard comes from,
2. which workspace/package/example/binary lanes were actually witnessed,
3. and whether machine fixes touched only Rust source or the whole migration surface.

Do not let future passes quietly flatten upgrade-pack work into “release-plz handled it”, “SemVer checks were green”, or “cargo fix succeeded so the upgrade is automated.”


### Added 2026-03-20 (268): upgrade-pack work must keep source lineage, hazard arbitration, and active follow-through state separate

When a pass deepens **P-0514**, it must state explicitly:

1. which imported human-authored release surfaces were canonical enough to back hazard authority,
2. where adjacent authorities still disagreed and whether the honest answer was abstention/manual review,
3. and which migration steps are still actively requested on the current lane versus merely completed on an older lane.

Do not let future passes quietly flatten upgrade-pack work into “the release page says so”, “SemVer was green so the other evidence probably doesn’t matter”, or “docs were already fixed once so the current lane is done.”


### Added 2026-03-20 (270): upgrade-pack work must keep source heads and pack readiness separate

When a pass deepens **P-0514** again, it must state explicitly:

1. which imported migration surface is merely the current **operational head**,
2. which source, if any, is the **citation-ready head** for that lineage,
3. and whether the overall pack honestly remains `hold`, only reaches `candidate`, or is actually `freeze_ready`.

Do not let future passes quietly flatten upgrade-pack work into “the docs page exists”, “the latest guide is probably good enough to cite”, or “the receipts look present so the pack must be ready to freeze.”


### Added 2026-03-20 (271): upgrade-pack work must keep queued review debt and consistency checks explicit

When a pass deepens **P-0514** yet again, it must state explicitly:

1. which remaining actions are in the **review queue** and which state they are in,
2. which of those actions block `candidate` versus `freeze_ready`,
3. and whether a **cross-register consistency** pass still fails, passes, or stays unknown.

Do not let future passes quietly flatten upgrade-pack work into “there is one next step so the rest is probably fine” or “the bundle looks polished enough that consistency can be assumed.”


### Added 2026-03-20 (272): upgrade-pack work must keep export posture and public surface exact

When a pass deepens **P-0514** again, it must state explicitly:

1. whether the lane is only `private_working` / `private_candidate` or is actually fit for `public_candidate` / `public_frozen`,
2. which sensitivity flags or redaction blockers still stop public export,
3. and which exact files/receipts make up the public surface instead of the whole working tree.

Do not let future passes quietly flatten upgrade-pack work into “the pack looks good so it is probably shareable” or “the summary exists so the whole bundle must be the public contract.”


### Added 2026-03-20 (273): upgrade-pack work must keep deviations and warning registers explicit

When a pass deepens **P-0514** again, it must state explicitly:

1. whether any non-default freeze/export/consistency posture is being carried under an active, expiring `deviation-ledger` entry,
2. which authority approved that deviation and when it expires,
3. and which warnings are still active, blocking, public, or only maintainer-facing in the `warning-register`.

Do not let future passes quietly flatten upgrade-pack work into “we proceeded anyway”, “the warning label is probably obvious from context”, or “the blocker is temporary so it does not need a durable record.”

### Added 2026-03-20 (276): upgrade-pack work must keep exact capture context and sparse coverage matrices explicit

When a pass deepens **P-0514** again, it must state explicitly:

1. which imported receipts are bound to which exact `capture-context` entries,
2. which package/target/feature/profile cells are actually present in the `coverage-matrix`,
3. and which neighboring cells remain unknown, manual-review-only, unsupported, or unrequested.

Do not let future passes quietly flatten upgrade-pack work into “cargo fix succeeded”, “metadata was imported”, or “these features/targets were mentioned so the lane was checked.”


### Added 2026-03-20 (277): upgrade-pack work must keep public trace paths explicit

When a pass deepens **P-0514** again, it must state explicitly:

1. which public or downstream-facing claims have a `public-trace-path` route,
2. which exported receipt/warning/queue refs those routes land on,
3. and which routes still fail as `public_trace_fragment_missing`, `public_trace_target_missing`, or `public_trace_private_only`.

Do not let future passes quietly flatten upgrade-pack work into “the claim has evidence refs”, “the file is exported so the route is fine”, or “a broken anchor is close enough for a public contract.”


### Added 2026-03-20 (278): upgrade-pack work must keep lane-selection origin explicit

When a pass deepens **P-0514** again, it must state explicitly:

1. what the invocation subject was and how the manifest walk resolved,
2. whether workspace attachment came from ambient `default-members`, explicit package selection, `--workspace`, or another normalized cause,
3. and which omitted sibling members or gated targets remain outside the lane for ambient-selection reasons rather than reviewed clean status.

Do not let future passes quietly flatten upgrade-pack work into “the package scope is obvious”, “the workspace root means the whole workspace was intended”, or “a missing target was probably reviewed elsewhere.”


### Added 2026-03-20 (279): upgrade-pack work must keep durable public cues explicit

When future revisions sharpen **P-0514** or adjacent public-contract work, do not let the archive collapse these two claims into one fake “public warning surface” story:

1. **traceability** — whether a reader can follow a route into the governing exported receipt,
2. **durable visibility** — whether the controlling meaning is still unmistakably present on the exported entry surface without forcing the reader to chase it.

Do not let future passes quietly treat any of the following as sufficient by themselves:

- a warning label in `publication-surface.manifest.json`,
- a machine-readable warning/freshness/deviation register entry,
- a technically valid public trace route into a supporting receipt,
- or an exported bundle that merely contains the right file somewhere.

A blocking warning, supersession notice, or manual-review boundary that governs the public contract should stay durably visible on the exported entry surface, not just discoverable after extra inspection.


## Added 2026-03-20 (281)
- Do not let “the pack is internally consistent” turn into “the pack is independently reviewed”; maker-only polish, same-team checks, independent checking, and fallback review must stay distinct when shaping public/frozen upgrade surfaces.


## Added 2026-03-20 (284)
- Do not let an ordinary-looking Cargo command line stand in for the reviewed baseline; when hidden Cargo config hierarchy, `--config`, environment-variable overrides, `[patch]`, source replacement, or local path overrides materially shape a lane, keep that basis explicit rather than burying it in an `env` digest or stray note.


## Added 2026-03-20 (289)
- Do not let future pathfinder work flatten **freshness windows**, **revisit triggers**, **decision-watch state**, and **replacement choice** into one fake “starter-set drift” story. A frozen answer being due for review is not the same thing as being invalidated, and neither is the same thing as automatically choosing a new crate.


## Added 2026-03-20 (295)
- Do not let future workload-identity passes flatten **identity source**, **trust-domain scope**, **peer-identity visibility**, and **rotation/failure posture** into one fake “supports SPIFFE/SPIRE” story. A live Workload API X.509 path, a delegated identity path, and a static dev identity are not the same support surface.


## Added 2026-03-20 (116): do not mistake docs-visible surface for real usability

When future revisions notice stronger rustdoc/docs.rs conditional-API substrate — for example `doc_cfg` stabilization progress, docs.rs rustdoc JSON, or default-target changes — do not stop at “conditional API support is solved now.” Ask instead:

- is the item merely **docs-visible**,
- is it **doctest-usable**,
- is it **downstream-compile-usable**,
- and did a hosted default-surface change widen what readers see without widening real support?

Do not let the archive silently equate “a gate marker is rendered” or “docs.rs shows the item by default” with “another team can rely on this API in code.” The missing crate may be the **usability witness, default-surface drift report, or audience-specific diff** above that substrate.

## Added 2026-03-20 (117)
- Do not let future MSRV work flatten **declared policy**, **policy activation**, **command-family floors**, **pinned-lockfile buildability**, and **lockfile-authoring compatibility** into one fake “MSRV support” story. A green build from an existing lockfile is not the same witness as an active `fallback` resolver policy, and neither is the same thing as being able to keep running `cargo update`, `cargo generate-lockfile`, or `cargo package` on that same floor.


## Added 2026-03-20 (118)
- Do not let future publish-support work flatten **local artifact capture basis**, **authoritative index facts**, **publish identity**, and **docs/public-visibility lag** into one fake “publish succeeded” story. A release accepted by Cargo, a checksum observed in the index, and docs.rs eventually building are different truths and should remain separate in any honest post-publish contract.


## Added 2026-03-20 (119)
- Do not let future package-review work flatten **authored tree**, **raw `.crate` archive**, **Cargo JSON path lineage**, and **extracted verification-tree mutation** into one fake “reviewed package” story. A copied `Cargo.toml.orig`, a generated packaged `Cargo.toml`, and an extracted tree with `.cargo-ok` are different surfaces and should remain separate in any honest pre-publish contract.

## Added 2026-03-20 (301): crate test-surface packs must keep isolation class, runner assumptions, and reset posture separate

When refining **P-0523** or any adjacent downstream-testing lane, do not collapse these questions into one fake “isolated test support” story:

1. **isolation class** — fresh per call, fresh per test, process-shared, externally shared, or only safe because the runner isolates each test process;
2. **runner assumption** — safe under shared-process `cargo test`, only under serial execution, only under nextest, or manual-review-required;
3. **reset / cleanup posture** — OS cleanup, Drop cleanup, explicit reset, best-effort external teardown, or no reset support.

Do not let a deterministic seam, a witness artifact, or a Docker-backed topology masquerade as proof of cross-test contamination safety.
A mock server can still be shareable-unsafely, an environment-mutating helper can still be runner-specific, and a temp-state helper can still rely on destructors rather than OS cleanup.

## Added 2026-03-20 (302): localization/runtime work must keep schema, data, coverage, and fallback separate

When refining **P-0039** or any adjacent localization lane, do not collapse these into one fake “supports localization” story:

1. **message schema** — what arguments a public message actually accepts;
2. **data profile** — compiled defaults, baked subsets, runtime providers, and mixed modes;
3. **formatter coverage** — plain substitution versus ICU4X-backed rich formatting families;
4. **fallback witness** — the actual locale-resolution path observed for a request.

Do not let “uses ICU4X”, “uses Fluent”, or “compile-time checked ids/args” masquerade as proof that another team can rely on rich formatting breadth or a particular locale/fallback contract.

## Added 2026-03-20 (304): schema-compatibility work must not flatten basis, profile, strength, and policy

When future revisions sharpen **P-0124** or adjacent schema/tooling ideas, do not let the archive collapse these four claims into one fake “no breaking schema changes” story:

1. **what was compared** — pairwise baseline, latest-only subject check, transitive all-history check, generated schema diff, or validation-only current schema;
2. **which profile ruled** — Buf `FILE`/`PACKAGE`/`WIRE_JSON`/`WIRE`, OpenAPI severity threshold, registry compatibility mode, or validation-only posture;
3. **how strong the finding is** — definite, potential, witness-backed, validation-only, or manual-review-only;
4. **what policy changed the outcome** — ignore files, waivers, thresholds, and review-only gates.

Do not let future passes quietly restate any of the following as a universal compatibility verdict:

- “Buf passed”,
- “OpenAPI diff is clean”,
- “registry compatibility passed”,
- “JSON Schema validates”.

The sharper move is to ask for one compact contract that keeps **basis**, **profile**, **strength**, and **policy** explicit.



## Added 2026-03-20 (125)
- Do not let future Cargo config work flatten **effective config**, **live invocation basis**, **redaction safety**, and **replayability** into one fake “Cargo config captured” story. A safe-to-share support bundle is not automatically a replayable invocation bundle, and a reconstructed file scan is not automatically the same thing as a live failing command’s exact config context.


## Added 2026-03-20 (126)
- Do not let future secret-handling work flatten **revelation path**, **persistence posture**, **memory posture**, and **export posture** into one fake “uses secrets safely” story. A native keychain path is not the same as an env-string path later wrapped in `SecretBox<T>`, a zeroize-on-drop wrapper is not the same as protected memory, and debug redaction is not the same as serialization or reveal-path denial.


## Added 2026-03-20 (308): feature lists and all-features CI do not prove feature support truth

When **P-0528** is in play, do not let a crate sound like it has an honest feature contract merely because:

- the `[features]` table is documented,
- `cargo tree -e features` can explain activation causes,
- `--all-features` passes in CI,
- or a workspace-hack crate unifies features for speed.

The sharper move is to ask which feature names are **public support surface**, which are **hidden dependency plumbing**, which **named profiles** are actually supported, whether conflicts are explicit, and where unification/default behavior can still surprise downstream users.


## Added 2026-03-20 (309): channel names do not prove channel support truth

When **P-0529** is in play, do not let a crate sound like it has an honest channel contract merely because:

- it says “bounded”,
- it exposes `Sender` / `Receiver`,
- it documents clean shutdown somewhere,
- or benchmarks show high throughput.

The sharper move is to ask what **capacity posture** exists, what the **overflow policy** is, what send success actually means in terms of **delivery obligation**, and what **close/drop/drain** do to buffered work. A latest-only watcher, lagging broadcast, rendezvous handoff, and drop-oldest ring are materially different support surfaces even when each is truthfully called a channel.


## Added 2026-03-21 (311): CLI support must keep parse surface, output modes, terminal posture, and exit meaning separate

When future revisions touch command-line tooling, do not let the archive collapse these four claims into one fake “polished CLI” story:

1. **what parses** — command/subcommand/flag/value-hint surface, aliases, and deprecation posture;
2. **what emits** — human summary, machine-readable records, stdout/stderr ownership, and framing;
3. **what changes with terminal context** — color policy, progress visibility, prompts, editor/pager handoff, and pipe/CI behavior;
4. **what termination means** — success, usage error, empty result, partial success, interruption, or manual review.

Do not mistake `clap`, `anstream`, `indicatif`, `dialoguer`, or CLI snapshot tests for proof that the receiver-facing contract already exists.
When **P-0531** is in play, require those four truths to stay distinct.


## 2026-03-21 refinement — debuggability support now needs backend coverage and capability ceilings

- Treat `meta/debuggability-support-product-plan-2026-03-17.md` and `meta/debuggability-support-backend-coverage-2026-03-21.md` as the current working sketch for **P-0486**.
- Keep **support-class truth**, **symbol-layout / handoff truth**, **backend-coverage truth**, **advanced-capability truth** (`async_debugging`, `expression_evaluation`), and **source-lookup impact truth** explicit.
- Prefer tiny receiver-facing artifacts such as `support-posture.report`, `artifact-handoff.manifest`, `debugger-backend-coverage.report`, and `source-lookup-impact.report` rather than another debugger launcher, crash backend, or giant IDE integration layer.


## Added 2026-03-21 (316): Cargo cache cleanup claims need surface and recovery truth

When future revisions touch Cargo cache/storage tooling, do not let the archive collapse these four claims into one fake “Cargo cache cleaned safely” story:

1. **what surface was governed** — Cargo-home global cache, target-dir final artifacts, build-dir intermediates, or a future user-wide/plugin-backed cache;
2. **how evicted entries return** — local recreation, redownload, plugin fetch, or manual-review-only recovery;
3. **who pays the cost later** — local developer, CI/shared runner, remote cache, or an unknown future operator;
4. **whether offline posture changes the judgment** — an acceptable online cleanup plan can still be a bad offline policy.

Do not mistake `cache.auto-clean-frequency`, `cargo clean`, a `du` report, or a third-party cache scanner for proof that a receiver-facing cleanup contract already exists.
When **P-0480** is in play, require those four truths to stay distinct.


## Added 2026-03-21 (317): trust-watch work must keep current visibility, advisory feeds, publish-identity posture, and blog coverage separate

When future revisions touch **P-0017** or adjacent trust/security lanes, do not let the archive collapse these four claims into one fake “trust watch configured” story:

1. **what is visible right now** — current Security-tab or advisory-page state;
2. **what is monitored continuously** — RustSec advisory imports / RSS or equivalent watch routes;
3. **what says something about publish identity** — Trusted Publishing posture and related settings;
4. **what is only partial or exceptional broadcast** — blog posts or incident writeups that are explicitly not comprehensive for routine malware removals.

Do not mistake a clean crate page, a Trusted Publishing setting, or one high-signal blog post for proof that another team has an honest ongoing dependency-trust watch surface.
When **P-0017** is in play, require those four truths to stay distinct.

## Added 2026-03-21 (318): workspace tool declarations do not prove route truth

When **P-0055** is in play, do not let a crate sound like it has an honest workspace tool contract merely because:

- the repo declares pinned tool versions somewhere,
- a local or CI bootstrap script installs tools,
- `$CARGO_HOME/bin` contains the expected `cargo-*` command,
- or the same binary path appeared in two runs.

The sharper move is to ask what **install-root posture** is being claimed, which **executable actually won resolution**, what **shadowing candidates** existed, and what **rustup/toolchain context** surrounded the run. A workspace-managed binary, a cargo-home subcommand, and the same binary under `cargo +beta` are materially different support surfaces even when all three look like “the tool ran”.


## Added 2026-03-21 (321): reflection/comptime work must keep source authority, coverage scope, execution posture, and loss accounting separate

When future revisions touch **P-0439** or adjacent reflection-like lanes, do not let the archive collapse these into one fake "reflection support" story:

1. **schema source / authority** — runtime registry export, associated-const shape export, compile-time const-eval adapter, serialization-format projection, or mixed/manual-review source;
2. **coverage scope** — declared type families, registered concrete instantiations only, format-schema projection only, or mixed/manual-review coverage;
3. **execution posture** — registry required, registry optional, pure static metadata, compile-time-only adapter, runtime value access, or manual-review posture;
4. **loss accounting** — which metadata classes were preserved, dropped, synthesized, or are still unresolved.

Do not let any of the following stand in for an honest bridge answer:

- "uses Bevy reflection",
- "has a SHAPE const",
- "can generate formats with Serde",
- "future const reflection will solve this",
- or "reflection metadata exists somewhere in the build".

A crate can have valuable reflection-like metadata while still leaving generic coverage, docs/attribute fidelity, runtime dependence, or mutation surface unresolved.


## Added 2026-03-21 (324): machine-readable test output does not prove a portable run contract

When **P-0106** is in play, do not let a crate sound like it has an honest test-run artifact contract merely because:

- it can emit JUnit,
- it can emit some JSON,
- it has a nextest recording,
- or its custom harness looks like libtest.

The sharper move is to ask what **run identity** is being claimed, what exact **selection basis** defined the run, what **retry/stress/fail-fast/process** semantics changed the verdict meaning, and whether the bundle is merely portable or actually **share-safe**. A replayable recording, a lossy import, and a public-safe artifact are materially different support surfaces even when each can be truthfully called “machine-readable test output.”


## Added 2026-03-21 (326): array work must keep semantic profile, layout/view, device+dtype, namespace coverage, and interop routes separate

When future revisions touch **P-0003** or adjacent numerics lanes, do not let the archive collapse these into one fake “supports arrays” story:

1. **semantic profile** — dense n-D core, dense linear algebra, tensor backend, columnar bridge only, or manual-review required;
2. **layout/view truth** — row/column/custom stride posture, borrowed/mutable view support, contiguous assumptions, and reshape/layout caveats;
3. **device+dtype truth** — host-only versus runtime devices, default device, default dtype basis, and transfer posture;
4. **namespace coverage** — creation, indexing, broadcasting, reductions, linear algebra, autodiff extensions, and columnar bridge support;
5. **interop routes** — borrowed, zero-copy, copy-required, lossy, or manual-review boundary crossings.

Do not let any of the following stand in for an honest array contract:

- “NumPy-like”,
- “backend agnostic”,
- “supports matrices”,
- “supports tensors”,
- or “can convert to Arrow”.

A crate can be valuable in one of those ways while still leaving profile, layout, device, or conversion truth unresolved.


## Added 2026-03-21 (329): verification work must keep obligation inventory, lane semantics, trust ledger, policy evaluation, and comparability separate

When future revisions touch **P-0485** or adjacent verification lanes, do not let the archive collapse these into one fake “verification green” story:

1. **obligation inventory** — what exactly needed to be checked and what evidence classes counted;
2. **lane semantics** — dynamic execution, bounded proof, deductive proof, refinement check, theorem proof, or manual-review route;
3. **trust ledger** — trusted functions, axioms, externals, stubs, waivers, and review owners;
4. **policy evaluation** — why the campaign is green, yellow, or red;
5. **comparability / drift** — whether tool/version/target/trust changes still permit a meaningful diff.

Do not let any of the following stand in for an honest campaign answer:

- “Miri passed”,
- “Kani proved it”,
- “Creusot replayed”,
- “Prusti only used one trusted function”,
- “Flux refined the core module”,
- or “Verus proved the hard part”.

A campaign can contain all of those truths and still remain yellow, partially comparable, or blocked on trust review.


## Added 2026-03-21 (331): bundle substrate receipts before more private bundle grammars

When a future pass touches **P-0256** or proposes another bundle-first crate, it must now say explicitly:

1. the **container basis** for deterministic-pack claims,
2. the **entry lineage** for raw vs projected vs generated vs imported content,
3. the **attestation lane** in use (if any),
4. the **publication route** (if any),
5. and the **share-safety posture** for exported packs.

Do **not** let “bundle verified” silently mean all of the following at once:

- local pack integrity,
- imported signature validity,
- OCI or transparency publication status,
- and “safe to send outside the team”.

Also preserve the archive-hygiene fact that the current fixture root is `fixtures/evidencebundle-core-kit/` until a deliberate bulk rename occurs.
Future passes should not oscillate between `evidencebundle` and `evidence-bundle` spellings inside one revision.


## Added 2026-03-21 (335): service-transition truth must keep activation, readiness, health, drain, and fate separate

When a future pass touches **P-0534** or adjacent service-operation lanes, do not let the archive collapse these into one fake “service is ready/healthy and drains gracefully” story. Keep explicit: (1) activation gate, (2) readiness surface, (3) health channel, (4) shutdown trigger, (5) drain policy, and (6) in-flight fate. `poll_ready` is not a load-balancer promise, a health endpoint is not startup completion, and graceful-shutdown enablement is not a proof of timeout aftermath.


For async dyn transition work specifically, also consult `meta/async-dyn-transition-product-plan-2026-03-21.md` and `meta/async-dyn-transition-lane-boundaries-2026-03-21.md` so recipe identity, object surface, allocation posture, tooling interop, and native-readiness posture do not get collapsed into one fake “async dyn support” story.


## Added 2026-03-21 (337): assurance-case passes must keep import policy, review gates, and export projection separate

When a future pass touches **P-0503 Assurance Case Workbench Kit**, it must say explicitly:

1. which **claim-library / argument basis** is in force,
2. what the **import policy** is for freshness and trust,
3. what the unresolved **assumption ledger** contains,
4. why the current **review gate** is green/yellow/red/blocked,
5. and what any **GSN / SACM** export preserves, redacts, or loses.

Do not let the archive silently treat a standards-shaped export as proof that the internal review status stayed lossless.


For sanitizer workflow evidence specifically, also consult `meta/sanitizer-profile-evidence-product-plan-2026-03-22.md` and `meta/sanitizer-profile-evidence-lane-boundaries-2026-03-22.md` so instrumentation scope, runtime-linkage route, symbolization route, and suppression policy do not get collapsed into one fake “sanitizer enabled” story.

## Added 2026-03-22 (343): crate stewardship must keep coverage, routing, and continuity separate

When a future pass touches **P-0011 Crate Health Contract Kit**, do not let the archive collapse these into one fake “maintained crate” story:

1. **maintenance coverage** — which duties are broadly covered,
2. **work routing** — where those duties are supposed to enter,
3. **response-channel posture** — public vs private vs structured vs manual-review-only,
4. **continuity backstop** — what keeps the crate responsive during absence or overload,
5. **succession** — what eventual handoff exists.

Do not let any of the following stand in for an honest stewardship answer:

- “the crate has issues enabled”,
- “CODEOWNERS exists”,
- “private vulnerability reporting exists”,
- “an organization owns the repo”,
- or “trusted publishing is enabled”.

A crate can have all of those facts and still leave real maintenance routing unresolved.

## Added 2026-03-22 (344): unsafe-review work must keep authority source, obligation inventory, interpreter boundary, and witness fidelity separate

When a future pass touches **P-0120 Unsafe Contract Auditor Kit**, do not let the archive collapse these into one fake “unsafe checked” story:

1. **authority source** — where each unsafe obligation came from,
2. **obligation inventory** — what unsafe sites and APIs actually need to be justified,
3. **interpreter boundary** — what the chosen witness could not observe,
4. **witness fidelity** — what a pass or fail actually means,
5. **bundle portability** — whether another reviewer can consume the result without local folklore.

Do not let any of the following stand in for an honest unsafe contract answer:

- “Miri passed,”
- “every unsafe block has comments,”
- “Loom found no race,”
- “the crate uses Rust 2024 `unsafe extern`,”
- or “unsafe attributes were added.”

A crate can have all of those facts and still leave authority-source truth, FFI limits, symbol obligations, or manual-review debt unresolved.


## Added 2026-03-22 (350): compile-time sandbox passes must keep authority, actor scope, mode, exceptions, and drift separate

When a future pass touches **P-0107 Cargo Sandbox & Capability Policy Kit**, do not let the archive collapse these into one fake “sandboxed build” story:

1. **policy authority** — where the effective policy came from,
2. **actor scope** — which build-time actor got which powers,
3. **enforcement mode** — observe, audit, or enforce,
4. **exception ownership** — which break-glass grants exist and who owns them,
5. **policy drift** — what materially changed.

Do not let any of the following stand in for an honest compile-time sandbox answer:

- “the build passed under cackle,”
- “cargo-sandbox was used,”
- “network is usually disabled,”
- “the manifest says default deny,”
- or “a CI wrapper exists.”

A workflow can have all of those facts and still leave the real authority route, proc-macro granularity, or release-to-release trust expansion unresolved.


## Added 2026-03-22 (351): rebuild-causality passes must keep baseline authority, comparison compatibility, reverse impact, and exactness separate

When a future pass touches **P-0469 Cargo Rebuild Explanation Kit**, do not let the archive collapse these into one fake “Cargo explained the rebuild” story:

1. **baseline authority** — why this comparison run was selected,
2. **comparison compatibility** — whether the compared runs were apples-to-apples enough to support the claim,
3. **reverse impact** — which dependents merely rebuilt,
4. **interface-change proof** — which stronger claims remain unproven,
5. **exactness class** — imported vs normalized vs inferred vs manual-review-only.

Do not let any of the following stand in for an honest rebuild explanation answer:

- “there was a session id”,
- “cargo report rebuilds printed a reason”,
- “the nearest prior run was used”,
- “reverse dependencies rebuilt”,
- or “timings HTML existed”.

A workflow can have all of those facts and still leave the real comparison-window authority or reverse-fanout meaning unresolved.


## 2026-03-22 addendum — trait-solver drift hygiene

When sharpening **P-0442**, prefer adding product-plan detail, solver-lane receipts, obligation-class reports, diagnostic-normalization rules, minimization-lineage receipts, and scenario fixtures before inventing another neighboring compiler-drift crate. Keep borrowck transition work (**P-0446**), SemVer/public-surface witness work, and raw compile-fail harnessing separate from the joined solver-drift verdict.

## Added 2026-03-22 (364): MC/DC-facing work must keep decision authority, construct support, independence evidence, caveats, and lineage separate

When future revisions touch **P-0433** or adjacent coverage lanes, do not let the archive collapse these into one fake “MC/DC coverage is supported” story:

1. **decision authority** — what decision inventory was actually in scope;
2. **construct support** — which language constructs were supported, unsupported, or excluded;
3. **independence evidence** — whether each condition has witnessed independence pairs;
4. **caveat basis** — which unstable flags, toolchain limits, or known issues constrained the result;
5. **evidence lineage** — which concrete runs and merged profiles back the verdict.

Do not let any of the following stand in for an honest answer:
- “coverage ran successfully”,
- “`cargo llvm-cov --mcdc` was used”,
- “overall percentages improved”,
- “the HTML report looks right”,
- or “LLVM emitted branch data”.

A crate can have all of those truths and still leave decision scope, unsupported constructs, independence evidence, or lineage unresolved.


## Added 2026-03-22 (367): single-file-package support must keep frontmatter authority, discovery scope, invocation semantics, cache residency, and export lineage separate

When future revisions touch **P-0435**, do not let the archive collapse these into one fake “Cargo scripts are handled” story:

1. **frontmatter authority** — what was explicit, inferred, defaulted, or rejected;
2. **discovery scope** — what workspace/config discovery rules applied or stayed out of scope;
3. **invocation semantics** — whether Cargo used manifest-command or subcommand behavior;
4. **cache residency** — where target-dir and lockfile state actually lived;
5. **export lineage** — what must be preserved when materializing a normal package.

Do not let any of the following stand in for an honest answer:
- “the script runs on nightly”,
- “frontmatter parsed”,
- “workspace auto-discovery was disabled”,
- “a `Cargo.lock` exists somewhere”,
- or “we can export it later”.

A workflow can have all of those facts and still leave provenance, portability, or handoff truth unresolved.

## Added 2026-03-22 (368): broad scans must keep territory mapping, synthesis, and docs/assistant lanes separate

When a future pass is broad (“what is Rust still missing?”), do not let the archive collapse these into one fake “we found more ideas” story:

1. **territory rerank** — what actually moved up or down in ecosystem salience;
2. **synthesis/elimination** — which old ideas should be merged, reframed, or rejected;
3. **support-contract deepening** — which lane deserves a sharper receiver-facing artifact rather than a new wrapper;
4. **docs/support/search handoff** — which lane owns canonical crate knowledge for downstream consumers;
5. **assistant-facing exports** — which machine-readable bundles are for packaging and handoff rather than inference.

Do not let any of the following stand in for an honest broad scan:
- “there are lots of new crates,”
- “users want AI tooling,”
- “rustdoc JSON exists,”
- “docs.rs hosts docs,”
- or “a README can be embedded.”

A pass can have all of those truths and still fail to say which lane actually owns canonical crate knowledge.

Before adding any new docs/assistant-facing proposal, explicitly check whether the idea is already substantially owned by **P-0051**, **P-0472**, **P-0476**, **P-0455**, or **P-0536**.



## Added 2026-03-22 (370): top-lane readiness beats adjacent proposal sprawl

When a top-five lane already exists and still lacks one of the following:
1. a first-class artifact schema,
2. a worked scenario fixture,
3. or a clean boundary against an adjacent lane,

prefer deepening that lane before adding another nearby proposal.

Apply this especially to:
- dependency lifecycle vs trust scoring / off-ramp / source parity,
- crate knowledge vs docs wrappers / assistant portals,
- crate health vs funding/popularity dashboards.

Do not let “new research found more nuance” turn automatically into “open another proposal”.
A lot of the archive’s value now comes from bringing high-salience lanes to **schema-and-scenario parity**.


## Added 2026-03-22 (372): crate stewardship must keep imported context, routing drift, and support bundles separate

When a future pass touches **P-0011 Crate Health Contract Kit**, do not let the archive collapse these into one fake “maintained crate” story:

1. **maintainer-declared stewardship artifacts** — what maintainers actually promised,
2. **imported stewardship context** — what crates.io or the host platform currently exposes,
3. **routing drift** — what changed across releases, transfers, or routing edits,
4. **portable support bundle truth** — what another team can inspect in one bundle,
5. **manual-review gaps** — what richer substrate still does not answer.

Do not let any of the following stand in for an honest stewardship answer:

- “the crate has a Security tab”,
- “Trusted Publishing Only Mode is enabled”,
- “`pubtime` exists in the index”,
- “CODEOWNERS exists”,
- “private vulnerability reporting is enabled”,
- or “the repo transferred successfully”.

A crate can have all of those facts and still leave real support routing, release ownership, docs freshness, or continuity meaning unresolved.


## Added 2026-03-22 (373): async runtime assurance passes must keep runtime model, evidence class, drift, and bundle lanes separate

When future revisions touch **P-0532** or adjacent async/runtime lanes, do not let the archive collapse these into one fake “runtime support” story:

1. **runtime model** — Tokio-style hosted runtime, Embassy-style embedded executor, RTIC-style interrupt-priority scheduler, or mixed/custom lane;
2. **evidence class** — docs only, docs plus metrics, docs plus on-target measurement, imported assurance artifact, or manual review;
3. **drift meaning** — runtime model changed, only evidence changed, or broader support meaning changed;
4. **bundle shape** — host-only lane, target-only lane, or mixed host-and-target runtime bundle.

Do not let any of the following stand in for an honest answer:
- “the crate uses Tokio”,
- “we export runtime metrics”,
- “it runs in host integration tests”,
- “the runtime is embedded-friendly”,
- or “we have an assurance note somewhere”.

A crate can have all of those truths and still leave runtime-model meaning, target scope, evidence class, or bundle boundaries unresolved.

## Added 2026-03-22 (377): rebuild-causality passes must keep baseline choice, comparison scope, route drift, and adjacent imports separate

When future revisions touch **P-0469** or nearby Cargo build-pain lanes, do not let the archive collapse these into one fake “we know why Cargo rebuilt” story:

1. **baseline authority** — why this comparison window was chosen,
2. **comparison scope** — whether the sessions are actually comparable enough to explain together,
3. **artifact-route drift** — whether `build-dir`, `target-dir`, rust-analyzer private target-dir, or wrapper lanes changed reuse meaning,
4. **observed rebuild causes** — what Cargo or live capture actually showed,
5. **adjacent-lane imports** — tool-parity, contention, or historical context that remained explicitly imported.

Do not let any of the following stand in for an honest answer:
- “Cargo reported rebuilds,”
- “the nearest session looked similar,”
- “the target directory was the same,”
- “rust-analyzer also built here,”
- or “the timings report showed work happened.”

A bundle can have all of those facts and still fail to say whether the comparison was in scope, whether route drift changed reuse expectations, or whether adjacent context was over-read as proof.

## Added 2026-03-22 (378): lock-contention passes must keep same roots, conflicting lock modes, residual surfaces, and mitigation outcomes separate

When future revisions touch **P-0490** or nearby Cargo contention lanes, do not let the archive collapse these into one fake “Cargo lock problem solved” story:

1. **shared roots** — which target/build/package-cache roots were actually shared,
2. **conflicting lock modes** — whether those roots were in a mode that should interfere,
3. **residual contention** — what still remains after the mitigation,
4. **mitigation outcome** — what really changed before vs after,
5. **artifact duplication cost** — what the mitigation bought at storage/reuse cost.

Do not let any of the following stand in for an honest answer:
- “they used the same package cache,”
- “we set a different target dir,”
- “build-dir was split,”
- “Cargo was active in the background,”
- or “the symptom looked better afterward.”

A bundle can have all of those truths and still fail to say whether the lock mode actually conflicted, whether significant residual contention remained, or whether the before/after outcome was proved rather than merely changed.

## Added 2026-03-22 (381): FFI passes must keep interface authority, callback lifetime, representation, and coverage separate

When future revisions touch **P-0121** or adjacent interop lanes, do not let the archive collapse these into one fake “the bindings are covered” story:

1. **interface authority** — whether Rust declarations, WIT, bridge modules, or another artifact is primary;
2. **generated derivatives** — headers/bindings emitted from that authority but not themselves the primary contract;
3. **callback execution** — where callbacks run and how they complete;
4. **callback lifecycle** — clone/free/unregister/cancel/drop rules and late-call-after-teardown hazards;
5. **binding coverage** — directly checked, generated-only, packaging-only, docs-only, or manual review;
6. **representation / error posture** — by-value/shared, opaque, serialized, canonical-ABI, result/exception/status/panic routes.

Do not let any of the following stand in for an honest answer:
- “we use UniFFI,”
- “the crate has a C header,”
- “CXX has static assertions,”
- “callbacks are supported,”
- or “the mobile bindings build in CI.”

A crate can have all of those truths and still leave primary authority, callback teardown, lifetime hazards, or verification scope unresolved.


## Added 2026-03-22 (384): FFI passes must keep authority, projection basis, parity, and built/package proof separate

When future revisions touch **P-0121** or adjacent interop lanes, do not let the archive collapse these into one fake “the foreign API is covered” story:

1. **primary authority** — Rust declarations, WIT, bridge modules, UDL/proc-macro declarations, etc.;
2. **projection basis** — what generated header/binding/custom section is being discussed and what tool/backend/config produced it;
3. **derivative parity** — whether that emitted artifact is full, subset, backend-shaped, renamed, or manual-review-only;
4. **build/package proof** — whether emitted source was actually built, packaged, or only generated;
5. **release-to-release drift** — whether receiver-visible foreign-surface change happened because authority changed, generator/config changed, or both.

Do not let any of the following stand in for an honest answer:
- “the header was generated,”
- “the bindings compile in one backend,”
- “the same bridge family is still in use,”
- “UniFFI generated source for Swift/Kotlin,”
- or “CXX still has static assertions.”

A crate can have all of those truths and still leave projection scope, parity class, receiver-visible drift, or build/package proof unresolved.

## Added 2026-03-22 (385): MC/DC passes must keep campaign scope, comparison basis, and qualification class separate

When future revisions touch **P-0433** or adjacent safety-critical coverage lanes, do not let the archive collapse these into one fake “MC/DC got better” story:

1. **decision authority** — what decision inventory was authoritative;
2. **construct support** — what language forms were supported, excluded, or manual-review-only;
3. **campaign scope** — which packages, targets, doctests, proc-macros, build scripts, external harnesses, and execution lanes were actually in scope;
4. **comparison basis** — whether two bundles may be trended together at all;
5. **qualification class** — whether the result is exploratory, evidence-only, mixed host/target, review-ready-with-caveats, or manual-review-required;
6. **evidence lineage** — what exact runs and profile artifacts back the verdict.

Do not let any of the following stand in for an honest answer:
- “the percentage increased,”
- “both runs used MC/DC mode,”
- “the same source revision was tested,”
- “the target triple string matched,”
- or “cargo-llvm-cov succeeded twice.”

A bundle can have all of those truths and still fail to say whether doctests were omitted, whether support imports changed, whether host-vs-target execution drifted, or whether the comparison is review-safe at all.



## Added 2026-03-22 (386): visualizer passes must keep asset presence, activation route, formatter origin, and backend verdict separate

When future revisions touch **P-0491** or adjacent debugger lanes, do not let the archive collapse these into one fake “the visualizers work” story:

1. **asset presence** — what embedded or companion visualizer asset exists;
2. **activation route** — whether the debugger loaded it automatically, declined it for trust reasons, required a launcher script, needed manual commands, or never supported that route;
3. **formatter origin** — whether the effective formatter behavior came from the repo asset, a repo-shipped external script, a toolchain launcher, debugger-local config, or builtin debugger support;
4. **backend verdict** — what actually passed or failed for that backend/version/target lane;
5. **portable bundle completeness** — what another maintainer can inspect without guessing how the debugger was started.

Do not let any of the following stand in for an honest answer:
- “the crate embeds NatVis,”
- “rust-lldb works on my machine,”
- “GDB loaded something,”
- “LLDB has formatters,”
- or “the golden output looked fine once.”

A project can have all of those truths and still fail to say whether the relevant lane was embedded, script-routed, trust-blocked, debugger-local, or actually unsupported by design.


## Added 2026-03-22 (387): doctest passes must keep extraction basis, rewrite lineage, execution mode, grouping comparability, and support class separate

When future revisions touch **P-0455** or adjacent docs-example lanes, do not let the archive collapse these into one fake “the docs examples are tested” story:

1. **extraction basis** — whether the inventory came from rustdoc doctest JSON, rustdoc test collection, preextracted import, Markdown fallback, or manual inventory;
2. **rewrite lineage** — what rustdoc or the environment injected/rewrote after extraction;
3. **execution mode** — standalone, merged, wrapper-executed, compile-only, ignored, or render-only posture;
4. **grouping comparability** — whether two bundles can be trended together at all;
5. **support class** — host run, target run, compile-only, render-only, ignored, or manual-review-only;
6. **portable bundle completeness** — what another maintainer can inspect without guessing how the docs examples were collected.

Do not let any of the following stand in for an honest answer:
- “cargo test --doc passed”,
- “docs.rs built”,
- “the examples are visible in the docs”,
- “the crate moved to Edition 2024”,
- or “the target runner exists”.

A project can have all of those truths and still fail to say whether the inventory authority changed, whether grouping semantics drifted, or whether two green runs mean the same witness class at all.

## Added 2026-03-22 (388): doctest runtool passes must keep runner route, execution basis, working-directory basis, and results separate

When future revisions touch **P-0481** or adjacent doctest runner lanes, do not let the archive collapse these into one fake “cross-target doctests work” story:

1. **runner route** — whether execution came from explicit rustdoc flags, Cargo target-runner config, environment override, direct execution, or manual reconstruction;
2. **execution basis** — what target/support class/ignore policy was being claimed;
3. **working-directory basis** — where doctests were compiled from and where they actually ran;
4. **observed results** — what passed or failed once the route and basis were in place;
5. **portable bundle completeness** — what another maintainer can inspect without reconstructing config, env, and wrapper state by hand.

Do not let any of the following stand in for an honest answer:
- “we use QEMU for doctests,”
- “cargo test --doc --target passed,”
- “there is a target runner in .cargo/config.toml,”
- “the examples are ignored on Windows,”
- or “persisted doctest binaries exist.”

A project can have all of those truths and still fail to say whether the wrapper route was explicit, inherited, stale, path-sensitive, or even comparable to the last green run.


## Added 2026-03-22 (389): debugger visualizer passes must keep probe surface and comparison basis separate

When future revisions touch **P-0491** or adjacent debugger-visualizer lanes, do not let the archive collapse these into one fake “visualizers worked” story:

1. asset bytes and provenance,
2. activation/trust route,
3. formatter origin,
4. probe surface (CLI, DAP, IDE, wrapper, delivery container, version, OS),
5. comparison basis,
6. backend verdict,
7. broader symbol/source posture.

If a proposed crate cannot keep those facts separate, it is probably debugger folklore rather than a durable support contract.


## Added 2026-03-22 (390): MC/DC passes must keep profile compatibility, campaign policy, and review debt separate

When future revisions touch **P-0433** or adjacent safety-critical coverage lanes, do not let the archive collapse these into one fake “the MC/DC bundle is good enough” story:

1. **profile compatibility** — whether the retained or merged profile artifacts are safe for the intended use;
2. **campaign policy** — what support bar, exclusions, and execution requirement the campaign explicitly adopted;
3. **manual-review debt** — what unsupported constructs, macro visibility gaps, host/target gaps, or policy exceptions still need human review.

Do not let any of the following stand in for an honest answer:
- “the runner succeeded twice,”
- “we have `.profraw` and `.profdata` files,”
- “the HTML output looks stable,”
- or “the unsupported construct did not trigger a test failure.”

A bundle can have all of those truths and still fail to say whether its retained inputs are durable, whether unsupported constructs were explicitly excluded by policy, or whether blocking review debt remains.


## Added 2026-03-22 (392): cargo-event-stream passes must keep native events, foreign output, rendering policy, session identity, and warehouse/replay layers separate

When future revisions touch **P-0042** or adjacent Cargo build-observability lanes, do not let the archive collapse these into one fake “Cargo JSON is handled” story:

1. **native Cargo/rustc events** — intentionally emitted structured messages;
2. **foreign output** — proc-macro/build-script/runner/tool text that contaminates the stream;
3. **rendering policy** — embedded rendered field versus Cargo-rendered or ANSI-rendered diagnostics;
4. **session identity** — command lane, workspace, profile, target posture, toolchain basis;
5. **historical warehouse** — multi-run import/trend storage that belongs more cleanly to **P-0035**;
6. **replay container** — whole-run event/output archives that belong more cleanly to **P-0057**.

Do not let any of the following stand in for an honest answer:
- “we parse `cargo_metadata::Message`,"
- “the stream was mostly JSON,”
- “Cargo now has structured logging,”
- “we stored stdout and stderr,”
- or “the bundle contains the log.”

A workflow can have all of those truths and still leave foreign-output containment, rendering-policy truth, session provenance, or lane ownership unresolved.


## Added 2026-03-23 (394): projection/reborrow passes must keep authority, mode coverage, witness basis, and uncovered paths separate

When future revisions touch **P-0440** or adjacent smart-pointer ergonomics lanes, do not let the archive collapse these into one fake “projection support exists” story:

1. **projection authority** — which macro/manual/trait/wrapper surface is actually authoritative;
2. **borrow-mode coverage** — which shared/mutable/pinned/nested/reborrow/raw-escape modes are supported or caveated;
3. **witness basis** — what came from ordinary tests, Miri, imported evidence, or manual review;
4. **uncovered paths** — which sharp edges were not exercised at all;
5. **portable bundle completeness** — what another maintainer can inspect without re-deriving the unsafe argument.

Do not let any of the following stand in for an honest answer:
- “the crate uses `pin-project`,"
- “there is a reborrow trait,"
- “Miri passed,"
- “the API returns `Pin<&mut _>`,"
- or “future language support will solve this.”

A crate can have all of those truths and still leave authority, coverage, witness basis, or unresolved paths unclear.

## Added 2026-03-23 (398): example/onboarding passes must keep officiality, viability, visibility, and witness separate

When future revisions touch **P-0524** or adjacent docs/onboarding lanes, do not let the archive collapse these into one fake “the crate has examples” story:

1. **officiality** — what source actually blessed the path as the start here route;
2. **viability** — what command/feature/env lane actually works;
3. **visibility** — what docs.rs/rustdoc surfaces show;
4. **witness** — what success was actually observed.

Do not let any of the following stand in for an honest answer:
- “the README mentions it,”
- “cargo test builds examples,”
- “docs.rs shows the snippet,”
- or “scraped examples are enabled.”


## Added 2026-03-22 (402): debuggability-support passes must keep session scope, task witnesses, and claim ceilings separate

When future revisions touch **P-0486** or adjacent debugging lanes, do not let the archive collapse these into one fake “debugging worked” story:

1. **broad support posture** — interactive, backtrace-only, crash-symbolication-only, or weaker;
2. **backend-family observation** — which debugger family / version / OS lane was checked;
3. **session scope** — live local, attached, remote, containerized, or post-mortem;
4. **capability witness** — which concrete tasks were actually demonstrated (`breakpoint_hit`, `step_over`, `backtrace`, `locals_expand`, `pretty_render`, `rust_expression_eval`, `async_task_inspection`, etc.);
5. **claim ceiling** — what strongest honest outward-facing claim survives after the narrower evidence is considered.

Do not let the archive silently turn “we opened a core dump”, “the backtrace looked good”, or “LLDB on Linux worked once” into a broad claim about interactive debugging, Rust expression evaluation, async inspection, or cross-platform debugger parity.


## Added 2026-03-23 (403): off-ramp support must keep successor class, authority, stopgaps, and witness scope separate

When working on **P-0515 Crate Off-Ramp Pack Kit**, do not flatten these into one generic migration verdict:
1. successor class (`drop_in`, `partial`, `security_only_stopgap`, `no_successor`),
2. successor authority (pack-declared, rustdoc note, docs page, advisory stopgap, third-party inference),
3. stopgap horizon (temporary, review-due, deadline-known, deadline-unknown),
4. declared recipe,
5. witnessed recipe scope.

A deprecation note is not automatically a long-term successor contract, and one passing rename recipe is not automatically broad migration proof.

## Added 2026-03-23 (407): Cargo SBOM precursor passes must keep capture route, coverage, transform loss, and claim ceilings separate

When future revisions touch **P-0125** or adjacent supply-chain lanes, do not let the archive collapse these into one fake “Cargo emitted an SBOM” story:

1. **capture route** — same-invocation env/stream capture versus imported target/artifact trees;
2. **artifact coverage** — which outputs were actually eligible for precursor generation;
3. **transform loss** — what later normalization or format emission preserved or dropped;
4. **claim ceiling** — where copied outputs, imported trees, or fresh-cache reuse stop stronger claims.

Do not let any of the following stand in for an honest answer:
- “a `*.cargo-sbom.json` file exists,”
- “`CARGO_SBOM_PATH` was mentioned,”
- “the artifact was copied with `--artifact-dir`,”
- “a CycloneDX/SPDX file was emitted,”
- or “Cargo reported a compiler artifact.”

A workflow can have all of those truths and still leave capture route, coverage, or same-invocation completeness unresolved.

## Added 2026-03-23 (408): workspace-tool support must keep command authority, component availability, and fallback ceilings separate

When future revisions touch **P-0055** or adjacent tool-install lanes, do not let the archive collapse these into one fake “the tool ran” story:

1. **install-root posture** — where the executable lived and who governed that root;
2. **command authority** — rustup component proxy, Cargo external subcommand, workspace-managed executable, or PATH fallback;
3. **component availability** — whether the expected optional component was installed for the checked toolchain;
4. **toolchain selection context** — `+toolchain`, environment override, directory override, toolchain file, or default;
5. **fallback ceiling** — what strongest honest outward-facing claim survives after fallback is considered.

Do not let any of the following stand in for an honest answer:
- “the repo declares the tool,”
- “the binary existed in `$CARGO_HOME/bin`,"
- “rustup has a proxy with that name,”
- “the same path appeared twice,”
- or “the command returned success.”

A workflow can have all of those truths and still leave command authority, component parity, or fallback ceilings unresolved.


## Added 2026-03-23 (411): compile-iteration passes must keep reload surface, restart ceiling, and readiness class separate

When future revisions touch **P-0537** or adjacent dev-loop lanes, do not let the archive collapse these into one fake “hot reload works” story:

1. **reload surface** — RSX / UI markup, CSS/static assets, frontend HMR, Rust logic hotpatch, or rebuild/restart;
2. **restart ceiling** — which edit classes still force full rebuild or restart;
3. **readiness class** — visual update visible, Rust logic ready, or restarted-app ready;
4. **framework route** — Dioxus-local, Tauri mixed dev route, Trunk/cargo-leptos browser route, or plain watcher loop;
5. **budget basis** — direct local measurement versus imported framework expectation.

Do not let any of the following stand in for an honest answer:
- “the framework has hot reload,”
- “the browser changed instantly,”
- “the Rust code was watched,”
- “there is a dev server,”
- or “the edit felt fast.”

A workflow can have all of those truths and still leave route class, restart ceiling, or readiness class unresolved.


## Added 2026-03-23 (415): pathfinder passes must keep freeze-time basis, current view, visibility drift, and replacement choice separate

When future revisions touch **crate pathfinder / starter-set** work again, do not let the archive collapse these into one fake “best crate” story:

1. **freeze-time basis** — what evidence window the original decision actually relied on;
2. **current-view replay** — what the ecosystem looks like now under the same task lane;
3. **visibility drift** — what changed only in public docs/registry surfaces;
4. **fresh-release timing** — what was still inside cooldown or otherwise out of bounds at freeze time;
5. **replacement authority** — what a human or policy explicitly approved to replace the old starter set.

Do not let any of the following stand in for an honest answer:
- “the crate ranks higher now,”
- “cargo add found it,”
- “cargo info shows a nice package summary,”
- “docs.rs lands on a more persuasive target today,”
- or “the current release looks obviously better.”

A bundle can contain all of those facts and still fail to say what was actually knowable when the starter set was frozen or whether replay truly authorizes replacement.

## Added 2026-03-23 (417): compile-iteration passes must keep edit scope, barrier cause, and readiness class separate

When future revisions touch **P-0537** again, do not let the archive collapse these into one fake “the edit stayed fast” story:

1. **edit scope** — what artifact family actually changed;
2. **interface impact** — whether the edit preserved the public interface;
3. **barrier cause** — why the strongest fast path narrowed or failed;
4. **fallback class** — visual-only, relink-only, reinstancing, restart, or manual review;
5. **readiness class** — visual change visible, logic ready, restart complete, or not yet achieved.

Do not let any of the following stand in for an honest answer:
- “the framework has hot reload,”
- “the browser changed instantly,”
- “the code change was small,”
- “the linker is faster now,”
- or “the state was preserved.”

A workflow can have all of those truths and still leave edit scope, barrier cause, or fallback class unresolved.

## Added 2026-03-23 (420): crate-knowledge passes must keep item identity, citation route, build surface, and conditioned availability separate

When future revisions touch **P-0536** or adjacent docs/search/assistant-facing lanes, do not let the archive collapse these into one fake “the crate surface is known” story:

1. **item identity** — what conceptual item the claim refers to;
2. **citation route** — what exact locator can be cited for that claim;
3. **build surface** — what feature/target/toolchain/docs-build recipe produced the visible surface;
4. **conditioned availability** — whether the subject is present only under that recipe, absent under another, or still manual-review-only;
5. **material basis** — what exact hosted/local artifacts were imported.

Do not let any of the following stand in for an honest answer:
- “the item exists in rustdoc JSON,”
- “docs.rs has a page for it,”
- “the example shows up in docs,”
- “the witness matches,”
- or “the citation locator works.”

A bundle can contain all of those truths and still fail to say under which recipe the subject was actually visible.

## Added 2026-03-23 (426): concurrency passes must keep delivery memory, backlog pressure, cancellation, and fairness separate

When future revisions touch **P-0538** or adjacent async/channel lanes, do not let the archive collapse these into one fake “message passing works” story:

1. **delivery memory** — what is remembered when nobody is ready right now;
2. **backlog pressure** — what happens when producers outrun consumers;
3. **cancellation effect** — what waiting/receiving loses when a waiter is dropped or a race is lost;
4. **fairness/order** — how waiters or queued work are prioritized;
5. **fanout multiplicity** — single delivery, latest shared state, or per-receiver history.

Do not let any of the following stand in for an honest answer:
- “it’s a channel,”
- “it has buffering,”
- “a receiver can subscribe,”
- “lag is reported,”
- or “messages are sent asynchronously.”

A surface can have all of those truths and still leave memory class, pressure class, or delivery multiplicity unresolved.


## Added 2026-03-23 (427): concurrency passes must keep delivery audience, claim semantics, memory, and pressure separate

When future revisions touch **P-0538** or adjacent async/channel lanes, do not let the archive collapse these into one fake “message passing works” story:

1. **delivery audience** — who is actually eligible to observe a wake/value/message unit;
2. **consumption claim** — what one observer taking / marking the unit does to others;
3. **delivery memory** — what is remembered when nobody is ready right now;
4. **backlog pressure** — what happens when producers outrun consumers;
5. **cancellation effect** — what waiting or receiving loses when a waiter is dropped or a race is lost.

Do not let any of the following stand in for an honest answer:
- “there are multiple receivers,”
- “a receiver can subscribe,”
- “it has buffering,”
- “it wakes all waiters,”
- or “it is async message passing.”

A surface can have all of those truths and still leave audience class, claim class, or late-joiner posture unresolved.


## Added 2026-03-23 (428): concurrency passes must keep delivery acceptance, observation evidence, audience, and claim semantics separate

When future revisions touch **P-0538** or adjacent async/channel lanes, do not let the archive collapse these into one fake “send succeeded” story:

1. **delivery acceptance** — what producer-visible success meant at the moment of send / notify;
2. **observation evidence** — what evidence exists later that anybody actually observed or processed the unit;
3. **delivery audience** — who was eligible to observe the unit;
4. **consumption claim** — what one observer taking / marking the unit did to others;
5. **delivery memory** — what is remembered when nobody is ready right now;
6. **backlog pressure** — what happens when producers outrun consumers.

Do not let any of the following stand in for an honest answer:
- “`send` returned `Ok`,”
- “there was an active receiver,”
- “the returned count was N,”
- “the sender can observe close,”
- or “the primitive notified listeners.”

A surface can have all of those truths and still leave acceptance meaning, observation proof, or acknowledgment needs unresolved.


## Added 2026-03-23 (430): concurrency passes must keep closure finality, post-close availability, memory, and acceptance separate

When future revisions touch **P-0538** or adjacent async/channel lanes, do not let the archive collapse these into one fake “channel closed” story:

1. **closure finality** — whether close is immediate terminal, drain-then-terminal, reopenable, or race-sensitive;
2. **post-close availability** — what buffered tail, retained history, latest snapshot, or in-flight value remains observable after close;
3. **delivery memory** — what is remembered before close when nobody is ready right now;
4. **delivery acceptance** — what producer-visible success meant at send time;
5. **observation evidence** — what proof exists later that anybody actually observed or processed the unit.

Do not let any of the following stand in for an honest answer:
- “the sender dropped,”
- “the receiver called close,”
- “`changed` returned `RecvError`,”
- “there is still a last value,”
- or “the queue had buffering.”

A surface can have all of those truths and still leave closure finality, retained-tail posture, or reopenability unresolved.

## 2026-03-23 addendum — do not flatten observer entry into generic subscription support

When touching **P-0538**, keep these stories separate:

- a late joiner is admitted,
- the late joiner starts with future sends only,
- the late joiner starts with the current snapshot already seen,
- the late joiner starts from the current tail,
- a future waiter can consume one stored permit,
- and the surface has no late-join route at all.

Do not let “subscribe exists” or “receiver can be created” erase those distinctions.


## Added 2026-03-23 (438): broad refreshes must keep salience, shipability, and freshness basis separate

When future revisions do broad reranks, do not let the archive collapse these into one fake “top crates” story:

1. **salience** — how much ecosystem pain and leverage the crate addresses;
2. **shipability** — how believable the next reviewable `0.1` is under current substrate;
3. **freshness basis** — which current sources were actually re-checked this pass;
4. **evidence class** — evergreen docs, current goal signals, policy/incident updates, or explicit manual inference.

Do not let any of the following stand in for an honest rerank:
- “a new blog post exists,”
- “the topic feels hot right now,”
- “the crate sounds more ambitious,”
- or “it has many neighboring files already.”

A proposal can be very high in salience and still sit later in the practical queue.
A proposal can also be easy to ship and still remain below the main control-plane frontier.


## Added 2026-03-24 (446): when a pass deepens packet-producing crates, ask the consumer question too

When future revisions touch **P-0509**, **P-0536**, **P-0535**, **P-0472**, or nearby packet-producing lanes, they must ask explicitly:
1. how does another system import this packet,
2. what route/schema caveats survive intake,
3. what gets materialized locally versus left remote,
4. what degrades or stays manual,
5. and what receipt records that honestly.

Do not let future passes stop at producer-side schemas when the sharper missing seam is a **consumer contract**, **intake receipt**, or **materialization plan**.

Do not let future passes flatten any of the following into one fake “imported successfully” story:
- `cargo metadata` vs registry-index import,
- `latest` route vs pinned route,
- docs.rs download archive vs offline-ready docs,
- `.cargo_vcs_info.json` vs verified provenance.

## Added 2026-03-24 (449): front-door passes must keep task, adopter profile, evidence floor, and non-claim separate

When future revisions touch **P-0509**, **P-0536**, **P-0535**, **P-0472**, **P-0496**, or adjacent front-door lanes, do not let the archive collapse these into one fake “recommended crate” story:

1. **task profile** — what work is being done;
2. **adopter profile** — who is asking and under what assurance posture;
3. **evidence floor** — what minimum evidence must exist before the packet may say yes;
4. **current satisfaction** — whether that floor is met, conditional, manual-only, or failed;
5. **non-claim** — what still must not be inferred even if the report says pass.

Do not let any of the following stand in for an honest answer:
- “it has docs on docs.rs,”
- “the crate has a Security tab,”
- “trusted publishing is enabled,”
- “the package is popular,”
- or “the same starter set worked in another scenario.”

A surface can have all of those truths and still fail the adopter’s actual evidence floor.


## Added 2026-03-25 (462): do not collapse evidence into policy, or policy into vibes

When future revisions touch the front-door stack, preserve six layers explicitly:
1. reviewed evidence inputs,
2. policy-pack revision,
3. rule-level outcomes,
4. final verdict vocabulary,
5. override / waiver object,
6. recheck / expiry trigger.

Do not let any of the following stand in for an honest decision surface:
- “the tool recommended it,”
- “the bundle looked good,”
- “CI was green,”
- “trusted publishing is enabled,”
- or “we can always override later.”

A surface can have all of those truths and still fail to provide a reviewable verdict.
