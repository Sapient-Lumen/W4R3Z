# 445 — Explicit release decisions, frozen public surfaces, and no-release records

## One-line thesis

Consequential public AI should not move from “reviewed” to live use by implication; institutions should record an explicit publish, hold, or no-release decision and preserve the exact public-facing governance surface that was in force at that moment.

## Why this matters

Public AI governance often accumulates careful artifacts — impact assessments, system cards, registry entries, notices, appeal routes, operator scripts — and then still fails at the last administrative step: nobody can point to the exact decision that authorized go-live, the date it took effect, the owner who approved it, or the public description that was actually on the record when the system first reached consequential use.

That gap creates a specific form of governance drift. Teams mistake completed review for release authority, treat launch as the default unless someone objects, overwrite public disclosures instead of freezing what was actually shown, and leave later reviewers unable to reconstruct whether a harmful production state was ever truly authorized. The archive should reject that posture. For consequential public AI, **release is its own governance decision**, not merely the final side effect of technical readiness.

## Pattern pack

### 1. Separate readiness evidence from release authority

A system can be:

- assessed,
- peer reviewed,
- technically deployable,
- fully configured,
- and still not yet authorized for consequential use.

The archive should distinguish at least three states:

- **ready for release review**,
- **explicitly approved for release**,
- **actually live in consequential use**.

This prevents the common collapse where “the paperwork is basically done” becomes a de facto launch authorization.

### 2. Record an explicit publish, hold, or no-release outcome

Every consequential launch or material-change activation should end in a recorded release outcome such as:

- **publish**,
- **hold pending condition**,
- **no release / rejected**,
- or **rollback to prior approved state**.

That record should name:

- the approving role,
- the decision date,
- the effective date or window,
- the governed baseline or version,
- the reasons or gating conditions,
- and the next review trigger if the answer is hold rather than publish.

A consequential system should not become live merely because the work queue moved forward without a contrary signal.

### 3. Treat no-release and hold states as first-class governance artifacts

A failed or deferred launch is governance evidence too. Institutions should keep a compact record when a system or change package is:

- blocked for unresolved rights or safety concerns,
- delayed for missing notice or appeal materials,
- paused for accessibility, language, or data-governance gaps,
- or rejected because fallback continuity is not ready.

If only successful launches leave a visible trail, the archive loses the evidence that governance ever constrained anything.

### 4. Freeze the public-facing governance surface at each release point

For the first live launch and every material consequential change, preserve an immutable snapshot of the public-facing governance surface that was actually in force, including where applicable:

- the registry or inventory entry,
- the public system card,
- point-of-interaction notice and explanation text,
- public appeal or complaint routing,
- version label and effective date,
- and any short warning label shown in the interaction path.

The point is not archival maximalism. The point is to preserve the answer to a later accountability question: **what exactly did the institution tell the public when this version went live?**

### 5. Bind release records to the governed baseline, not merely the software build

A release decision should point to the concrete governed baseline that mattered for public accountability, such as:

- model or policy version,
- threshold or business-rule set,
- prompt or retrieval baseline where relevant,
- approved data source set,
- human-review posture,
- and fallback or rollback path.

This keeps the release record attached to the actual governance object rather than to a vague deployment event.

### 6. Make public-surface refresh part of the release gate

A material change should not become live until the institution can show that the outward-facing governance surface was refreshed together. This commonly means:

- updated registry or transparency record,
- updated notice or warning label,
- updated system card,
- updated review or appeal description,
- updated version/effective-date marker,
- and an archived prior public snapshot where practical.

A changed system with an unchanged public record is still an unauthorized public representation of the live state.

### 7. Link release decisions to rollback, pause, and incident routes

Release records should also say what happens if live evidence turns against the change. At minimum, the institution should be able to identify:

- the rollback target,
- the pause authority,
- the incident or complaint trigger that would reopen the release decision,
- and the owner responsible for deciding whether the system stays live.

That way a release decision remains reversible under evidence rather than becoming administratively invisible once launch occurs.

## Guardrails

- Do not treat completed review as implicit authority to launch.
- Preserve release decisions for rejected and deferred launches, not only successful ones.
- Freeze the public-facing governance surface that was actually in force at release time.
- Tie each release decision to a governed baseline and effective date.
- Block live use when the public record still describes an older state.

## Failure modes

- **implicit launch**: the system becomes live without a named release decision.
- **review-is-release confusion**: teams mistake readiness evidence for authorization.
- **overwritten disclosure**: the public record is edited in place and the live-at-launch surface cannot later be reconstructed.
- **success-only history**: failed, held, or rejected launch attempts disappear from the archive.
- **baseline blur**: a release record exists but does not identify the threshold, data, model, or workflow state it authorized.

## Practical tests

A release discipline passes when it can answer yes to all of the following:

1. Does consequential go-live require an explicit publish, hold, or no-release decision?
2. Can the institution name the approver, effective date, and governed baseline for each live release?
3. Are rejected and deferred launch attempts preserved as compact governance records?
4. Is the exact public-facing governance surface at release time frozen or otherwise reconstructible?
5. Would a material change be blocked until the public-facing record matches the new live state?

## Compression rule for the archive

If nobody can show **who authorized this version to go live and what the public record said at that moment**, the system is still running on **implied release authority**.
