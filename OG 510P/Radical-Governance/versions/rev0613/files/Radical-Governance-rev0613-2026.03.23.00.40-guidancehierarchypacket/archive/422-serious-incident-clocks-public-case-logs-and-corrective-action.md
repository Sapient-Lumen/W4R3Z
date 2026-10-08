# 422 — Serious-incident clocks, public case logs, and corrective action

## One-line thesis

When public automated systems cause or plausibly cause serious harm, response should run on explicit **incident clocks** and a visible corrective-action track, not on vague promises to “look into it”.

## Why this matters

Many institutions still handle automation failures as a mix of support ticket, PR problem, and internal technical bug. That creates predictable failures:

- harmful incidents are noticed late,
- the first report is delayed while teams try to be sure,
- evidence gets overwritten by ordinary fixes,
- affected people cannot tell whether the system is still in use,
- lessons remain trapped in one unit instead of improving the portfolio.

Current official frameworks are moving toward timed, operational treatment. The EU AI Act pairs post-market monitoring with serious-incident reporting, severity-based timelines, investigation, and corrective action. NIST’s AI RMF playbook likewise pushes organizations to define incident thresholds, exercise response plans, preserve evidence, and record errors, near-misses, incidents, and negative impacts. The archive should therefore make time and status first-class governance objects.

## Design rule

Every consequential public automated system should operate under a standing **incident clock regime**. That regime should define:

- what counts as a serious incident,
- who can declare one,
- how quickly an initial alert must be filed,
- when a public case log entry appears,
- when mitigation, rollback, or suspension must be decided,
- how corrective action is tracked to closure.

## Pattern pack

### 1. Separate alert, assessment, and closure clocks

The first alert should not wait for full certainty. Treat incident handling as staged:

- **initial alert** when a plausible harmful event or malfunction is known,
- **validated incident report** once a causal link or reasonable likelihood is established,
- **closure review** once corrective action and restart conditions are decided.

This avoids the trap where nothing is reported because everything is still being debated.

### 2. Define severity classes before the failure happens

Different harms justify different clocks. Death, major rights deprivation, or widespread harms should move faster than ordinary defects. Severity classes should already be linked to:

- notification deadlines,
- escalation routes,
- pause or rollback authority,
- executive review requirements,
- public disclosure defaults.

### 3. Keep a public case log for consequential incidents

Not every technical detail should be public, but the existence and status of serious cases should be. A public incident log should show, where lawful:

- system name,
- incident class,
- date opened,
- current status,
- current operating state of the system,
- corrective-action stage,
- closure date and summary.

This turns invisible institutional memory into a portfolio-level learning surface.

### 4. Freeze evidence before patching away the trace

When a serious incident is declared, the operator should preserve relevant logs, model versions, inputs, outputs, and workflow context before remediation alters the record. Silent hotfixes should not erase the evidentiary trail.

### 5. Treat near-misses as pre-incident material

A system that narrowly avoided serious harm is already telling you something about thresholds, oversight, or workflow weakness. Near-misses should feed the incident system even if they do not trigger full public treatment.

### 6. Make corrective action legible

Corrective action should have:

- a named owner,
- a due date,
- a status,
- a test for completion,
- a decision on whether the system may continue, pause, narrow, or retire.

A promise to “monitor closely” is not corrective action.

### 7. Run after-action review across the portfolio

Each serious case should produce a short after-action review that asks:

- what failed,
- what indicators were missed,
- whether thresholds were too loose,
- whether training or delegation failed,
- what similar systems should change now.

Otherwise every incident stays local and expensive.

## Guardrails

- Permit rapid initial reporting even when some details are still unknown.
- Preserve legal, forensic, and audit evidence before system changes.
- Keep a public-facing status layer even when full technical details must remain restricted.
- Link incident closure to measurable remediation, not just time passed.
- Ensure affected people have a route to challenge outcomes linked to the incident.

## Failure modes

- **certainty delay**: teams wait too long to report because proof is incomplete.
- **ticket laundering**: serious harms get misclassified as ordinary service issues.
- **silent patching**: remediation erases the ability to reconstruct what happened.
- **case-log blackout**: the institution knows the case exists, but the public cannot tell.
- **closure without learning**: the local incident closes but portfolio rules do not improve.

## Practical tests

A serious-incident regime passes when it can answer yes to all of the following:

1. Are severity classes and response clocks defined in advance?
2. Can teams file an initial alert before full certainty is reached?
3. Is there a visible case log or equivalent public status layer?
4. Are corrective actions owned, dated, and testable?
5. Do incidents generate changes beyond the single affected system?

## Compression rule for the archive

When a public automated system goes wrong, ask:

**What clock started, who owns the case, what evidence was frozen, what status is public, and what must be fixed before trust is restored?**

If those answers are fuzzy, the institution is still treating harm as noise.
