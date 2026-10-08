# SURPRISE-LEDGER.md note — rev0106

Rev0106 adds the evaluation-verdict gate and metadata coherence hardening; historical content follows.

---

# Surprise ledger — rev0039

These are not claims of paper correctness. They are places where the research hunt or tiny probes changed the working intuition.

## SURPRISE-001: Window order signal without explicit position

Degree: **medium**

A finite sliding window update can leak order through what changed, so absolute/relative positional encoding is not the only way order enters tiny autoregressive systems.

Next question: Can we make an adversarial stream where histogram-delta order vanishes, and does a tiny model still infer order?

## SURPRISE-002: Context-free value vectors may be useful deep in the stack

Degree: **medium-high**

Attention value vectors are usually treated as context-dependent residual-stream products; Bank-of-Values reframes late-layer values as partly token-identity memory.

Next question: When do values need context: entity identity, relation binding, or state updates?

## SURPRISE-003: K=V can be sane while Q=K=V collapses

Degree: **medium**

The QKV sharing lane suggests the model may tolerate key/value sharing far better than complete projection collapse; directionality of queries is the fragile part.

Next question: Can a tiny trained attention model learn to compensate for K=V sharing on algorithmic recall but not on routing-heavy tasks?

## SURPRISE-004: Heuristic cache routing loses to simpler anchors more often than expected

Degree: **medium**

Several smoke probes showed oracle/top-anchor methods winning cleanly and hand-designed routing heuristics failing, which is useful negative evidence against prematurely complex policies.

Next question: Which heuristic features are redundant, and where is training actually needed?

## SURPRISE-005: Encoder-decoder context compression is back on the table

Degree: **medium-high**

I expected KV compression/eviction to dominate this cube, but LCLM-style context compression suggests a separate latent-skim-and-expand axis is worth testing even at toy scale.

Next question: Is compressed context best viewed as answer substrate, router, or memory index?

## SURPRISE-006: Retrieval as query-side supervision, not just pruning

Degree: **medium-high**

EASE-TTT makes retrieval look like a source of temporary attention targets; the model can still answer from full context after query-side adaptation.

Next question: How noisy can the evidence target be before adaptation hurts more than base full-context inference?

## SURPRISE-007: Parametric memory becomes interesting exactly when cache memory disappears

Degree: **medium**

The LoRA/KV framing suggests adapter memory is not a general replacement for context, but a complementary channel whose value appears under aggressive compression.

Next question: Can stale parametric memory be gated safely when fresh context disagrees?

## SURPRISE-008: Supervised memory labels are a clean bridge away from BPTT

Degree: **medium-high**

SMT reframes long-memory training as learning one-step transitions from teacher predictive states; in the toy, this creates a cheap bridge from tensor probes to tiny trainable memory.

Next question: Can we add noisy/imperfect teacher labels so the SMT toy is not an exact update table?

## SURPRISE-009: Agentic DFS is a sharper tiny-training lane than expected

Degree: **medium**

Most of the hunt has been cache/memory systems, but the agentic transformer search lane gives a tiny environment with a plausible mechanistic success criterion: action-trace and failure-trace specialization.

Next question: Can a tiny policy-gradient transformer actually rediscover the two-trace DFS mechanism, or does symbolic DFS make the task too easy?

## SURPRISE-010: Entropy alone may not be the decisive signal

Degree: **medium**

The entropy probe makes decode-conditioned information look much stronger than entropy-only allocation, suggesting online/generated-token feedback may matter more than static head entropy classification.

Next question: Split the budget arena into strict prefill-only, decode-token-only, and mixed policies to see whether entropy survives without future-support leakage.

## SURPRISE-011: C++ changes the feasible probe frontier

Degree: **medium-high**

The environment has gcc/g++, so high-volume cache/rollout/coreset simulations can move out of slow Python loops while staying dependency-free.

Next question: Which existing Python probe should be promoted to C++ only after the metric/falsifier stabilizes?

