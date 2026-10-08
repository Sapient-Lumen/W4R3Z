# Architecture — rev0159

## Purpose

Revision 0159 adds one governed **retcon checkpoint** above Lacuna’s existing event-sourced custody kernel. The checkpoint is an exchange and host protocol, not a new truth engine: external workers generate, compare, and compress speculative alternatives; Lacuna freezes the context and policy they were supposed to receive, validates every returned object, rechecks deterministic selection, rehearses the proposed typed mutation through the real kernel, and commits only from parent authority.

The database remains schema 8 and the immutable event envelope remains schema 1. The revision advances exchange contracts and host orchestration.

## Architectural layers

```text
player/campaign state
        │
        ├─ ordinary play ── request v4 purpose=play ── turn run/preparation/receipt
        │
        └─ backstage checkpoint ── request v4 purpose=checkpoint
                                      │
                                      ▼
                           protected state + fixed policy
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
             generator       provenance-blind judge    compressor
        exact candidates       exact score slots       selected only
        exact rollout beats    deterministic winner    narrow operations
                 └────────────────────┬────────────────────┘
                                      ▼
                           parent proposal assembly
                                      │
                                verifier card
                         proposal-visible advisory check
                                      │
                                      ▼
                         real kernel review under rollback
                                      │
                                      ▼
                           parent commit / exact recovery
```

No worker owns the cube, run state, assembly, review, commit, recovery, or player presentation.

## Typed request boundary

New turn issuance uses:

- `lacuna.turn-request.v4`;
- `lacuna.turn-grant.v2`; and
- source protocol `lacuna.turn-request-source.v3`.

Request v4 separates `input_kind` from `request_purpose`. “Will you DM?” is normally `session-control` with purpose `play`; a retcon trigger is `session-control` with purpose `checkpoint`. The same words cannot silently acquire checkpoint authority after issuance.

Historical request v2/source v1 objects remain readable as `play-turn`/`play`. Historical request v3/source v2 objects preserve their input kind and default to purpose `play`. Grant v1 remains readable for those historical packets. Validation uses version-specific exact field sets rather than accepting hybrids.

## Protected-state compiler

`checkpoint begin` verifies the cube, records one source-bound request, and derives a deterministic protected-state object containing:

- audience assertions;
- anchors and cross-world consensus;
- visible fair-play metadata;
- claim relations and cardinality constraints;
- consequence links and revision guards;
- open questions and unsettled claims; and
- a canonical exact set of unknown identifiers.

The protected state is not a prose summary. Its canonical digest is carried through task cards, worker returns, assembly, review, and receipt custody. The checkpoint policy fixes candidate count, rollout horizon, compression character budget, operation budget, exact scoring dimensions and integer weights, selection rule, blind-judging requirement, unknown preservation, observed-canon prohibition, and the ban on laundering aesthetic scores into particle weights.

## Cardinality-explicit task cards

A weaker model should not have to infer how many array elements a phrase such as “generate several candidates” implies. The generator template preallocates exactly `candidate_count` objects with stable candidate IDs. Every candidate template preallocates exactly one ordered rollout beat for each declared horizon turn. The judge template preallocates exactly one complete score slot for every candidate.

Each `lacuna.checkpoint-task-card.v1` includes:

- one deterministic task identity;
- request and ordered upstream digests;
- one complete least-context input payload;
- explicit withheld context;
- exact instructions;
- exact output schema and populated template;
- forbidden actions; and
- parent-only next-step custody.

Task validation recomputes the card from the request and upstream artifacts. A schema-shaped but edited card does not pass.

## Information-flow topology

### Generator

Receives protected planner context, policy, and exact candidate template. Returns noncanon candidates with explicit hidden-state hypothesis, preserved unknowns, provenance declaration, risks, summary, and exact ordered rollout beats. It receives no commit authority.

### Provenance-blind judge

Receives a canonical candidate view with generator provider/model/invocation labels and notes removed. It still sees candidate substance and rollout beats because those are what it must judge. Blindness therefore removes one declared provenance channel; it is not semantic anonymity or proof of independent contexts.

The judge returns all fixed dimension scores, weighted arithmetic, disqualifiers, eligibility, rationale, and one winner. Validation recomputes every weighted total and applies the exact highest-eligible-then-lexicographic tie rule.

