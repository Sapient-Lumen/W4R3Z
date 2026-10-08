# Constitutional Amendment & Entrenchment (Change Control for the Highest Rules)

**Merge relation:** broader foundational-change and entrenchment memo. Use `206-constitutional-change-and-amendment-rails.md` as the canonical front door for concrete amendment packets and thresholds, `171-constitutional-maintenance-and-amendment-ops.md` for the standing maintenance docket, `205-constitutional-review-observability-and-precedent-ledgers.md` for review/compliance visibility, and `288-constitutional-change-maintenance-and-review-stack-guide.md` for cluster routing.

**Purpose:** make foundational change *legible, slow when it must be slow, reversible when it can be reversible, and contestable always*—so “constitutional moments” don’t become capture moments.

**Person served:** the governed person who must be able to understand what changed, why, and how to challenge it—without insider access.

## Why this memo exists

Constitutions (or foundational charters) are the system’s **highest leverage code**. If change control is weak, everything else (rights, courts, oversight, elections, budgets) can be rewritten by a temporary coalition.

This memo defines a **portable constitutional change protocol** that can be used at micro‑local → national → supranational scopes (with scope‑appropriate consent rules).

(Anchors: Venice Commission guidance on amendment discipline and referendums; International IDEA primers on constitutional reform.)
(See: [BIB-VENICE-CONST-AMEND-2010], [BIB-VENICE-REFERENDUM-2022], [BIB-IDEA-CONST-AMEND-PRIMER].)

## Non‑negotiables (must hold across scopes)

1. **Legibility:** every proposed change has a stable ID and an explanation a non‑expert can audit.
2. **No stealth:** no “omnibus” bundles that force unrelated trades without explicit consent per item.
3. **No retroactivity by default:** constitutional change does not retroactively criminalize, disenfranchise, or strip vested rights without the highest scrutiny (and explicit justification).
4. **Contestability:** standing + windows to challenge procedure *and* substance.
5. **Capture resistance:** entrenchment can’t be used to freeze a captured order forever; but it also can’t be bypassed by “emergency” shortcuts.

## Core objects (registries + receipts)

### 1) Foundational Rule Registry (FRR)

A public, versioned registry that stores:

- `FID-*` — Foundational instrument IDs (constitution, charter, compact)
- `FSEC-*` — Section IDs (stable pointers)
- `FVER-*` — Versions (hashable; dated)
- `FLOG-*` — Change log entries (what changed, why, who proposed, who approved)

### 2) Amendment Proposal Packet (APP)

Every proposed change must publish an `APP-*` packet containing:

- scope + affected persons definition (who is bound)
- exact diffs: section‑level changes (`FSEC-*` pointers)
- intent + impact summary (plain language)
- risk tier (minor / structural / rights‑affecting / emergency)
- compatibility notes with treaties/rights charters (if any)
- what the proposer is *not* changing (anti‑misdirection)

### 3) Constitutional Change Receipt (CCR)

Issued at each gate:

- `CCR-PROPOSED` — proposal accepted for consideration (links to `APP-*`)
- `CCR-DELIBERATED` — deliberation record completed (links to `111`)
- `CCR-DECIDED` — adoption/rejection with reasons + vote tallies / consent artifacts
- `CCR-CONTESTED` / `CCR-REVIEWED` — procedural/substantive challenge outcomes

These receipts must be joinable to the archive’s **Decision Receipt** model (`DRR`) and **Rule Change Receipts** (`RCR-*`) in `118`.

## Change gates (the default pipeline)

### Gate 0 — Scope & consent classification (must)

Before any substantive vote, classify:

- **Scope:** micro-local / municipal / regional / national / supranational
- **Consent mechanism:** voice/exit rules and who counts as “the people” for this scope (`106`, `117`)
- **Risk tier:** minor → structural → rights‑affecting

Output: `CCR-SCOPE` with the selected pipeline and justification.

### Gate 1 — Notice + contestable framing (must)

- publish `APP-*` with an **anti‑bundle rule**: unrelated items get separate `APP-*` IDs
- minimum notice period proportional to risk tier
- publish “argument map” slots: pro / con / alternatives / minority reports (`111`)

Output: `CCR-NOTICE`.

### Gate 2 — Deliberation that binds (should for structural; must for rights-affecting)

At least one of:

- a representative assembly + transparency rules
- a stratified citizens’ panel (with `DR-*` receipts; see `119`)
- a mixed chamber model (e.g., elected + sortition oversight) for structural rewrites

Output: `CCR-DELIB`.

### Gate 3 — Decision + legitimacy proof (must)

Decision artifact depends on scope:

- legislative supermajority thresholds for structural changes
- referendum rules follow good-practice constraints (question clarity, campaign fairness, timing)
 (Anchor: [BIB-VENICE-REFERENDUM-2022].)
- for compacts/federations: dual consent (member units + affected persons) (`117`)

Output: `CCR-DECIDED` including:
- who approved, thresholds met, and dissent/minority reports
- explicit rights-floor compatibility statement (`LAW-1`, `SAFE-*`)
- implementation plan + effective date + transition/continuity plan (`109`, `114`)

### Gate 4 — Independent review window (must)

- bounded pre‑enactment review for procedure (and substance where applicable)
- emergency shortcut still triggers **post‑hoc review** and automatic sunset (`112`)

Output: `CCR-REVIEWED`.

### Gate 5 — Activation + replayability (must)

- FRR updates produce a new `FVER-*`
- publish a **past‑rule replay** interface: “what did the rule say on date X?” (`118`)
- publish a migration plan for institutions affected (appointments, courts, procurement, etc.)

Output: `FLOG-*` entry + `FVER-*`.

## Entrenchment discipline (avoid “forever locks”)

Entrenchment is allowed only when:

- it protects a **rights floor** or prevents obvious capture vectors
- it includes a *bounded* review trigger (e.g., generational review; see `122`)
- it never blocks the ability to restore contestability, elections, or remedies

Design primitive: **Entrenchment Register** (`ENT-*`) listing:
- what is entrenched
- why
- how it can be amended (if ever)
- review triggers + “breakglass” constraints

## Failure modes & circuit breakers (portable)

- **Omnibus trap:** split into separate `APP-*` IDs; if not, auto‑invalid (`CCR-INVALID`).
- **Timing manipulation:** blackout windows around elections/crises unless explicitly justified.
- **Emergency constitutionalism:** treat as exception control (`112`): automatic sunset + mandatory review + disclosure.
- **Identity capture (“who is the people”):** require `CCR-SCOPE` justification and allow challenge on standing/definitions (`106`).

## Minimal metrics (to keep this honest)

- `% of amendments with separate APP IDs per item` (anti‑bundle compliance)
- median days of notice by tier
- challenge rate + success rate (procedure vs substance)
- proportion of structural changes with a deliberative panel / mixed chamber
- reversal rate after activation (signals rushed change)

## Hooks into the archive

- `118-rulemaking-and-change-control.md` for versioning, diffing, replay
- `111-deliberation-to-decision-binding.md` for duty-to-respond + minority reports
- `119-selection-and-sortition-integrity.md` for panel selection receipts
- `112-exception-control-and-emergency-powers.md` for “constitutional emergencies”
- `122-intergenerational-and-future-protection.md` for generational review

---
