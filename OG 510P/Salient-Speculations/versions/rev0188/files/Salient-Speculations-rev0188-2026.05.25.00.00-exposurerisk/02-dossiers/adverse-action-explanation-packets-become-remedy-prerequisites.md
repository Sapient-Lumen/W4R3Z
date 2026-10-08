---
id: ss-0185-adverse_action_explanation_packets_become_remedy_prerequisit
revision_promoted: rev0185
title: Adverse-action explanation packets become remedy prerequisites
constellation:
- managed-legibility
- administrative-repair
- market-and-state-capacity
status: dossier
maturity: S2-artifact-emerging
confidence: medium-high
time_horizon: near
domain:
- AI / model governance / automated decisions
- credit / financial services
- platform moderation / content governance
- public benefits / eligibility
bottleneck_type:
- appealability / redress
- explanation sufficiency
- decision traceability
- admissible evidence
enforcement_surface:
- consumer credit compliance
- AI Act deployer obligation
- platform governance
- public-service eligibility
artifact_type:
- statement of reasons
- explanation packet
- decision trace
- contestability notice
lifecycle_stage:
- decision
- notice
- explain
- intake
- review
failure_modes:
- empty-explanation
- wrong-factor-disclosure
- automation-bias
- noncontestable-notice
- trade-secret-overclaim
refactor_cluster:
- remedy-lifecycle
remedy_role: explanation sufficiency and contestability packet
remedy_stage:
- decision
- notice
- explain
- intake
- review
consolidation_status: standalone-mechanism
state_family:
- remedy
source_refs:
- S1542
- S1547
- S1548
- S1549
- S1550
- S1551
---
# Adverse-action explanation packets become remedy prerequisites

## Core claim

A person cannot meaningfully appeal a decision they cannot understand. As automated, scored, brokered, moderated, and delegated decisions spread, the decisive object will not be a generic explanation. It will be a structured **adverse-action explanation packet**: the reasons, factors, input records, model or ruleset role, reviewer status, appeal path, clock start, evidence route, and minimum contestable fields that let a remedy proceed.

The speculative claim: **adverse-action explanation packets become remedy prerequisites**. Explanation will stop being a prose courtesy and become a gated evidence package. If the packet is incomplete, the appeal clock may not start, the denial may be non-final, the user may get a stronger stay, or the institution may fail audit.

## Why this belongs in the cube

The cube has many proof objects that enable reliance: validation reports, product passports, authority logs, compliance packets, source snapshots, and state labels. It has fewer proof objects that enable **challenge**. This dossier says the challenge-enabling object is becoming its own infrastructure.

The signals cut across domains. The DSA gives users routes to contest platform moderation decisions and requires reasoned decision practices around restrictions [S1542, S1552]. Credit rules require adverse-action notices with specific reasons rather than vague score references [S1547]. The EU AI Act timeline brings high-risk AI obligations into force in stages, while Article 86 creates a right to clear and meaningful explanations of certain individual decision-making using high-risk AI systems [S1548, S1551]. Article 85 separately adds a complaint path to market-surveillance authorities for alleged AI Act infringements [S1550].

The archive should treat these not as isolated rights, but as one mechanism family: the decision must produce enough structured explanation for the affected party, reviewer, regulator, auditor, or counterparty to know what can be contested.

## Minimum viable packet

A mature adverse-action explanation packet would include:

1. decision identifier and finality status;
2. affected subject and scope;
3. decision authority, including whether a human, model, policy rule, vendor feed, or delegated agent contributed;
4. decisive factors, ranked or grouped by materiality;
5. input-record references sufficient to challenge errors;
6. policy threshold or rule class applied;
7. human-review status and reviewer authority;
8. available remedy forums;
9. clock start and filing deadline;
10. evidence needed to contest each factor;
11. restrictions on disclosure and a path to request more information;
12. whether continued reliance is stayed, restricted, or allowed while contested.

This is not a demand that every decision disclose trade secrets or every model expose internals. It is a claim that contestability requires a standard sufficiency layer.

## Speculative consequences

### 1. Explanation sufficiency becomes auditable

Auditors, regulators, and dispute bodies will ask whether explanations were sufficiently specific, timely, and tied to actual decision factors. Vague notices will become procedural defects even when the underlying decision may be substantively defensible.

### 2. Explanation packets become reusable across forums

The same packet may support an internal appeal, external dispute settlement, regulator complaint, insurance claim, procurement protest, litigation hold, or civil-rights review. Firms will build packet-generation systems because manual prose cannot scale.

### 3. Trade-secret boundaries become a recurring fight

Institutions will claim confidentiality over model features, vendor scores, policy rules, fraud signals, safety thresholds, or security controls. Remedy systems will need redacted packets, neutral-review access, sealed exhibits, and sufficiency certifications.

### 4. Human review becomes packet-dependent

A human reviewer without the packet is not meaningful review. The packet decides whether the reviewer can see the right source records, override the output, request vendor evidence, or restore access.

## Abuse and capture

Explanation packets can be performative. They can list too many factors, cite irrelevant model features, hide behind generic policy labels, start clocks before the user has usable information, or over-disclose sensitive data to pressure abandonment. They can also be reverse-engineered by bad actors to evade fraud systems.

The governance challenge is sufficiency without total transparency: enough explanation to contest, not enough to expose unrelated people, security controls, or trade secrets.

## Falsifiers

This thesis weakens if courts and regulators accept generic adverse-action language, if users rarely appeal, or if firms can satisfy explanation duties with static policy pages. It strengthens if regulators, auditors, procurement templates, or dispute bodies begin rejecting explanations as procedurally insufficient even apart from merits.
