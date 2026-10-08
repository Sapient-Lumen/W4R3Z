# Beyond retcon planning

## The useful inversion

Gwern’s proposal reverses the usual burden of interactive narrative: preserve what the player experienced, keep unseen causes soft, periodically infer a better latent world, roll it forward, compress it, and forget the rollout.

Lacuna accepts the inversion but changes the state representation.

```text
retcon state card                    Lacuna direction
-----------------                    ----------------
observed canon paragraph       ->    typed observations, testimony, beliefs, and visibility
one winning hidden world       ->    governed population of partial candidate worlds
commitment budget              ->    commitments plus explicit consequence and repair custody
story-so-far explanation       ->    evidence factors, provenance, and competing latent valuations
model-generated narration      ->    presentation plus declared disclosures
coherence score                ->    separate epistemic, causal, character, and dramatic tests
```

The thesis is not “rewrite reality often.” It is **delay commitment while preserving every consequence that already constrains honest continuation**.

## Retcon is inference plus control, not rewriting

A robust engine has at least three different loops:

1. **Inference:** which latent worlds remain plausible after recorded evidence?
2. **Control:** which situation should the host present next to create pressure, choice, information, or payoff?
3. **Disclosure:** which accepted facts may this audience now experience, and in what prose?

Collapsing those loops into one LLM completion lets a good sentence impersonate a valid state transition. Lacuna makes inference custody explicit, leaves dramatic control outside the kernel, and treats narration as a separately checked projection.

## Why a single winner is still premature

Selecting and compressing one winning hypothesis repeats the original failure at a shorter cadence. The engine becomes attached to the latest explanation and must later retcon that explanation again.

A better controller retains a population. Shared assignments may appear as current consensus without becoming anchors. Minority worlds can survive because they preserve a distinct explanation, character motive, or future affordance even when their current planning weight is low.

Rev0153 extends the operational step. It can:

- build a complete bank over live or selected worlds;
- normalize authored raw weights;
- fingerprint explicit valuation separately from assignment custody;
- review one active evidence assertion against the complete bank;
- apply one likelihood per world atomically;
- preserve immutable update arithmetic and rationales;
- report ESS, entropy, maximum mass, zero likelihoods, valuation duplicates, and divergent assessments; and
- surface reweighting debt when an applied evidence assertion is later superseded;
- reconstruct an immutable baseline for the latest structurally coherent factor epoch;
- replay every active factor in log space while preserving ended factors as excluded custody; and
- append a separately reviewed reconciliation instead of editing historical updates.

It does **not** propose, resample, merge, prune, select, or canonize worlds. Those are separate powers.

## A weight is not a truth value

The familiar formula

```text
new attention(world) ∝ old attention(world) × assessment(evidence | world)
```

is useful because it forces a planner to state how one evidence record bears on every surviving candidate. It is dangerous because normalized numbers look more objective than they are.

Lacuna’s likelihoods are authored planning quantities. The candidates are incomplete and dependent; their proposal process is not calibrated; and the bank may omit the best explanation entirely. Therefore:

- normalization means the vector sums to one, not that it is statistically correct;
- maximum weight means “most attention under this model,” not “true world”;
- information gain means concentration changed under these assessments, not that the player learned that much;
- ESS means weight concentration, not a literal count of independent good worlds; and
- a clean-looking vector may still carry reweighting debt.

The ledger’s job is to make those limitations impossible to forget.

## Evidence must have factor custody

Without a factor ledger, repeated “consider the clues again” prompts can multiply the same observation indefinitely. Lacuna takes a strict first position: one assertion ID may authorize one particle update.

That does not prove independence. Two separately recorded assertions may describe the same underlying observation. But single use prevents the simplest accidental exponentiation and gives future dependence policy something concrete to inspect.

If an applied assertion is superseded, rev0153 does not reverse history. It reports debt until an authorized reconciliation reconstructs current weights from:

```text
immutable epoch baseline × still-authorized factor 1 × ... × still-authorized factor n
```

The ended factor remains in historical custody as explicitly excluded. Log-space replay avoids treating floating-point underflow as epistemic extinction. Structural world changes start a new epoch rather than laundering stale likelihoods across changed custody.

This still does not solve dependence. Two active assertions may describe the same observation, and a mistaken likelihood vector has no replacement lineage yet.

## Resampling is not reweighting

Sequential Monte Carlo literature treats weighting, resampling, proposal, and rejuvenation as different operations for good reason. Resampling can erase low-mass modes and duplicate high-mass particles. In narrative systems that means losing qualitatively different explanations or futures merely because one evidence packet temporarily favored another.

