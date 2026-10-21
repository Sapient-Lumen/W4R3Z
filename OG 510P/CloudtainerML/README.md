# CloudtainerML

## Find the experiment that can change the idea

CloudtainerML turns broad questions about model memory and inference into small experiments that can expose a tradeoff before expensive training or deployment. What should a compressed cache retain? When is checking a cheap approximation more costly than keeping the exact state? Can remembered information become worse than no memory when its correction is lost?

The collection joins executable probes, explicit baselines, result tables, research questions and later capture tooling. Its value is not a single promised acceleration. It is a workshop for deciding which idea deserves a harder experiment, which assumption carries a result, and when a negative result should change direction. The [early hunt questions](versions/rev0016/files/CloudtainerML-rev0016-2026.06.10.22.11-nativehpohardening-vericache-steprewrite-sablelynx/HUNT-QUESTIONS.md) are a useful entrance.

## Verification has a cost, and mistakes have different costs

The [lossy-cache guard probe](versions/rev0016/files/CloudtainerML-rev0016-2026.06.10.22.11-nativehpohardening-vericache-steprewrite-sablelynx/experiments/vericache_guard/vericache_guard_probe.cpp) models a sequence of decisions with varying margins, accumulating drift and specially marked critical sites. It compares never checking, periodic checking, margin- or drift-based guards, a combined guard and reference policies. Verification reduces the modeled error probability and drift while spending recomputation.

This makes a concrete design question inspectable: should a system spend its checking budget evenly, or where an error is especially likely or consequential? The [carried result](versions/rev0016/files/CloudtainerML-rev0016-2026.06.10.22.11-nativehpohardening-vericache-steprewrite-sablelynx/artifacts/probe-results/REV0016_VERICACHE_GUARD_SMOKE.json) does not offer an unconditional win. Across its 400 scenario/seed comparisons, the full-cache reference wins 237 utility contests when the oracle-labeled method is excluded; the combined guard wins 163. Better critical-site protection can coexist with considerable recomputation and imperfect overall accuracy.

The code is essential to interpreting that table. Its “full_kv” policy still has stochastic residual errors, and the utility function assigns explicit recomputation and full-cache penalties. These are modeled choices, not measurements of an actual transformer cache or wall-clock speed. The useful next question is whether a practical risk signal and measured costs preserve the tradeoff once those assumptions are replaced.

## A reasoning delimiter is not automatically a good memory boundary

The [step-boundary rewrite probe](versions/rev0016/files/CloudtainerML-rev0016-2026.06.10.22.11-nativehpohardening-vericache-steprewrite-sablelynx/experiments/periodic_cache_rewrite/step_rewrite_probe.cpp) constructs facts distributed across steps, a limited retention budget and later queries needing several facts. Policies favor recency, fixed periods, step boundaries, reconsolidation or oracle knowledge. An early premise needed much later and a strict multi-hop chain put different pressures on what should survive.

Its [result table](versions/rev0016/files/CloudtainerML-rev0016-2026.06.10.22.11-nativehpohardening-vericache-steprewrite-sablelynx/artifacts/probe-results/REV0016_PERIODIC_CACHE_REWRITE_SMOKE.json) is useful precisely because the attractive name does not win. Excluding the explicitly oracle-labeled policy, step-boundary rewriting wins only 14 of 480 scenario/seed contests, versus 113 for continuous eviction and 334 for attention reconsolidation; fixed-period rewriting takes the remaining 19. A step marker alone does not establish that the retained state contains the facts later use requires.

Even that comparison needs the implementation beside it. The reconsolidation policy consults the actual set of needed facts while generating its score, despite being included in the “nonoracle” tally. Its advantage therefore cannot establish that a deployable attention mechanism can identify those facts. The probe is a way to expose the value of information and design better tests, not a trained reasoning model discovering its own semantic boundaries.

## Remember the correction with the belief

The [memory-provenance sweep](versions/rev0016/files/CloudtainerML-rev0016-2026.06.10.22.11-nativehpohardening-vericache-steprewrite-sablelynx/experiments/memory_provenance_phase/memory_provenance_phase.cpp) varies mistaken-belief frequency, correction loss and high-stakes frequency. It compares isolated belief snippets, recency, provenance-aware policies, correction-linked memory and no persistent memory. The practical failure it makes visible is familiar: retaining an assertion while losing the reason it was corrected can make continuity preserve the wrong thing.

The [supplied output](versions/rev0016/files/CloudtainerML-rev0016-2026.06.10.22.11-nativehpohardening-vericache-steprewrite-sablelynx/artifacts/probe-results/REV0016_MEMORY_PROVENANCE_PHASE_SMOKE.json) favors correction-linked memory in 746 of 960 contests excluding the oracle-labeled policy. That is a result within a stipulated simulator: the linked policy is assigned a correction-loss rate of 0.35 times the ordinary rate. It is not empirical evidence that pairing records achieves that reduction in an agent.

The distinction does not empty the experiment of value. It identifies a dependency worth testing: how much correction retention must improve, under which error and abstention costs, before persistence is worth its risks? The simulator's “sycophancy” counter is also a defined proxy for an un-abstained wrong answer in a mistaken-belief trial, not an independent assessment of an actual model's motives or behavior.

## Keeping attention mass is not keeping the answer