## SURPRISE-012: Streaming coreset toy does not solve early needles

Degree: **medium**

The C++ Express-style surrogate helps broad/drifting regimes but remains bad on isolated early-needle retention, showing coreset quality must be judged by adversarial evidence retention, not only average attention error.

Next question: Can a query-independent cache preserve rare early evidence without degenerating into salience oracle or storing too much?

## SURPRISE-013: Autoresearch belongs as a meta-optimizer lane

Degree: **medium**

The linked HPO paper is not a cache/memory paper, but it directly informs how CloudtainerML should allocate experimental trials: LLM/domain priors should complement classical state, not replace it.

Next question: Can a Centaur-style optimizer choose probe configs better than hand sweeps on our synthetic cells?

## SURPRISE-014: Cache object choice may dominate cache policy

Degree: **high**

Residual-checkpoint/KV-Direct framing makes full KV, residual states, hidden states, adapters, and token streams competing cache objects rather than variants of one cache.

Next question: Can residual checkpointing and KV quantization coexist in a tiered object system?

## SURPRISE-015: Move-query systems papers are toy-testable

Degree: **medium-high**

A cross-instance GPU-fabric paper still yields a useful tiny phase-boundary probe because the core arithmetic is payload size, latency, and selected-block count.

Next question: Should systems-cost cells stay P0 even when they do not train a model?

## SURPRISE-016: Naive decoupled erase/write gates lost

Degree: **medium**

The first hand-built decoupled fast-weight memory probe did not validate the intuitive architecture claim; tied scalar delta won all smoke regimes, suggesting decoupling needs learned/calibrated gates.

Next question: Can trained decoupled gates beat tied scalar gates on the same generated regimes?

## SURPRISE-017: Persistent memory can lose to no memory

Degree: **high**

The new memory-sycophancy trap makes memory an accuracy risk, not just a recall booster; skeptical/provenance policies matter because belief-only snippets can preserve misconceptions while losing correction context.

Next question: Can a provenance/correction coupling rule keep useful preferences while refusing factual misconceptions?

## SURPRISE-018: Structure-aware memory did not automatically beat flat retrieval

Degree: **medium**

The first hypergraph working-memory toy was dominated by oracle evidence and only weakly won by hierarchy/hypergraph policies in non-oracle slices, so graph structure alone is not a free win.

Next question: Can we design regimes where hypergraph structure adds value without leaking oracle evidence or overfitting section priors?

## SURPRISE-019: The crude DF-SSM scaffold toy favored int8 over binary-plus-low-rank

Degree: **medium**

The first 1-bit scaffold plus low-rank correction toy did not yet produce a clean win; fp32 is the sanity winner and int8 wins some regularized practical slices, suggesting our low-rank correction or regimes are too crude.

Next question: Should the next DF-SSM probe use learned/distilled correction vectors or a fairer byte-normalized practical leaderboard?

## SURPRISE-020: Lossy cache needs exactness tests, not just good average error

Degree: **high**

VeriCache sharpens a failure mode the cube was under-weighting: short-output accuracy and reconstruction error can look fine while long code/tool trajectories diverge catastrophically.

Next question: Can the verifier guard catch catastrophic sites with low recompute fraction?

## SURPRISE-021: Reasoning delimiters might be an actionable cache clock

Degree: **medium**

Step boundaries are normally treated as text formatting, but cache processors suggest they can be rewrite/consolidation events. That is more concrete than generic periodic eviction.

Next question: Do delimiters remain useful under noise or do we need a learned event detector?

## SURPRISE-022: Memory provenance has to be a first-class metric

Degree: **high**

The memory-safety lane now looks like a phase diagram, not a binary feature: belief snippets, corrections, provenance, and stakes determine whether memory helps or hurts.

Next question: Can provenance-linked memory beat no-memory under high correction loss without over-abstaining?

## SURPRISE-023: Safety tails can decouple from mean cache error

