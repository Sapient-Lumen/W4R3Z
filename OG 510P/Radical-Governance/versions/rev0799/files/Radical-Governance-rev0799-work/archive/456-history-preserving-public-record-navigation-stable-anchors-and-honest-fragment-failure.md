# 456 — History-preserving public-record navigation, stable anchors, and honest fragment failure

## One-line thesis

Consequential public-AI records, notice pages, case portals, and appeal surfaces should preserve stable addresses and anchors, create browser history only when the user crossed a meaningful state boundary, and fail honestly when a cited deep link or fragment no longer resolves.

## Why this matters

Governance increasingly happens through navigation, not only through content. A person receives a link to a public system card, a case page, an incident record, a notice-and-rights section, a review packet, or an appeal step. They rely on the URL, the fragment, the title, the back button, and the expectation that the path they just used can be retraced later. When those assumptions fail, governance meaning fails with them. A back action returns somewhere surprising. A deep link opens the right page but the wrong section. A route silently replaces history so the user cannot recover the earlier basis. A citation fragment no longer lands anywhere, yet the page pretends it succeeded.

That is not merely a browser nicety. Stable navigation is part of administrative memory. It lets affected people revisit the exact public explanation they were shown, lets reviewers trace the same route a person took, and lets records, notices, and citations remain inspectable over time. The archive should therefore treat history behavior, stable anchors, and deep-link honesty as governance concerns whenever consequential public-AI surfaces depend on them.

## Pattern pack

### 1. Preserve stable addresses for authority-bearing public surfaces

Authority-bearing surfaces such as public transparency records, system cards, appeal pages, incident updates, and rights explanations should have stable canonical addresses wherever practical. Cosmetic redesign or layout migration should not casually break the location people were told to trust.

### 2. Distinguish meaningful state transitions from cosmetic in-page movement

Not every scroll or tab shift deserves a browser-history entry. But when the user crosses a meaningful governance boundary, history should preserve it. Examples include:

- opening a different case or record,
- moving from summary to rights explanation,
- entering an appeal step,
- opening a different evidence packet,
- or switching between current head and frozen citation head.

The archive should distinguish legitimate replace-in-place updates from transitions that deserve durable back/forward meaning.

### 3. Keep anchors and fragments stable enough to cite

If a public record expects section-level citation, anchors should be named, stable, and reviewable. When headings change materially, the institution should prefer re-anchoring, redirects, or visible aliasing over silent anchor death.

### 4. Fail honestly when a deep link or fragment misses

A stale or malformed fragment should not quietly drop the user at the top of a long page and pretend the citation succeeded. The surface should say that the requested section was not found and, where possible, offer:

- the nearest surviving anchor,
- the canonical current head,
- the frozen historical head matching the citation period,
- or a clear re-anchoring explanation.

False success is worse than visible miss.

### 5. Preserve route witnesses when navigation shaped rights or review

If a public service claims that a person saw certain notice text, reached an explanation page, or was routed through a required review step, the archive should be able to preserve a witness of the route or cited target involved. Navigation can itself be part of the evidence story.

### 6. Keep visible labels flexible while preserving canonical targets

Short captions, translated labels, or mobile-friendly titles may vary, but the underlying canonical target for citation, history, and records should remain stable. Public legibility may change the label; it should not silently change the object that a link refers to.

### 7. Treat navigational breakage as a governance regression

A broken deep link, a misleading back-stack change, or a silent replace of a consequential earlier state should trigger review like other public-surface regressions. Navigation drift can erase accountability without changing a single sentence of governance prose.

## Guardrails

- Do not casually change authority-bearing URLs or anchors that people were told to rely on.
- Do not use silent replace-in-place behavior for meaningful governance transitions.
- Do not let stale fragments fail invisibly.
- Do not confuse changed captions or layout with permission to break canonical targets.
- Do not treat route evidence as unimportant when notice or appeal obligations depend on it.

## Failure modes

- **back-stack erasure**: a consequential earlier state is silently replaced and cannot be revisited.
- **false anchor success**: a fragment miss lands somewhere generic and looks correct enough.
- **citation rot**: public links remain syntactically valid while their cited target disappears.
- **label-target blur**: a friendly visible label changes the underlying object without warning.
- **route amnesia**: the institution cannot reconstruct which notice or explanation route the person actually took.

## Practical tests

A history-preserving public-record navigation discipline passes when it can answer yes to all of the following:

1. Do authority-bearing public surfaces keep stable canonical addresses wherever practical?
2. Do meaningful governance transitions create durable back/forward meaning instead of silent replacement?
3. Are section anchors stable enough for citation, re-anchoring, or historical redirection?
4. Does a stale or malformed fragment fail honestly instead of pretending it succeeded?
5. Can the institution preserve route or target witnesses when navigation itself mattered to notice, review, or appeal?

## Compression rule for the archive

If a person cannot answer **where they were, how they got there, and whether the cited section actually resolved**, then the public surface still lacks **governable navigation**.
