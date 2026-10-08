# CloudtainerML mission audit — rev0077

**Status:** pass_with_blockers  
**Promotion:** blocked  
**Claim boundary:** mission/surface/trace-ingress audit only; no public-model or GPU result.

## Heart of the mission

Convert architecture claims into cheap adversarial falsifiers, enforce exactness/cost/provenance vetoes, and promote only mechanisms that survive measured deployment—not accumulate ideas, probes, or green checks.

The cube is best understood as a **claim compiler**: it should turn a proposed mechanism into the cheapest decisive experiment, force the experiment through exactness and cost vetoes, and either stop the lane or escalate it to measured implementation. Its product is a trustworthy decision, not a growing registry.

## What had gone severely wrong

### critical-corrected: semantic-trace-capture-stage

The inherited Llama/Mistral/Gemma projection-hook adapter captured q_proj/k_proj outputs before rotary/architecture-specific Q/K transforms, while the evaluator treated them as the vectors actually scored by attention.

**Correction:** Public claims now require post_model_qk_transforms, verified score inputs, and dense-reference parity. Raw projection captures remain diagnostic and are rejected by the preflight.

### critical-corrected: score-semantics-and-self-attested-parity

Even post-transform Q/K is insufficient unless replay also knows the model's exact score rule. The inherited contract omitted attention scaling and score bias/mask, and accepted dense-reference parity as a boolean plus claimed error instead of recomputing it.

**Correction:** Public qkv_npz_v2 bundles must carry explicit attention_scale, score_bias, a supported score_transform, and dense_reference_output. The gate recomputes softmax attention and rejects missing, unsupported, or forged references.

### high-corrected: mutable-provenance-accepted-as-immutable

The prior provenance gate required nonempty revision labels but could accept mutable branches or tags; tokenizer identity and trusted remote code were not enforced as immutable inputs.

**Correction:** Public claims now require immutable full model and tokenizer commit/content hashes, plus an immutable code revision when trusted remote code is enabled. The preflight exercises all three vetoes.

### high-corrected: head-dimension-cost-substitution

Imported Q/K/V traces were evaluated with a global D_HEAD=32 even when q.shape[-1] differed; the rev0075 fixture is D=12. This corrupted QK byte estimates at the exact cost-truth boundary the mission treats as decisive.

**Correction:** TraceRow carries d_head; Q/K/V derives it from q.shape[-1]; score-only bundles must supply it; the preflight proves D=12 is propagated.

### high-corrected-partially: green-check-semantic-gap

The inherited validators proved labels, hashes, shapes, and fail-closed claims, but not whether captured tensors and replay equations meant what the scientific claim said they meant.

**Correction:** rev0076 added tensor-stage, score-rule, recomputed-parity, and immutable-revision checks; rev0077 adds an executable synthetic post-transform contract harness proving exact post-transform replay and raw-projection failure. A real public model bundle and real HF architecture adapter remain missing.

### high-corrected: live-surface-multiple-truths

The source rev0075 package exposed rev0074 in README/START_HERE/reentry surfaces and mixed rev0071/rev0072/rev0074 fields in SURFACE-STATUS.json.

**Correction:** Critical entry surfaces are rewritten around one current revision contract and checked by this audit.

### high-partially-corrected: historical-runners-can-launder-current-revisions

The static scan found 63 legacy Python runners/reports that can inherit the live cube revision and write revision-derived artifact paths; 12 also pair that dynamic revision with a hard-coded historical timestamp. A rerun can therefore look current while carrying historical code and time semantics.

**Correction:** The three public-trace historical experiments and their three paired audits are pinned to their original revisions and marked frozen history (6/6 protected surfaces safe). The remaining legacy runners are enumerated by the current revision-lineage static audit and require staged migration rather than silent relabeling.

## What is missing

- real HF architecture-aware post-transform Q/K/V capture on an actual public pretrained model
- immutable public model/tokenizer/code/config provenance on an actual trace bundle
- multi-prompt, multi-position, multi-length real-model trace coverage rather than synthetic contract coverage
- GPU/fused sparse-kernel implementation and named-hardware end-to-end timing
- end-to-end task quality under the same model, prompts, and serving constraints
- controlled status/family taxonomy and typed ledger references
- revision budget/stop rule that prevents governance work from becoming the product
- explicit run-lineage contracts for legacy runners so historical code cannot inherit the current revision or overwrite retained evidence

## Waste and drift

- 643 of 660 questions remain open (97.4%).
- 324 source families classify 343 sources; the taxonomy is nearly one family per source.
- Idea and experiment-cell ledgers use 53 and 47 distinct status strings.
- The research registry contains 14 duplicated arXiv-ID groups.
- 3 historical JSON summaries disagree between the revision in their filename and the revision in their content; they are preserved as history and should be indexed as corrections rather than silently mutated.
- Compiled artifacts occupy 510,272 bytes across 7 files; exact duplicate recovery is only 1,302,683 bytes, so the larger footprint is mostly historical inputs/results rather than accidental copies.
- The lineage scan still finds 63 legacy artifact-minting hazards, including 12 dynamic-revision/hard-coded-time contradictions; six public-trace surfaces are now pinned.
- The dominant process waste is not storage; it is revision attention spent perfecting ingress governance around real public-model and hardware evidence that still does not exist.

## What should change

1. **Stop gate-only churn.** No more trace-governance revision without a demonstrated new defect. Require a real verified trace, verified adapter parity, or named-hardware result.
2. **Make semantic fidelity a first-class veto.** Capture post-transform Q/K/V, record exact scale/bias/transform semantics, recompute dense parity, pin model/tokenizer/code commits, and record config hashes.
3. **Measure systems, not proxies.** Keep the CPU/NumPy wind tunnel for falsification, but treat promotion as a named-hardware kernel and end-to-end task-quality decision.
4. **Compress the registries.** Normalize statuses/families, type references, merge duplicate questions/sources, and keep only a small funded frontier active.
5. **Adopt revision budgets.** Target 70% mechanism/kernel work, at most 20% audit/provenance, and at most 10% registry/docs unless a concrete integrity defect is found.
6. **Separate history from reruns.** Freeze historical runners to their original revisions. A genuine rerun must declare a new run revision, generate its execution time at runtime, hash code/dependencies, and write to a separate namespace.

## Current corrective result

The rev0077 post-transform contract covers 54 synthetic rows across 3 prompts, 9 positions, 3 layers, and 2 heads. Post-transform replay error is 0.0; raw projection Q/K fails against the same reference with max error 0.004210351652120303. The inherited preflight still passes 16 of 16 adversarial cases.

## Next hard stop

The next revision should not add another synthetic contract or policy layer. It should either (a) capture a real immutable public trace with an architecture-aware adapter, (b) run a sparse kernel on named hardware with end-to-end quality, or (c) explicitly stop this lane and redeploy the claim-compiler machinery to a different mechanism.