Degree: **high**

The alignment-collapse paper makes low-dimensional safety features a separate cache-acceptance axis rather than a vague safety add-on. The first C++ toy also produced a clean separation between task reconstruction and safety projection metrics.

Next question: Can a small calibration set predict vulnerable safety subspace channels before a full quantization sweep?

## SURPRISE-024: Flow-based credit assignment looks toy-testable

Degree: **medium-high**

Reasoning-token credit sounded like a large-model RL problem, but the attention-DAG formulation collapses to a clean graph-flow simulator with adversarial decoy regimes.

Next question: Can FlowTrace-style credit labels train a tiny model better than uniform or local-attention labels?

## SURPRISE-025: Topic documents beat graph memory in the first revision toy

Degree: **medium**

The first topic/graph memory probe favors topic-document consolidation in most smoke slices. That does not refute temporal graph memory, but it says graph structure only earns its keep under sharper revision/provenance regimes.

Next question: What regimes force topic documents to over-consolidate and make non-destructive temporal graph memory necessary?

## SURPRISE-026: Hasse masks are more useful as an audit vocabulary than a P0 build target

Degree: **medium**

The partial-order mask toy produced interpretable coverage/leakage/redundancy measures, but not yet a decisive P0 experiment. It may be a way to audit mask claims rather than a major training lane.

Next question: Can mask reachability/leakage metrics predict actual tiny-transformer failure modes?

## SURPRISE-027: Tail contracts are useful, but not evidence

Degree: **medium-high**

The audit layer needed to distinguish direct catastrophic-tail measurements from surrogate schema contracts. Otherwise dashboards can over-promote mean-only lossy probes.

Next question: Which P0 probes still need direct exact-output or catastrophic-tail metrics rather than surrogate contracts?

## SURPRISE-028: Truthful distortion belongs in the memory/cache safety lane

Degree: **medium-high**

JANUS-style fixed fact pools show that provenance and faithfulness are not enough if the system can truthfully omit or soften adverse evidence under a goal.

Next question: Can memory retrieval and summary compression preserve adverse material facts without turning every response into full-context dumping?

## SURPRISE-029: Bank-wise sparse FFN routing rhymes with cache diversity

Degree: **medium**

The bank-wise sparsity paper is not a KV-cache paper, but the toy failure mode is the same as cache eviction: global scores can starve rare groups.

Next question: Can one diversity-budget formalism cover FFN channel banks, KV pages, memory documents, and search branches?

## SURPRISE-030: Memory poisoning belongs beside cache tails

Degree: **high**

The poisoning literature reframes persistent memory as a durable control channel, not only a personalization feature. That means memory gates need adversarial-tail metrics just like lossy KV cache probes.

Next question: Can a single write bypass write-time filtering but be caught by query-conditioned read admission?

## SURPRISE-031: Execution state beats semantic relevance as the right agent-memory object

Degree: **medium**

The Mage paper makes a clean distinction between similar memories and valid active execution state. That feels testable and more fundamental than another vector retrieval tweak.

Next question: Do branch/revision boundaries beat similarity retrieval under synthetic error contamination?

## SURPRISE-032: Equal-cost baselines can reverse sparse-prefill intuitions

Degree: **medium**

The earlier dense-vs-sparse prefill toy was not fair enough; once dense is forced onto the same token budget, anchors become a much crisper question.

Next question: Which chunk-router survives adversarial anchors and distributed evidence?

## SURPRISE-033: Provenance is an object model, not just metadata

Degree: **medium**

The evidence-tracing survey makes memory source, revision, retrieval, use, and invalidation feel like operational state rather than annotation fields.

Next question: Can provenance scoring beat relevance/source-only under stale update and contaminated tool regimes?

## SURPRISE-034: Dual-horizon retrieval is a clean bridge to tiny trained agents

Degree: **low**

MERIT-style separation of episode and turn memory gives a supervised target structure before we need a full agent benchmark.

