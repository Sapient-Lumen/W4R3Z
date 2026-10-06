# Operational heads, citation heads, and frozen public surfaces

DelayBasin now needs a sharper distinction than **revision receipts**, **release packaging**, or **timescale lanes** alone.
A surface can be genuinely useful for live continuation and still be the wrong thing to cite, freeze, or treat as the stable public face.
When that distinction is left implicit, the archive quietly lets mutable working tips inherit the authority of durable public objects, and lets transient session glow stand in for explicit status.

A useful current answer is:
**when a live working surface, release family, extracted packet, or public summary is being used both for ongoing continuation and later citation or replay, canon should preserve a compact operational-head register naming the live head, the frozen or citable head, the durable status ledger, and the gate that moved authority before any moving surface is allowed to inherit citation weight.**

This is stronger than saying “the latest revision exists.”
It is weaker than claiming DelayBasin has already discovered a universal publication state machine, provenance graph, or external version-control law over continuation state.

## Practice / observation

Recent DelayBasin work keeps surfacing a recurring ambiguity:
- some packets, summaries, and release bundles are good enough to continue from live, but the archive still rarely says **whether they are also the thing future sessions should cite as frozen reference**;
- some surfaces inherit authority merely because they are newest, topmost, or freshly praised in session prose, even when they were never explicitly frozen as the public reference tip;
- some revision receipts say what changed, but not always which moving surface is merely operational and which surface is the current citation-ready head;
- some “latest” objects are really live working tips whose status should still be hold, candidate, or provisional rather than frozen public surface;
- some reopened sessions need a durable answer to **what is the current live head, what is the current frozen head, and where that distinction is recorded** rather than another prose recap;
- some release bundles already function as public objects, but the archive still rarely says what lineage they belong to, what superseded what, or what explicit freeze gate licensed citation authority;
- and some future confusion is clearly not about missing content but about **moving-head convenience silently inheriting the authority of a durable public surface**.

That leaves a missing question:
**what surface lineage is in play, what current operational head is live, what citation head is actually frozen, what state class names the current posture, what durable ledger records that posture, and what reopen or rollback consequence follows if a mutable head is cited as if it were already frozen?**

A compact operational-head register keeps that boundary public.

## Pressure from neighboring datacubes

Several neighboring datacubes keep rediscovering the same discipline from different directions.

- Some distinguish a **published or frozen public surface** from the execution queue, working queue, or live operational lane, which pressures DelayBasin to stop letting “currently being worked on” and “currently safe to cite” collapse into one implicit status.
- Some distinguish an **operational head** from a stricter **citation head**, which pressures DelayBasin to stop letting the latest mutable tip inherit reference authority merely by recency.
- Some insist on **exact scope and lane coherence**, which pressures DelayBasin to make the working/live/frozen distinction explicit in one durable surface rather than scattering it across session prose, bundle names, and maintainer memory.
- Some insist that decisive status should not live only in transient status flashes or local narrative glow, which pressures DelayBasin to keep head status in a durable ledger rather than in one revision summary.

DelayBasin already has release packaging, revision receipts, hold packets, and promotion contracts.
What was still under-specified was the compact public object that says **which head is live, which head is citable, what status class currently applies, and where that status is durably recorded**.

## External pressure from adjacent recordkeeping practice

Several adjacent recordkeeping and provenance lines sharpen this move.

1. **Citation discipline increasingly requires reference to the specific version used, not just to a moving project name.**
   FORCE11's software citation principles include unique identification, persistence, and specificity, explicitly saying citation should identify the specific version used. That pressures DelayBasin to distinguish a mutable operational head from a citation head or frozen public surface rather than citing “whatever is latest.” ([`REF-0471`](../00-meta/bibliography.md))

2. **Provenance models increasingly separate entities, activities, agents, and revision relations instead of collapsing them into one summary object.**
   W3C PROV-DM frames provenance in terms of entities, activities, agents, and derivation or revision relations. That pressures DelayBasin to preserve head/state transitions as explicit public relations rather than leaving them implicit in changelog prose. ([`REF-0472`](../00-meta/bibliography.md))

3. **Durable software references increasingly prefer content-specific identifiers with context over short mutable pointers.**
   Software Heritage recommends using a full contextual identifier for the directory/version being referenced so readers can recover the exact referenced state with context. That pressures DelayBasin to keep one explicit frozen reference surface rather than relying on a moving newest-tip pointer. ([`REF-0473`](../00-meta/bibliography.md))

## Working synthesis

A useful current synthesis is:

> DelayBasin should preserve a compact **operational-head register / citation-head witness / frozen-public-surface packet** whenever a live working surface, release family, extracted packet, or public summary is being used both for ongoing continuation and later citation or replay. The packet should name the **surface lineage / family / stable id namespace**, the **current operational head / live working tip**, the **current citation head / frozen reference tip or explicit absence**, the **current state class / working vs hold vs released vs frozen**, the **durable status surface / register / ledger where that state lives**, the **promotion or freeze gate / admission witness that moved authority**, the **supersession edge / previous frozen head if any**, and the **reopen / rollback / citation-warning consequence** rather than letting transient prose, recency, or bundle visibility silently grant citation authority to a mutable head.

