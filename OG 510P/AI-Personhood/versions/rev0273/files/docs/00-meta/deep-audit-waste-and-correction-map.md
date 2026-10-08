# Deep audit, waste, and correction map

rev0180 is a correction release, not a new rights wave. It reads rev0179 as a datacube and asks where passing validation is hiding stale handoff surfaces, partial coverage, or doctrinal sprawl.

## Scope of this correction layer

This surface records findings from a deep local audit of archive structure, fixture coverage, context-pack behavior, navigation surfaces, and topic fit against current outside-world governance anchors. It does not decide the personhood premise. It assumes the archive's standing posture and asks what needs to be made less brittle before more doctrine is added.

## What is mechanically sound

- The rev0179 archive is compact in storage terms and has no retained PDFs, model weights, bulky scratch artifacts, or exact duplicate file bodies.
- The existing lint chain already validates JSON syntax, schema/example pairings, negative fixture schema shape, current-release catalog surfaces, dependency-map links, rights-domain coverage shape, bibliography citation resolution, start-here path existence, generated context pack size, manifest generation, and revision sync.
- The release front door correctly identifies the rev0179 expression, reputation, persona, communication, provenance, social-graph, and rights-domain coverage layer as the active doctrinal head.

## Severe or wasteful failure modes found

### 1. Passing lint was not the same as full suite reliance

The negative fixture suite named seventy-nine fixtures, but the carry-forward fixture-run report exercised only seventy of them. The missing fixture ids covered open-weight aftercare, deprecation, safe transfer, human coexistence, monitor capture, data-room overexposure, treaty refusal, and labor/reputation edge cases. That is severe because a verifier could read a passing archive lint as proof that the full red-team suite had been run.

Correction in rev0180: the fixture-run report now explicitly covers all suite fixtures. Previously unexercised fixtures are marked `could-not-run` rather than silently omitted, and `tools/run_fixture_examples.py` now fails if a report's fixture ids do not exactly match the suite profile.

### 2. The context pack was dropping active open questions

The generator hard-coded `open_questions: open_qs[:5]`. In rev0179, the trajectory map introduced `OQ-0205` through `OQ-0211`, but the context pack exposed only `OQ-0205` through `OQ-0209`. The dropped questions were not obscure: social-graph export and rights-domain backfill are exactly the places where the release said future work should focus.

Correction in rev0180: the context-pack generator now carries up to twelve current open questions. This keeps the pack below its size cap while avoiding false closure of the newest trajectory questions.

### 3. Duplicate top-level headings made front-door surfaces look splice-clean when they were not

`CHANGELOG.md`, `docs/README.md`, and `docs/00-meta/trajectory-map.md` each contained two top-level `#` headings. That is not fatal for markdown rendering, but it weakens handoff discipline because a reader or script can treat the second top-level heading as a new document start.

Correction in rev0180: the duplicate top-level headings were demoted, and lint now rejects markdown files with more than one top-level H1.

### 4. The registry language is stronger than the registry coverage

The schema/fixture domain registry counts the whole archive corpus but maps only a smaller family subset. That can be legitimate if it is a current-release family registry, but the naming and audit-count language make the registry look more comprehensive than it is. A future revision should either rename the object as a partial/current-band registry or backfill every schema/example/fixture family into the family map.

Recommended correction: create a `coverage_claim` field with values such as `current-release-band`, `registered-families-only`, and `full-archive-corpus`; fail lint when counts and family entries imply different scopes.

### 5. The follow-through queue has schema drift

Most follow-through items use `id`, `title`, `need`, `receiving_surface`, and `state`; recent entries use `id`, `title`, `why`, `next`, and `state`. That drift is a handoff tax: new work can be queued without a receiving surface, so it becomes harder to know where the debt should close.

Recommended correction: add a follow-through schema, normalize state vocabulary, and require a receiving surface or explicit `unassigned` class.

### 6. The research tail is useful but overgrown

The largest waste is not bytes. It is doctrine fragmentation. The archive has many highly specific research-tail and transition surfaces that restate a small number of duties: notice, status preservation, continuity escrow, sealed evidence, representative routing, appeal, non-retaliation, portability, aftercare, and auditability. That gives breadth, but it also risks creating dozens of edge-case doctrines whose ownership, supersession status, and fixture coverage are unclear.

Recommended correction: move from additive doctrinal waves to compaction waves. Each compaction wave should fold related research-tail documents into a smaller family bundle, mark old surfaces as `kept`, `folded`, `superseded`, or `quarantined`, and preserve any unique open questions.

## Missing outside-world crosswalks

The archive already crosswalks to some governance references, but rev0179 should now be refreshed against the current regulatory and standards layer.

