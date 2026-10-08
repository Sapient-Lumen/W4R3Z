# Novelty hypotheses — rev0031

This file answers a deliberately dangerous question: what looks surprising and possibly under-discovered?

Caution: CloudtainerML does **not** claim global novelty. The status labels below mean: observed in our cube, under-mentioned relative to the papers and summaries collected so far, and worth testing harder.

## Evidence tiers

- **Tier A:** paper claim + independent CloudtainerML probe pressure + clear falsifier.
- **Tier B:** CloudtainerML probe pressure + plausible paper neighborhood.
- **Tier C:** odd intuition; not yet enough evidence.

## Prioritized candidates

### 1. DCT plus attention residual may be the default tiny operator baseline, not a fancy router endpoint

Evidence tier: **A**.

External anchor: CHIAR reported that learned routing collapsed to DCT plus attention and rejected RBF. Internal evidence: `REV0030_SPECTRAL_OPERATOR_HPO_SWEEP_SMOKE.json` found fixed DCT+attention residual still beating router HPO on many held-out slices, while alias traps forced attention residuals.

Novelty caution: CHIAR already discovered the collapse. The CloudtainerML-specific hypothesis is narrower: at tiny scale, route search may be less valuable than building a strong residual pair and spending HPO on alias/tail guards.

Best next test: actual tiny transform/routing model with DCT-only, attention-only, DCT+attention, entropy router, and learned router under equal cost.

### 2. Phase smoothness / monitorability may be an architecture metric

Evidence tier: **A-**.

External anchor: the copy-head phase paper predicts first-order softmax emergence versus smoother linear-attention crossover. Internal evidence: `REV0030_COPY_HEAD_PHASE_SMOKE.json` favored smoother methods when abruptness and monitor risk were scored.

Novelty caution: the phase-transition claim is from the paper; the project-specific twist is treating transition shape as an engineering criterion, not just a mechanistic curiosity.

Best next test: train one-head softmax, entmax, and linear copy models; measure loss, copy order, abruptness, precursor diagnostics, and final accuracy.

### 3. Sparse attention is an arbitration problem, not a method class

Evidence tier: **A-**.

External anchors: MoSA selects content-sparse tokens by expert-choice routing; LoLA-style sparse cache solves different fixed-state/locality regimes. Internal evidence: `REV0030_EXPERT_CHOICE_SPARSE_ATTENTION_SMOKE.json` split winners across MoSA-like expert-choice, LoLA-like sparse cache, and hybrids.

Novelty caution: the individual methods are known. The CloudtainerML hypothesis is that the real object is a regime router over sparse methods, and the router's candidate-set recall is more important than mean sparsity.

Best next test: matrix-level MoSA-vs-LoLA-vs-hybrid toy with exact-copy and needle guards.

### 4. Functional component rank allocation may beat generic compression even at toy scale

Evidence tier: **B+**.

External anchors: A3 splits QK/OV/MLP and STAR-KV uses adaptive rank control for K/V cache. Internal evidence: component-rank and STAR-KV HPO probes repeatedly looked stronger when K/V asymmetry, tail error, and mixed precision were scored.

Novelty caution: component-aware compression is already explicit in A3/STAR-KV. The under-tested idea is whether small random/tiny-trained models show the same phase surfaces before large-model deployment.

Best next test: real SVD/random-matrix sweep with QK/OV/MLP surrogate objectives and equal kernel-cost guard.

### 5. FFN sparsity may export computation into attention rather than remove it

Evidence tier: **B**.

External anchor: sparsity/work redistribution papers already suggest architecture choices move computation. Internal evidence: the FFN-attention redistribution probe penalized sparse FFN variants that apparently lowered FLOPs while increasing attention burden.

Novelty caution: not globally novel. The useful CloudtainerML angle is making computation redistribution a required guard for all sparse FFN/MoE claims.

Best next test: one-layer trained toy where sparse FFN routing is ablated and attention-head metrics reveal compensatory attention work.

### 6. Cheap-screen regret is a discovery filter, not dashboard hygiene

Evidence tier: **B**.

Several probes had attractive winners until regret, realized-cost, alias, rare-miss, or dense-baseline guards were added. This is not a model architecture discovery; it is a project-method discovery.

Best next test: require every P0 promotion to report regret versus a dense/simple baseline and a known adversarial trap.

### 7. Exact-copy / needle exactness should be the veto test for efficient memory alternatives

Evidence tier: **B-**.

Repeated cache, ranker, spectral, and sparse methods look good on average but fail isolated needles or copying. The project-specific claim is that exact copying is not just another benchmark; it is a veto condition for many efficient-memory claims.

Best next test: common exactness harness plugged into spectral, sparse attention, ranker-contextualization, and linear-memory probes.

### 8. Dynamic local mixing is conditional and should have an explicit bypass

Evidence tier: **B-**.

Dynamic short convolution is promising in associative/local regimes, but our adversarial no-locality and alias setups punish it. The likely useful primitive is dynamic conv plus bypass/anti-alias guard, not dynamic conv everywhere.

### 9. Null experts and confidence-adaptive compute need rare-token guards

Evidence tier: **B-**.

Null experts and confidence-adaptive SwiGLU looked attractive only when rare-critical misses were explicitly guarded. The under-tested hypothesis is that rare-token guardrails are the general tax on adaptive compute.

### 10. C++ phase diagrams are the project's main scientific instrument

Evidence tier: **A as process**, not architecture.

The native probes changed priorities faster than summaries alone. They exposed negative results, winner collapse, dense-friendly baselines, alias traps, and regret fields cheaply enough to steer trained escalation.


## rev0033 additions

- **Routing absorption vs coordination split:** token-selection gates and coordination routers should not share a promotion rubric.
- **Random-router baselines are mandatory:** if a router cannot beat frozen random or hidden-state self-routing under equal cost, it is not a core performance idea yet.
- **Contribution weights as promotion guard:** attention mass should not be the only retention/attribution metric when values can differ in magnitude or direction.