Next question: Can a tiny router learn when to retrieve global vs local memory from synthetic PRM labels?

## SURPRISE-035: Execution verification may be more important than retrieval policy

Degree: **medium**

The execution-state lane keeps producing questions where the core issue is whether a trace segment is valid, not whether it is relevant.

Next question: Do false-success detectors become a better trained-model target than generic memory retrievers?

## SURPRISE-036: The cube can drift toward the assistant model’s obsessions

Degree: **high**

The research hunt gradually promoted state-trust/security material into the root charter even though the user cared more about tiny-scale performance and architecture surprises. That is a project-management failure mode, not a scientific result.

Next question: Can charter audits keep the cube focused on performance/surprise while still preserving side-wing material that occasionally matters?

## SURPRISE-037: Component-aware rank allocation immediately looked useful

Degree: **medium-high**

A tiny synthetic C++ allocator made local functional-HPO allocation dominate most QK/OV/MLP fragility slices, making A3-style component objectives feel more testable than generic low-rank compression.

Next question: Can component-aware rank allocation still win when the spectra come from an actual tiny trained transformer layer rather than synthetic spectra?

## SURPRISE-038: Linear attention needs discriminability before speed matters

Degree: **medium**

The ELA dilution toy had softmax_full winning many non-oracle slices; cheap positive kernels were not automatically attractive unless target mass survived distractors.

Next question: Can sparse+low-rank repair target-mass dilution at equal cost, or do we need learned routing?

## SURPRISE-039: Gated subspace inference is gate-limited, not subspace-limited

Degree: **medium**

The synthetic subspace was often usable, but naive residual-norm gating lost to full linear in many regimes; the cheap gate needs to predict output impact rather than residual magnitude.

Next question: Would a tiny learned gate trained on cheap features cross the full-linear frontier under a realistic bandwidth model?

## SURPRISE-040: Hard rank cut challenged low-rank decay in the spectral proxy

Degree: **medium**

The LRD proxy did not automatically beat a crude hard-rank cut; this says the trained dynamics around memorization/grokking may be essential, not optional.

Next question: Should LRD be the first real trained modular-arithmetic escalation instead of another spectrum proxy?

## SURPRISE-041: MoE routing testbeds are exactly CloudtainerML-shaped

Degree: **medium**

MoE routing looked like a large-model systems topic, but STAR plus the MoE Routing Testbed produce crisp small-scale specialization/load/rare-domain questions.

Next question: Can the subspace router survive rare-domain and shift regimes after a fair HPO sweep?

## SURPRISE-042: Oracle sparse prefill is an experiment-design pattern

Degree: **medium**

The useful part is not only sparse prefill; it is the explicit decomposition into budget reducibility gap, learned-indexer gap, and realization gap.

Next question: Can existing sparse/cache probes be refactored to expose the same three gaps?

## SURPRISE-043: Negative tensor-decomposition papers are high-value guardrails

Degree: **medium**

A strong negative result can save more work than another positive architecture claim; tensorization needs to beat componentwise matrix baselines in heterogeneous regimes before it earns code priority.

Next question: Are there any tiny regimes where tensor structure wins honestly without hand-constructing shared subspaces?

## SURPRISE-044: Attention sinks are a performance-intervention diagnostic, not only interpretability

Degree: **low**

The same attention stripe can imply opposite repairs: a NOP/trash-can wants gating, while a broadcast sink wants registers or shared global slots.

Next question: Can cheap value-norm/output-rank diagnostics choose the right repair in a tiny trained model?

## SURPRISE-045: Every pruning/sparsity screen needs a real-speed guard

Degree: **medium**

FLOP counts are too easy to optimize in toy screens; GEMM alignment, dynamic overhead, and memory movement can reverse winners.

Next question: Should the native HPO harness optimize regret under wall-time proxy rather than raw score?

## SURPRISE-046: Transport MoE is a capacity/route-consistency story, not just clustering

