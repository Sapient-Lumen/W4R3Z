# Context access and the perspective firewall

## One structured builder

All JSON and Markdown context renderers consume one structured context builder. Filtering rules are not duplicated in presentation code.

A perspective context and a named candidate world are mutually exclusive:

```bash
./lacuna context ./stories --agent-id player --world-id wld_hidden
```

returns `unsafe-context-scope` without emitting a packet.

## Two views, never one ambiguous view

A director turn may need both what the audience may know and what the planner may consider. The safe shape is two labelled objects:

```text
audience_context  -> perspective, privileged=false
planner_context   -> planner, privileged=true
```

The audience object is never widened merely because planner access exists beside it.

## Subagent context slicing

An orchestrated host may possess both labelled views, but it should not replicate that privilege into every worker:

- the planner may receive `player_input`, `audience_context`, `planner_context`, the write grant, and response contract;
- the narrator receives `player_input`, `audience_context`, and an approved observable beat plan after hidden rationale has been removed;
- the proposal builder receives the complete fresh packet plus approved narration and approved typed operations so it can preserve source-bound fields exactly;
- the verifier receives the fresh packet and candidate proposal for an independent binding, grant, leakage, and custody check;
- the parent/coordinator alone issues the packet and submits the final commit.

This split is an information-flow policy, not a claim that four agents are always better. A trivial narration-only turn can stay monolithic. A turn comparing hidden worlds, creating high-commitment custody, revising consequences, or changing the particle bank benefits from explicit separation.

Provider task cards and empty/read-only tool lists reduce accidental widening, but the model host remains responsible for enforcing the handoff. A provider instruction file is not a cryptographic access boundary.

## Perspective visibility

An assertion is visible to an agent when it is public, held by that agent, asserted by that agent, or restricted to an audience containing that agent.

An open question is visible when public, opened by the agent, or restricted to that agent.

A fair-play seal is visible when public or when its restricted audience contains the agent. Before reveal, a visible seal exposes its digest and publication metadata only; no payload or nonce exists in the cube. Perspective seal rows and receipts omit privileged `source_id` linkage. After reveal, the authorized perspective may receive the exact published opening.

## Planner-only categories

Perspective context omits:

- candidate worlds, assignments, particle weights, and valuation/custody fingerprints;
- cross-world consensus;
- claim relations and cardinality constraints;
- evidence-link interpretation, particle-update/reconciliation history, factor dispositions and rationales, reconciliation reviews, and reweighting debt;
- explicit consequence links, replacement lineage, and repair-review frontiers;
- revision guards and commitment/dependency diagnostics;
- relation-, cardinality-, or consequence-derived conflict details.

These categories can reveal culprit structure, required alternatives, hidden motives, causal promises, or the existence of latent possibilities even when no assignment value is shown.

The packet’s `omitted` map states these boundaries explicitly. Empty privileged arrays must not masquerade as “no hidden records exist.”

## Omission must not become a covert channel

Perspective safety is more than removing rows. A hidden anchor, candidate-world consensus, hard commitment, or hidden consequence must not alter whether a visible claim appears settled in a way that reveals the hidden cause.

Perspective-relative lacunae are computed from the perspective’s visible record surface. Hidden ontology and diagnostics are omitted together.

## Interpretation contract

Every context includes reminders that:

- unknown is not false;
- belief is not world truth;
- constraints reject but do not fill unknowns;
- candidate worlds may disagree;
- normalized particle weights are planner attention, not truth or calibrated probability;
- one evidence assertion may act as one particle factor; superseded current-epoch factors create visible debt until separately reconciled;
- factor reconciliation replays recorded support and does not certify calibration, independence, causation, or truth;
- ambient exposure is not explicit dependence;
- commitment raises are monotone;
- truth change creates a revision successor;
- consequences survive endpoint changes until deliberately repaired;
- a passing fair-play seal proves byte continuity only, not truth, clue sufficiency, or fair play.

These statements constrain downstream interpretation; they are not extra facts about the story.

## Explanations use the same boundary

`explain --agent-id AGENT` cannot bypass context filtering. Every returned link is visibility-checked, privileged target kinds are refused, and event custody is reduced to a safe envelope. Historical visibility is honored without revealing records that were never visible.

## Explicit nonclaim

A perspective projection prevents known structured records from leaking through that projection. It cannot prove that an external model will not infer, remember, fabricate, or deliberately reveal hidden information through another channel. A model receiving planner context is a privileged component.


## Repair frontier

Privileged planner context may expose `consequence_repair_frontier`: active repair-required consequence links paired with digest-bound review receipts. This is an execution aid for a director, not audience knowledge. Perspective contexts return no repair rows, no frontier entries, and no hidden IDs derived from them.

Opening a source-bound director turn rebinds embedded receipts to the packet's post-request-source base head. The adapter may do this only because its issuance event adds provenance without changing the reviewed epistemic projections.

## Complete-population particle boundary

An unscoped planner context may include:

- `particle_bank`;
- recent `particle_updates`;
- the current `particle_reconciliation_review`; and
- recent `particle_reconciliations`.

The bank covers every live or selected world and includes its digest, normalized attention, fingerprints, valuation-equivalence groups, factor epoch boundary, applied-factor status, resolution custody, and reweighting debt. The reconciliation review exposes the complete current factor set, excluded factors, blockers, projected log-space replay, and head-bound authorization digest. This is intentionally global planner state.

A world-scoped planner context omits all four surfaces even though it may include that world’s assignments. Normalizing or repairing a filtered slice would create a false denominator and could leak the existence or mass of omitted alternatives. A world-scoped director therefore cannot receive `update_particle_bank` or `reconcile_particle_bank` authority.

Perspective context omits these surfaces structurally, including counts, IDs, weights, diagnostics, update receipts, factor identities/dispositions, rationales, review blockers, repair history, and debt. `explain` treats particle updates and reconciliations as planner-only targets.

An unscoped director packet may carry either reviewed entrance:

- a new evidence update requires active unused evidence, exact complete coverage, and a fresh bank digest;
- a factor reconciliation requires a replayable current epoch, exact baseline/current custody, a fresh complete review digest, and no identical prior repair.

Any earlier in-transaction change to membership, status, weight, assignment custody, or factor authority is observed by the mutation path and can stale or block the reviewed operation. Source-bound turn issuance rebinds the review to the turn's base head without hiding intervening semantic changes.


## Post-checkpoint continuation context

A role card can constrain what a checkpoint worker receives, but worker separation alone does not constrain the model that narrates the next turn. After a committed managed checkpoint, `checkpoint run next-turn` authenticates the accepted checkpoint and opens one source-bound audience-only ordinary turn. It emits one private continuation dispatch containing:

- accepted previous checkpoint narration;
- post-commit typed audience context;
- selected compressed state card;
- retained and omitted elements;
- preserved unknown IDs;
- forbidden contradictions and next pressures;
- exact next player input;
- exact ordinary proposal template and return path; and
- optional exact public-history text with separate source custody.

The projection excludes candidate sets, rejected rollouts, scores, worker provenance, verifier findings, parent history, and all acceptance/commit powers. The optional history compiler accepts only explicitly supplied committed ordinary turns from the same cube/audience in immutable event order and must end before the checkpoint request. Invalid history refuses before a new turn is opened.

A clean continuation condition gives the complete dispatch to a new narrator context. The parent retains checkpoint and ordinary-turn sidecars for audit and alone accepts, prepares, commits, and presents. This boundary is structural inside the artifact; actual provider memory isolation and transcript completeness remain host claims.
