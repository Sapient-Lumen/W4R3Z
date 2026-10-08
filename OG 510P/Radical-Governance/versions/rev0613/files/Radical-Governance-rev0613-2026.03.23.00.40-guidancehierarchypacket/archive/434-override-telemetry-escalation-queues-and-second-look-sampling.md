# 434 — Override telemetry, escalation queues, and second-look sampling

## One-line thesis

Human oversight is not real unless overrides, disagreements, and stop decisions are counted, reviewed, and turned into operating changes instead of disappearing as private friction.

## Why this matters

Public institutions often claim that AI is “only advisory” or that “a human remains in the loop.” That claim is weaker than it sounds if nobody measures what the human actually does with the output.

An oversight regime that cannot say how often staff accept, modify, reject, or stop AI output is mostly ceremonial. It may satisfy a procurement checklist while still allowing automation bias, silent rubber-stamping, or unobserved drift in operator behavior. Over time, the absence of telemetry makes it impossible to tell whether the machine is genuinely supporting judgment or whether the human role has become a thin ritual around default acceptance.

Current official materials point toward a more instrumented model. The AI Act’s human-oversight provisions require natural persons to remain aware of automation bias, to decide in a particular situation not to use a high-risk system or to disregard, override, or reverse its output, and to intervene or interrupt the system through a stop mechanism. NIST’s AI RMF Playbook makes the operational implication explicit: organisations should measure the frequency of override decisions, evaluate and document results, and feed insights back into continual improvement. NIST’s Generative AI Profile adds that overrides should be monitored and documented, and that structured human feedback should be verified as part of design, deployment approval, monitoring, and decommission decisions, including analyses of recourse mechanisms across subgroups.

The archive should therefore treat **override telemetry** as a first-class governance signal. Disagreement with the model is not operational noise. It is evidence about the real boundary between acceptable assistance and unsafe delegation.

## Pattern pack

### 1. Record the operator’s disposition, not just the model output

For consequential uses, systems should record whether the human operator:

- accepted the output as-is,
- accepted it with edits,
- rejected it,
- escalated it,
- or stopped the system path entirely.

A raw log of model outputs without a log of what the operator actually did is incomplete evidence.

### 2. Measure override patterns by context, not only in the aggregate

Override telemetry should be broken down by factors such as:

- office or service channel,
- model or provider version,
- user role,
- language path,
- case type,
- data condition,
- and whether the case was routine or unusual.

An average override rate can conceal a serious problem in one subgroup or one operating context.

### 3. Create escalation queues for override spikes and anomaly clusters

Institutions should define triggers that route cases into review when there are:

- sudden spikes in overrides,
- repeated operator corrections of the same error class,
- rising disagreement between junior and senior reviewers,
- stop-button events,
- or a divergence between user complaints and internal acceptance patterns.

The point is to make disagreement actionable before it becomes a scandal.

### 4. Sample accepted outputs for second-look review

Human oversight should not examine only the cases where operators noticed something wrong. It should also sample cases where the output was accepted and run a second-look review to detect:

- rubber-stamping,
- subtle reasoning defects,
- group-specific problems,
- overreliance in high-volume workflows,
- and unreported operator discomfort.

Accepted outputs can be more revealing than rejected ones because they show where the institution may be normalising machine suggestions too easily.

### 5. Connect override evidence to launch, scope, and rollback decisions

Override telemetry should change governance outcomes. Depending on what it shows, the institution may need to:

- narrow the use case,
- add stronger human verification,
- publish stronger warnings,
- pause a language or region,
- retrain staff,
- retrain or replace the model,
- or roll the system back.

If override patterns do not affect operating conditions, the measurement becomes decorative.

### 6. Preserve and classify stop events

Any stop-button event, safe-halt invocation, or emergency manual bypass should be preserved as a special record with:

- case context,
- triggering condition,
- operator notes,
- follow-up disposition,
- and whether the event implies a wider system risk.

These are governance events, not merely technical exceptions.

### 7. Use disagreement to improve recourse and public explanation

Override and escalation patterns should feed back into:

- explanation templates,
- appeal packet design,
- known-limits sections in the system card,
- operator runbooks,
- and public complaint routing.

The institution should learn from where its own staff distrust the system.

## Guardrails

- Do not treat low override rates as automatically good; they may signal overreliance or poor operator confidence.
- Avoid using override statistics to punish operators for cautious behavior.
- Separate quality learning from individual blame unless there is clear misuse.
- Keep stop mechanisms usable under real workload conditions, not only in theory.
- Analyse disagreement across subgroups and service contexts, not just global totals.

## Failure modes

- **ceremonial oversight**: humans are nominally present but their agreement or disagreement is never measured.
- **override blind spot**: the institution logs outputs but not human response to them.
- **acceptance bias**: only rejected cases are reviewed, leaving rubber-stamped errors invisible.
- **telemetry without force**: override data is collected but never changes launch, scope, or safeguards.
- **stop without memory**: emergency halts happen, but the institution does not preserve or learn from them.

## Practical tests

An oversight regime passes when it can answer yes to all of the following:

1. Can the institution show how often operators accept, edit, reject, escalate, or stop the AI path?
2. Are override patterns reviewed by context, subgroup, and workflow rather than only in the aggregate?
3. Is there a defined queue for spikes, clusters, or unusual disagreement?
4. Are some accepted outputs sampled for second-look review?
5. Do override patterns change approval, scope, or rollback conditions?

## Compression rule for the archive

If human oversight cannot count its own disagreement with the machine, it is still mostly **ceremonial oversight**.
