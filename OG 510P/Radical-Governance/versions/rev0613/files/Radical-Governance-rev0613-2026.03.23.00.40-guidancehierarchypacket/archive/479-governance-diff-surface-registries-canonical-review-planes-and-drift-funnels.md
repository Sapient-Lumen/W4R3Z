# 479 — Governance diff-surface registries, canonical review planes, and drift funnels

## One-line thesis

Consequential public-AI programs should maintain a canonical registry of governance diff surfaces so review, release, and audit can say which change planes exist, which ones were checked, and which new surface types require explicit admission instead of silently creating fresh drift territory.

## Why this matters

The archive already requires material-change refresh, coupled follow-through matrices, baseline pinning, queue honesty, and canonical public heads. What it still lacked was a standing answer to a simpler but deeper review problem: *what are the change planes that count here at all?*

In practice, drift hides wherever the institution forgot to treat something as a review surface. Prompt text changes while the model card stays old. Thresholds move but the public explanation template does not. A language variant changes while the accessibility variant lags. A hotline script, operator macro, retention join, or dashboard rule changes outside the formal release packet because nobody treated it as a canonical diff plane. Later, teams review what they remembered to diff rather than what the program actually exposes.

The archive therefore needs one persistent registry layer under the per-change matrix: a compact list of the governance surfaces that must be considered reviewable drift territory in the first place.

## Pattern pack

### 1. Keep one canonical registry of governance diff surfaces

Each governed program should maintain one registry of typed change planes such as:

- model, prompt, retrieval, and threshold surfaces,
- rules, forms, questionnaires, and decision trees,
- public notices, cards, and official communications,
- operator macros, runbooks, and training materials,
- appeal packet schemas, logs, and retention joins,
- dashboard metrics, alert thresholds, and blocker vocabularies,
- accessibility, language, mobile, PDF, API, and assisted-digital variants,
- supplier declarations, dependency records, and external evidence heads.

### 2. Treat the registry as the standing review funnel

The registry should not replace per-change review. It should tell reviewers what kinds of diffs are canonical candidates whenever a material change opens.

That turns review from "remember the obvious files" into "walk the registered surfaces."

### 3. Give each surface a typed diff expectation

For each registered surface, say what counts as a meaningful delta, for example:

- textual diff,
- schema diff,
- threshold diff,
- route-map diff,
- linkage or join-key diff,
- head or version diff,
- parity-only review,
- or manual attestation that no machine diff is possible.

A surface can still be reviewable even when the diff must be partly human.

### 4. Require rationale before adding new surface types

If a program invents a new governance-relevant surface type, such as a new operator macro family or public answer layer, it should be added to the registry with a reason for why it matters, how it is reviewed, and which claims depend on it.

This prevents drift territory from expanding in silence.

### 5. Distinguish critical, supporting, and observational surfaces

Not every surface has the same release weight. The registry should say whether a surface is:

- critical to legality, rights, or public guidance,
- supporting but required for safe operation,
- or observational and useful mainly for diagnosis or monitoring.

That helps the archive block the right claims without pretending every surface has equal force.

### 6. Link the registry to change objects and closure packets

Every material change object should reference the registered surfaces it touched, left unchanged, or explicitly excluded. Closure packets should be able to say not only what changed, but which canonical surfaces were reviewed and why some were not.

### 7. Use the registry to expose hidden drift classes

Repeated review gaps should be turned into named surface classes. Examples include:

- stale hotline scripts,
- untranslated corrections,
- mismatched notice templates,
- supplier-side threshold changes,
- or dashboard logic that no longer matches the live queue semantics.

The registry becomes a learning mechanism for institutional blind spots.

## Guardrails

- Do not assume source code diff covers the full governance surface.
- Do not let unregistered public or operator surfaces become de facto authority planes.
- Do not treat manual-review-only surfaces as exempt from registry status.
- Do not add new surface types without naming their review method and claim impact.
- Do not collapse critical and observational surfaces into one undifferentiated checklist.

## Failure modes

- **forgotten plane drift**: a governance-relevant surface changed because nobody treated it as a review surface at all.
- **code-only review fiction**: technical diff passed while public, operator, or parity surfaces quietly diverged.
- **surface sprawl without admission**: new artifact families appear and become consequential before the registry catches up.
- **checklist without typing**: reviewers mark surfaces as reviewed but cannot say what kind of delta they were looking for.
- **criticality blur**: dashboards, notices, thresholds, and runbooks are reviewed with no distinction in release weight.

## Practical tests

A diff-surface discipline passes when it can answer yes to all of the following:

1. Is there one canonical registry of governance-relevant change planes?
2. Does each surface carry a typed diff expectation or explicit review method?
3. Must new surface types be admitted explicitly before they count as governed surfaces?
4. Can a change object show which registered surfaces were touched, checked, excluded, or still pending?
5. Does the registry distinguish critical, supporting, and observational surfaces for release decisions?

## Compression rule for the archive

If a consequential program can say **we reviewed the change** but cannot also say **which canonical governance surfaces exist and which diff planes were actually checked**, then it is still letting **forgotten surfaces impersonate reviewed stability**.
