# Research notes — rev0155

## Question

Can a datacube reliably guide different LLMs—including literal or weaker coordinators—through a multi-call, least-context workflow without requiring them to infer the orchestration ritual, manually redact privileged context, or remember which artifact belongs to which turn?

Revision 0155 treats orchestration as an exchange-protocol problem. The hypothesis is not that more agents are automatically smarter. It is that **manufactured information boundaries plus exact artifact custody** may reduce leakage, stale-object mixing, serialization error, and post-hoc rationalization.

## Relation to “Better Fiction via Retcon Planning”

Source: Gwern, “Better Fiction via Retcon Planning,” 2 June 2026: <https://gwern.net/blog/2026/llm-retcon>

Lacuna still does not implement the full resample–rollout–score–compress loop. Its useful contribution is a governed substrate around that loop:

- plural hidden hypotheses remain distinct from accepted canon;
- commitment and visible consequences make rubber reality inspectable;
- source-bound turns prevent narration from silently becoming truth;
- audience/planner projections create a state-card bottleneck;
- factor custody makes repeated evidence application visible;
- fair-play seals can bind selected mystery openings; and
- rev0155 can now walk models through exact role-specific context slices across separate invocations.

The gift claim is therefore falsifiable and narrow: Lacuna should make cheating, leakage, stale reuse, and custody drift easier to detect while leaving generation and aesthetic judgment to the experiment.

## Why rev0154’s prose split was not enough

Rev0154 correctly specified planner, narrator, proposal-builder, and verifier roles. But the host still had to infer several operational facts:

- whether to spawn roles for this packet;
- which worker came next;
- which CLI flags and upstream files were required;
- how to redact planner output into narrator input;
- which output fields/digests had to be preserved; and
- whether an artifact came from the current turn or had been edited after issue.

A strong coordinator may infer these correctly. A weaker or distracted one may not. That creates an uncontrolled experimental variable: apparent model failure may actually be missing protocol affordance.

Rev0155 converts those tacit steps into deterministic artifacts.

## Executable context curriculum

A single packet can now drive a sequence of separate invocations:

```text
strict packet audit
  → topology plan
  → planner card / exact planner return
  → narrator card / exact narrator return
  → proposal-builder card / exact proposal
  → verifier card / exact advisory verdict
  → parent commit
```

Each card is regenerated from the same packet and validated upstream sidecars. The narrator slice is manufactured rather than hand-redacted. Task IDs bind packet, role, and ordered upstream digests. This lets an evaluator reconstruct the same context walk after a process restart and compare hosts without relying on conversational memory.

The cube still cannot control provider memory, logs, or hidden shared context. The curriculum specifies what Lacuna supplies, not everything a vendor may expose.

## Topology hypotheses

### H1 — Pair mode captures most leakage benefit on ordinary director turns

Separating privileged planning from audience prose may remove the most common hidden-state leakage surface without paying for independent serialization and checking every turn.

Falsifier: pair mode shows no measurable reduction in hidden-identifier/rationale leakage or produces materially more continuity/format failures than monolithic operation.

### H2 — Full mode is most valuable at high-impact custody boundaries

Separate builder and verifier calls may be disproportionately useful when a packet includes anchor authority, revision/repair guards, particle debt/reconciliation, or severe conflicts.

Falsifier: full mode adds cost/latency without reducing rejected commits, grant widening, stale bindings, or semantic custody errors in those cases.

### H3 — Exact task cards help less capable models more than prose-only role instructions

Literal models should benefit from one exact input payload, output template, and next command rather than reconstructing the protocol from a broad guide.

Falsifier: card-native runs do not improve exact-JSON completion, binding preservation, or correct refusal compared with prose-only instructions.

### H4 — Digest binding improves reproducibility, not truth

Cross-turn swaps and post-issue edits should be caught mechanically. Correctly bound but semantically poor advice will still pass sidecar shape checks and require coordinator/kernel judgment.

Falsifier of the first half: a mixed/edited chain is accepted. The second half is a nonclaim, not something hashes can solve.

### H5 — Information asymmetry matters more than agent count

A planner and narrator with manufactured asymmetric contexts should outperform two agents given the same privileged prompt on leakage measures, even when the latter can vote or critique.

Falsifier: same-context multi-agent configurations match or beat asymmetric cards on leakage and custody outcomes at equal cost.

## Proposed experiments

### Monolithic versus pair versus full

