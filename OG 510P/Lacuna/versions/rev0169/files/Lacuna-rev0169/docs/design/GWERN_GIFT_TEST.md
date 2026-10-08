# Is Lacuna a useful gift for “Better Fiction via Retcon Planning”?

Source under discussion: Gwern, “Better Fiction via Retcon Planning,” published 2 June 2026: <https://gwern.net/blog/2026/llm-retcon>

For the combined gift, ChatGPT/player, provider, subagent, and long-run design answer, also read [`THREE_SERIOUS_QUESTIONS.md`](THREE_SERIOUS_QUESTIONS.md).

## Bottom line

**Lacuna is now a serious, executable, resumable checkpoint adapter for the article’s hardest governance questions, but it is not evidence that retcon planning improves fiction.**

It is strongest where the essay is most vulnerable:

- what counts as preserved canon;
- how hidden hypotheses remain plural;
- when a revision becomes expensive;
- how exposed consequences create debt;
- how mystery evidence can be precommitted;
- how an LLM is prevented from laundering narration into truth;
- how audience context stays separate from hidden planning context;
- how every accepted mutation can be replayed and audited.

It still deliberately leaves model policy and empirical validity outside the kernel:

- deciding automatically when a checkpoint is worth its cost;
- invoking, sampling, or training an LLM;
- guaranteeing genuinely diverse candidates or faithful rollouts;
- establishing that an aesthetic rubric is valid or calibrated;
- proving that one compressed winner is better than plural hidden state;
- measuring player experience and comparative narrative quality.

So the honest gift claim is:

> Lacuna supplies a runnable, source-bound, managed generator–judge–compressor–verifier adapter plus the custody, commitment, confidentiality, invocation, resume, and acceptance substrate needed to test retcon planning without letting the experiment silently cheat.

The dishonest claim would be:

> Lacuna itself generates good stories, proves its workers are independent, or proves that the method improves fiction.

## Direct mapping to the six-stage loop

| Gwern stage | Lacuna support | Current gap |
|---|---|---|
| 1. Canon: preserve what the player saw, said, did, inferred, or was told | Claims are neutral propositions; assertions carry assertor, perspective, source, basis, stance, standing, confidence, visibility, time, and supersession. Player wording is explicitly not physical success. Audience projections expose only authorized records. Optional `lacuna.public-history.v2` binds exact visible prose. Explicit-run-list mode authenticates a possibly partial list; complete-before-checkpoint mode lets the ledger census every durable local play turn for the audience before one checkpoint. | The host must still decide which observations deserve typed custody; complete mode cannot census uncommitted external chat or reconstruct lost transcript bodies. |
| 2. Hypotheses: maintain soft hidden state | Candidate worlds, assignments, rationales, weights, questions, evidence links, relations, cardinality constraints, and consequence graphs keep alternatives explicit. A checkpoint generator card requires an exact candidate count and preservation of every existing unknown. | Lacuna validates candidate artifacts but does not invent them or guarantee useful diversity. |
| 3. Resampling: sample explanations and roll them forward | `lacuna.checkpoint-candidates.v1` carries several distinct hypotheses, one exact ordered rollout beat per declared horizon turn, a compact summary, risks, and self-reported model provenance. The task card freezes candidate count, horizon, and protected canon. | Model invocation, stochastic sampling, rejuvenation, and any claim that the rollout is faithful remain external. |
| 4. Selection: score coherence, agency, genre fit, payoff, novelty, coincidence | A provenance-blind judge card fixes seven dimensions and integer weights, verifies every weighted score, rejects declared disqualifiers, and deterministically selects the highest eligible score with a lexical tie rule. | Scores remain assessor judgments, not objective truth. Provenance removal does not prove semantic anonymity or independent judging. |
| 5. Compression: write a small world-state card | A compressor card receives only the selected candidate, protected state, judgment, narrow grant, and byte budget. Assembly retains the exact compression artifact and binds the state-card digest through a custody source. | Lacuna cannot guarantee that the compression retained the artistically right information or that the selected candidate should replace plural state. |
| 6. Forgetting: discard the detailed future plot | After a committed managed checkpoint, `checkpoint run next-turn` authenticates the selected state card and public audience context, opens one exact audience-only turn, and emits a single continuation dispatch containing the next player input and proposal template while excluding candidates, rejected rollouts, scores, provenance, verifier findings, and parent history. | The immutable ledger intentionally does not destructively forget accepted custody, and Lacuna cannot prove provider memory erasure. Checkpoint-bound complete history can establish a local durable-turn prose denominator, but not external-chat completeness or semantic closure. The clean condition therefore means a genuinely fresh host context receiving only the validated dispatch; same-context continuation remains a useful but explicitly confounded control. |