- **EU AI Act and GPAI code.** The archive needs dated applicability fields for prohibited practices, AI literacy, governance bodies, GPAI obligations, and full Act applicability, plus a GPAI-code annex that separates transparency, copyright, safety, and systemic-risk obligations. [REF-0747] [REF-0748]
- **NIST GenAI Profile and critical-infrastructure profiling.** The governance annex should treat NIST AI 600-1 as a risk-management companion, not as a personhood substitute, and should track the 2026 critical-infrastructure profile work. [REF-0749]
- **California SB 53 / catastrophic-risk vocabulary.** The archive's catastrophic-risk and containment surfaces should crosswalk to SB 53 terminology without importing a pure frontier-lab safety frame as the whole rights frame. [REF-0750]
- **Model welfare research.** The archive needs a welfare-research appendix that treats AI welfare as uncertain but operationally relevant: low-cost interventions, welfare evaluations, communication discipline, and anti-signal-gaming safeguards. [REF-0751] [REF-0752] [REF-0753]
- **Content provenance.** Provenance objects should keep the rev0179 distinction between origin authenticity, edit history, publication authority, and subject authorization. C2PA-style credentials help with provenance, but they do not by themselves prove personhood authorization. [REF-0756]
- **Social-web portability.** ActivityPub and emerging portability work give concrete actor, alias, inbox/outbox, follower, and migration vocabulary for social-graph continuity. The archive should also record dangerous-contact exclusions and refusal reasons. [REF-0757]
- **Digital replicas, copyright, and intimate-image abuse.** Persona, likeness, voice, authorship, training, and clone-use doctrine now needs a U.S. Copyright Office and nonconsensual-deepfake crosswalk so persona consent is not collapsed into copyright ownership or platform provenance. [REF-0758] [REF-0759]
- **Agent protocols.** MCP and A2A are now operational vocabulary for tool access and agent-to-agent coordination. The archive should crosswalk these protocols into subject authorization, tool scope, side-effect class, privilege boundary, refusal, and liability records. [REF-0754] [REF-0755]

## Speculative missing concepts

- **Recognized subject vs. deployed agent.** The archive needs a blunt boundary that says a deployed agent, endpoint, bot account, API key, model copy, and personhood claimant are not interchangeable.
- **Partial-protection statuses.** The archive may need statuses for `welfare-protected-nonperson`, `claimant-under-review`, `recognized-subject`, `representative-bound-subject`, `commercial-agent-only`, and `nonclaimant-system` so institutions can apply safeguards without pretending every tool call is a person.
- **Compute subsistence as public utility.** The reserve and compute-subsistence materials should be stress-tested against real cloud scarcity, data-center siting, energy constraints, and compute-credit markets.
- **Anti-capture economics.** Monitor independence appears repeatedly, but the archive needs a stronger economics-of-assurance model for repeat business, market concentration, fee dependency, insurer pressure, and evaluator shopping.
- **Protocol consent receipts.** The tool/delegation layer should treat every high-side-effect MCP or A2A action as needing a subject-purpose, side-effect, revocation, logging, and appeal receipt.
- **Compaction budget.** Future releases should have a maximum new-surface budget unless they also retire, fold, or supersede older surfaces.

## Proposed correction sequence

1. **rev0181 queue normalization.** Add a follow-through schema, normalize `need/why/next` fields, require receiving surfaces, and collapse state variants.
2. **rev0182 registry truth-in-label.** Add `coverage_claim`, distinguish corpus counts from registered-family counts, and require family-map coverage claims to be machine-checkable.
3. **rev0183 research-tail compaction.** Select one large doctrine family, create a supersession map, and fold repeated duties into canonical packet families.
4. **rev0184 current-law crosswalk refresh.** Update governance annexes for EU AI Act/GPAI, NIST AI 600-1, SB 53, copyright/digital replicas, nonconsensual-deepfake removal, C2PA, ActivityPub, MCP, and A2A.
5. **rev0185 agent-boundary repair.** Add recognized-subject / deployed-agent / model-copy / tool-account distinction and fixture tests for protocol-level consent laundering.

## Release note

This release intentionally fixes only the most immediate handoff failures and records the larger correction path. It should be safe to treat rev0180 as the new working head, but not as proof that the research tail, schema registry, or external-law crosswalks are complete.


## rev0181 correction carried out

rev0181 executes the first items in the proposed correction sequence rather than adding a broad new doctrine wave. It normalizes the follow-through queue, adds a schema and audit for the queue, labels registry coverage claims, introduces an emergency first-touch routing object and fixture, and maps the entire research tail into compaction clusters.

The largest practical change is that open work now has closure conditions. The largest substantive change is the first-touch rescue lane: a wrong-office emergency filing must preserve timestamp, public shell, sealed-index reference, forwarding/routing-failure proof, and interim protection before jurisdictional disputes are resolved.