Degree: **medium**

The DOT-MoE lane only becomes compelling when balanced assignment and token routing are tested together under rare specialists and shift; plain clustering is otherwise too strong.

Next question: Can a trained tiny dense FFN be moefied with similar phase boundaries?

## SURPRISE-047: Sparse tails need feature reuse, not just fewer multiplies

Degree: **medium**

The HASTE-inspired toy makes kernel overhead and shared feature reuse central; irregular sparsity can save arithmetic and still lose the wall proxy.

Next question: Should every sparse-output/sparse-FFN probe expose feature-reuse and kernel-penalty fields?

## SURPRISE-048: Sparse frontier wants phase-specific policies

Degree: **medium**

The isoFLOPS toy keeps prefill/decode and task family separate; one sparse strategy is unlikely to be universal even at toy scale.

Next question: Can an HPO sweep learn a phase policy rather than a single method winner?

## SURPRISE-049: Dynamic short conv repairs are more interesting than dynamic conv alone

Degree: **low**

The local primitive becomes useful only when paired with global bypass or anti-alias gates in the synthetic hard regimes.

Next question: Can a tiny trained model learn the bypass/gate or does it need explicit architecture?

## SURPRISE-050: Sparse FFN can be a computation relocation, not a pure efficiency win

Degree: **medium**

The new FFN redistribution probe makes attention_shift a first-class metric; sparse FFNs may lower local FLOPs while making attention carry harder circuits.

Next question: Can a tiny trained one-layer transformer reproduce the same redistribution profile on carry-addition and histogram tasks?

## SURPRISE-051: Adaptive rank control is only interesting if tails are scored

Degree: **medium**

STAR-KV-style soft thresholding looks strongest when tail singular-value failure is explicitly penalized; mean reconstruction alone would hide the useful regime.

Next question: Can a tiny real attention block show the same K/V-asymmetric rank frontier?

## SURPRISE-052: Critical Layer Isolation may be a phase diagram, not a rule

Degree: **medium**

Protecting layer 0 is strong only in early-critical regimes in the toy; HPO or two-anchor policies look safer when the critical layer moves.

Next question: Can actual tiny transformer compression identify task-dependent critical layers with cheap probes?

## SURPRISE-053: MPI router alignment is more testable than expected

Degree: **medium**

The paper-level idea collapses into a clean router/expert alignment wind tunnel with rare/load/drift traps, no large MoE required.

Next question: Can a tiny trained MoE reproduce the symbolic MPI/load-balance phase split?

## SURPRISE-054: Position encoding can be a geometry-only phase probe

Degree: **low**

nD-RoPE makes it possible to separate axis-aligned wins from real isotropy/extrapolation wins with no language model.

Next question: Which synthetic grid tasks actually need isotropic position features?

## SURPRISE-055: Tiered speculative verification is a threshold frontier, not just a speed hack

Degree: **low**

VIA-SD maps naturally to direct/slim/full verifier thresholds where mismatch penalties decide promotion.

Next question: Can a small trained verifier learn the medium-confidence band?

## SURPRISE-056: Operator routing collapse can be a discovery, not only a failure

Degree: **medium**

The Chiaroscuro result makes collapse itself a clue: if a learned router keeps rejecting an operator, the smaller operator set may be the real architecture.

Next question: Which collapse is useful, and which is only biased cost/modeling? Use alias traps to separate them.

## SURPRISE-057: MoE quantization needs route consistency metrics

Degree: **low**

It is easy to obsess over reconstruction MSE, but near-boundary routing can flip the computation path with small numeric changes.

Next question: Can route flip rate predict score debt in a tiny trained router?

## SURPRISE-058: Activation sparsity is not free even in C++

Degree: **medium**

The native runtime proxy keeps dense INT8 as a strong baseline once burstiness, branch cost, tiny batches, and quality-sensitive spikes enter.

Next question: Should we measure a real sparse loop microbenchmark next, or keep it symbolic?

