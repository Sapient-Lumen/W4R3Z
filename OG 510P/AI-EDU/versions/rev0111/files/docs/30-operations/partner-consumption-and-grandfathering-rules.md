# Partner consumption and grandfathering rules for maintenance signals

This document closes the last major gap left by the archive's standing-recognition publication work.

The archive already had:

- a typed packet and recognition rail;
- sector defaults for recognition strength;
- standing-list governance, publication, recency, exception, maintenance, and public-history rules.

What it still lacked was a compact answer to the operational question:

> **when a partner system sees a standing-entry change, what should it actually do—and when should prior uses stay grandfathered rather than reopened?**

This document now supplies the timing-class action grammar. The more specific protection vocabulary for learners already in motion lives in [`in-flight-teach-out-and-substitute-equivalent-rules.md`](in-flight-teach-out-and-substitute-equivalent-rules.md).

The archive's answer is:

> **default to future-use change, not retroactive churn. Grandfather settled uses unless the problem is about fraud, issuer authority, legal invalidity, or credential-integrity failure tied to the use itself.**

This move is grounded in a converging set of public signals. W3C's verifiable-credentials work says status evaluation is ultimately verifier policy, distinguishes cryptographic-integrity revocation from ordinary status change, and notes that a revoked digital credential can coexist with a still-valid backing educational achievement. 1EdTech's badge requirements treat revocation, expiration, and versioning as ordinary metadata while explicitly allowing new versions without altering previously issued versions. ACE re-reviews evaluated learning every three years, treats materially changed offerings as a fresh evaluation matter, and still leaves actual credit to receiving institutions. Public university catalog practice also keeps a default non-retroactivity intuition alive: degree rules ordinarily attach to a declared major or catalog year and do not reopen every already-set requirement whenever policy changes. See `B53`, `B66`, `B68`, `B70`, `B71`, `B72`, and `B73`.

## Core rule

The archive now distinguishes three timing classes for every standing-entry change:

- **future use** — no learner-facing action yet exists; consume the updated rule immediately;
- **in-flight use** — a learner has submitted, been routed, or been advised, but the receiving decision is not yet settled;
- **settled use** — a waiver, placement, requirement satisfaction, non-duplication determination, transcripted credit, or equivalent receiving-node action has already been posted or formally committed.

The default posture is:

- **future uses follow the new signal;**
- **in-flight uses may require confirmation;**
- **settled uses are grandfathered unless the failure family is unusually strong.**

The archive rejects both extremes:

- **blind auto-consumption**, where every visible status change reopens learner outcomes automatically;
- **frozen trust**, where a partner system ignores meaningful suspension, authority collapse, or legal invalidation signals because reopening is administratively inconvenient.

## Action vocabulary

The archive now uses a small partner-action vocabulary.

- `C0 continue` — no local change beyond cache refresh.
- `C1 continue_with_note` — keep using the entry, but surface the new note to staff or learner.
- `C2 auto_swap_successor` — future uses move to the successor entry automatically.
- `C3 confirm_before_next_use` — future and in-flight uses require local human confirmation before relying on the entry.
- `C4 pause_automatic_use` — stop automatic reliance for future and in-flight cases; route to local review.
- `C5 exceptional_reopen` — consider reopening a settled use only through a governed exceptional process.

The archive keeps `C5` deliberately rare.

## Grandfathering classes

The archive also names three grandfathering outcomes. Detailed in-flight teach-out, successor-substitution, challenge, and substitute-equivalent defaults now live in [`in-flight-teach-out-and-substitute-equivalent-rules.md`](in-flight-teach-out-and-substitute-equivalent-rules.md).

- `G0 none` — settled uses may be revisited.
- `G1 settled_only` — previously settled uses remain valid, but in-flight and future uses follow the new signal.
- `G2 settled_and_inflight_commitments` — settled uses remain valid, and in-flight cases with documented learner reliance should get teach-out, substitution, or a close equivalent rather than a hard restart.

The default archive bias is `G1`.

## Default consumption matrix

### 1. Editorial or metadata-only changes

Typical pattern:

- `change_kind = clarified`
- `reason_family = editorial_correction`
- `scope_impact = metadata_only`

Default action:

- `C0 continue`
- grandfathering = `G2`

Rationale:

These changes improve legibility, not validity.

### 2. Successor publication without weaker recognition

Typical pattern:

- `change_kind = superseded`
- `action_hint = use_successor_entry`
- same or narrower scope, equal or stronger recognition ceiling

Default action:

- future uses: `C2 auto_swap_successor`
- settled uses: `G2`

Rationale:

A successor entry should update future routing without undoing earlier lawful uses of the predecessor.

### 3. Recency expiry or version drift without evidence of bad faith

Typical pattern:

- `reason_family = version_drift` or `recency_failure`
- `scope_impact = future_uses_only` or `specific_versions_only`

Default action:

- future uses: `C3 confirm_before_next_use`
- in-flight uses: local review; preserve documented learner reliance when feasible
- settled uses: `G1`

Rationale:

The problem is stale standing trust, not proof that prior uses were illegitimate.

### 4. Narrowed scope or lowered ceiling

Typical pattern:

- `change_kind = narrowed_scope` or `lowered_ceiling`
- `reason_family = scope_clarification` or `construct_mismatch`

Default action:

- future uses: `C3 confirm_before_next_use`
- in-flight uses: `C4 pause_automatic_use` for the affected requirement family until a human checks fit
- settled uses: `G1`

Rationale:

These changes often mean the old shortcut was too broad, but they do not automatically prove that every already-settled use was wrong.

### 5. Suspension during review

Typical pattern:

- `change_kind = suspended`
- `maintenance_status = suspended`
- `action_hint = pause_automatic_acceptance`

