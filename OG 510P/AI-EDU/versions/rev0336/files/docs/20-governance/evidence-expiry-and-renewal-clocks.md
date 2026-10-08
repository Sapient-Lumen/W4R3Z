# Evidence-expiry and renewal clocks

Evidence does not stay fresh forever. A service can keep operating only if its public claims,
internal ceilings, and renewal packet still match the model, workflow, population, policy, owner,
security posture, and educational construct that were actually tested.

This surface adds expiry clocks to the claim-family matrix.

## Expiry states

| State | Meaning | Public claim posture |
|---|---|---|
| `FRESH` | evidence still matches the tested context | claim may remain, with grade and limits |
| `WATCH` | evidence is near expiry or drift is accumulating | claim may remain only with renewal scheduled |
| `STALE` | context has drifted or the clock has expired | claim must be narrowed or marked unproven |
| `EXPIRED` | material change or expiry makes the claim misleading | remove claim, re-pilot, or retire the use |

`STALE` does not mean the service is dangerous. It means the public story is no longer entitled to
sound confident.

## Default renewal clocks by claim family

| Claim family | Default clock | Early-expiry trigger |
|---|---|---|
| `CL-TASK` | each term, semester, or major service cycle | workflow, interface, user group, or task changes materially |
| `CL-LEARN` | each cohort / course cycle, and before scale | construct, age band, modality, model, prompt, or support pattern changes |
| `CL-ACCESS` | each access cycle or term | subgroup gap, protected-route change, device/connectivity shift, or chilling report |
| `CL-WORKLOAD` | each staffing or course cycle | review burden, support burden, incident burden, or queue burden shifts |
| `CL-VALIDITY` | before each assessment cycle | construct, rubric, proof bundle, disclosure rule, or AI-permission grammar changes |
| `CL-SAFETY` | continuous incident watch plus scheduled renewal | wellbeing incident, dependency signal, bias report, disciplinary spillover, or minor-facing change |
| `CL-SECURITY` | before launch, after material change, and at least each service cycle | prompt-injection exposure, tool permission, retrieval corpus, output channel, or vendor change |
| `CL-CONTEST` | each publication / high-stakes service cycle | users cannot find, use, or receive timely remedy through the route |
| `CL-COMPLIANCE` | on policy, contract, law, or assessment-body change | named authority changes, scope changes, or compliance owner changes |

For `AA3+` workflows, `CL-SECURITY` and `CL-CONTEST` cannot rely on a stale clock. For protected
support, `CL-ACCESS` and `CL-SAFETY` cannot rely on stale evidence.

## Evidence record fields

Every claim-family entry should now carry these fields.

```text
Claim family:
Claim being made:
Evidence grade:
Evidence source:
Population / context:
What this evidence does not prove:
Expiry date:
Early-expiry triggers:
Owner:
Renewal or re-pilot trigger:
Public claim to remove if evidence stays weak or expires:
```

The expiry date should be a real date, not just “annual.” A vague renewal promise lets stale claims
survive because nobody owns the calendar.

## Renewal decisions

At renewal, choose one of five actions for each claim family.

| Action | Use when |
|---|---|
| keep | evidence remains fresh and no material drift occurred |
| narrow | the service may continue but the public claim must shrink |
| re-pilot | evidence may be recoverable, but the tested context has changed |
| pause | learner or record risk is too high to continue while evidence is unresolved |
| retire | the service cannot justify the claim or the operating burden |

The service decision and the claim decision can differ. A service may continue as convenience
support while its learning or validity claim is removed.

## Public-claim removal rule

Every public-facing pilot summary must state at least one claim that will be removed if evidence
stays weak. This changes renewal from “do we like the service?” to “what are we no longer entitled
to say?”

Examples:

| Weak or expired claim | Public wording to remove |
|---|---|
| `CL-LEARN` remains `EV1-EV2` only | “improves learning outcomes” |
| `CL-WORKLOAD` lacks total-labor evidence | “saves teachers time” |
| `CL-ACCESS` lacks subgroup evidence | “improves access for all learners” |
| `CL-VALIDITY` lacks construct evidence | “supports fair assessment” |
| `CL-SECURITY` red-team is stale | “secure workflow” or “safe integration” |
| `CL-CONTEST` route was not tested | “easy to appeal or correct” |

## Micro-change interaction

Evidence expires immediately when the micro-change budget says the service record no longer
describes the deployed path. A prompt tweak may not matter; a prompt tweak plus new retrieval
corpus, new memory field, new owner, and new queue action probably does.

## Current archive bet

Evidence-expiry clocks are a lightweight substitute for indefinite pilot optimism. They do not make
services more bureaucratic; they make stale public claims removable before failure has to become a
learner incident.

See
[`claim-family-evidence-matrix.md`](claim-family-evidence-matrix.md),
[`micro-change-cluster-reset-and-change-budget-defaults.md`](micro-change-cluster-reset-and-change-budget-defaults.md),
[`../30-operations/ai-implementation-review-cycle-and-stop-rules.md`](../30-operations/ai-implementation-review-cycle-and-stop-rules.md),
[`../30-operations/machine-readable-service-record-schema-and-validator.md`](../30-operations/machine-readable-service-record-schema-and-validator.md),
and `B275`, `B276`, `B279`, `B280`, `B281`.
