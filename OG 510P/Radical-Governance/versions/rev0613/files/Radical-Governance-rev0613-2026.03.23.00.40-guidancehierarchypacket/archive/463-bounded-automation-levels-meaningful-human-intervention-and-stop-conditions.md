# 463 — Bounded automation levels, meaningful human intervention, and stop conditions

## One-line thesis

Consequential public-AI systems should declare bounded automation levels for each governed workflow, name where meaningful human intervention can still occur, and make stop conditions and escalation rights explicit, so “human in the loop” does not hide who can actually interrupt, overrule, or approve what.

## Why this matters

Public bodies often say a system has human oversight without specifying what that means operationally.

A human may see a recommendation but have no time to review it. An operator may be able to pause a queue but not stop a model route. A manager may approve launch but not a later autonomy increase. A reviewer may be nominally in the loop while the workflow, backlog, or interface makes rubber-stamping the default. In other settings, instant responses may be appropriate, but only if meaningful human control exists at earlier or later stages.

The archive already covers sign-off, fallback review, approved use cases, monitoring, and contestability. What it still lacked was one direct grammar for the **level of automation itself**. Without that grammar, institutions drift into autonomy theater: a workflow grows more self-acting while the archive keeps repeating the same vague phrase about human oversight. The archive should therefore require bounded automation levels, named intervention points, and explicit stop rights.

## Pattern pack

### 1. Declare automation level per workflow step, not only per system

A consequential system should not be described only as “decision support,” “human reviewed,” or “automated.” It should declare, for each material step, whether the system:

- drafts or suggests,
- ranks or prioritizes,
- recommends a single path,
- executes only after human confirmation,
- executes by default with sampled or thresholded human review,
- or executes autonomously with only later oversight.

A service can occupy more than one level across one end-to-end workflow. The archive should preserve that detail.

### 2. Name the human intervention point and its real authority

If human involvement exists, the archive should specify:

- who may intervene,
- at what stage,
- using what information,
- with authority to do what,
- under what time constraints,
- and whether that intervention can actually change the outcome.

Seeing the output is not the same as having meaningful authority over it.

### 3. Distinguish pre-action, in-action, and post-action control

Human control can exist at different moments:

- before action, through approval, configuration, or scope gating,
- during action, through confirmation, pause, or step-up review,
- after action, through monitoring, override, appeal, correction, or rollback.

The archive should not let strong post-action remedy be described as if it were strong pre-action control, or vice versa.

### 4. Require additional basis when human review is claimed

A claimed human review point should say what the human can see beyond the bare AI output, such as:

- source material,
- confidence or abstention state,
- policy or rule basis,
- prior case history,
- alternatives or fallback routes,
- and grounds for departure.

A human cannot supply meaningful review if the workflow withholds the basis needed to disagree.

### 5. Make autonomy increases first-class governance changes

A workflow should reopen review when it changes from one automation level to another, including shifts such as:

- suggestion to recommendation,
- required confirmation to default execution,
- full review to thresholded sampling,
- or operator-triggered use to background autonomous action.

Autonomy drift is a material change even when the model family stays the same.

### 6. Keep stop conditions and escalation rights visible

Every consequential automation level should carry visible answers to:

- who can halt the workflow,
- what triggers an automatic stop,
- what triggers mandatory human takeover,
- what happens to queued work,
- and what fallback path keeps the service running.

A system with no credible stop path is governed only until the first real emergency.

### 7. Reflect automation level in notices, dossiers, training, and logs

The current automation level should be consistent across:

- public notices and system cards,
- impact dossiers and approvals,
- operator runbooks and drills,
- event logs and case packets,
- and monitoring or incident surfaces.

If the public record says “assisted” while the runtime path is effectively autonomous, the archive is already stale in a load-bearing way.

## Guardrails

- Do not use “human oversight” as a blanket phrase without naming the intervention point and its authority.
- Do not treat observation alone as meaningful review.
- Do not let post-hoc appeals masquerade as pre-action control.
- Do not increase autonomy without reopening approval and public record refresh.
- Do not leave stop conditions, fallback paths, or takeover rights implicit.

## Failure modes

- **human-in-the-loop theater**: a person is present in name but cannot meaningfully change the outcome.
- **mode creep**: a workflow quietly shifts toward greater autonomy while the archive keeps the old description.
- **review without basis**: staff are asked to validate outputs without the evidence needed to disagree.
- **backlog autopilot**: nominal review remains on paper, but service pressure makes automation effectively self-executing.
- **stop-right illusion**: teams discover during an incident that no one can actually pause or divert the live path.

## Practical tests

An automation-level-honest regime passes when it can answer yes to all of the following:

1. Are automation levels declared per consequential workflow step rather than in one fuzzy system-wide label?
2. Does every claimed human intervention point name who can act, when, and with what authority?
3. Is pre-action control kept distinct from post-action remedy and monitoring?
4. Do human review points include enough basis to support meaningful disagreement?
5. Will any material increase in autonomy reopen approval, disclosure, and training?

## Compression rule for the archive

If a system says it has **human oversight** but cannot also say **which stage, which actor, which authority, and which stop path**, then it is still letting **oversight language impersonate control**.