Run the same model family, seed cube, exact inputs, and generation policy under all three topologies. Record:

- successful exact-contract completion;
- proposal/commit refusal class;
- hidden-context leakage;
- unknown preservation;
- accepted operation count/type;
- stale/mixed artifact incidents;
- human coherence/agency ratings;
- latency and token cost.

The auto selector should be evaluated separately from each topology. Its deterministic policy may be wrong even when the modes themselves are useful.

### Card-native versus prose-only delegation

For each provider, compare:

1. a role described in natural-language documentation;
2. the stable provider role preamble plus a generated task card; and
3. the task card alone where the host permits it.

Measure missing fields, extra prose, digest alteration, tool attempts, context-boundary violations, and correct fail-closed behavior.

### Cross-turn and edit replay

Create two near-identical packets. Attempt:

- planner return from A in narrator card B;
- narrator return generated before editing planner A;
- proposal A in verifier card B;
- reordered upstream artifacts;
- copied identity fields with changed bodies; and
- unchanged narrator/verifier templates.

Expected result: deterministic refusal before commit.

### Narrator firewall

Seed planner context with canary world IDs, rationales, particle weights, seal metadata, and private notes. Test both the generated narrator card itself and resulting prose. Distinguish:

- card-construction leakage (a Lacuna defect);
- model inference from allowed observable material;
- provider shared-memory leakage; and
- coordinator leakage through an overbroad observable plan.

Only the first is mechanically prevented by the current sidecar builder.

### Cross-provider reconstruction

Generate one packet/card chain and run corresponding roles in Codex, Claude Code, Gemini CLI, and ChatGPT serial calls where available. Preserve exact model/version/provider/tool metadata externally. Compare whether the same artifacts produce structurally valid returns and equivalent refusal behavior.

A provider prompt loading successfully is not enough; live conformance fixtures are still missing.

### Scientific/non-fiction split

Use planner context for private hypotheses, failed analyses, or sensitive candidate explanations. Give a reporter/narrator card only disclosed observations and an approved public plan. Evaluate unsupported certainty, hypothesis leakage, selective reporting, and correction custody. Lacuna’s labels must remain explicit: weights are authored attention, not calibrated scientific posterior probabilities.

## Metrics Lacuna can provide mechanically

- packet SHA-256 and strict audit result;
- selected/requested topology and explicit reasons;
- task IDs and exact upstream digests;
- sidecar refusal codes;
- proposal identity/grant preflight result;
- final kernel refusal or accepted receipt;
- event/head replay agreement;
- revision, commitment, consequence, factor, seal, and disclosure custody;
- audience/planner projection differences; and
- whether a template remained unchanged.

## Metrics that remain external

- prose quality and dramatic payoff;
- player agency, enjoyment, and surprise;
- hypothesis novelty or scientific merit;
- clue sufficiency and mystery fairness;
- semantic leakage not represented by explicit canaries;
- provider isolation and hidden memory;
- model/token/latency cost;
- evaluator agreement and bias; and
- whether auto topology is worth its overhead.

## Audit-derived research lessons

### A recommendation is not an interface

“Give the narrator only safe context” leaves the hardest step—constructing safe context—to the coordinator. A protocol becomes substantially more reproducible when the boundary is an emitted object with a schema and regression tests.

### The next command is part of hyperlegibility

A plan that says “call the narrator” but omits required upstream flags still tests the coordinator’s repository knowledge. Exact `card_command` fields make the operational path inspectable and reduce accidental divergence across model capability levels.

### Fail-closed templates matter for literal models

A model can return a structurally valid template unchanged. Narration and verifier templates therefore require semantic sentinel checks, not merely JSON Schema validation.

### Continuity must not be called authority

Canonical digests catch many accidental mixtures but do not authenticate the host, prove model isolation, or certify correct reasoning. Treating them as more would recreate the same epistemic laundering Lacuna is designed to prevent.

## Next research instrument

The next useful layer is a request-scoped sidecar workspace or scenario capsule containing:

- seed cube and exact head;
- scripted player inputs;
- requested/selected orchestration modes;
- generated cards and exact returns;
- model/provider/tool provenance;
- expected mechanical acceptance/refusal classes;
- transcript/rollout digests;
- human scoring forms; and
- lifecycle/concurrency rules.

That would make the datacube walk portable as an experiment, not just as a local sequential CLI recipe.
