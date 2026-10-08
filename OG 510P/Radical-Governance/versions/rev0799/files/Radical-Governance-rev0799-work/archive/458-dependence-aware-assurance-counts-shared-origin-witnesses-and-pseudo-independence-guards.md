# 458 — Dependence-aware assurance counts, shared-origin witnesses, and pseudo-independence guards

## One-line thesis

Public-AI assurance should record shared origins across tests, judges, vendors, datasets, prompts, and reviewers so multiple agreeing checks are not mistaken for multiple independent grounds for trust.

## Why this matters

Consequential public-AI teams increasingly assemble reassuring evidence stacks: benchmark results, supplier reports, internal evaluations, external red-team findings, model-judge outputs, peer reviews, second-look samples, conformance results, incident-free periods, and public feedback summaries. That plurality is often good. But it is also easy to misread.

Three green checks do not mean three independent reasons for confidence if they were produced by the same supplier family, the same base model line, the same prompt scaffold, the same dataset distribution, the same evaluator, or the same organizational interest. Apparent plurality can conceal one monoculture. Agreement can be real and still not add much new information.

The archive already values independent challenge, diverse red teams, and contextual evaluation. What it still lacked was one explicit rule for **dependence-aware assurance counting**. Without that rule, a dossier can become numerically busy while epistemically thin. The archive should therefore force evidence stacks to declare which parts are meaningfully independent, which are coupled, and what weight they should honestly carry.

## Pattern pack

### 1. Preserve shared-origin facts for each assurance line

For each major assurance input, record relevant shared-origin properties such as:

- supplier or provider family,
- evaluator or review team,
- model lineage,
- prompt or rubric family,
- dataset family,
- runtime or deployment context,
- contracting relationship,
- and whether the evidence was internally generated, supplier-generated, independently generated, or mixed.

The archive should not count evidence as separate merely because it arrived in separate files.

### 2. Separate evidence count from evidence diversity

A useful dossier may report both:

- how many checks were performed, and
- how many materially distinct evidence families those checks represent.

Five evaluations may still amount to one evidence family if they share the same origin and blind spots. The archive should make diversity visible instead of letting raw count impersonate robustness.

### 3. Mark pseudo-independent agreement explicitly

Where evidence lines are coupled, the record should say so. Useful formulations include:

- these reviews used the same base model or shared provider family,
- these tests reuse substantially the same benchmark or sampling frame,
- these judge outputs are separate runs of one rubric family rather than distinct evaluators,
- these red-team findings are independent in personnel but not in environment,
- or these supplier and internal results both depend on the same underlying telemetry source.

The goal is not to reject coupled evidence. It is to stop coupled evidence from pretending to be independent corroboration.

### 4. Require at least one differently situated challenge lane where stakes justify it

For high-impact deployments, significant waivers, or disputed safety claims, the assurance stack should usually include at least one challenge lane that is meaningfully different from the dominant evidence family. That difference may be in:

- assessor independence,
- deployment environment,
- evaluation method,
- population sample,
- or institutional incentive position.

Otherwise the archive risks certifying a system by repeated self-echo.

### 5. Discount judge agreement when judges share blind spots

When AI or rubric-driven judges are used, the archive should not equate agreement with truth unless the evidence also addresses shared failure modes. Agreement among coupled judges may still be useful for triage or throughput. It should not automatically be treated as strong assurance of correctness.

### 6. Carry dependence notes into public summaries and signoff packets

Where an institution publishes a compact assurance summary or relies on an evidence stack for signoff, it should preserve the main dependence story in plain language. Reviewers should be able to see whether the case rests on:

- plural independent evidence,
- plural but coupled evidence,
- or mostly one dominant supplier or evaluator family.

### 7. Reopen the case when the evidence stack collapses to one family

If substitutions, budget limits, incidents, or review shortcuts leave the assurance case dependent on one family of tests or one provider's own evidence, the archive should reopen that assurance posture rather than silently carrying forward the old confidence story.

## Guardrails

- Do not equate repeated agreement with independent corroboration.
- Do not count supplier self-evaluation and near-clone internal replay as two distinct assurance lines unless the dependence is explicit.
- Do not let one benchmark family stand in for broad contextual evaluation.
- Do not hide judge monoculture behind plurality language.
- Do not treat a crowded evidence table as stronger than a sparse but genuinely diverse one.

## Failure modes

- **pseudo-independent comfort**: multiple agreeing checks create false assurance because they share one origin.
- **benchmark echo**: repeated success on one family of tests is retold as broad readiness.
- **judge monoculture**: several judging passes share the same rubric or model blind spots.
- **same-supplier double credit**: vendor evidence and derivative internal summaries are counted as separate corroboration.
- **plurality theater**: the dossier looks thick while its evidence diversity is thin.

## Practical tests

A dependence-aware-assurance discipline passes when it can answer yes to all of the following:

1. Does each major assurance line record relevant shared-origin facts?
2. Can reviewers distinguish evidence count from evidence diversity?
3. Are coupled or pseudo-independent lines explicitly marked rather than silently aggregated?
4. Is there at least one differently situated challenge lane where the stakes justify it?
5. Do signoff packets and public assurance summaries preserve the main dependence story honestly?

## Compression rule for the archive

If a dossier cannot answer **which assurances are genuinely distinct and which are one family repeating itself**, then it is still mistaking **agreement** for **independent evidence**.