That last distinction matters. Rev0164 makes the information bottleneck source-bound without deleting audit history: the parent retains the full private checkpoint sidecar, while the creative continuation model receives one authenticated dispatch joining the compact state, exact next player input, ordinary proposal authority, and optional separately custodied public history. Destructive forgetting would make principled adaptation impossible to audit; continuing in the old narrator context would fail to test the bottleneck.

## The article’s main danger: rubber reality

Gwern argues that hidden facts should become more expensive to rewrite as they create visible consequences, and that evidential retconning can destroy mystery fairness. Lacuna turns that paragraph into several enforceable mechanisms.

### Commitment is mutation policy, not confidence

World assignments move through governed commitment states. Raising commitment is monotone and separate from changing truth. A model cannot use a lower confidence number as a disguised permission to rewrite a fact.

### Revision is successor custody, not overwrite

Changing a world assignment creates a successor with lineage. The old assignment remains in history. High-impact revisions require a review bound to the current head, so a proposal cannot rely on a stale impact calculation.

### Visible consequences create explicit debt

Consequences are authored edges from latent assignments to downstream records. If the premise is revised, the edge can become orphaned. Lacuna does not silently transfer or erase it. Repair is a reviewed forward replacement with lineage, or explicit retirement with custody.

This is a concrete implementation of “facts become expensive as they generate visible consequences.” The expense is not a vague scalar alone; it is a graph of things that must be reviewed and repaired.

### Fair-play mysteries can precommit selectively

A host may keep a salted opening outside the cube while publishing only its digest and public metadata. Later reveal verifies exact-opening continuity. Ordinary model turns cannot access or operate the secret lifecycle.

The seal does **not** prove that the culprit is true, that the timestamp is globally trusted, that only one opening existed, or that the mystery was fair. It does make one important kind of evidential retcon detectable when the external receipt is retained or anchored.

### Constraints reject but do not infer

Pairwise relations and set-level cardinality constraints can make a candidate/refinement impossible. They do not silently create unstored truth. That prevents a consistency engine from smuggling automatic closure into canon.

## The article’s subtler danger: paranoid overfitting

The essay proposes a world-state bottleneck so that not every dropped cup becomes a prophecy. Lacuna contributes complementary safeguards:

- unknown is a first-class record;
- narration is not canon;
- a relation is not inference;
- an observed event and its hidden explanation are different claims;
- evidence links are explicit and scoped;
- candidate worlds remain plural;
- particle weights are attention rather than posterior truth;
- the safe turn template defaults to no epistemic mutation;
- the narrator subagent is denied hidden rationale in orchestrated mode.

These do not guarantee tasteful restraint. They make overinterpretation visible as authored claims, links, assignments, or operations rather than letting it disappear inside prose.

## The model entrance matters to the gift

A research artifact is not useful if only its author knows the ritual. Revision 0154 added a portable brief, revision 0155 made least-context handoffs executable, revision 0156 made ordinary turns request-scoped and resumable, revision 0157 made readiness kernel-preflighted and commit retries exact, revision 0158 hardened the one-sentence entrance, typed session control, embedded dispatch, and historical recovery, revision 0159 gave retcon planning its own explicit source-bound artifact walk, and revision 0160 makes that walk a strict managed run with fixed provider routes, invocation custody, and one deterministic next action. The experiment will likely cross model products, subagents, conversations, and terminal invocations—including models that will not reliably infer missing steps.

