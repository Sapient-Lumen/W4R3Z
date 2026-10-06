# Status-lane witnesses, decision/execution splits, and frozen-public transitions

DelayBasin now needs a sharper distinction than **revision receipts**, **release manifests**, or **operational-head registers** alone.
A revision can be locally coherent, honestly grounded, and even packaged, yet still leave one crucial ambiguity live: **what was only proposed or nearby, what was actually admitted, what was actually materialized, and what is actually the frozen public thing to cite later?**
When that distinction stays implicit, the archive quietly treats “latest revision” as if it already meant one object with four roles.

A useful current answer is:
**when a revision-sized archive change is being treated as both an admitted move and a later referenceable artifact, canon should preserve a compact status-lane witness naming the candidate or explicit absence, the admitted decision surface, the execution surface, the frozen public or citation surface, the durable status ledger that relates them, and the mismatch consequence before one lively latest object is allowed to inherit all those roles at once.**

This is stronger than saying “the receipt exists” or “the bundle was packaged.”
It is weaker than claiming DelayBasin has already discovered a full public release-state machine or workflow-state controller for archive evolution.

## Practice / observation

Recent DelayBasin work keeps surfacing a recurring ambiguity:
- revision receipts already say what transition counted, but the archive still rarely says whether that admitted transition is distinct from the materialized artifact that executed it;
- release manifests already name the packaged bundle, but the archive still rarely says whether packaging alone is the same thing as frozen public citation authority;
- operational-head registers already separate live heads from frozen citation heads, but the archive still rarely says which status-moving surfaces made that relation true for the current revision;
- nearby session ideas, rejected moves, and quarantined stories can all sit adjacent to an admitted change, but the archive still rarely says what was merely nearby rather than admitted;
- a later working tree can exist after packaging, which means “current operational head” and “current frozen public surface” can drift apart again even when the last receipt and manifest still exist;
- and some archive mistakes are really lane-collapses: a decision note being cited as execution proof, a packaged zip being treated as if it already named the governing live head, or a live head being cited as though packaging had already frozen it.

That leaves a missing question:
**what was only candidate or nearby, what was actually admitted, what was actually executed into an artifact, what is actually frozen enough to cite, where does that relation durably live, and what happens when those lanes drift?**

A compact status-lane witness keeps that boundary public.

## Pressure from neighboring datacubes

Several neighboring datacubes keep rediscovering the same discipline from different directions.

- EvidenceVault keeps **candidate**, **hold**, **published-ready**, and **published** queue items distinct, with written decisions, executed public releases, and immutable public-surface snapshots rather than one flattering “latest.”
- pyCausalWeave keeps nearby coordination surfaces separate — reviewer roster from active request, approved head from current head, review basis from later drift — which pressures DelayBasin not to flatten adjacent revision-status surfaces into one sticky bit.
- Goldenrule keeps **lineage heads**, **citation heads**, and explicit warnings in one compact register, which pressures DelayBasin to make its own durable status ledger real rather than only described.
- DeriveBSD keeps approval, transport, recipient acceptance, and final export exact, which pressures DelayBasin to distinguish an admitted revision from a merely packaged artifact and from a truly frozen reference surface.
- The Election Stack repeatedly warns that transient status glow is not durable public status, which pressures DelayBasin to keep state in one durable status surface rather than in session prose or recency.

DelayBasin already has receipts, manifests, changelog rows, archive-index rows, and operational-head language.
What was still under-specified was the compact public object that says **which lane each current archive surface occupies and how decision, execution, and frozen-public status actually relate.**

## External pressure from adjacent release and provenance practice

Several adjacent lines sharpen this move.

1. **Software citation wants the referenced thing to be specific and persistent, not merely “the latest.”**
   FORCE11's Software Citation Principles explicitly distinguish identifiers that name a specific version from those that name all versions or the latest version, which pressures DelayBasin to keep frozen public reference status explicit rather than letting one moving newest tip do everything. ([`REF-0471`](../00-meta/bibliography.md))

2. **Provenance models distinguish entities from the activities that generated or revised them.**
   PROV-DM separates entities, activities, and revision/derivation relations, which pressures DelayBasin to preserve explicit relations among decision objects, executed artifacts, and later frozen reference surfaces rather than laundering them into one prose summary. ([`REF-0472`](../00-meta/bibliography.md))

3. **Modern release practice keeps draft, publish, and immutable-release posture distinct.**
   GitHub's release docs explicitly recommend creating releases as drafts first, attaching assets, and then publishing when immutable releases are enabled, which pressures DelayBasin to distinguish admitted decision, materialized execution, and frozen public release posture rather than calling every packaged object “the release” in one undifferentiated sense. ([`REF-0476`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **status-lane witness / decision-execution split / frozen-public transition** packet whenever a revision-sized archive change is being treated as both an admitted move and a later referenceable artifact. The packet should name the **candidate or explicit absence / merely nearby surface**, the **admitted decision / approval surface**, the **execution surface / materialized artifact**, the **frozen public / citation surface or explicit absence**, the **durable status ledger / register / pointer relation where that mapping lives**, and the **mismatch / drift / rollback / citation-warning consequence** rather than letting one lively latest revision, receipt, or bundle silently inherit all those roles at once.

