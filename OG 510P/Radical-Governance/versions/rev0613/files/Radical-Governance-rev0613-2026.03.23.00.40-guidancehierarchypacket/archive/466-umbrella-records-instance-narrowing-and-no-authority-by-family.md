# 466 — Umbrella records, instance narrowing, and no authority by family

## One-line thesis

Family-level, program-level, supplier-level, or umbrella governance artifacts for consequential public AI should not be treated as authority-bearing for a specific deployment, workflow, or decision route until the archive narrows them to a named instance or explicitly states the residual gap.

## Why this matters

Consequential public-AI governance often starts with broad artifacts: a supplier model family notice, a ministry-wide policy, a reusable system-card template, a program-wide impact statement, or one central approval packet covering a whole class of tools. Those umbrella artifacts are useful. They reduce repetition, preserve shared facts, and help institutions govern common infrastructure once rather than many times.

But they also create a recurring overclaim problem. A broad record about one model family gets cited as if it fully describes a local deployment. A central transparency page gets treated as if it covers every workflow that reuses the underlying component. A family-level approval packet quietly becomes a local go-live basis even though the actual decision route, fallback path, training posture, or affected population differs. The archive already knows how to pin canonical heads, exact audiences, material-change refresh, and use-case-specific approval. What it still lacked was one note naming the specific hazard of **authority by family resemblance**.

The archive should therefore distinguish umbrella artifacts from instance-governing artifacts and require an explicit narrowing bridge before stronger local claims are made.

## Pattern pack

### 1. Name whether an artifact is umbrella-scoped or instance-scoped

Each consequential governance artifact should say whether it is primarily:

- family-scoped,
- platform-scoped,
- supplier-scoped,
- program-scoped,
- jurisdiction-scoped,
- deployment-scoped,
- workflow-scoped,
- or case-scoped.

The scope label should be visible enough that readers do not have to infer it from prose density or file location.

### 2. Require an explicit narrowing bridge from umbrella to instance

If a broad artifact is being used to support a narrower live deployment, the archive should preserve a compact narrowing bridge that states:

- which umbrella artifact is being inherited,
- which specific instance is being governed,
- which claims carry forward unchanged,
- which local facts must be added,
- which umbrella claims are blocked or overridden locally,
- and who accepted the narrowed posture.

Inheritance should be explicit, not atmospheric.

### 3. Keep shared facts and local divergences separate

A narrowing bridge should be able to say, for example:

- supplier identity comes from the family register,
- but the local retrieval corpus is different,
- the ministry-wide notice language is reused,
- but the local appeal route and fallback clocks are different,
- the family-level benchmark packet exists,
- but the local subgroup-risk review remains pending.

This keeps shared infrastructure from pretending to be shared governance in every respect.

### 4. Block instance-strength claims until instance-critical facts exist

Some facts can remain umbrella-level for a while. Others should not. The archive should not allow a local system to claim things like:

- fully current public notice,
- locally complete impact review,
- ready operator guidance,
- deployment-specific approval,
- or deployment-specific appeal sufficiency,

unless the missing instance-critical facts have actually been narrowed and recorded.

### 5. Preserve "family exists / instance not yet governed" as an honest state

The archive should support an explicit intermediate truth:

- a family artifact exists,
- a specific local instance is proposed or partially deployed,
- but the instance has not yet earned full local governance status.

That state is healthier than either pretending the umbrella record is enough or hiding the relationship entirely.

### 6. Let instance retirement and divergence break family inheritance cleanly

When a local deployment is retired, forked, materially changed, or moved to a different workflow, the narrowing bridge should reopen. The archive should preserve whether the instance is:

- still aligned with the umbrella artifact,
- locally diverged,
- retired while the umbrella family continues,
- or replaced by a sibling instance that needs a fresh narrowing pass.

Family continuity should not erase local history.

### 7. Preserve a citation path both upward and downward

A reviewer should be able to move:

- from the instance record up to the umbrella artifact for shared context,
- and from the umbrella artifact down to the governed instances that actually rely on it.

That path helps stop broad papers from becoming fake local evidence and local exceptions from disappearing inside broad summaries.

## Guardrails

- Do not let a family-level artifact quietly stand in for a deployment-specific record.
- Do not hide scope class in metadata that ordinary reviewers never see.
- Do not inherit local approval, notice, or appeal sufficiency merely because the underlying component family is already documented.
- Do not use umbrella language to blur real local divergence.
- Do not retire a local instance by simply deleting its narrowing bridge.

## Failure modes

- **authority by family resemblance**: a broad artifact is treated as if it fully governs a narrower live instance.
- **template-as-approval**: a reusable card or notice skeleton quietly becomes a release basis.
- **central-record overreach**: a ministry-wide or vendor-wide disclosure is mistaken for workflow-specific accountability.
- **local divergence burial**: the shared family story stays neat while instance-specific risks or exceptions disappear.
- **retired-instance ghosting**: an old local deployment seems current because the family artifact still looks live.

## Practical tests

An umbrella-honest governance regime passes when it can answer yes to all of the following:

1. Does each major artifact visibly declare whether it is umbrella-scoped or instance-scoped?
2. When a narrower deployment relies on a broader artifact, is there a reviewable narrowing bridge?
3. Are shared facts and local divergences kept separate rather than blended into one approval story?
4. Are instance-strength claims blocked until instance-critical facts actually exist?
5. Can a reviewer move from umbrella to instance and from instance back to umbrella without guesswork?

## Compression rule for the archive

If a broad record can say **this family exists** but cannot also say **which exact instance it governs, what was narrowed, and what still remains local**, then it is still letting **family resemblance impersonate authority**.