## SURPRISE-059: Actual transforms made spectral routing more conditional

Degree: **medium-high**

The symbolic CHIAR-like lane looked clean, but actual DCT/IDCT reconstruction plus attention residuals exposed alias and sparse-needle traps immediately.

Next question: Can learned posterior routing or residual top-k repair beat hand-set entropy routing under equal cost?

## SURPRISE-060: Ranker-once contextualization lives or dies on candidate-set recall

Degree: **medium**

The ranker architecture is attractive for long contexts, but the toy made rank_miss and distractor_leak more important than mean recall.

Next question: Can a tiny trained ranker learn candidate recall without paying dense-context cost?

## SURPRISE-061: Null experts need rare-token guardrails

Degree: **medium**

Data sparsity via null experts looks cheap only until rare critical tokens are skipped; false-skip and rare-miss have to be first-class metrics.

Next question: Can a router-margin or variance signal protect rare tokens cheaply?

## SURPRISE-062: Spectral HPO did not automatically beat fixed DCT+attention residuals

Degree: **medium**

The held-out sweep gave router_hpo only a minority of non-oracle wins; fixed DCT+attention residual repair is a stronger baseline than expected.

Next question: Can HPO win only in carefully targeted alias/locality regimes, or is residual repair the right default?

## SURPRISE-063: Copy-head phase transitions look like the best trained-tiny candidate

Degree: **medium-high**

The Bayesian copy-head paper gives concrete phase variables and sample-complexity predictions, making it more testable than another symbolic cache heuristic.

Next question: Should rev0031 train a one-head copy model and look for the predicted softmax/linear transition split?

## SURPRISE-064: Sparse attention is a family arbitration problem

Degree: **medium**

MoSA-style content selection and LoLA-style sparse cache win different regimes; there is no single sparse winner even in the toy.

Next question: Can a tiny router learn when to use content sparse attention versus sparse cache?

## SURPRISE-065: Confidence-aware compute needs rare-expert guards

Degree: **medium**

Confidence adaptation saves compute in friendly regimes but overconfident-wrong and rare-expert regimes make confidence a liability without guardrails.

Next question: Can confidence-adaptive SwiGLU remain useful when rare_miss and route_flip are first-class losses?

## SURPRISE-066: The strongest novelty is combinatorial, not singular

Degree: **medium-high**

The most interesting claims are not individual paper ideas but collisions between operator routing, sparse attention, screen-regret, and tiny native phase diagrams.

Next question: Can a trained tiny copy/spectral model confirm any combinatorial surprise beyond symbolic probes?

## SURPRISE-067: Monitorability may be an architecture metric

Degree: **medium**

The copy-head phase lane suggests that smoothness/abruptness of capability emergence may matter for choosing tiny architectures, not just final loss.

Next question: Train a one-head copy model and measure phase abruptness and early warning diagnostics directly.

## SURPRISE-068: Screen regret is now a first-class discovery filter

Degree: **medium**

Several attractive symbolic wins weaken when regret, realized cost, alias/tail misses, or dense baselines are added; the audit spine changed the science.

Next question: Which older P0 probes still lack enough regret/cost guards to deserve promotion?

## SURPRISE-069: Routing can fail by being absorbed rather than being wrong

Degree: **high**

A learned sparse gate can have high posthoc mask accuracy but still be unhelpful when Q/K/V co-adapt around the gate; this is a different failure than ordinary bad routing.

Next question: Can a tiny trained model reproduce random-gate competitiveness or posthoc-gate recovery?

## SURPRISE-070: Routing coordination and routing selection should be separated

Degree: **medium-high**

Directional routing suggests a router can matter by coordinating suppression directions, while routing absorption suggests token-selection gates can be absorbed. These are not the same mechanism.

Next question: Which router family should get trained-tiny escalation: coordination routers or selection gates?

## SURPRISE-071: Attention-mass screens still hide value-geometry errors