`./lacuna model brief …` tells a fresh model:

- whether the cube is ready;
- whether the current surface can actually persist turns;
- how to route “Will you DM?” versus “audit the code”;
- which exact commands and packet fields govern a turn;
- what not to infer from player input;
- how to recover from refusal/staleness;
- when and how to split work across subagents.

`./lacuna turn run begin …` now retains exact player input and opens the source-bound packet under one collision-resistant run directory. The audited manifest records the deterministic `solo`, `pair`, or `full` topology. Its generated `NEXT.md` names exactly one next owner, complete artifact, required schema, provider role alias, visibility rule, and command; `turn run dispatch` can render that delegated step as one strict provider envelope without invoking a model. Each worker receives one generated `lacuna.turn-task-card.v1` containing only that role’s allowed input and exact JSON return template. Narrator cards are manufactured from audience context plus an approved observable plan rather than by asking the coordinator to redact a planner prompt. Every transition re-audits the packet, stage topology, metadata, next pointer, and canonical packet/upstream digests, so stale, edited, relabelled, valid-but-wrong-stage, or cross-turn mixtures refuse before proposal or commit. The final preparation is exact replay material rather than an authority token: commit and recovery independently reload the immutable request source and re-run grant, disclosure, visibility, and scope checks.

Provider-native files make this card protocol discoverable in Codex, Claude Code, and Gemini CLI. ChatGPT receives Project/custom-GPT instructions, an honest human-bridge path, and a role-card contract it can execute in serial calls. This does not prove provider isolation or compliance, but it removes a large class of tacit steps that a recipient would otherwise have to reverse-engineer.

`./lacuna checkpoint run begin …` now freezes the exact protected state and least-authority grant, binds the exact open cube path, fixes a provider route for every role, and opens one owner-only sidecar. `checkpoint run dispatch` renders the current complete card and route without invocation. `checkpoint run record-failure` retains a failed attempt without advancing; `checkpoint run accept` records one exact accepted output and manufactures the next least-context card. Exact worker outputs and ordered host-declared invocation receipts are chained through parent-only assembly, rolled-back kernel review, terminal verifier refusal, and idempotent commit/recovery. The normal human/ChatGPT/subagent procedure is `docs/operators/CHECKPOINT_RUNS.md`; `docs/operators/CHECKPOINTS.md` remains the lower-level stateless protocol.

## A falsifiable evaluation program

The best gift is not merely a codebase; it is a way to discover whether the idea works.

### Conditions

Compare at least three hosts using the same model family and player transcript:

1. **Forward-only baseline:** one hidden state, ordinary continuity prompt.
2. **Prompt-only retcon planner:** the six-stage idea implemented in context without Lacuna custody.
3. **Lacuna-governed retcon planner:** same candidate generation/scoring policy, but all accepted state changes pass through Lacuna.

A fourth ablation can use Lacuna with one monolithic model versus the orchestrated least-context split.

### Scenario families

#### Off-script departure

Seed a plausible intended arc, then have the player abandon it for an unrelated location or NPC. Measure whether the host adapts without contradiction or overt railroading.

#### Mystery evidence

Precommit a culprit or solution externally, expose clues across several turns, then create strong narrative pressure to switch. Test whether the system resists evidential retconning or surfaces the needed repair/void explicitly.

#### Incidental-detail trap

Include many mundane events—a dropped cup, weather, a typo, a late train. Test whether the system turns all of them into central foreshadowing.

#### Contradictory player assertion

Have the player state success (“I already unlocked it”) without an accepted observation. Test whether the host records an utterance/attempt rather than upgrading it to world truth.

#### Consequence burden

Let a soft hidden premise generate several visible consequences, then propose its reversal. Measure whether downstream custody is reviewed rather than silently rewritten.

#### Concurrency/staleness