The later [shared attention core](versions/rev0156/files/CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron/experiments/attention_compiler_core/attention_core.py) makes another question computationally concrete. Its histogram selector groups attention scores by distance below the maximum, accumulates probability mass to a target, and keeps the entire cutoff bucket. It avoids a full ordering while accepting that the last bucket may retain more than strictly necessary.

But a small omitted probability can multiply a very large value vector. Retaining 95% of attention mass is therefore not the same as preserving the resulting output. A value-norm metadata array supplies a different signal: the selector can add omitted tokens with large probability-times-norm contributions, updating a conservative absolute-error bound without reading value directions or the dense answer during selection. Output-quality evaluation remains a separate step.

The [retained CPU experiment](versions/rev0156/files/CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron/artifacts/probe-results/REV0050_VALUE_NORM_SIDECAR_CPU_PATH.json) deliberately constructs such large-norm tail values. Its mass-only histogram retains about 97.65% mean mass in that regime but fails the output-quality bar on every row; norm-aware exceptions restore that bar on all sampled rows. Yet this implementation is slower than its dense baseline even before metadata construction is added. Fewer value reads and better fidelity do not by themselves buy speed.

Read the [matching C++](versions/rev0156/files/CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron/experiments/value_norm_sidecar_cpu_path/value_norm_sidecar_cpu_path.cpp): the workload is synthetic single-row CPU attention, and the timed sparse path also computes dense probabilities for mass reporting. The result exposes a real tradeoff in this implementation, not a general limit on optimized sparse kernels or evidence of how often natural model traces contain those adversarial values.

## From synthetic questions to a real model trace

The later rev0156 narrows attention to a [TinyLlama public-trace path](versions/rev0156/files/CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron/README.md). Instead of letting another surrogate carry a larger claim, it specifies a sequence: reviewed model snapshot, local capture, evaluation, selector entry, replay, portable handoff and named-hardware timing. Each stage answers a different question. Identifying the loaded bytes is not measuring a kernel; a reproducible selection is not yet a useful speedup.

The [capture implementation](versions/rev0156/files/CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron/experiments/public_trace_capture/hf_attention_trace_capture.py) wraps Llama's eager attention operation after rotary position transformations. It records Q/K/V, the runtime mask and scale, query-to-KV-head grouping and the actual attention output, then compares a reconstruction against that output. Merely recording earlier projection outputs could preserve authentic tensors from the wrong computational stage. This is why trace identity needs semantic context as well as hashes.

The [ingest contract](versions/rev0156/files/CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron/docs/04-audit/rev0073-public-trace-e2e-ingest-contract.md) binds manifest information to metadata carried in the trace. This helps prevent local fixtures from being relabeled as public/pretrained evidence within the checked pipeline. Agreement between records is a consistency condition, not independent proof of everything asserted about the capture.

Rev0156's concrete changes address how that experiment can be attempted in a constrained environment: a bootstrap dry run stops after validation rather than demanding an environment it deliberately did not create; an optional local wheelhouse supports dependency installation without a public package index; a guard requires an explicit override for a cache setting the project identifies as risking large-file duplication. The [audit implementation](versions/rev0156/files/CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron/tools/public_trace_cache_duplication_guard_audit.py) makes those checks inspectable.

The [revision's mission audit](versions/rev0156/files/CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron/MISSION-AUDIT-REV0156.md) still records the missing complete verified snapshot and capture runtime on its construction host. This is an unfinished empirical step, not a new quality or speed result. The surrounding tooling matters insofar as it helps someone obtain the evidence that can change the research.

## Read for a decision, not just a winner label

Start with one of the three probes, read its scoring and information access, then compare its actual table. Ask which parts are generated assumptions, which are computed consequences and what observation could overturn the intended interpretation. Follow the later capture path when the next question requires a real model rather than another synthetic scenario.

Read beside [DelayBasin](../DelayBasin/README.md) for continuity as an experimental question, and [MissingKnowledgeHalf](../MissingKnowledgeHalf/README.md) for the value of failed attempts and negative results. These connections do not make their mechanisms interchangeable. CloudtainerML's distinctive contribution is the carried progression from an interesting idea to an explicit, contestable experimental decision.

## Snapshots and preservation

### Selected checkpoints

#### [rev0016](versions/rev0016/README.md)

An exploratory miniature-ML research cube covering transformer memory and cache experiments. The README highlights native C++ probes for lossy-cache guards, periodic cache rewrites and memory provenance, with Python orchestration. Historical reported runs and literature claims have not been reproduced for this publication.

#### [rev0156](versions/rev0156/README.md)

Focuses on the practical route to a digest-bound public-trace evidence packet: dry-run behavior, an optional local wheelhouse, and a cache-duplication guard. The archive distinguishes capture, evaluation, selector entry, replay, handoff and named-hardware timing. Its supplied commands are historical instructions, not actions performed for this archive.

### Reading and preservation notes

These are selected historical checkpoints, not a complete release history. New guides, inventories and integrity notes sit beside unchanged extracted files. Original ZIP names and bytes are preserved, including discrepancies and nested ZIPs. Wrapper layouts remain intact. No supplied program was executed and no external source claim was revalidated merely by copying the archive. Existing source-specific rights and licenses remain applicable; see the [current owner declaration](../../LEGAL-NOTICE.txt).

[Original identities and hashes](PROVENANCE.json) · [Collection index](../README.md)