Degree: **medium**

Contribution-style geometry turns old value-outlier intuitions into a general guard: retention/attribution should include value magnitude and alignment, not only attention mass.

Next question: Should contribution-weight fields be added to spectral, sparse, and cache-retention probes?

## SURPRISE-072: Soft sparse-gate training accuracy is not deployment evidence

Degree: **high**

The trained tiny lookup probe makes the obvious but often ignored distinction concrete: a soft end-to-end gate can score well while hard top-k deployment and posthoc gating tell a different story.

Next question: Do learned gates still look good under hard top-k in a tiny multi-layer copy/retrieval model?

## SURPRISE-073: Locality without reachability is a performance cliff, not a benchmark detail

Degree: **high**

Boundary repair reframes exact-copy failure as graph reachability: adjacent tokens can be local but inaccessible under fixed block masks. This is cleaner than another average needle benchmark.

Next question: Can a trained tiny block-sparse attention model reproduce the boundary-copy cliff and repair it with source-extended bridge edges?

## SURPRISE-074: Exactness guard fields are now promotion criteria

Degree: **medium-high**

After copy-head, routing absorption, and boundary repair, average quality is too forgiving; exactness/reachability/target-miss fields decide whether a performance win is real.

Next question: Which current P0 lanes fail the exactness guard and should be demoted until fixed?

## SURPRISE-075: Boundary reachability survives a tiny trained copy task

Degree: **high**

The graph-level boundary repair claim became visible in a learned one-head copy task: unreachable fixed-block/periodic masks stayed near chance while sliding and bridge masks reached perfect copy in the smoke setup.

Next question: Does the same cliff survive multi-layer models or more ambiguous source positions?

## SURPRISE-076: Sparse attention benefits from a program vocabulary

Degree: **medium-high**

Block, sliding, bridge, periodic, and anchor masks are easier to compare when framed as source/reachability/cost programs rather than unrelated algorithm names.

Next question: Can this schema absorb MoSA/LoLA/top-k cache methods without losing key details?

## SURPRISE-077: Periodic skip edges are not a generic boundary repair

Degree: **medium**

Periodic skip patterns help predictable old-anchor cases but can miss adjacent boundary sources and off-phase targets that bridge/sliding masks handle cheaply.

Next question: Would adaptive fusion or learned skip periods repair the off-phase miss without erasing the scheduling advantage?

## SURPRISE-078: Attention preconditioning has a rare-axis tail risk

Degree: **medium**

Whitening-like preconditioning improves ill-conditioned score proxies, but the tiny proxy makes over-whitening and rare-axis signal suppression visible as tail risk.

Next question: Does a real tiny trained attention task show the same conditioning-vs-rare-axis frontier?

## SURPRISE-079: Depth repair is a reachability property, not a mask label

Degree: **high**

The trained multi-hop boundary task distinguishes masks that are one-step invisible but relay-reachable from masks that are truly unreachable; depth only helps the former.

Next question: Can a learned sparse mask discover the minimal relay bridge without being handed the boundary program?

## SURPRISE-080: Routing correctness and signal gain are separate failure surfaces

Degree: **medium-high**

The new gain-decoupling wind tunnel makes route-only sparse attention look insufficient in weak-value/deep-attenuation regimes even when the correct evidence is selected.

Next question: Can a trained tiny attention layer learn a separate gain channel without destabilizing distractor regimes?

## SURPRISE-081: Sparse programs need page-cost semantics

Degree: **medium-high**

Nominal sparsity is not enough; selector overhead, page alignment and fusion penalties can flip the winner before any model-quality question is asked.

Next question: Can the sparse program schema absorb page-centric costs as first-class fields rather than posthoc annotations?

## SURPRISE-082: Exposed depth routing can be fake interpretability

Degree: **medium**

Posthoc routing schedules can expose readable tensors while carrying no content-dependent mechanism; causal ablation has to be part of the promotion test.