A future Lacuna resampler should therefore require:

- explicit parent/child ancestry;
- a named policy and random seed or deterministic receipt;
- pre/post diversity diagnostics;
- a minority-explanation reserve or declared reason for its absence;
- separate events for world birth and world retirement; and
- no automatic promotion of survivors into canon.

The next safe step is proposal and ancestry, not `argmax`.

## Commitment should be causal, not merely chronological

“Seen earlier” is an incomplete revision-cost rule. A hidden fact becomes expensive when other visible facts depend on it.

Lacuna’s impact review and consequence graph approximate this distinction:

```text
review burden = ambient recorded exposure
                + explicit consequence severity
                + inherited live descendants
                + commitment level
                + disclosure / anchor pressure
```

Hard commitments and binding consequences block in-place revision; softer consequences remain repair debt. These weights are policy, not calibrated player-harm estimates, but they make the distinction inspectable.

## Plasticity needs a fair-play counterweight

Delayed commitment should not become a license to claim every late solution was fixed from the beginning. Lacuna’s selective host-custodied seal provides an orthogonal mechanism:

```text
external payload + random nonce -> published digest -> later exact reveal
```

A campaign may keep motives, routes, secondary conspirators, and thematic meaning plastic while precommitting to one culprit or random seed. Conversely, a seal may bind a design choice that never becomes world truth.

The receipt proves only exact-opening continuity under one cube/seal identity. It does not prove clue sufficiency, uniqueness, trusted time, or fair-play quality. A verifier must retain or externally anchor the pre-reveal receipt to obtain evidence against a host that can fork local history.

> Late-bind what may adapt; explicitly seal what the experience promises was fixed; never confuse either operation with truth.

## Meaning and causation must be scored separately

A retcon system can make every player choice appear meaningful by reinterpreting the same eventual outcome. That is interpretive payoff, not necessarily agency.

Lacuna should support paired counterfactual tests:

1. replay from the same head;
2. alter one player action;
3. hold the initial candidate population and random receipts as constant as possible;
4. measure changes in reachable states, resources, relationships, and endings; and
5. separately measure how much explanatory text and latent interpretation changed.

A system whose explanations change dramatically while reachable consequences barely change is cosmetically responsive and causally inert.

## The disclosure compiler

The player does not experience a database. They experience prose. A narrative engine therefore needs a compilation boundary between semantic changes and presentation.

Lacuna’s source-bound declared-disclosure contract is the first weak form:

```text
accepted operations -> visible assertions -> narration source -> returned prose
```

A stronger future compiler would:

- generate prose only from an accepted semantic delta;
- extract candidate propositions back from the prose;
- compare them with the permitted disclosure set;
- refuse, redact, or regenerate when prose leaks hidden ontology or invents unsupported physical facts; and
- retain exact transcript bytes outside the cube against source digests.

This seam matters more than eloquence. It separates a trustworthy world transition from a persuasive hallucination.

## Dead matter is a realism primitive

Retcon scoring that rewards payoff density will turn every cup, cough, and cloud into a clue. A plausible world requires irrelevant texture and unresolved noise.

Candidate scoring should include a reincorporation tax:

- penalize the number of formerly independent details newly connected;
- penalize specificity unsupported by evidence;
- preserve a target proportion of details as atmosphere or accident;
- reward explanations that predict future observations, not merely accommodate past ones; and
- distinguish “this clue was likely under the world” from “the world was invented to absorb this clue.”

An information bottleneck alone does not prevent conspiracy-shaped overfitting.

## Character identity needs conservation laws

Motives cannot be as plastic as unused geography. A character model should separate:

- slowly changing core values and attachments;
- medium-term goals and loyalties;
- fast-changing tactics, attention, and local beliefs; and
- interpretations that remain genuinely ambiguous.

A revelation should make earlier behavior more predictive, not merely redescribe it after the fact. Future particle fingerprints may need a character-identity layer distinct from proposition-level valuation.

## Candidate worlds are not belief worlds

Lacuna’s candidate worlds are global planner hypotheses. Formal epistemic models use possible worlds differently: each agent has an accessibility relation describing which worlds that agent cannot distinguish, and actions update those relations according to who observed what.

Conflating the two would recreate the category error Lacuna exists to prevent. A future epistemic-action layer should distinguish:

- an **ontic delta**: what physically changed;
- an **observation policy**: which agents perceived which parts;
- a **belief update**: what each agent now takes to be possible; and
- a **nested-belief update**: what agents believe about other agents’ observations and beliefs.

The assertion ledger can record explicit results of those updates. It does not yet compute global logical closure or nested belief automatically.