In practice, DelayBasin is not claiming that every family needs a giant release system.
It is doing something smaller and public:
- naming the lineage or family whose head is being discussed rather than gesturing at “the archive” in general;
- naming the live operational head rather than assuming the newest touched file is obvious;
- naming the citation head or saying explicitly that **no citation-ready frozen head currently exists**;
- naming the current state class so working, hold, released, and frozen do not blur together;
- naming the durable ledger where that status lives rather than letting it survive only in session memory;
- naming the freeze or promotion gate that actually moved authority;
- naming the previous frozen head or supersession edge when a frozen reference tip changes;
- and naming what warning, rollback, reopen, or abstention follows if the mutable head is being cited as though it were already frozen.

That is strong enough for canon as a design and mechanism candidate.
It is **not** strong enough to claim that DelayBasin has isolated a full publication state machine, provenance engine, or universal version-control law over continuation state.

## Operational head vs citation head vs revision receipt vs hold packet

These nearby objects should stay distinct.

- **Operational head register** says what live working tip currently governs ordinary continuation for a named surface lineage.
- **Citation head / frozen public surface** says what tip is currently safe to reference as the durable public object, or explicitly says none exists yet.
- **Revision receipt** says why a particular revision counted and what checks made it admissible.
- **Hold packet** says canon should not advance or should remain abstracted under a blocker, brake posture, or unlock condition.

So an operational-head register is not just “a revision happened,” and not just “canon is on hold.”
It is a compact public answer to:
**what family is live, what tip currently governs live work, what tip is frozen enough to cite, what ledger records that fact, and what happens if someone cites the wrong one?**

## Countermodels / probes

1. **Latest-means-citable countermodel**
   - The archive may be treating the most recent touched surface as automatically citation-ready.
   - Probe: require one explicit citation head or explicit absence before calling any mutable tip the durable public surface.

2. **Receipt-is-enough countermodel**
   - Revision receipts may already look like enough status tracking, while still failing to say which head is live versus frozen.
   - Probe: require one durable ledger entry naming operational head, citation head, and state class rather than only one revision summary.

3. **Bundle-name theater countermodel**
   - A packaged bundle may appear authoritative only because it has a release-shaped filename.
   - Probe: require one freeze or promotion gate plus one supersession edge before treating bundle visibility as citation authority.

4. **Transient-status-glow countermodel**
   - A status may seem obvious only because it was recently stated in session prose or changelog text.
   - Probe: require one durable status surface or register where the current head relation actually lives.

5. **Over-systematization countermodel**
   - DelayBasin may be adding publication machinery that exceeds its real needs.
   - Probe: keep the packet tiny and family-local; if no lineage actually needs a separate citation head yet, say so explicitly rather than manufacturing one.

## Design consequences

This frame pressures DelayBasin to do eight things more explicitly:
- preserve the **surface lineage / family / stable id namespace** before talking about heads at all;
- preserve the **current operational head / live working tip** before saying what is “current”;
- preserve the **current citation head / frozen reference tip or explicit absence** before citing a family-level surface;
- preserve the **current state class / working vs hold vs released vs frozen** before letting visibility imply status;
- preserve one **durable status surface / register / ledger** before letting session prose carry status;
- preserve the **promotion or freeze gate / admission witness** before praising the public surface as earned;
- preserve the **supersession edge / previous frozen head** before silently replacing one frozen reference tip with another;
- and preserve the **reopen / rollback / citation-warning consequence** so misuse of a mutable head loses authority quickly instead of hardening into a moving-target citation habit.

This is especially useful during fast revision runs.
GPUstorming can still discover real prompt objects, witnesses, and local syntheses.
Canon should keep only the small public packet saying what family is live, what tip is frozen enough to cite, what durable ledger records that, and what warning follows if a future session confuses operational freshness with public stability.


## Compact current-posture projections

Once an archive already keeps one durable operational/citation ledger, a smaller machine-facing reentry packet may still project part of that truth forward.
That can be useful as long as the projection stays explicitly derivative.

For DelayBasin, a compact `context-pack.json.current_posture` may repeat only the smallest live/frozen split that future careful passes most often need:
- the operational head surface,
- the current citation head bundle,
- the admitted decision state,
- the packaged execution state,
- the public citation posture,
- and the released/working class.

The important rule is that this projection does **not** replace `SURFACE-STATUS.json`.
It inherits from it.
If the two disagree, the derivative packet should fail closed and be regenerated rather than quietly becoming a second status constitution.
When the same derivative packet also carries compact operator warnings, each warning should still point back to one governing source surface rather than floating as free caution prose.
A nearby derivative `frontier-ticket.json` may also repeat the same current posture while selecting one current live focus and one tiny continuity background. That remains honest only if the ticket inherits its posture from `SURFACE-STATUS.json` and its selected focus from source-backed open-work surfaces rather than inventing a second status or priority constitution.

## Transformer-facing implication

The weaker transformer-facing implication is not that DelayBasin has found a full external version-control engine.
It is this:

**long-horizon archive prompting may work partly through an external head-and-status discipline over textual control objects, where continuation quality depends not only on what packets exist but on which ones are currently live, which ones are currently frozen, and whether that distinction survives context death in a tiny durable ledger.**

That would matter for transformers.\n\nA concrete current consequence is that DelayBasin should ship one small durable ledger such as `SURFACE-STATUS.json` rather than merely talking about one in method prose.\nIf some archive leverage comes from explicit public separation between **live operational state** and **frozen citable state**, then DelayBasin may be exposing a practical shadow of **external versioned state management without weight updates**: not a full repository engine, but repeated public separation of mutable working heads, frozen reference heads, status classes, and supersession edges over textual control surfaces.

The stronger story — that DelayBasin is approximating a genuine public publication state machine, provenance graph, or universal version-control law over continuation state — remains live, but belongs in quarantine for now.