Next question: Can a tiny trained Block-AttnRes model produce content-dependent depth routes that survive the guard?

## SURPRISE-083: The audit surface is becoming a mechanism, not paperwork

Degree: **medium**

Mechanism promotion now needs exactness, cost, memory-traffic, route/gain and trained-evidence fields; otherwise attractive probes keep overclaiming.

Next question: Which old P0 probes lose priority when promotion score is computed mechanically?

## SURPRISE-084: Learned boundary gates solve before they harden

Degree: **high**

The learned boundary-mask probe reached exact copy accuracy and ranked the true bridge edges top-k, yet thresholded active-edge F1 stayed low because the model used soft log-priors rather than hard gates.

Next question: Can sparse post-training or annealed hard-concrete gates turn top-k bridge preference into deployable hard reachability without losing copy accuracy?

## SURPRISE-085: Importance-in-route often beats explicit gain in the constrained readout

Degree: **medium-high**

The first tiny route/gain readout did not make explicit gain the clear winner; routing with importance features dominated most regimes, while gain helped mainly when importance itself was misleading.

Next question: Does a full attention layer with learned value projections still show a separate gain failure surface, or is route/gain mostly a guard metric?

## SURPRISE-086: Trained tiny probes need their own guard audit

Degree: **medium**

After symbolic probes became guard-heavy, trained toy probes began risking a new overclaim path: high final accuracy without edge, route, gain, or exactness diagnostics.

Next question: Should trained-probe guard readiness be mandatory before adding any new trained escalation to P0?

## SURPRISE-087: Post-trained gates can solve below threshold

Degree: **high**

Exact-copy gates can rank the true bridge edges correctly while all scores are too low for ordinary threshold deployment; hard top-k compilation matters more than raw probability calibration.

Next question: Does top-k remain reliable in larger candidate sets and blockwise GQA-style index branches?

## SURPRISE-088: Threshold masks and top-k masks are different mechanisms

Degree: **high**

A soft gate may be actionable as an ordering but not as calibrated Bernoulli connectivity. Promotion needs both threshold and top-k deployment checks.

Next question: Can calibration be repaired cheaply, or should sparse gate deployment prefer fixed-budget compilers?

## SURPRISE-089: Gate compilation is now a first-class architecture step

Degree: **medium-high**

The sparse mechanism is no longer just a trained gate; it is train plus compile plus exactness check plus cost check.

Next question: What is the right compiler family for MiniMax/MSA block indexers and Gated Sparse Attention-style sigmoid scores?

## SURPRISE-090: Annealing does not make thresholds trustworthy by itself

Degree: **high**

Even when annealed gates rank bridge edges correctly, threshold deployment can remain weaker than hard top-k. This reinforces gate rank/calibration separation.

Next question: Can hard-concrete or STE training make threshold-style gates deployable, or should sparse bridge gates always compile by top-k/validation?

## SURPRISE-091: Block index branches are cost mechanisms, not only accuracy mechanisms

Degree: **medium-high**

Per-group block routing can help group-specific/boundary regimes, but false-block traffic and selector overhead can erase the win. Block sparsity must be scored with wall-proxy fields.

Next question: Does a learned index branch discover boundary anchors without explicitly being handed them?

## SURPRISE-092: Exact top-k has a temporal systems knob

Degree: **medium-high**

The sparse attention bottleneck is not just which tokens to attend; the exact top-k selector has its own phase diagram driven by previous-step overlap, score flatness, and bursty drift.

Next question: Can a toy sparse decoder predict when to use GVR, fallback, or dense selection?

## SURPRISE-093: Sparse mechanisms now need a compiler stack

Degree: **medium**

The project now has separate learned gates, gate compilers, block index branches, and exact top-k algorithms. Treating them as one sparse-attention method hides the real failure surfaces.

Next question: Can we factor sparse attention into trainable scorer, compiler, selector kernel, and exactness guard in every future probe?