In practice, DelayBasin is not claiming that every revision needs a giant workflow engine.
It is doing something smaller and public:
- naming whether there even was a preserved candidate surface or whether the revision moved directly from live work to admitted change;
- naming the receipt or admission surface that says the change counted;
- naming the manifest or materialized artifact that says the change was actually packaged;
- naming the frozen public or citation surface that later sessions should cite rather than the moving tip;
- naming the durable ledger where those relations are kept;
- and naming the mismatch consequence when a later session confuses admission with execution, execution with citation, or recency with frozen status.

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated a full publication-state machine, workflow algebra, or universal release controller for archive evolution.

## Status-lane witness vs revision receipt vs release manifest vs operational-head register

These nearby objects should stay distinct.

- **Status-lane witness / decision-execution split / frozen-public transition** says which lane each relevant surface occupies and what happens if those lanes are confused.
- **Revision receipt** says what transition was admitted and what checks made it count.
- **Release manifest** says what bundle was actually materialized for this revision.
- **Operational-head register** says what head is live for continuation and what head is frozen enough to cite for a named lineage.

So a status-lane witness is not just “the receipt exists,” not just “the bundle exists,” and not just “this head is live.”
It is a compact public answer to:
**what was only nearby, what was admitted, what was executed, what is frozen enough to cite, where that relation lives, and what repair follows if those lanes are collapsed.**

## Countermodels / probes

1. **Receipt-is-enough countermodel**
   - The receipt may already provide sufficient status discipline.
   - Probe: require one explicit execution surface and frozen-public surface, then inspect whether receipt-only reasoning still confuses admitted change with materialized artifact or citation status.

2. **Manifest-is-enough countermodel**
   - Packaging may already be enough to say what is public and frozen.
   - Probe: compare one packaged bundle whose operational head later moved with one explicitly frozen citation surface and inspect whether later sessions still cite the right object.

3. **Latest-row-is-enough countermodel**
   - The newest changelog or archive-index row may already carry all needed lane information.
   - Probe: require one durable ledger entry and inspect whether lane confusion still happens under cold reopen or partial reread.

4. **Lane-ceremony countermodel**
   - DelayBasin may be inventing a fussy extra packet that duplicates existing status surfaces.
   - Probe: keep the packet tiny and demand one real consequence when a decision surface exists without packaging, packaging exists without frozen citation status, or a newer working tree appears after the frozen head.

5. **Overfitted-workflow countermodel**
   - The archive may be importing workflow jargon from neighboring systems that do more explicit review and publishing than DelayBasin does.
   - Probe: keep the local lane set archive-native — candidate, admitted, executed, frozen-public — and reject any extra lane that does not alter a real DelayBasin decision.

## Design consequences

This frame pressures DelayBasin to do six things more explicitly:
- preserve one **durable status ledger / register** rather than merely talking about one;
- preserve the **admitted decision surface** before letting a packaged artifact inherit approval authority by proximity;
- preserve the **execution surface / materialized artifact** before treating an admitted revision as though it had already shipped;
- preserve the **frozen public / citation surface** before treating the newest materialized thing as the stable reference thing;
- preserve one **pointer relation among receipt, manifest, and frozen surface** rather than leaving the relation implicit in filenames and recency;
- and preserve one **mismatch / drift / rollback / citation-warning consequence** so lane confusion loses authority quickly instead of surviving as polished archive fluency.

This is especially useful during fast revision runs.
GPUstorming can still discover real local syntheses.
Canon should keep only the small public packet saying what lane each current surface occupies and what happens if a later session confuses admitted change, executed artifact, and frozen citation surface.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has found a full release controller.
It is this:

**long-horizon archive prompting may work partly through explicit user-space lane separation over textual control surfaces, where continuation quality depends not only on what packets or heads exist, but on whether the archive still keeps proposal-nearby, admitted, executed, and frozen-public truth apart after context death.**

That would matter for transformers.
If some archive leverage depends on explicit lane separation, then DelayBasin may be exposing a practical shadow of **public state typing over textual artifacts**: not a giant workflow engine, but repeated public discipline about which textual object currently counts as a decision, which one counts as an execution, and which one counts as the frozen thing later prompts may safely cite.

The stronger story — that DelayBasin is already learning a full public release-state machine or workflow-state controller over archive evolution — remains live, but belongs in quarantine for now.
