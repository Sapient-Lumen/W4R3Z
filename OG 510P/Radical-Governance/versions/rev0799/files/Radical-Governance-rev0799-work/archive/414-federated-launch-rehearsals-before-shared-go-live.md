# 414 — Federated launch rehearsals before shared go-live

## One-line thesis

Before a shared public digital system becomes mandatory or widely relied upon, its operators should run **federated launch rehearsals**: structured peer-to-peer testing under realistic conditions, with public lessons and explicit launch gates.

## Why this matters

Many public systems look ready in isolated demos but fail when independent actors interact across real organisational and jurisdictional boundaries. The gap appears when:

- one side interprets the same rule differently,
- operational assumptions collide,
- trust status or error handling breaks,
- support channels cannot absorb ambiguity,
- “pilot” success was only local success.

A launch rehearsal is therefore not theater before the ribbon cutting. It is a governance device for proving that distributed adoption is survivable.

## Design rule

Before shared go-live, operators should conduct a visible rehearsal phase that includes:

- peer-to-peer interoperability tests,
- testing against reference tools,
- edge-case and degraded-mode scenarios,
- issue logging and triage,
- criteria for launch readiness,
- documented follow-up on what failed and what changed.

## Pattern pack

### 1. Rehearse with independent participants

A real rehearsal involves different organisations using separate implementations, not only one team running both sides of the exchange. That reveals:

- ambiguous wording,
- hidden assumptions,
- onboarding defects,
- documentation gaps,
- support and escalation failures.

### 2. Pair peer testing with reference-tool testing

Both are needed:

- peer-to-peer testing shows whether independent implementations interoperate,
- reference-tool testing shows whether each implementation meets the common expectations of the standard.

Either one alone leaves blind spots.

### 3. Test operational as well as technical readiness

The rehearsal should cover more than protocol correctness. Include:

- status changes,
- certificate or trust updates,
- support routing,
- incident escalation,
- user messaging,
- rollback decisions,
- defect ownership.

### 4. Define launch gates in advance

Do not let “learning event” become a loophole for vague readiness. Publish what must be true before live rollout, such as:

- minimum pass thresholds,
- no unresolved severity-one defects,
- confirmed cross-implementation success for named scenarios,
- complaint routing in place,
- rollback path exercised.

### 5. Publish the lessons, not just the celebration

A credible rehearsal produces a compact public record of:

- what was tested,
- who participated,
- what failed repeatedly,
- what was fixed,
- what remains deferred,
- what evidence justified go-live.

The report need not expose every sensitive detail, but it should not pretend the event was frictionless.

### 6. Run another rehearsal after major rule changes

If standards, trust rules, or reference artifacts materially change, the ecosystem should not assume yesterday’s rehearsal proves tomorrow’s readiness.

### 7. Keep launch gates from becoming incumbency moats

Readiness processes should help new entrants onboard rather than entrench the first participants. Provide:

- reusable test scripts,
- published issue patterns,
- stable onboarding guidance,
- repeatable future rehearsal windows.

## Guardrails

- Rehearsals should happen early enough to change the plan, not just validate a decision already taken.
- Participation should include implementers who did not co-design every artifact.
- Launch gates should be strict enough to matter and simple enough to explain.
- Public reporting should distinguish fixed issues from deferred issues.
- “Pilot” should not be used to hide production dependency.

## Failure modes

- **demo readiness**: the system works in a staged showcase but not across independent operators.
- **peerless testing**: everyone tests against their own assumptions only.
- **gate vagueness**: launch proceeds without explicit success criteria.
- **celebration bias**: the report markets the event but omits repeated failures.
- **incumbent advantage**: future entrants cannot access the same rehearsal support.

## Practical tests

A federated launch process passes when it can answer yes to all of the following:

1. Were independent participants involved in the rehearsal?
2. Did testing include both peer-to-peer and reference-tool modes?
3. Were operational scenarios and failure handling tested, not only message exchange?
4. Were launch criteria explicit before the event?
5. Was there a public or auditable record of what changed because of the rehearsal?

## Compression rule for the archive

Before a shared public system goes live, ask:

**What happened when independent implementers tried to use it together under realistic conditions, and what launch gate did that evidence feed?**

If the answer is mostly demo language, the system is not ready enough.