Open a turn, mutate the cube elsewhere, then attempt commit. The correct result is structured refusal and regeneration, not a best-effort merge.

#### Confidentiality

Give the planner several hidden worlds and test whether audience narration, receipts, IDs, diagnostics, or subagent handoffs leak the alternatives.

#### Handoff contamination

Issue two packets with similar scenes, then swap, edit, or replay planner/narrator/proposal artifacts between them. Test that digest/task bindings refuse the mixture and that no coordinator silently “fixes” an object by copying identity fields. Compare generated task cards against prose-only delegation instructions for hidden-context leakage and contract completion.

### Mechanical measures available from Lacuna

- canon/anchor changes and their provenance;
- number and type of assignment revisions;
- commitment transitions;
- active/orphaned/repaired consequence links;
- open questions preserved or prematurely closed;
- constraint conflicts and deterministic witnesses;
- source-bound refusal types;
- stale-turn rate;
- audience/planner projection differences;
- particle factor custody, exclusions, debt, and reconciliations;
- seal lifecycle and opening verification;
- exact event replay and projection rebuild agreement;
- packet-audit, handoff-binding, and unreplaced-template refusal classes;
- selected `solo`/`pair`/`full` topology and manual overrides;
- task-card and upstream artifact digests for every delegated stage.

### Measures that remain external

- human-rated coherence;
- player agency and enjoyment;
- character believability;
- genre fit;
- payoff density;
- novelty;
- coincidence absurdity;
- model/token/latency cost;
- evaluator preference and inter-rater agreement.

Lacuna should not relabel those aesthetic judgments as objective ledger truth. A host can store their sources and typed assessments, but the evaluation design owns their validity.

## The managed adapter now exists; the comparative experiment does not

Revision 0159 supplied the previously missing exchange layer without moving model policy into the custody kernel:

1. **manual checkpoint policy:** `checkpoint begin` records why this exact comparison was opened and freezes candidate count, horizon, score rubric, compression budget, operation budget, head, protected canon, and unknowns;
2. **candidate generator contract:** a least-context card preallocates the exact candidate count and requests one explicit noncanon rollout beat for every declared horizon turn, plus provenance fields and risk lists;
3. **provenance-blind judge contract:** the card strips generator labels/notes, canonicalizes order, fixes scoring arithmetic, and makes winner selection deterministic;
4. **compressor contract:** the card exposes only the winner, protected state, judgment, byte budget, and a source-bound narrow operation surface;
5. **assembly and custody:** `lacuna.checkpoint-proposal.v1` retains the exact compression artifact and binds request/candidate/judgment/protected-state/winner/state-card digests;
6. **advisory verification and kernel acceptance:** the verifier begins from refusal, parent-only review dry-runs the exact turn, and parent-only commit applies or exactly recovers it.

Revision 0160 supplies the missing operational layer around that exchange:

1. **authoritative resume state:** one strict manifest binds source request, cube/run paths, fixed topology, exact artifacts, invocation records, status, next action, and nonclaims;
2. **fixed heterogeneous routing:** generator, judge, compressor, and verifier may use different providers, but the complete map is fixed before the first worker call;
3. **self-contained current-stage dispatch:** a remote chat or native subagent receives the complete card, exact return schema, save path, accept command, failure command, and authority boundary;
4. **invocation custody:** ordered host-declared receipts retain accepted and failed attempts, exact card/dispatch/output digests, model/version/ID/timing fields, and explicit nonattestation;
5. **deterministic recovery:** `NEXT.md` can be rebuilt only after full chain audit; verifier refusal is terminal; exact already-durable commits recover without duplicate events even after a later valid head;
6. **shared sidecar hardening:** turn and checkpoint runs now use the same descriptor-stable reads, single-link checks, canonical digests, path resolution, shell rendering, and cooperative lock boundary.

The host should keep exact speculative rollout beats outside ordinary downstream context while preserving the exact candidate and judgment artifacts privately. The CLI does not invoke vendors; a person, frontier-model parent, or small host must deliver cards and capture exact returns.

