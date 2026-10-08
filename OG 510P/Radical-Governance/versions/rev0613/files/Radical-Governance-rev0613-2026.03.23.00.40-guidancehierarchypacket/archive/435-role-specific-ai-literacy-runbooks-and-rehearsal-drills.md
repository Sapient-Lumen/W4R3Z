# 435 — Role-specific AI literacy, runbooks, and rehearsal drills

## One-line thesis

AI literacy in public institutions should be role-specific and operational: staff need current runbooks, escalation paths, and rehearsal drills for the failures they are expected to catch, not just generic awareness that AI exists.

## Why this matters

Institutions often respond to AI governance pressure by commissioning a short training deck or a generic awareness module. That is better than silence, but it is not enough for consequential public use.

The real governance question is whether the people who touch the system know what to do when it behaves badly, when the workflow drifts, when sensitive data appears, when a public-facing answer is wrong, or when a case should leave the AI path entirely. Generic literacy does not answer that. Public services need **role-specific operational literacy**: operators, managers, approvers, security staff, legal reviewers, and communications teams each need different knowledge, different red flags, and different escalation moves.

Current official materials strongly support this shift. The AI Act’s literacy requirement is contextual: providers and deployers should ensure a sufficient level of AI literacy for staff and other people dealing with AI on their behalf, taking account of technical knowledge, experience, training, the context of use, and the people affected. The UK’s AI Cyber Security Code implementation guide says AI security training should be regularly reviewed and updated, include monitoring and escalation paths, and be tailored to the specific roles and responsibilities of staff. Cabinet Office guidance from The People Factor and the Mitigating Hidden AI Risks Toolkit adds the organisational layer: effective AI adoption depends on cultural and behavioural conditions, not only technical controls, and teams should design effective safety training, assign accountability for risk categories, and maintain regular risk-review and escalation routines. Ofsted’s policy paper grounds this inside a public body, stating that it scrutinises workforce training plans before approval and ensures staff use AI according to the approved use case.

The archive should therefore treat **runbooks and drills** as core governance artifacts. People do not become trustworthy overseers merely because they have heard a presentation about AI. They become trustworthy when they can recognise boundary conditions and act correctly under real operating pressure.

## Pattern pack

### 1. Define a role matrix for AI literacy

Each consequential system should identify the roles that need distinct training and runbooks, such as:

- frontline operators,
- supervisors and approvers,
- policy or legal reviewers,
- security and privacy teams,
- technical maintainers,
- communications staff,
- and senior owners.

Each role should know what they are expected to notice, decide, document, and escalate.

### 2. Give every role a short current runbook

A useful runbook should answer practical questions such as:

- what this system is approved for,
- what it must not be used for,
- what signs suggest it is outside its envelope,
- when to stop using the output,
- what data may not be entered,
- who to escalate to,
- what evidence to preserve,
- and what must be communicated to affected people or other teams.

If those answers live only in a long policy or an engineer’s head, they are not yet operational.

### 3. Teach people the likely failure modes in their own workflow

Training should include the actual failure modes relevant to the service, for example:

- hallucinated or stale source material,
- prompt injection or data leakage,
- unsupported language use,
- automation bias,
- inappropriate use in nuanced or disputed cases,
- inaccessible outputs,
- or attempts to reuse a tool outside its approved use case.

People learn safer behavior faster when the examples resemble the pressures they face in work.

### 4. Rehearse escalation, halt, and fallback decisions

Teams should periodically rehearse scenarios such as:

- a harmful answer reaches a user,
- a model starts producing a recurring error pattern,
- sensitive information is entered into the wrong tool,
- a public-facing system is found to be outside its approved scope,
- or a major override spike suggests the model has drifted.

Rehearsal should cover the exact escalation path, pause authority, fallback service route, and evidence-preservation steps.

### 5. Link access renewal to training currency and runbook acknowledgement

Where a tool is consequential or handles sensitive data, access should expire unless the user has:

- completed the role-specific training,
- acknowledged the current runbook,
- and, where relevant, participated in a recent drill or review exercise.

Expired understanding should be treated as a governance risk, not a clerical inconvenience.

### 6. Update runbooks whenever the real system changes

Runbooks should be refreshed when:

- the model or provider changes,
- a new data source is connected,
- public interaction is added,
- known limitations change,
- new no-go zones are discovered,
- or incident and override patterns reveal a new recurring risk.

Old runbooks are a quiet form of misinformation.

### 7. Treat near misses and drill findings as design input

Training is not the end of the loop. Institutions should record:

- what staff misunderstood,
- where escalation pathways were confusing,
- which examples were missing,
- where fallback routes were too slow,
- and what near misses or drills revealed about workflow design.

That evidence should update the runbook, the approval conditions, and the public description of the system where relevant.

## Guardrails

- Do not confuse one-off awareness training with operational readiness.
- Avoid role-neutral modules for role-specific risks.
- Keep runbooks short enough to use during work, but specific enough to guide real decisions.
- Rehearse halt and fallback moves, not only ordinary use.
- Make senior owners participate in drills rather than exempting them from operational learning.

## Failure modes

- **generic literacy theater**: staff receive a broad AI presentation but no workflow-specific guidance.
- **orphan runbook**: a runbook exists but is stale, buried, or unknown to the people who need it.
- **training decay**: users keep access long after the system or its risks have changed.
- **escalation improv**: staff know something is wrong but must invent the escalation path in the moment.
- **executive exemption**: leaders approve AI systems without ever rehearsing how they would pause, explain, or roll them back.

## Practical tests

An operational-literacy regime passes when it can answer yes to all of the following:

1. Is literacy defined separately for operators, owners, reviewers, and technical teams?
2. Does each role have a current short runbook covering approved uses, no-go zones, escalation, and evidence preservation?
3. Do training examples match the real workflow and its likely failure modes?
4. Are halt, fallback, and escalation paths rehearsed rather than merely documented?
5. Does access depend on current training and runbook acknowledgement?

## Compression rule for the archive

If staff must improvise how to question, stop, or route the system when it goes wrong, the institution is still **undertrained in practice**.
