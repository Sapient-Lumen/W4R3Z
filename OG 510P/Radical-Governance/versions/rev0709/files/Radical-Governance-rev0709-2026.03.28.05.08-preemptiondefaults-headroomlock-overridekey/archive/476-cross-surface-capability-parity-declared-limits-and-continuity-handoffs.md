# 476 — Cross-surface capability parity, declared limits, and continuity handoffs

## One-line thesis

Consequential public-AI systems should preserve the same core capability classes across their major surfaces—or declare exact limits and continuity-preserving handoffs—so web, mobile, kiosk, PDF, API, assisted-digital, and operator projections do not quietly tell different governance stories.

## Why this matters

The archive already protects preview honesty, progressive disclosure, accessibility, and human-channel parity. What it still lacked was a stronger rule for **cross-surface semantic parity**.

Public institutions increasingly expose the same governed system through several projections at once: a web portal, a mobile-friendly page, an accessible PDF, a call-center script, a chatbot answer pane, a caseworker dashboard, an email notice, an API, or a printed packet. Layout differences are expected. Semantic differences are dangerous.

A small-screen view omits the reason a control is blocked. A PDF preserves the decision but drops the appeal route. A hotline can trigger a fallback that the portal never mentions. An operator console shows the current basis while the public surface shows only the last successful status. A public API exposes live state that the visible interface rounds away. Once that happens, users and reviewers do not merely have different convenience; they have different governance truth.

The problem is not that every surface must look identical. The problem is that people should not need folklore to know which rights, explanations, exports, or next actions still exist on a given surface.

## Pattern pack

### 1. Define capability classes that should survive across surfaces

At minimum, consequential systems should decide which of the following capability classes exist and where:

- read current state,
- explain current state,
- inspect governing basis,
- export or receive a packet,
- request review, correction, or fallback,
- complete or resume a draft,
- and perform authorized action.

The archive should not let these capabilities vary silently by surface.

### 2. Preserve semantic parity, not pixel parity

Surface parity does not mean every affordance, shortcut, or layout must match. It means:

- the same underlying truth can be inspected,
- repeating functions keep the same meaning,
- missing capabilities are declared explicitly,
- and any handoff to another surface preserves enough context to continue honestly.

### 3. Declare limits in one fixed grammar

If a capability is missing on a surface, that surface should say:

- what can be done here,
- what cannot be done here,
- why it is unavailable here,
- and which exact handoff preserves continuity.

Omission is not good enough. A missing action should not force the user to guess whether the task is forbidden, unsupported here, temporarily unavailable, or hidden behind another ritual.

### 4. Preserve context through handoffs

A handoff between surfaces should preserve as much relevant context as is safe and honest, such as:

- subject or case identity,
- current status view,
- draft or packet handle,
- current basis or version,
- and the exact reason for handoff.

A handoff should not silently reset the user into a generic home page or generic helpline with no continuity.

### 5. Keep repeating functions consistently identified

If the same function appears across several surfaces, keep its name and meaning stable enough that users do not have to relearn it every time. A route labeled `review`, `appeal`, `request human handling`, or `export packet` should not quietly change semantic scope across projections.

### 6. Measure parity defects as governance defects

Institutions should track when one surface lags or weakens another in consequential ways, for example:

- public web exposes appeal while mobile omits it,
- PDF explains status but not the clock,
- operator view shows degraded state while public view still looks green,
- or an assisted-digital script preserves fallback rights that the portal no longer mentions.

These are not purely UX defects; they are governance mismatches.

### 7. Keep smaller or constrained surfaces honest

A constrained surface may legitimately be read-only, preview-only, or handoff-first. That is acceptable only if it says so plainly and points to the stronger surface without pretending to offer the same governance function.

## Guardrails

- Do not let one surface become the “real” semantics while others rely on support lore.
- Do not let layout compression erase rights, clocks, reasons, or next actions.
- Do not hide missing capabilities behind absent buttons or generic documents.
- Do not hand off across surfaces without preserving honest continuity.
- Do not use inconsistent labels for repeating consequential functions.

## Failure modes

- **projection folklore**: staff or users must learn from rumor which surface can really complete the task.
- **semantic drift by surface**: different projections expose different governance truth for the same matter.
- **dead-end handoff**: a user is sent to another surface but loses case identity, basis, or draft continuity on arrival.
- **small-screen amputation**: constrained layouts omit the information needed to act or contest safely.
- **label drift**: repeating functions keep changing names or meaning across surfaces.

## Practical tests

A cross-surface parity discipline passes when it can answer yes to all of the following:

1. Are core capability classes named explicitly for the system?
2. If a capability is missing on one surface, does that surface explain the limit and the next honest handoff?
3. Can users carry meaningful context across surfaces rather than restarting from scratch?
4. Are repeating consequential functions identified consistently enough to remain predictable?
5. Are parity defects tracked as governance defects rather than only as cosmetic UI bugs?

## Compression rule for the archive

If the same governed system tells materially different users materially different truths depending on which surface they reached—and the archive cannot say **which capabilities survive where, which limits are declared, and how continuity handoffs work**—then it is still letting **surface variety impersonate governance parity**.
