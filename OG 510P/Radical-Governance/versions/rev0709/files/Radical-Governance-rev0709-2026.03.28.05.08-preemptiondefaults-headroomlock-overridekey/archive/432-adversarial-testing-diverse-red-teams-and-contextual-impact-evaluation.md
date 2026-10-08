# 432 — Adversarial testing, diverse red teams, and contextual impact evaluation

## One-line thesis

Before and during consequential public deployment, AI systems should face a plural evidence stack: adversarial testing, diverse red-teaming, baseline comparison, impact evaluation in context, and renewed evaluation whenever the intervention or setting materially changes.

## Why this matters

Too many public AI systems are justified by thin technical evidence: a benchmark score, a vendor demo, or a lab evaluation run far from the context where the system will actually shape public outcomes.

That is rarely enough. A system can perform well on internal tests while still producing harmful operational behavior, interacting badly with human workflows, shifting burdens across groups, undermining trust, or degrading when moved into a new service environment. Public governance therefore needs more than narrow model evaluation. It needs an evidence stack that joins technical stress testing with intervention-level evaluation.

Current official guidance strongly supports this. NIST’s Generative AI Profile says pre-deployment testing is a primary focus, calls for documenting assumptions and limitations, and recommends executing independent audit, AI red-teaming, impact assessments, or other structured human feedback exercises where appropriate. NIST also describes AI red-teaming as a controlled exercise to identify adverse behavior and stress-test safeguards, noting that demographically and interdisciplinarily diverse teams are better able to surface flaws across real contexts of use. The UK’s Model for Responsible Innovation operationalises this for public-sector teams through dedicated AI red-teaming workshops, tailored risk reports, and six-month follow-up. The UK’s 2025 guidance on impact evaluation of AI interventions adds the missing second half: think about evaluation as early as possible, define the baseline or business-as-usual clearly, design evaluation to be flexible for evolving systems, check for different impacts on different groups, and conduct further evaluation when a tool is applied in a new context or changed significantly.

The archive should therefore reject one-dimensional assurance. **A benchmark is not a deployment case.** The public deserves evidence that the system was stressed, compared, observed in context, and re-evaluated when the real intervention changes.

## Pattern pack

### 1. Separate model testing from intervention evaluation

A sound assurance stack distinguishes at least three layers:

- component or model testing,
- workflow and human-in-the-loop testing,
- impact evaluation of the public intervention as deployed.

These layers inform one another, but none can substitute for the others.

### 2. Define the baseline before live rollout

Teams should record what business-as-usual looks like before the AI intervention changes it. That includes:

- current workflow steps,
- current timelines,
- current error patterns,
- current disparities across groups,
- current user and staff burdens,
- and what the intervention is supposed to improve.

Without a baseline, post-launch claims about improvement or fairness are usually too soft to govern.

### 3. Run diverse adversarial and red-team exercises

Red-teaming should not be restricted to one security-style exercise by insiders. It should include combinations of:

- domain experts,
- frontline operators,
- people who resemble expected users,
- affected communities where appropriate,
- specialists in bias, safety, security, or accessibility,
- and cross-functional reviewers who understand the service context.

Different participants expose different failure surfaces.

### 4. Turn findings into deployment gates, not workshop residue

Red-team and evaluation results should feed an explicit decision:

- fix before launch,
- restrict scope,
- add human verification,
- delay release,
- publish stronger warnings,
- or reject the intervention.

Findings that do not change approval or operating conditions are too easy to ignore.

### 5. Evaluate impacts for different groups and settings

A public intervention should not be judged only by average performance. Evaluation plans should ask:

- who benefits,
- who is burdened,
- where performance differs,
- whether public attitudes or trust shift,
- whether accessibility or language differences change outcomes,
- and whether the intervention behaves differently across offices, regions, or service channels.

This makes evaluation more aligned with actual public-service risk.

### 6. Re-evaluate when the context or intervention changes materially

Further evaluation should be triggered when:

- the system is moved into a new domain,
- the user population changes,
- the model or provider changes,
- a new language path is added,
- automation depth changes,
- or the surrounding workflow changes enough to alter the system’s real effects.

A system proven in one setting is not automatically proven in another.

### 7. Publish a compact assurance summary with unresolved risks

For consequential systems, publish a compact summary that states:

- what testing was done,
- what groups were involved,
- what baseline was used,
- what major limitations remain,
- what mitigations were adopted,
- and what evidence is still incomplete.

The goal is not to dump raw notebooks onto the public. The goal is to make the evidence case inspectable.

## Guardrails

- Do not confuse benchmark success with operational readiness.
- Avoid red-team exercises made up only of insiders who share the same assumptions.
- Keep unresolved limitations visible in approval and public records.
- Tie evaluation cadence to the speed of system change.
- Distinguish “no evidence of harm found” from “evidence that the intervention is safe and effective in context”.

## Failure modes

- **benchmark theater**: a public deployment is justified mostly by model scores detached from service reality.
- **monoculture red team**: one narrow expert group exercises the system and misses lived-context failures.
- **baseline void**: the team cannot say what the AI intervention improved relative to prior practice.
- **evaluation freeze**: the system changes rapidly while the evidence case remains tied to an older version or context.
- **findings without force**: serious issues are documented but do not affect go-live, scope, or operating rules.

## Practical tests

An evaluation regime passes when it can answer yes to all of the following:

1. Are technical testing, workflow testing, and intervention impact evaluation explicitly separated?
2. Was the pre-AI baseline documented before rollout?
3. Did red-team or adversarial testing include diverse perspectives relevant to the real context of use?
4. Do findings change launch, scope, safeguards, or warning conditions?
5. Is further evaluation required when the tool or deployment context changes materially?

## Compression rule for the archive

If the institution can show that a model works but not that the intervention works **here, for these people, under these conditions**, it still lacks a real deployment case.