## Experiments Lacuna should enable

### Seam-hunting suite

Adversarial players revisit ignored locations, ask adjacent counterfactual questions, compare witness accounts, and stress temporal intervals.

### Factor replay audit

Apply several evidence factors, supersede one, reconcile, and verify that original update arithmetic remains unchanged while the current vector is separately custodied and independently replayable. Then change the world structure and verify that the old epoch is retired rather than silently transported.

### Causal-agency differential

Paired runs change one player decision and score physical divergence separately from explanatory divergence.

### Motive-drift audit

A character’s core-value representation is compared before and after replanning; changes require proportionate recorded causes.

### Coincidence ledger

Every explanation declares which independent events it connects. Complexity and coincidence costs become visible data rather than one opaque quality score.

### Culprit commitment challenge

Use fair-play seals to bind an initial culprit, candidate set, random seed, or solution version. Separately test clue chronology and weight updates; the seal alone does not show that exposed evidence remained fair. A future Merkle scheme could bind a clue-generation policy and reveal leaves independently.

### Missing-mode challenge

Give assessors evidence that fits none of the current particles. A healthy controller should propose a new world or declare bank inadequacy rather than force all mass onto the least-wrong existing option.

## The cube as an executable context curriculum

A datacube can do more than persist state. Because every projection is deterministic and every turn is bound to a particular head, it can define the exact sequence of contexts through which a model is allowed to walk. That makes the cube useful as an experimental curriculum:

- start several hosts from the same head and audience projection;
- expose one controlled observation or source-bound player message;
- let each host propose against the same write grant;
- commit or refuse under the same invariants;
- invoke a later CLI process and reconstruct the next context from the ledger rather than from model memory;
- compare monolithic and multi-agent hosts while giving each role an explicitly different slice; and
- retain transcript, rollout, model/version, and latency records as external sidecars bound by digests.

This is stronger than a long prompt because the path is executable and replayable. In rev0158, a typed request distinguishes `session-control` from `play-turn`, and one request-scoped run retains exact input, packet, topology, cards, returns, proposal, exact rollback preparation, verifier result, and receipt. Its audited manifest and deterministic `NEXT.md` expose one owner, one complete input, one schema, one provider alias, and one command at every stage. A provider-neutral dispatch embeds the exact current task card, so a remote chat context need not infer or access a local path. Role-specific cards contain exact slices and return templates; downstream task IDs bind the packet plus ordered upstream digests. A later invocation can resume without conversational memory, refuse a mixed, edited, relabelled, wrong-stage, symlinked, hard-linked, substituted, or tampered-pointer chain, and independently re-run the prepared envelope against the request-head ledger prefix. Pointer recovery repairs only `NEXT.md`; direct commit must reproduce the frozen event chain and contexts; post-commit recovery verifies rather than reapplies it.

Rev0159 extends that context curriculum to a backstage checkpoint without turning the model into kernel authority. Request v4 fixes purpose `checkpoint`, protected state, candidate count, rollout horizon, rubric, compression budget, and narrow grant. The generator card preallocates every candidate and every ordered rollout beat; the judge receives a canonical provenance-stripped view with one score slot per candidate; the compressor receives only the deterministic winner; and the verifier receives only proposal-visible custody. Parent assembly rechecks the full selection chain, then the existing rollback preparation and exact commit/recovery path decides whether any typed mutation is accepted. Exact rejected futures remain private experiment artifacts and are omitted from ordinary downstream context.

Rev0160 makes the checkpoint curriculum literally walkable across processes and products. One strict managed manifest fixes the exact open cube path and all role-to-provider routes before the first call. At each state, an audited `NEXT.md` and self-contained dispatch expose one owner, one complete card, one return schema, and one parent command. Failed calls can be recorded without advancing; accepted calls receive ordered host-declared receipts binding the exact card, dispatch, and retained output. The next card is manufactured only after validation. Verifier refusal is terminal, review remains parent-only, and an already-durable commit can be authenticated and recovered after later writes without replaying it. A later invocation therefore needs the run directory, not private conversational memory or an author’s unwritten ritual.

It is also narrower: the cube controls custody and context projection, not what a provider remembers internally, whether a vendor truly isolates agents, or how well a model follows instructions. Routes and invocation receipts are host declarations, not provider attestations. The run, ordinary/checkpoint cards, model returns, scores, compressed state card, and verifier verdict are advisory sidecars rather than ledger events. A future experiment bundle should pair one seed cube with a scripted sequence of player inputs, expected refusal/acceptance classes, role-specific card fixtures, exact model/provider declarations, cost/latency records, and external scoring forms. The same bundle could test fiction, scientific hypothesis maintenance, incident analysis, or any domain where privileged working hypotheses must not leak into a public report.

