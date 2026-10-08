# 420 — Drift budgets, rollback paths, and decommission thresholds

## One-line thesis

Public automation should not merely be monitored; it should come with **predefined thresholds for rollback, deactivation, or retirement**. A system that drifts past its risk tolerance should face a governed response path, including fallback operation and, where necessary, decommissioning.

## Why this matters

Many public systems are good at noticing trouble and bad at deciding what happens next.

- teams can describe model drift but not the trigger for action,
- nobody knows when a workaround becomes a rollback,
- harmful systems linger because retirement feels operationally disruptive,
- fallback processes are improvised only after public damage has already accumulated.

Official guidance is again sharper than practice. NIST says organizations should establish continual monitoring, capture negative impacts, verify contingency processes to handle mission-critical harms and deactivate systems, and decommission systems that exceed risk tolerances. It also says systems may need to be superseded, disengaged, or deactivated when risks exceed thresholds or timely mitigation is not feasible, with redundant or backup systems minimizing disruption. The UK ATRS policy requires retired tools to remain visible, and OECD notes that governments still struggle with continuous monitoring and surfacing risks. The archive should therefore pair monitoring with explicit off-ramps.

## Design rule

Every consequential public automated system should have a **drift and response budget** that specifies:

- what kinds of degradation or harm matter,
- what thresholds trigger review, rollback, pause, or retirement,
- what fallback path keeps service continuity,
- who can authorize each action,
- how the public record changes when the status changes.

## Pattern pack

### 1. Define response thresholds before production, not during crisis

Do not wait for a controversy to invent the trigger conditions. Write down in advance what counts as enough trouble to justify:

- heightened monitoring,
- partial rollback,
- suspension of a workflow,
- full pause,
- permanent retirement.

### 2. Budget for drift, not infinite tolerance

No live system should be assumed to remain acceptable indefinitely. Set tolerances for:

- performance degradation,
- fairness or subgroup disparity,
- override and appeal rates,
- incident severity,
- dependency on unavailable staff workarounds,
- supplier or model-component instability where relevant.

### 3. Keep rollback and fallback as separate ideas

Rollback means moving to an earlier technical or operational version. Fallback means continuing the public service by another route, often manual or less automated. High-impact systems usually need both.

### 4. Practice the off-ramp before it is needed

A deactivation plan that has never been rehearsed is a comforting fiction. Operators should periodically test:

- whether the fallback path can absorb real workload,
- whether staff know the pause protocol,
- whether data and logs remain available for review,
- whether the public record can quickly reflect a status change.

### 5. Make decommissioning a governed end state

Retirement should be more than shutting off access. It should answer:

- what replaced the system, if anything,
- what historical outputs remain consequential,
- what records are retained,
- how external users are notified,
- what lessons or incidents drove the retirement.

### 6. Tie threshold breaches to ownership and clocks

Once a threshold is crossed, the next step should not depend on informal persuasion. The response path should name:

- who gets alerted,
- how quickly review must happen,
- who may order pause or rollback,
- what evidence is required to resume service.

### 7. Prefer graceful retreat over brittle commitment

Public legitimacy is strengthened, not weakened, when a system can be safely disengaged after evidence of harm. Resilience means the service survives the automation, not the other way around.

## Guardrails

- Define thresholds in advance and revisit them during reapproval.
- Keep service continuity plans realistic and staffed.
- Preserve logs and records needed for incident review and retirement decisions.
- Distinguish temporary pause from permanent retirement in public records.
- Do not let supplier dependency block deactivation when risk tolerance is breached.

## Failure modes

- **monitoring without consequences**: teams observe drift but never trigger action.
- **threshold vagueness**: nobody can say what level of harm is too much.
- **rollback confusion**: technical version reversal is mistaken for service continuity.
- **retirement invisibility**: tools disappear without preserving accountability.
- **continuity hostage-taking**: a system is kept alive because no fallback was maintained.

## Practical tests

A drift-response regime passes when it can answer yes to all of the following:

1. Are there written thresholds for pause, rollback, or retirement?
2. Is there a distinct fallback path that can keep the service running?
3. Have off-ramp procedures been rehearsed under plausible conditions?
4. Do threshold breaches trigger named owners and response clocks?
5. Does retirement remain visible in the public record rather than disappearing?

## Compression rule for the archive

When a public automated system is drifting, ask:

**What is the threshold for action, who can pull the system back or shut it off, and how does the service keep going afterward?**

If that answer is improvised, the system is more brittle than it looks.