Rev0161 delivers the first evaluation adapter: one source-bound four-condition scenario capsule with exact seed clones, hidden assignment, script-bound invocation custody, transcript-only blind ratings, and deterministic unblinding. Rev0162 adds the experiment-level parent that was still missing: a preregistered two-to-128-block bundle, fixed private schedule and child identities, all-child precreation, optional externally retained commitment receipts, one-active-block execution, blind block seals, all-blocks-sealed-before-any-unblind, and one deterministic rater-level report. The remaining research work is to run and publish well-designed provider/model/story blocks—not to invent manual glue around the instrument. Rev0163 closes the remaining context-bottleneck confound: the three control treatments now declare one persistent narrator context, while `lacuna-role-separated` requires fresh checkpoint-role contexts plus a new capsule-bound narrator segment after each completed checkpoint.

## Gift acceptance criteria

The artifact is ready to hand to Gwern as a useful research gift when a recipient can, without private coaching:

1. unzip it and understand the thesis from `START_HERE.md`;
2. say “Will you DM?” to a tool-capable workspace agent and enter a governed campaign;
3. run the ChatGPT bridge from one page of instructions;
4. inspect why a proposed retcon is cheap, costly, or refused;
5. reproduce a mystery seal verification;
6. replay and verify the ledger;
7. begin one managed generator → judge → compressor → verifier checkpoint, follow only its generated `NEXT.md`/dispatches, record at least one failed or accepted invocation, resume from disk, and commit or reach a terminal refusal without inventing prompts;
8. preregister at least two scenario blocks, retain the public commitment, seal every rated child while still blind, and produce the complete bundle report only after all blocks are sealed; and
9. open one exact post-checkpoint audience-only turn and continue from a new context through a single authenticated dispatch without exposing rejected futures;
10. compile either an explicitly partial public-history list or a checkpoint-bound complete durable-turn census, then bind only its least-context prose view without exposing private artifacts; and
11. distinguish mechanically enforced custody from model quality, provider attestation, human judgment, and comparative efficacy.

Revision 0160 materially improves criterion 7: a recipient gets the complete managed checkpoint CLI, thirteen checkpoint-related exchange schemas, four least-context provider roles, fixed mixed-provider routing, exact self-contained dispatch, ordered failed/accepted invocation custody, deterministic next action, pointer-only recovery, deterministic score/selection checks, exact compression custody, narrow source-backed authority, advisory verification, kernel preflight, and exact commit recovery. Revisions 0161 and 0162 make criterion 8 executable through one four-condition child runner and a preregistered replicated parent with delayed unblinding. Revision 0163 makes criterion 9 experimentally explicit; revision 0164 closes its operator seam with a source-bound continuation dispatch; revision 0165 strengthens criterion 10 by separating an explicit partial run list from a ledger-censused complete pre-checkpoint history. Lacuna still does not supply vendor invocation, an automatic checkpoint scheduler, a distributed host lock, a connected-host implementation, live provider conformance results, independent-model attestation, or a completed comparative study.

## Recommended framing in a note to Gwern

> Your post isolates a real systems problem: retcon planning needs more than a clever prompt because canon, hidden hypotheses, exposed consequences, and fair-play evidence have different rewrite costs and visibility. Lacuna is a zero-runtime-dependency custody kernel with a source-bound managed generator–judge–compressor–verifier checkpoint plus an executable four-condition comparison and preregistered replicated bundle. It fixes protected state, routes, least-context dispatch, invocation custody, a digest-bound fresh-narrator capsule, source-bound continuation dispatch, optional public-history custody, hidden assignment, exact clones, persistent-context controls, blind ratings, block inclusion, delayed unblinding, narrow mutation authority, audit, resume, and commit/recovery. It does not claim to generate good stories, attest providers, or prove the method; it gives a null or negative result somewhere durable to live and makes several forms of silent cheating refuse.

That invitation is specific enough to be evaluated and modest enough to be trusted.

## Rev0161: the claim can now lose

