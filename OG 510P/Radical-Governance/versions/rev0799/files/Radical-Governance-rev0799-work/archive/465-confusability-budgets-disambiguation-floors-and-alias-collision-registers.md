# 465 — Confusability budgets, disambiguation floors, and alias-collision registers

## One-line thesis

Consequential public-AI archives should budget confusability across system names, case states, model families, source labels, and decision routes, and require explicit disambiguation when nearby labels could cause misrouting or mistaken authority.

## Why this matters

A surprising amount of governance failure begins with two things that look too similar.

A case state says “under review” in one place and “review requested” in another. A public card names one model family while an internal register abbreviates it to a nearby sibling. Two queues differ only by a color or suffix. A stale alias still resolves to a retired disclosure head. A source label says “official guidance” without clarifying whether it means law, internal policy, vendor documentation, or a machine summary of any of those.

The archive already values stable identifiers, canonical heads, exact audience lanes, durable case cues, and witness-backed reconstruction. What it still lacked was one note for the **confusability problem itself**: the fact that labels, names, and route names can become governance hazards when they are too easy to mistake for one another. The archive should therefore treat high-stakes label collisions as reviewable risks, not as mere style issues.

## Pattern pack

### 1. Inventory the high-stakes labels that carry authority or routing consequences

At minimum, institutions should identify labels whose confusion could change action, such as:

- system and model names,
- workflow and queue names,
- case-state labels,
- approval and review statuses,
- source and citation labels,
- public versus internal artifact names,
- current versus historical record heads,
- and emergency, pause, or fallback route names.

Not every label deserves the same scrutiny. These ones do.

### 2. Test nearby labels for likely confusion

The archive should look for confusable pairs or families, including:

- near-identical wording,
- abbreviations that collapse distinct meanings,
- reused historical names,
- labels distinguished only by color or placement,
- singular/plural or tense changes that alter state meaning,
- and internal shorthand that looks authoritative when copied into public surfaces.

A small difference that disappears under service pressure is not a safe difference.

### 3. Require a minimum disambiguation floor where the risk is real

Where confusability matters, labels should add enough extra context to separate meaning, such as:

- owner or authority,
- lifecycle phase,
- date or version,
- audience class,
- environment,
- case identifier,
- or route consequence.

The archive should prefer a slightly longer truthful label over a short label that routinely misroutes people or claims.

### 4. Preserve aliases visibly instead of silently reusing them

Historical or colloquial names may still need to resolve for discoverability. When that happens, the archive should:

- preserve the alias,
- point it to the canonical target,
- warn when the alias is historical or potentially confusing,
- and forbid silent reuse of the same alias for a materially different object.

Alias support should improve navigation, not blur authority.

### 5. Force abstention or escalation when the label match is uncertain

If a workflow cannot reliably tell which object, route, or state a user or operator means, it should:

- ask for clarification,
- show the nearest distinct candidates,
- route to a safer fallback,
- or refuse the stronger action until the ambiguity is resolved.

Confident guessing is often the failure mode.

### 6. Keep an alias-collision register for repeated or unresolved confusions

Repeated confusion should leave behind a small durable object recording:

- the confusable labels,
- the context in which confusion occurred,
- the observed consequence or near miss,
- the chosen rename, alias, or warning treatment,
- and the trigger for reopening the issue.

This turns recurring label failure into an operational governance signal.

### 7. Carry disambiguation into public and internal surfaces alike

Disambiguation should not exist only in internal engineering notes. It should appear where people actually act:

- public disclosures,
- operator dashboards,
- approval packets,
- appeal paths,
- runbooks,
- and monitoring or incident surfaces.

A label that is exact only backstage is still too dangerous at the front door.

## Guardrails

- Do not treat label collisions as mere editorial taste when they can change routing or authority.
- Do not distinguish high-stakes states only by color, position, or staff memory.
- Do not silently reuse retired or historical names for new governance objects.
- Do not let internal shorthand leak into public records without disambiguation.
- Do not guess between confusable high-stakes targets when clarification is still possible.

## Failure modes

- **sibling-system swap**: staff or the public act on the wrong system, model, or queue because the names are too close.
- **state-label collapse**: nearby status phrases are treated as equivalent even though they carry different rights or next actions.
- **stale alias reuse**: an old name keeps circulating and inherits current authority it no longer deserves.
- **source-label laundering**: weak or mixed-origin material is mistaken for stronger official authority because the label is too vague.
- **misroute by shorthand**: an abbreviated command or route name quietly sends a case down the wrong path.

## Practical tests

A confusability-aware archive passes when it can answer yes to all of the following:

1. Are the labels that carry routing or authority consequences explicitly inventoried?
2. Are likely confusable pairs or families tested rather than discovered only through failure?
3. Do risky labels carry a minimum disambiguation floor such as owner, phase, version, audience, or identifier?
4. Are historical aliases preserved visibly instead of being silently reused?
5. Does uncertain label matching trigger clarification, fallback, or refusal rather than confident guessing?

## Compression rule for the archive

If two high-stakes labels can be **easily mistaken for one another** and the system still chooses one without explicit disambiguation, then it is still letting **name similarity impersonate governance certainty**.
