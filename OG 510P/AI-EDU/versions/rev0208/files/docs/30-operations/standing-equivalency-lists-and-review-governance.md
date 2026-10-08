# Standing equivalency lists and review governance

This document closes the archive's next recognition gap.

The archive already says what should travel in a packet and how different receiving sectors should treat outside AI-learning by default. But that still leaves one operational problem: **when should a provider, assessment, bridge completion, or outside learning experience move from one-off review into a standing published rule?**

The archive's answer is:

> **use small, reviewable standing lists with expiry, scope, and manual-review fallback—never hidden provider whitelists, never wallet-driven auto-credit, and never hard denial just because something is absent from the list.**

This move is grounded in a converging set of public signals. DOL's 2026 workforce guidance encourages portable, learner-controlled learning assertions. Credential Engine's prior-learning-recognition model treats policies, accepted evidence, methods, and outcomes as publishable infrastructure rather than invisible local discretion. ACE and NCCRS both make recognition depend on versioned evaluation, recurring review, and explicit dates rather than timeless trust in a provider name. CUNY's CPL/T-Rex stack shows a public-system example of standing equivalencies that remain visible, configurable, and non-final: if a training or exam is not listed, that does **not** automatically mean rejection. Europass adds a useful authentication layer through trusted issuers and accreditation checks, but also shows why authenticity alone is not enough to decide equivalency. Recent Workcred/NAC work matters as a live signal too: short-term workforce training is moving toward more structured quality review rather than informal trust. See `B40`, `B41`, `B45`, `B48`, `B49`, `B51`, `B52`, `B53`, `B54`, `B55`.

## Core rule

A standing equivalency list is a **published, reviewable rule table** maintained by a receiving node or authorized system steward. It says that a named outside learning experience, assessment, or quality-assured completion will usually produce a specific recognition outcome under specific scope conditions.

The archive's default posture is:

- publish standing rules for recurring cases that would otherwise create repeated local friction;
- keep those rules narrow, versioned, and review-dated;
- preserve manual review for out-of-scope or unlisted cases;
- and make absence from the list mean **"not yet pre-cleared"**, not **"categorically refused."**

## Who may maintain standing lists

The archive rejects the idea that wallet vendors, model vendors, or frontline staff should define standing equivalency on their own.

### Legitimate maintainers

- public-system offices with delegated authority;
- consortia or statewide bodies acting under published policy;
- college/university CPL or transfer authorities with faculty-governed sign-off for credit-bearing outcomes;
- bridge-provider networks with explicit receiving-partner rules;
- and public workforce/library networks for continuity and duplication-avoidance rules below transcripted credit.

### Illegitimate maintainers

- AI-wallet providers;
- model vendors selling their own badges;
- individual instructors promising cross-institution credit on their own;
- or private platforms that publish acceptance language without receiving-node authorization.

## Admission paths

An outside experience should enter a standing list only through one of four paths.

### P1. Evaluated-learning path

The outside learning has current external evaluation or credit-recommendation standing from a recognized evaluator or equivalent quality-assurance body.

Examples:

- ACE-evaluated learning with current dates and version logic;
- NCCRS-reviewed learning with active dates and revalidation history;
- a licensed or accredited credential whose issuing status can be verified.

Default recognition ceiling:

- `R3` by default,
- `R4` only where the receiving node has already published a formal CPL, challenge, or credit-award rule.

### P2. Standardized-assessment path

The outside learning is not trusted because of provider reputation alone, but because the learner passed a stable, externally legible assessment or challenge mechanism.

Examples:

- standardized examinations;
- challenge exams;
- supervised demonstrations with published criteria.

Default recognition ceiling:

- `R2` to `R4` depending on the stakes and the receiving sector.

### P3. Articulated public-bridge path

The outside completion is part of a public or public-partner bridge route already mapped to the receiving node.

Examples:

- community-college or workforce bridge modules;
- statewide foundational AI-literacy completions with published outcomes;
- public library/workforce/college co-designed onramps.

Default recognition ceiling:

- `R1` to `R3` by default,
- `R4` only when a receiving programme has explicitly approved stronger standing.

### P4. Local provisional path