### Compressor

Receives only the selected candidate, protected state, exact judgment, compression budget, and narrow checkpoint grant. Rejected alternatives and generator provenance are withheld. It returns one bounded state card, exact preserved unknown set, typed operations, narration, disclosures, rationale, and provenance.

The allowed operation surface is deliberately narrower than a normal director turn. It cannot anchor, harden commitment, update particle weights from aesthetic scores, operate fair-play secrets, or use unrestricted administrative mutation.

### Verifier

Receives the assembled proposal rather than raw candidates and scores. It begins from a fail-closed template and checks proposal-visible custody consistency, unknown preservation, protected-state respect, narrow authority, compression budget, and anti-rubber-reality hazards.

It cannot independently recompute candidate selection because the raw comparison set is intentionally absent. Parent assembly revalidates that complete chain. A verifier `pass` remains advisory and never authorizes commit or presentation.

## Proposal assembly and selection custody

Parent-only assembly validates the request, candidates, judgment, and compression in order. It recomputes candidate identities, exact rollout cardinality, blind judge view, score arithmetic, disqualifiers, deterministic winner, selected candidate digest, compression identity, preserved unknowns, and operation restrictions.

The resulting `lacuna.checkpoint-proposal.v1` retains the exact compressor artifact and adds a narrow provenance source operation whose metadata binds:

- checkpoint request digest;
- protected-state digest;
- candidate artifact digest;
- judgment artifact digest;
- deterministic selection rule and winner;
- selected-candidate digest; and
- compressed state-card digest.

The story ledger receives this custody source plus accepted typed operations, not rejected candidate bodies or the full score table.

## Dispatch and provider registry

`lacuna.checkpoint-agent-dispatch.v1` is a self-contained routing envelope. It embeds the exact card, provider alias, return schema/template, parent save/next command, authority split, and nonclaims. Dispatch validation does not merely inspect shape: it validates the embedded card and recomputes the exact envelope from that card and provider route.

A centralized provider registry now owns portable, Codex, Claude Code, Gemini CLI, and ChatGPT role aliases for both ordinary turns and checkpoint roles. Entrance briefs, run dispatch, checkpoint dispatch, and provider tests use the same registry, reducing alias drift.

Dispatch is not invocation. Provider credentials, network calls, retries, sampling, retention, model identity, and isolation remain host concerns.

## Kernel review, commit, and recovery

`checkpoint review` requires an accepted advisory verifier result and then passes the assembled ordinary turn proposal through Lacuna’s existing exact preparation path. The real mutation engine executes inside a transaction, builds events, projections, receipt, and contexts, and rolls back unconditionally. The review binds the resulting preparation digest.

`checkpoint commit` revalidates the request, proposal, verifier, review, and exact preparation. A current-head commit replays the frozen event envelope inside the durable transaction. If the same checkpoint was already committed but sidecar delivery failed, retry reconstructs and verifies the historical request-head prefix and exact durable event chain before materializing the same receipt. Later legitimate ledger changes do not invalidate this recovery; changed input, forged history, changed preparation, or a stale uncommitted proposal refuses.

## Compatibility and unchanged kernel doctrine

Rev0159 does not fork ordinary turn execution. Checkpoint assembly emits the existing `lacuna.turn-proposal.v2`, review uses `lacuna.turn-preparation.v1`, and accepted custody uses `lacuna.turn-receipt.v3`. Existing run v2, one-sentence play, descriptor-stable sidecar reads, cooperative same-run locking, pointer-only recovery, particle/factor protocols, revision/consequence governance, and fair-play seals remain intact.

## Explicit nonclaims

Revision 0159 does not prove that candidates are diverse, rollouts are faithful, judging is independent, scores are valid, compression is artistically optimal, or retcon planning improves fiction. It does not invoke or attest a model, schedule checkpoints automatically, provide a distributed lock, encrypt privileged artifacts, or make SQLite plus external files one transaction.

It supplies a reproducible context-and-authority walk in which missing rollout work, edited handoffs, score arithmetic drift, winner substitution, overbroad mutation, stale review, and duplicate retry are mechanically visible or refused.