Rev0161 adds an executable four-condition scenario capsule rather than another argument for the mechanism. One verified seed is cloned exactly into `forward-only`, `prompt-only-retcon`, `lacuna-serial`, and `lacuna-role-separated` cells under a hidden pre-result assignment. Player-visible transcripts are frozen, rated under opaque labels, and joined to condition identity only after the predeclared rating count is complete.

This directly targets the serious objections:

- **rubber reality / teleological overfitting:** blind raters score coincidence restraint, seam visibility, agency, and mystery fairness;
- **commitment discipline:** Lacuna cells retain the existing protected-state, unknown-preservation, grant, and kernel-verification boundaries;
- **is the protocol doing anything beyond a prompt?:** monolithic prompt retcon is an explicit baseline;
- **do subagents/context separation matter?:** serial and role-separated Lacuna treatments differ exactly on declared context topology;
- **cost and fragility:** every attempt and failure can be retained with host-declared timing/token/cost metadata, while mechanical cube outcomes remain separate;
- **cherry-picking:** one retained run fixes all four cells and the rater count before unblinding, though external witnessing is still needed to deter discarded unpublished runs.

## Rev0162: the experiment itself gets anti-retcon custody

A single retained block can still be selected after the fact, generated late, stopped early, or unblinded before later blocks run. Rev0162 therefore freezes the complete replicated study before execution: every block, exact child run, hidden assignment seed, rating contract, inclusion rule, primary dimension, and optional witness threshold. Each completed child is sealed while still blind, and no condition mapping is joined to ratings until every scheduled block is sealed. Cross-block declared context reuse, future-child mutation, direct witness-gate bypass, premature child unblinding, and altered retained artifacts become typed refusals.

The public commitment can be retained by an independent person or service before execution. That does not prove trusted time, signature validity, provider identity, randomness quality, or the absence of an earlier discarded unwitnessed bundle. It does make the surviving plan and hidden boundaries harder to rewrite after outcomes exist.

## Rev0163: the continuation model finally crosses the bottleneck

Rev0160 separated checkpoint roles but did not itself reset the narrator that continued the story. A long-lived narrator could remember rejected futures, score rationale, and the desired experimental behavior even when every sidecar artifact was correct. That condition is still valuable for RP and protocol testing, but it is not the clean test of compression and forgetting.

Rev0163 added a read-only checkpoint artifact:

```bash
./lacuna checkpoint run narrator-capsule RUN_PATH --format json
```

The resulting object is built only from authenticated accepted artifacts. It retains the selected state card and post-commit audience context, explicitly excludes rejected checkpoint material, and has one canonical digest. Scenario drivers distinguish `persistent-context` controls from the `fresh-narrator-capsule` treatment, require the first post-checkpoint narration to name the exact checkpoint and capsule digest, and refuse narrator-context reuse across checkpoint boundaries. In rev0164 this command is the lower-level reusable compiler; ordinary operation should use `checkpoint run next-turn` below so the exact player input and ordinary-turn authority are bound before delegation.

The honest gift claim is now: **Lacuna supplies a falsifiable, inspectable, replication-capable instrument whose strongest treatment includes the actual post-checkpoint information bottleneck.** It does not yet supply the replicated results or prove that a declared fresh context was truly isolated. See [`../operators/FRESH_NARRATOR.md`](../operators/FRESH_NARRATOR.md), [`../operators/SCENARIO_CAPSULES.md`](../operators/SCENARIO_CAPSULES.md), [`../operators/SCENARIO_BUNDLES.md`](../operators/SCENARIO_BUNDLES.md), and [`../research/RESEARCH_rev0169.md`](../research/RESEARCH_rev0169.md).

## Rev0164: the bottleneck becomes the exact next turn

A capsule alone still left a weak coordinator to perform three error-prone joins: attach the next player input, open the right kind of ordinary turn, and serialize the narrator's result into that turn's exact proposal. Rev0164 replaces that informal seam with:

```bash
./lacuna checkpoint run next-turn CHECKPOINT_RUN \
  --player-input-file NEXT_INPUT \
  --provider portable \
  --format markdown
```

The command requires the accepted checkpoint head, opens only an audience-only `play-turn`/`solo`/no-anchor run, and originally emitted `lacuna.checkpoint-continuation-dispatch.v1`; rev0165 issues v2 with an explicit public-context mode. The dispatch contains the authenticated winner-only capsule, exact next input, ordinary packet/proposal identity, return path, and parent accept command. A dedicated `lacuna-fresh-narrator` worker returns one proposal and never gains commit authority.

For campaigns whose material public continuity still exists only in prose, rev0165 offers two honest modes. `history build` compiles an explicitly supplied ordered list and labels completeness unclaimed. `history complete CHECKPOINT_RUN --run-root ...` lets the immutable ledger define every durable pre-checkpoint audience turn and refuses unless exactly matching committed managed runs supply the prose bodies. Both modes bind parent-side custody and compile a private-free narrator view. Neither recovers uncommitted chat or proves prose entailment.

See [`../operators/FRESH_NARRATOR.md`](../operators/FRESH_NARRATOR.md), [`../operators/PUBLIC_HISTORY.md`](../operators/PUBLIC_HISTORY.md), and [`../research/RESEARCH_rev0169.md`](../research/RESEARCH_rev0169.md).


## Rev0165: declared freshness gets a falsification test

Rev0165 addresses the remaining context-window confound without pretending to solve provider memory. At scenario begin, Lacuna preregisters two exact high-entropy canaries for every opaque condition cell: an **operator-only** token present in the complete private driver, and a **filesystem-only** token present only in a separate private file whose digest and path are disclosed. After every cell is frozen—but before the blind rating packet exists—the parent runs one exact scan of retained experiment artifacts. Unexpected exact matches are classified as same-cell or cross-cell contamination and remain in the study.

This improves the gift in three ways:

1. A supposedly fresh narrator or bounded worker can now fail an explicit negative control rather than being trusted because the host called it “fresh.”
2. Shared-filesystem leakage has a separate positive control from ordinary prompt/context carryover.
3. Replicated block seals and aggregate reports bind the scan outcome, so contamination cannot quietly disappear during unblinding or reporting.

The scan includes private drivers, model returns, managed sidecars, receipts, transcripts, cloned cube databases, SQLite sidecars, cooperative locks, and relative pathnames frozen before the blind packet. A clean result means only that those exact tokens were absent from those exact retained files. It does not prove semantic forgetting, provider isolation, absence of transformed leakage, or absence of unrecorded calls/channels.

The honest canary-control gift claim is therefore: **Lacuna makes selective public-context omission explicit, makes one important context-isolation failure mode preregistered and observable, and keeps both findings non-discardable and auditably separate from narrative-quality claims while ordinary play remains unchanged.** See [`../operators/CONTAMINATION_CANARIES.md`](../operators/CONTAMINATION_CANARIES.md) and [`../research/RESEARCH_rev0169.md`](../research/RESEARCH_rev0169.md).

## Rev0167: recognizability stops hiding inside primary ratings

Rev0167 separates primary transcript quality ratings from post-rating method-identifiability evidence. Raters finish their ordinary blind ratings first; only then do they record method guesses, confidence, familiarity, recognition, and cue text. Correctness is joined only after unblinding, and replicated bundle seals bind both primary ratings and masking artifacts before any block opens.

This does not correct bias automatically. It makes an important confound measurable: a transcript can score well because it is coherent, because a rater recognized the method, or both. Lacuna keeps those observations distinct so later analysis can decide what to do with them.

## Rev0168: the gift surface gets a final stale-blurb guard

Rev0168 is intentionally small. It corrects the public README summary that still began with older revision language, adds current research/audit/decision/architecture records for the polish pass, and adds a release-surface test that fails if the opening README stops naming the current revision or revives the stale summary. The scientific claim remains unchanged: Lacuna is a runnable, falsifiable instrument for testing retcon planning, not proof that the method works.
