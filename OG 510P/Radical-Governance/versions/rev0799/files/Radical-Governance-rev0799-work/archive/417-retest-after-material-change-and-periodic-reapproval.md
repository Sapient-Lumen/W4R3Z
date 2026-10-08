# 417 — Retest after material change and periodic reapproval

## One-line thesis

Evidence for a public automated system expires. When the system, its data, its oversight practice, or its context changes in a material way, it should be **retested and reapproved**; even without a trigger event, high-impact systems should face a periodic reapproval clock.

## Why this matters

Public automation often accumulates change faster than its governance artifacts do.

- the model is updated,
- new data sources are added,
- a pilot becomes production,
- operators use the tool differently,
- oversight workflows are adapted,
- the legal context changes,
- but the last “approval” remains on file as if nothing important happened.

Official guidance increasingly rejects that fiction. Risk management is supposed to be continuous and iterative; substantive changes to public transparency records require re-clearance; changes in high-risk systems can have legal consequences and may require renewed conformity assessment; updated oversight practices may need retesting. The archive should therefore treat approval as perishable.

## Design rule

Create two review pathways for consequential systems:

- **event-based reapproval** after material change, and
- **time-based reapproval** on a regular clock even when no material change is claimed.

The burden of proof should be on the operator to show that the existing evidence still matches the live system.

## Pattern pack

### 1. Define material change triggers in advance

A material-change list should be written before disputes arise. Typical triggers include:

- movement from pilot to production,
- introduction of new datasets,
- model replacement or major retuning,
- changed operating context or user population,
- changed human-oversight practice,
- changed legal or policy basis,
- changed downstream consequence severity.

### 2. Retest the oversight layer, not only the model layer

If operators receive new instructions, new interface cues, new warning thresholds, or new escalation rules, retest the oversight practice itself. A system can become less governable even when the model barely changes.

### 3. Reopen approval bundles when substantive facts change

Do not let updated technical artifacts inherit old governance sign-off automatically. Material changes should reopen:

- internal clearance,
- risk review,
- operating instructions,
- public documentation,
- phase labels,
- incident and appeal routing if needed.

### 4. Use periodic reapproval to catch unreported drift

Not all important changes announce themselves. Set a regular review clock for high-impact systems so that operators must periodically reconfirm:

- intended purpose,
- current datasets,
- actual operating context,
- live performance and harms,
- staff training,
- continuing legal basis,
- retirement or replacement options.

### 5. Tie post-market signals back into reapproval

Monitoring, logging, incident reports, complaints, and near-misses should not live in a separate archive universe. They should feed directly into the reapproval path. A good review clock asks not only “what changed in the system?” but also “what changed in what the system is doing to people?”

### 6. Preserve comparable evidence across versions

Retesting is useful only if old and new evidence can be compared. Keep enough versioned evidence to answer:

- what changed,
- when it changed,
- what was retested,
- which thresholds moved,
- whether the new version is better, worse, or simply different.

### 7. Do not let legacy public systems hide behind old deployment dates

Where public-authority systems face phased legal applicability or future review points, use that runway to prepare early. Legacy systems should not become a compliance surprise discovered at the deadline.

## Guardrails

- Keep trigger lists explicit and short enough to use.
- Require operators to document why a change is judged non-material.
- Retest under conditions similar to actual deployment.
- Do not treat periodic review as a paperwork refresh only.
- Link reapproval outcomes to phase labels, including pause or retirement where needed.

## Failure modes

- **approval fossilisation**: old sign-off survives despite major system drift.
- **model-only retesting**: governance ignores changed oversight or workflow conditions.
- **silent material change**: the system changes but the public record does not.
- **review theater**: periodic review checks boxes without using live evidence.
- **legacy surprise**: old public systems remain invisible until a legal date forces a scramble.

## Practical tests

A reapproval regime passes when it can answer yes to all of the following:

1. Is there a written list of material-change triggers?
2. Do changes in data, model, context, or oversight practices reopen review?
3. Does evidence include retesting under conditions similar to live use?
4. Is there a regular reapproval clock even when operators claim nothing important changed?
5. Can the archive compare the current version with the previously approved one?

## Compression rule for the archive

When someone says a public automated system is already approved, ask:

**Approved for which version, with which data, under which oversight practice, and reviewed again when?**

If that answer is missing, the approval has probably expired.
