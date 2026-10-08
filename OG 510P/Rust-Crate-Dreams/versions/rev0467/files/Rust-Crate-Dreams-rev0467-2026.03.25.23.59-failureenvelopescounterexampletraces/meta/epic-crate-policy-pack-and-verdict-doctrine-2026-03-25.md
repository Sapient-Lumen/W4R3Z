# Epic crate policy-pack and explainable-verdict doctrine — 2026-03-25

This note answers the practical question the archive had still not made explicit enough:

**If a worthy crate can produce evidence and conformance packets, what exact policy object should it hand another team so a real decision can be made and defended later?**

## Main judgment

A worthy crate should usually **not** stop at “export evidence”.
It should ship a **versioned policy-pack and explainable-verdict contract**.

That means:
- a stable policy pack,
- one small verdict vocabulary,
- a reviewed verdict report,
- an override / waiver path,
- and a recheck story.

## Default verdict vocabulary

Use a bounded core vocabulary unless a lane has a stronger domain-specific reason:

1. **allow** — evidence satisfied the active rule floor
2. **warn** — usable, but drift or weakness needs visibility
3. **block** — the active rule set says do not proceed
4. **manual-review** — the crate cannot honestly automate the decision
5. **waived** — a human exception exists and is still in force
6. **expired** — a prior waiver or verdict is no longer current

These verdict words should be explicit outputs.
They should never have to be inferred from side effects or exit codes alone.

## Default policy artifact family

A strong first policy kit usually includes:

### A. `policy-pack.json`
This says:
- which adopter posture is in scope,
- which bundles and dimensions are required,
- rule thresholds,
- rule severity,
- override eligibility,
- and expiry / recheck semantics.

### B. `verdict-request.json`
This says:
- which reviewed bundles are being evaluated,
- which profile is active,
- which policy pack revision is requested,
- and what organization-local inputs were supplied.

### C. `verdict-report.json`
This is the compact reviewed decision artifact.
It should summarize:
- the active policy pack,
- final verdict,
- per-rule outcomes,
- failing / degraded reasons,
- imported bundle identifiers,
- and next recheck triggers.

### D. `override-ticket.json`
This captures the exception path.
It should say:
- who approved the override,
- why the exception exists,
- what scope it covers,
- when it expires,
- and what event invalidates it early.

### E. `policy-explain.md`
This is the human-facing decision sheet.
It should explain:
- what the final verdict was,
- which rules mattered most,
- what evidence was decisive,
- what is only waived temporarily,
- and what still must not be inferred.

### F. `recheck-plan.json`
This says:
- what changes force a rerun,
- which bundles are freshness-sensitive,
- what expiry windows apply,
- and what can be reused from prior runs.

## Policy doctrine

### 1. Keep evidence and policy separate
Evidence bundles are not policy verdicts.
Do not bury organizational rules inside low-level adapters.

### 2. Keep verdict words few and stable
A six-word core vocabulary is more reusable than dozens of nearly synonymous states.

### 3. Make rules explainable
A downstream reviewer should be able to see:
- which rule fired,
- what evidence it inspected,
- why it passed or failed,
- and what would change the outcome.

### 4. Put organization-local policy above shared core meaning
The shared core should define bundle and verdict semantics.
Organization-local thresholds and approval rules should live in overlays or pack revisions, not in the universal evidence schema.

### 5. Treat overrides as first-class, expiring objects
An override without scope, owner, and expiry is not a reviewable policy surface.

### 6. Recheck triggers belong in the contract
If policy depends on release freshness, mirror parity, public-boundary drift, or support-basis age, the rerun triggers should be explicit.

## Release doctrine

### Honest `0.1`
Ship:
- one stable policy pack schema,
- one verdict vocabulary,
- one verdict report,
- one override ticket path,
- one recheck plan,
- and a clear split between evidence imports and policy outcomes.

Do **not** ship at `0.1`:
- giant policy DSLs,
- organization-specific enterprise theater,
- opaque scoring systems with no rule explanation,
- or fake claims that every lane can already be automated.

### Strong `0.3`
Add:
- rule bundles for common adopter profiles,
- diffing between verdict reports,
- stronger override invalidation triggers,
- and import adapters for more reviewed bundle families.

### Real `1.0`
Usually means:
- verdict vocabulary is stable,
- policy pack compatibility is explicit,
- override semantics are stable,
- and the human-readable explanation matches the machine verdict semantics.

## Anti-patterns

### Anti-pattern 1 — evidence theater pretending to be policy
Symptoms:
- the tool prints a recommendation,
- but there is no policy pack,
- no rule IDs,
- and no explanation of why the recommendation followed.

### Anti-pattern 2 — hidden override culture
Symptoms:
- teams routinely bypass the tool,
- but there is no override object,
- no expiry,
- and no carry-forward review.

### Anti-pattern 3 — bespoke verdict vocabularies everywhere
Symptoms:
- every lane invents its own pass/warn/risk/good/bad language,
- translation becomes manual,
- and downstream automation becomes brittle.

### Anti-pattern 4 — raw substrate treated as policy-stable
Symptoms:
- policy directly parses unstable or prototype outputs,
- rule meaning changes with upstream substrate churn,
- and users mistake tool breakage for policy changes.

## Practical archive rule after this pass

When planning a top-lane crate, the archive should now answer:
1. what reviewed bundles the policy consumes,
2. what the rule pack looks like,
3. what final verdict vocabulary it uses,
4. how overrides work,
5. what forces a rerun,
6. and what remains manual or out of scope.

If the pass cannot answer those questions, the lane is still underplanned.