The outside learning is not yet mature enough for a systemwide standing rule, but repeated one-off acceptances suggest it may deserve bounded provisional status.

Default recognition ceiling:

- `R1` to `R2`,
- or `R3` only inside a named receiving programme family.

The archive prefers provisional status over silent shadow precedent.

## Mandatory fields for every list entry

A standing-list entry should be short, but it must publish enough to be usable and contestable.

Every entry should name:

- issuer / provider / assessment owner;
- exact experience title and version;
- claim family (`A0`-`A3` or equivalent local mapping);
- eligible receiving sector or programme family;
- recognition outcome (`R1`-`R4`) and ceiling;
- affected requirement, module, or duplicated-basic area;
- admission path (`P1`-`P4`);
- evidence basis (for example ACE, NCCRS, challenge exam, public articulation, accredited issuer, or local pilot history);
- effective date and review-by date;
- recency rule, where the content domain changes quickly;
- manual-review route for exceptions;
- and the explicit note that absence from the list does not by itself mean rejection.

## Statuses

The archive recommends five statuses.

- `provisional` — bounded pre-clearance with narrow scope and short review date;
- `active` — currently published standing rule;
- `expiring` — still visible, but review due soon;
- `expired` — no longer pre-cleared, route to manual review;
- `retired` — no longer used because quality, relevance, or construct fit no longer hold.

The archive prefers visible expiry to stale silent trust.

## Review cadence

Standing lists should not invent new freshness fantasies when source review already exists. The better rule is to inherit or tighten the strongest existing review cycle.

### Default cadence rule

- If the entry depends on an external evaluation body with a published cycle, mirror that cycle or tighten it.
- If the content area is fast-moving, add a shorter local recency window.
- If there is no external cycle, require at least annual review and a hard expiry unless re-approved.

### Current public signals the archive uses

- ACE states that evaluated/endorsed learning is re-reviewed every three years, and that materially changed versions are evaluated separately. See `B48`, `B51`.
- NCCRS uses annual review plus revalidation up to every five years, with dated exhibits and end dates when substantive changes occur. See `B52`.
- CUNY's public CPL/T-Rex pattern shows that standing equivalencies can be visible and configurable without pretending to settle all future cases. See `B53`.

### AI-specific recency bias

The archive's current bias is that AI-literacy and tool-specific completions need shorter shelf lives than slower-changing foundational literacies. The detailed profile and default windows now live in [`standing-list-publication-profile-and-recency-windows.md`](standing-list-publication-profile-and-recency-windows.md).

## First-wave list candidates

The archive now treats the following families as the best early candidates for standing publication.

### F1. Public foundational AI-literacy completions with named outcomes

Especially when they are run by public systems, aligned to a shared framework, and already used as duplicated-basics content.

Typical ceiling:

- `R1` or `R2` in libraries, workforce systems, bridge/noncredit routes;
- narrow `R2` in credit-bearing settings where they duplicate orientation or foundational digital-literacy content.

### F2. Standardized or supervised assessments

Typical ceiling:

- `R2` to `R4` depending on stakes and local CPL/challenge policy.

### F3. ACE/NCCRS-style evaluated learning and similar quality-reviewed offerings

Typical ceiling:

- `R3` by default;
- `R4` only with published receiving-node authority.

### F4. Articulated bridge completions with repeated receiving-node acceptance

Typical ceiling:

- `R2` or `R3`;
- stronger outcomes only where the articulation is already explicit.

### F5. Tool/model/vendor-specific workflow badges

These can be useful for routing or provisional recognition, especially when they carry verifiable issuer and criteria metadata. But they age quickly, and authenticity is still not equivalency.

Typical ceiling:

- `R0` to `R2` by default;
- stronger outcomes only through a separate public evaluation or articulation route.

## What should stay off standing lists for now

- generic vendor participation badges;
- attendance-only webinars;
- completions without version or date information;
- wallet imports that prove possession but not learning quality;
- and any credential whose support depends on raw chat logs, detailed telemetry, or protected accessibility/accommodation records.