Default action:

- future uses: `C4 pause_automatic_use`
- in-flight uses: `C4 pause_automatic_use`
- settled uses: usually `G1`, unless the suspension reason is integrity-, authority-, or law-linked

Rationale:

Suspension is a warning against fresh automation, not yet proof that every earlier use should be reversed.

### 6. Authority collapse, fraud, or legal invalidity

Typical pattern:

- `reason_family = authority_change` where issuer authorization disappears or was falsified;
- local evidence of fraud, impersonation, forged records, or claimant-specific misrepresentation;
- legal/privacy findings that make the underlying use itself invalid.

Default action:

- future uses: `C4 pause_automatic_use`
- in-flight uses: `C4 pause_automatic_use`
- settled uses: `C5 exceptional_reopen`
- grandfathering = `G0 none`

Rationale:

This is the narrow family where reopening may be justified because the problem is not just drift or overbreadth; it is the validity of the underlying authority or claim.

### 7. Credential-integrity failure with still-valid backing achievement

Typical pattern:

- digital signature compromise;
- revoked or replaced verifiable credential;
- backing course, exam, or achievement may still be valid.

Default action:

- future uses: `C3 confirm_before_next_use` or `C2 auto_swap_successor` if a refreshed credential exists;
- in-flight uses: request refreshed or alternate proof;
- settled uses: `G1` unless local evidence suggests the underlying achievement itself is false.

Rationale:

The archive follows the W3C distinction here: a digital credential can fail while the underlying educational achievement remains valid.

## Receiving-node defaults by outcome type

The archive now adds a second layer: what kind of settled use is at stake?

### Continuity / routing (`R1`-like uses)

Examples:

- skip duplicate orientation;
- route learner into the next public module;
- preserve advising continuity.

Default grandfathering:

- `G2`

These are the easiest to preserve because the cost of retroactive reversal is usually higher than the risk.

### Waiver of repeated basics / placement (`R2`-like uses)

Examples:

- basic AI-literacy module waived;
- placement into a higher starting point;
- duplicate training avoided.

Default grandfathering:

- `G1`

Reopen only for fraud, authority failure, or a clear construct-integrity problem.

### Prior-learning review eligibility or challenge pathway (`R3`-like uses)

Examples:

- learner granted access to portfolio review;
- learner admitted to a challenge exam path.

Default grandfathering:

- `G2`

A later standing change should rarely strip access to a review pathway already opened in good faith.

### Formal credit or transcripted equivalency (`R4`-like uses)

Examples:

- transcripted credit posted;
- degree audit satisfied;
- requirement formally waived in the student record.

Default grandfathering:

- `G1`, with very strong bias against reopening;
- `G0` only for fraud, claimant misrepresentation, authority collapse, or legal invalidity that directly contaminates the posted result.

The archive is intentionally conservative here. Formal posted outcomes should not become unstable merely because a standing shortcut later narrows.

## Teach-out and substitute-equivalent rule

When in-flight reliance exists but the entry can no longer be used as published, the archive prefers:

- teach-out of the already-started public module;
- a near-equivalent successor path;
- or a local challenge/review route.

It rejects routine hard restart where the learner must begin from zero despite prior documented reliance.

This is the archive's public-learning analogue of catalog-rights logic: changes should usually govern future entry, not erase previously authorized progress.

## Notification posture

The archive now prefers a minimal but explicit notification rule.

When a partner system consumes a change that affects future or in-flight uses, it should be able to tell the learner one of four things:

- **nothing material changed for your case**;
- **future cases use a successor rule**;
- **your case needs local confirmation, but prior documented work still counts toward review**;
- **your settled result remains in force unless a fraud/authority/legal exception applies.**

The archive rejects silent status consumption when the learner's path is actually affected.

## What should never auto-trigger reopening

The following should not, by themselves, reopen settled uses:

- editorial clean-up;
- shorter review windows for future cohorts;
- normal supersession by a clearer successor entry;
- family-specific freshness tightening;
- metadata corrections;
- replacement of a digital credential wrapper where the underlying learning remains verified.

## What may justify exceptional reopening

Only a narrow set of cases should trigger `C5 exceptional_reopen`:

- credible evidence of claimant fraud or impersonation;
- issuer authority never existed or was materially falsified;
- the underlying result was unlawfully issued;
- a legally required correction to the institutional record;
- or a direct finding that the settled use depends on a false backing achievement rather than on mere metadata drift.

Even then, the archive prefers governed exceptional review over automatic batch reversal.

## Minimum machine-readable additions

The public-history profile can stay thin, but the partner layer now benefits from three extra fields:

- `consumption_default` — one of `C0`-`C5`;
- `grandfathering_default` — one of `G0`-`G2`;
- `reopen_basis_required` — boolean, true only when settled-use reopening is thinkable.

Optional but useful:

- `successor_auto_swap_ok`
- `teachout_expected`
- `inflight_confirmation_required`

This is enough for software to triage without smuggling local case files into the shared layer.

## Failure modes this document is trying to prevent

- **retroactive churn** — learners lose already-settled value because a future-facing rule changed;
- **administrative panic** — every suspension triggers mass reopening;
- **silent drift** — partner systems keep using stale entries because they lack an action grammar;
- **false finality** — partner systems auto-close review even when a signal really should pause future reliance;
- **digital-wrapper confusion** — credential revocation is treated as proof that the underlying learning never happened;
- **unbounded grandfathering** — even fraud or authority collapse can never trigger correction.

## Current archive bet

The archive's current best guess is that **future-use default, protected settled uses, and a very narrow exceptional-reopening family** will outperform both blanket reopening and blanket grandfathering.
