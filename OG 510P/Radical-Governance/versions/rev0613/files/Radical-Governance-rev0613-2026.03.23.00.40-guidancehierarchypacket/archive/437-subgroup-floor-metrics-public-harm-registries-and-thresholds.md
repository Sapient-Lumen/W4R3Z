# 437 — Subgroup floor metrics, public harm registries, and thresholds

## One-line thesis

Public AI systems should not pass on aggregate accuracy alone: they need **subgroup floor metrics**, visible harm registries, and predefined thresholds that trigger mitigation, fallback, or suspension when particular groups are carrying disproportionate risk.

## Why this matters

Institutions often defend a system by showing one overall performance number. But public harm is rarely distributed evenly. A system can look “good on average” while failing badly for a smaller community, a disability group, a language minority, or people whose cases differ from the training-data norm.

Current official materials support moving beyond averages. NIST’s AI RMF says measurement approaches can fail when they do not account for differences in affected groups and contexts, and that harms may affect varied groups or sub-groups differently. The UK’s ATRS guidance says public bodies should describe any bias and fairness evaluation they have undertaken, including model performance over subgroups within the dataset, and should explain measures taken to address issues identified. Accessibility Standards Canada’s 2025 AI standard goes further still: organisations should conduct ongoing monitoring and impact assessment to identify bias or discrimination toward people with disabilities, maintain a public registry of harms, contested decisions, barriers to access, and inequitable treatment related to AI systems, and establish thresholds for unacceptable levels of risk and harm with disability organisations and domain experts.

The archive should therefore reinforce a stricter rule: consequential public AI should be judged by the **floor**, not only the average. Governance fails when the worst-served group is hidden inside an acceptable mean.

## Pattern pack

### 1. Define minimum subgroup floors before deployment

Before consequential live use, the institution should set explicit minimum acceptable performance and harm thresholds for relevant groups, such as:

- disability-related user groups,
- official-language groups,
- demographic groups where lawful and appropriate measurement is possible,
- outlier case types that differ materially from the training distribution,
- and people routed through accessibility or assisted channels.

These floors should be defined before launch so that they are not moved after poor results appear.

### 2. Pair model metrics with service metrics

Subgroup governance should track more than technical quality. Each relevant group should be assessed on:

- answer or recommendation quality,
- error severity,
- contest or complaint rates,
- override rates,
- completion or abandonment rates,
- time to human help,
- and downstream adverse effects.

A group can be poorly served even when the model looks technically “accurate.”

### 3. Publish a harm registry that shows who is getting hurt

A public-facing registry need not expose personal information, but it should show, in accessible form:

- categories of harm or barrier reports,
- contested-decision counts,
- accessibility failures,
- open investigations,
- mitigation status,
- and where relevant, which kinds of users or service routes were disproportionately affected.

This makes cumulative harm visible before it becomes scandal or litigation.

### 4. Treat missing subgroup evidence as a release blocker

If a group is too small, too hard to measure, or poorly represented in the test data, that is not proof of safety. It is a reason to narrow scope, add fallbacks, or avoid deployment in that context.

“No evidence of differential harm” is not persuasive when the system was never tested in a way that could have found it.

### 5. Include outliers and edge populations in evaluation design

Teams should explicitly test people and cases that are far from the statistical average, including:

- atypical combinations of traits or circumstances,
- users who rely on assistive technologies,
- people using different languages or translation layers,
- and users whose cases involve rare but high-stakes exceptions.

Public institutions should assume that the hardest cases are often the most governance-relevant.

### 6. Predefine what happens when a subgroup floor is missed

Every subgroup floor should be linked to a concrete response, such as:

- warning labels or tighter use limitations,
- additional human review,
- routing that group to an alternative path,
- narrower deployment scope,
- retraining or redesign,
- or full pause and rollback.

A threshold without a reaction plan is only measurement theater.

### 7. Revisit subgroup floors during live operation

Subgroup performance should be re-measured after:

- model or prompt changes,
- new data sources,
- policy or service-design changes,
- increased scale,
- or shifts in who is using the system.

The floor can deteriorate long after launch.

## Guardrails

- Do not let a single aggregate score stand in for public safety.
- Combine technical fairness checks with lived-service evidence.
- Avoid assuming that unmeasured groups are unaffected groups.
- Make public harm reporting accessible and continuous.
- Tie thresholds to actual operational consequences.

## Failure modes

- **average-score camouflage**: a strong overall metric hides serious underperformance for a subgroup.
- **thin-sample complacency**: a group is declared low risk only because there was not enough evidence gathered to see the harm.
- **registry without action**: harms are recorded but no thresholds or mitigation pathways are tied to them.
- **edge-case abandonment**: people furthest from the training norm are told the system is not intended for them only after harm occurs.
- **fairness reset by upgrade**: a model, prompt, or workflow change silently invalidates earlier subgroup testing.

## Practical tests

A subgroup-governance regime passes when it can answer yes to all of the following:

1. Have minimum subgroup floors and unacceptable-harm thresholds been defined before deployment?
2. Are both model-level and service-level outcomes tracked for relevant groups?
3. Is there an accessible public registry of harms, contested decisions, or barriers related to the system?
4. Does missing evidence about a group block or narrow deployment rather than count as reassurance?
5. Are thresholds linked to explicit mitigation, fallback, or suspension actions?

## Compression rule for the archive

If the system is only safe on average, then it is still **unsafe for governance**.