The archive explicitly rejects turning private support traces into standing-recognition evidence. The archive now also treats digital-credential form as orthogonal: a badge or verifiable credential can help with issuer authenticity, but it does not itself create standing equivalency or determine shelf life.

## Sector posture

Standing lists should remain asymmetric across sectors.

- libraries and civic first-contact points can publish generous continuity / non-duplication lists;
- workforce systems can publish routing and duplicated-basic waiver lists plus bounded training-entry rules;
- bridge/noncredit/public college systems can publish the most generous practical standing lists short of automatic transcripted credit;
- credit-bearing programmes can publish standing rules only through faculty-governed CPL / exam / articulation authority;
- universities should use standing lists mainly to define where challenge, waiver of repeated basics, or prior-learning review becomes available—not to universalize auto-credit.

## Appeals and manual review

Standing publication should reduce friction, not erase discretion.

The archive's rule is:

- listed cases get the published default;
- stronger-than-default outcomes require the receiving node's formal pathway;
- unlisted cases route to manual review;
- and unlisted must never be treated as proof of no value.

This is where the archive borrows a useful public lesson from CUNY's Transfer Explorer posture: **absence from a standing table should trigger review, not silent denial.** See `B53`.

## Failure modes this document is trying to prevent

- **provider-brand shortcuts** — a famous AI company badge gets treated as automatic equivalency;
- **stale trust** — outdated AI-learning completions remain pre-cleared long after the content changed;
- **vendor capture** — the issuer, wallet, or platform becomes the de facto recognition authority;
- **shadow precedent** — repeated local exceptions accumulate without public rules;
- **hard-denial by omission** — learners are told "not recognized" when the real answer is "not yet reviewed";
- **privacy spillover** — support-channel records become recognition evidence;
- **credit inflation** — continuity-friendly public nodes start promising formal credit they do not control.

## Current archive bet

The archive's current best guess is that **small standing equivalency lists with expiry, published authority, and manual-review fallback** will outperform both pure case-by-case discretion and broad provider-brand trust.

That means:

- use standing lists to reduce repeated friction;
- keep them versioned, dated, and scoped;
- let trusted-issuer infrastructure prove authenticity, not automatic equivalency;
- and preserve a route upward from continuity to waiver to challenge/review to formal credit only when the receiving node has actually published that route.

This remains paired with the packet rule, sector defaults, the small public handoff standard, the standing-list publication profile, and the bounded exception grammar. Use standing lists for recurring cases, the publication profile for dates and machine-readable fields, and the exception grammar for repeated partial-equivalency or local-override logic. The archive now answers the maintenance-logic question with a separate privacy-light rule for appeal feedback, aggregate signals, and bounded revision triggers, and answers the disclosure question with a thin public history/profile for state, date, scope, reason family, and action hint. The next live question is narrower still: which continuity-reserve or public-entitlement triggers, proof minima, claiming windows, and publication fields truly travel across sectors, and when repeated `K2` / `K3` burdens should stay as predeclared reserves rather than harden into learner-facing entitlement floors. See [`appeal-feedback-and-standing-list-maintenance.md`](appeal-feedback-and-standing-list-maintenance.md), [`public-maintenance-history-and-trust-signals.md`](public-maintenance-history-and-trust-signals.md), [`no-fault-transition-cost-absorption-and-fee-waiver-rules.md`](no-fault-transition-cost-absorption-and-fee-waiver-rules.md), `OQ-0008`, and `FT-0034`.

## Detailed publication profile

This governance document now points to two separate load-bearing publication surfaces:

- [`standing-list-publication-profile-and-recency-windows.md`](standing-list-publication-profile-and-recency-windows.md) for field-level publication and family-specific review windows;
- [`standing-recognition-exception-profile-and-local-overrides.md`](standing-recognition-exception-profile-and-local-overrides.md) for bounded exception logic, partial equivalencies, and named manual-review triggers.


## Downstream consumption

Publishing standing entries is not enough. The archive now pairs these governance rules with a default downstream action grammar in [`partner-consumption-and-grandfathering-rules.md`](partner-consumption-and-grandfathering-rules.md) so partner systems know when a change is future-use-only, when in-flight uses need confirmation, and when settled uses should remain grandfathered.
