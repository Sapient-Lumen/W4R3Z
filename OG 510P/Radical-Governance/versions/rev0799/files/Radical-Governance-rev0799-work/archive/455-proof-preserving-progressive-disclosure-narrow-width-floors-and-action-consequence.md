# 455 — Proof-preserving progressive disclosure, narrow-width floors, and action consequence

## One-line thesis

Consequential public-AI interfaces may compress layout, stack panels, or rely on progressive disclosure, but they should preserve an accessibility-aware semantic minimum that keeps provenance, scope, blocker reason, future effect, and action consequence reachable without guesswork.

## Why this matters

Governance promises often disappear first on the smallest or densest accessibility surfaces. A desktop review page may show authority basis, scope, blocker reason, effective audience, future effect, and appeal route, while the same service on mobile, in narrow-width panels, dense tables, or assistive layouts collapses those facts into a status dot, a one-word button, and a hidden drawer. The system still claims parity, but the governing meaning has moved behind interaction debt.

That is not merely a design bug. For consequential public AI, it is a governance failure. A person should not need extra dexterity, screen width, product memory, or institutional insider knowledge to learn whether an action is blocked, whether a route is advisory only, what changes if they proceed, or which basis currently governs. Progressive disclosure may reduce visual clutter. It should not reduce semantic truth.

The archive should therefore impose a narrow-width semantic floor. Rendering may change. Compression may change. Dense rows may exist. But a consequential surface should still preserve access to the facts that make an action safe to understand.

## Pattern pack

### 1. Preserve a semantic minimum across layouts

Every consequential narrow or dense rendering should still expose, directly or within one honest step:

- provenance or governing source,
- scope or audience class,
- strongest honest current answer,
- blocker or risk reason where relevant,
- future effect or continuity consequence,
- and action consequence when a user can proceed.

If one of those disappears entirely, the surface has become semantically weaker, not merely smaller.

### 2. Compress chrome before proof

When space is scarce, interfaces should shed in roughly this order:

- decorative chrome,
- repeated labels,
- secondary history,
- long evidence lists,
- extended examples,
- then optional explanatory prose.

They should not first hide provenance, blocker reason, or consequence.

### 3. Keep action and consequence adjacent

A consequential button, link, or control should not float free from what it changes. If a narrow layout shows **Apply**, **Continue**, **Publish**, **Dismiss**, or **Approve**, the same compact surface should still keep nearby:

- what changes now,
- what does not change,
- what becomes visible or live afterward,
- what harder-to-undo state follows,
- and what proof or receipt the system will create.

The archive should resist action-first layouts that rely on user memory for the rest.

### 4. Preserve blocker truth in text, not dots alone

A blocked or risky state should not collapse into a color token, icon, or badge with hidden semantics. Narrow-width designs should preserve a short textual blocker reason, such as:

- missing approval basis,
- stale witness,
- unresolved authenticity,
- outside audience lane,
- appeal path unavailable,
- or material change pending refresh.

If the user must open three layers to learn why the action is blocked, the surface is already too compressed.

### 5. Require one-step expansion to the proof payload

Dense tables and mobile cards may defer full explanation, but the full proof payload should be one honest step away, not buried in a navigation maze. Expansion should resolve into the same governing object the compact view claims to summarize.

### 6. Preserve parity across input modes and assistive use

Touch, keyboard, screen reader, and narrow visual use may reach the payload differently, but the same core meaning should remain available. Accessibility is not satisfied when the desktop mouse path reveals facts that the assistive or narrow path only implies.

### 7. Treat layout-specific semantic loss as reviewable drift

A release that preserves logic but hides material governance meaning on one layout or mode should reopen review. Layout drift can change effective rights understanding even when the backend stays constant.

## Guardrails

- Do not hide provenance or governing basis first when compressing layout.
- Do not show action verbs without nearby consequence truth.
- Do not use color, iconography, or transient affordances as the only carrier of blocker meaning.
- Do not make full proof reachable only through a navigation hunt.
- Do not claim parity when one layout preserves semantics that another only hints at.

## Failure modes

- **layout amputation**: narrow surfaces drop the facts that made the wide surface trustworthy.
- **button without aftermath**: action controls remain visible while consequence truth disappears.
- **status-dot opacity**: blocker reasons collapse into badges or colors without text.
- **expansion maze**: the proof payload exists but is too many steps away to govern real use.
- **mode asymmetry**: desktop or insider paths retain meaning that mobile or assistive paths lose.

## Practical tests

A proof-preserving progressive-disclosure discipline passes when it can answer yes to all of the following:

1. Does every consequential compact surface preserve provenance, scope, current answer, blocker reason, future effect, and action consequence directly or within one step?
2. Does compression remove chrome before it removes load-bearing proof?
3. Are action verbs still adjacent to what changes and what receipt or public consequence follows?
4. Are blocker reasons expressed in text rather than only in dots, colors, or icons?
5. Can assistive, keyboard, mobile, and dense-table users still reach the same governing meaning?

## Compression rule for the archive

If a dense or narrow surface keeps the **button** but loses the **basis, blocker, or consequence**, then the interface is no longer a smaller truthful surface; it is a **semantic downgrade**.