The multi-agent split is especially useful here when it encodes information asymmetry rather than voting. Give the planner competing latent explanations, give the reporter a generated audience-only card plus an approved observable plan, give the serializer one fresh packet and validated upstream artifacts, and give the verifier the exact candidate object. More agents with the same context merely reproduce consensus theater. The useful ablation is therefore not “one model versus many” but “shared prompt versus manufactured context boundaries,” with monolithic, pair, and full topologies measured separately.

## Bold working hypothesis

The long-term object is not a story state. It is a **partially observed causal program with epistemic projections, a governed population of latent programs, and a narrative compiler**.

The “world” is the population of programs still compatible with custody. The “story” is a sequence of audience-specific disclosures. Plot is a control policy over which experiments, pressures, and choices to present next. Retconning becomes ordinary latent-state revision—except where anchors, commitments, consequence graphs, factor custody, and selectively sealed promises say the world has already paid to make something stable.

## Forward repair instead of retrospective laundering

A retcon planner is tempted to move every old clue, promise, motive, and probability onto whichever hidden-world hypothesis currently scores best. Lacuna instead requires explicit acts. The predecessor remains historical, the successor is fully restated, and a separate relation records why the transfer or recomputation was authored under a particular reviewed state.

The design target is not a perfect revised canon paragraph. It is a population of possible worlds plus an inspectable graph of observations, beliefs, factors, commitments, consequences, revisions, repairs, and selectively sealed promises.

## Rev0161: paired context curricula

A scenario capsule can now compare not only outputs but **ways of allocating context**. The same durable seed and scripted intervention are walked through four curricula: no hindsight revision, one monolithic retrospective call, one serial Lacuna role context, and four separated Lacuna role contexts. The cube manufactures the exact card at each boundary and retains the declared context topology.

This is useful beyond fiction. A scientific capsule could preserve one dataset boundary while comparing direct analysis, monolithic hypothesis revision, serial generate/judge/compress/verify, and separated-role review. The same nonclaim applies: declared role separation is an auditable protocol treatment, not proof of independent cognition.


## Rev0163: forgetting is a context transition, not a deletion operation

The immutable audit archive and the continuing narrator have different retention duties. The parent must retain candidates, judgment, compression, verifier output, and accepted receipt so the checkpoint can be audited. The narrator should not inherit those objects merely because the parent saw them.

A committed managed checkpoint can compile `lacuna.checkpoint-narrator-capsule.v1`. Its construction accepts only authenticated request, proposal/compression, receipt, and post-commit audience context. Raw candidates, rejected rollout beats, scores, provenance, verifier findings, and orchestration history are not builder inputs. Rev0164 originally bound that capsule, the exact next player input, and one already-opened audience-only ordinary turn into `lacuna.checkpoint-continuation-dispatch.v1`; rev0165 issues v2 with an explicit typed/partial/complete public-context mode. The fresh narrator receives only that complete envelope and returns one proposal under the parent’s existing accept/commit boundary.

This creates two experimentally distinct curricula:

```text
persistent-context control:
  one narrator/context retains the full history and checkpoint discussion

fresh-narrator treatment:
  checkpoint workers use bounded contexts
  -> parent commits
  -> next-turn opens a source-bound ordinary turn
  -> a new narrator segment receives one capsule-bound continuation dispatch only
```

The capsule does not prove that a provider erased memory, that a context ID is truthful, or that the state card is artistically sufficient. It does make the intended bottleneck concrete, digest-bound, and falsifiable, while leaving the full private evidence available for audit.

## Rev0165: the bottleneck needs both a public denominator and leakage controls

A fresh narrator experiment has two different failure surfaces. It may receive too little public history, making a compact state treatment look incoherent for the wrong reason; or it may receive private rejected material, making the treatment look stronger than its nominal bottleneck. Rev0165 addresses the two surfaces separately.

`history complete` uses the immutable ledger as the denominator for durable pre-checkpoint audience turns and retained managed sidecars as the source of exact prose. The resulting artifact is bound to one checkpoint request and cannot be called complete when a durable turn body is missing. Scenario canaries then test a different question: whether preregistered private bytes appear outside their allowed coordinator/file sources before blind rating.

Neither mechanism proves semantic equivalence, provider forgetting, or artistic sufficiency. Together they make a cleaner curriculum: the treatment can state what public text it received, what private artifacts were excluded by construction, and whether two exact leakage probes surfaced in retained outputs.
