# 478 — Structured decision traces, minimal bindings, reason codes, and safe explain surfaces

## One-line thesis

Consequential public-AI actions should leave behind a stable decision-trace object that records the governing basis, route, inputs used, matched rule or model context, reason codes, obligations, and redactions in a compact safe form, so explanations, appeals, and incident review do not depend on backend folklore or prose reconstruction.

## Why this matters

The archive already requires authority maps, notices, appeal packets, contemporaneous witnesses, and portable review evidence. What it still lacked was a **stable trace shape** for the decision or routing act itself.

Without that shape, the institution can preserve plenty of fragments while still failing the central contestability question: *why did this route, recommendation, threshold, or action happen for this person, case, or packet on this basis?*

A reviewer can find the notice shown to the person but not the policy object that matched. A caseworker sees the result and maybe the score, but not which rule family fired or which human obligation remained open. A public explanation names broad reasons while the internal reconstruction depends on ad hoc screenshots, debug logs, staff memory, or vendor-only tooling. The archive needs one sharper primitive in the middle: a typed, reviewable decision trace that is detailed enough to challenge and safe enough to preserve.

## Pattern pack

### 1. Preserve one stable decision-trace object per consequential act

For each consequential routing, recommendation, threshold crossing, approval gate, denial, or similar act, preserve a compact trace object that can be linked to the case or packet and exported into review channels.

The trace should be stable enough to survive UI changes, vendor swaps, and packet export.

### 2. Record the governing basis, not only the output

A trace should say what basis governed the act, such as:

- ruleset, rubric, or policy head,
- model or prompt baseline,
- threshold or parameter set,
- disclosure head or form version,
- route or wizard version,
- dependency or retrieval basis where relevant.

A result without basis identity is only half an explanation.

### 3. Keep minimal bindings for what was actually used

The trace should preserve minimal, reviewable bindings such as:

- input categories or fields actually used,
- matched rule or retrieval family where applicable,
- reason codes or disposition codes,
- output class, score band, or route selected,
- obligations created for human review, override, notice, or follow-up,
- and any confidence, abstention, or unresolved-conflict state that shaped the next step.

The goal is not maximal state capture. It is enough structure to make the act replayable in meaning.

### 4. Separate safe public explanation from fuller internal trace

One trace may support several explain surfaces:

- public-facing explanation,
- operator-facing route explanation,
- reviewer packet,
- regulator or court export.

These surfaces may differ in detail, but they should all point back to the same trace object or digest rather than becoming unrelated stories.

### 5. Keep redactions and omissions explicit

If some fields cannot be revealed for privacy, security, safety, or legal reasons, the trace should preserve that as a fact through named redactions or omission markers.

A reviewer should be able to tell the difference between:

- data not used,
- data used but withheld from this surface,
- and data unavailable or unresolved at the time.

### 6. Preserve route trace for classification and handoff decisions

When the system routes a person toward one process, queue, wizard, human team, or appeal lane, the trace should preserve:

- the route options considered or applicable class,
- the selector or decision point that narrowed the route,
- the handoff destination,
- and whether the system abstained, escalated, or required human confirmation.

Routing is often where public consequence begins even before a final merits decision exists.

### 7. Use stable reason codes and machine-readable obligations

Free text alone is too brittle for longitudinal review. Traces should prefer stable reason codes, obligation codes, and typed disposition states that can survive surface rewriting while remaining explainable in plain language.

### 8. Treat trace extraction as a deployment requirement

If the institution cannot extract a stable trace for consequential acts without vendor heroics or ad hoc log mining, then the system is not yet mature enough for high-stakes operational reliance.

## Guardrails

- Do not turn the trace into a secret-leaking debug dump.
- Do not preserve only narrative explanation when structured bindings are available.
- Do not let public, operator, and reviewer explanations drift apart with no shared anchor.
- Do not treat route selection as beneath the decision-trace boundary.
- Do not hide redactions or omitted fields as if they were never relevant.

## Failure modes

- **story-without-trace**: a human-readable explanation exists, but no stable object ties it to the actual basis and route.
- **score-without-meaning**: a score or label is stored, but not the rule family, threshold, or obligation context that made it matter.
- **route amnesia**: the institution can show where a person ended up, but not why they were sent there.
- **silent redaction drift**: different surfaces omit different facts with no visible record of what was withheld.
- **vendor-only explainability**: the trace exists only inside tooling the operator cannot independently export or inspect.

## Practical tests

A decision-trace discipline passes when it can answer yes to all of the following:

1. Does each consequential act preserve one stable trace object or digestable reference?
2. Does the trace name the exact governing basis, not only the result?
3. Are inputs used, reason codes, output class, and resulting obligations preserved in minimal structured form?
4. Can public, operator, and reviewer explanations all point back to the same trace anchor?
5. Are redactions, omissions, abstentions, and routing decisions preserved explicitly rather than hidden in prose?

## Compression rule for the archive

If a consequential system can say **what happened** but cannot also show **which basis, which route, which bindings, and which obligations produced that act**, then it is still letting **narrative explanation impersonate contestable traceability**.
