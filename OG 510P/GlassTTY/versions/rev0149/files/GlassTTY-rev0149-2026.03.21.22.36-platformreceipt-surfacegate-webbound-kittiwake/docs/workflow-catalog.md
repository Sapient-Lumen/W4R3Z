# Workflow catalog

This file expands the workflow contract into implementation-facing details.

## 1. surface-detect

Purpose:
- decide whether the current browser context belongs to a supported surface

Typical inputs:
- URL
- route hints
- DOM markers
- frame context

Success signals:
- stable surface key
- supportability status
- route or layout hint

Primary state outputs:
- `surface`
- partial `session`
- partial `navigation` when route continuity is relevant

Common failure classes:
- unsupported route
- logged-out or pre-auth route
- interstitial/consent wall
- route drift
- frame ambiguity

Evidence expectation:
- state snapshot or support bundle with route and cue summary
- browser-history witness when SPA route continuity is part of the support question

## 2. receiver-resolve

Purpose:
- decide which receiver/composer the next interaction should target

Typical inputs:
- DOM candidates
- focus state
- editable state
- frame hierarchy

Success signals:
- one primary receiver candidate
- confidence or resolution reason
- candidate inventory

Primary state outputs:
- `receiver`
- `diagnostics`

Common failure classes:
- multiple equally plausible receivers
- hidden or disabled composer
- modal takeover
- iframe targeting drift

Evidence expectation:
- receiver audit and candidate summary

## 3. composer-read

Purpose:
- read the current prompt draft or active compose text

Typical inputs:
- resolved receiver
- surface-specific editor extraction logic

Success signals:
- text recovered or explicit empty state
- editability status known

Primary state outputs:
- `composer`
- partial `receiver`

Common failure classes:
- masked editor model
- contenteditable drift
- placeholder-only false positives
- transient disabled state

Evidence expectation:
- state snapshot and receiver reference

## 4. composer-write

Purpose:
- write or replace prompt text in the active compose surface

Typical inputs:
- target receiver
- desired text
- replace/append mode

Success signals:
- post-write readback matches expectation sufficiently
- focus and editability remain valid

Primary state outputs:
- `composer`
- `action_outcome`

Common failure classes:
- write blocked by disabled state
- editor normalization changed text unexpectedly
- wrong receiver targeted
- browser permissions or clipboard fallback issues

Evidence expectation:
- action outcome plus before/after composer state

## 5. turn-submit

Purpose:
- trigger the current turn submission visibly in the browser

Typical inputs:
- ready composer state
- enabled submit control or equivalent shortcut path

Success signals:
- submission affordance activated
- generation state, turn list, or stable route/context changes afterward

Primary state outputs:
- `generation`
- `navigation` when context continuity could have changed
- `action_outcome`

Common failure classes:
- submit disabled
- modal interception
- shortcut mismatch
- route change before confirmation

Evidence expectation:
- action outcome and first post-submit generation state
- transient cue notes if present, but durable follow-up state preferred

## 6. generation-read

Purpose:
- classify current generation status

Typical inputs:
- streaming indicators
- stop button visibility
- assistant turn partials
- loading/error banners

Success signals:
- one of `idle`, `generating`, `blocked`, `error`, `unknown`
- optional stop availability
- confidence does not rely on a transient cue alone

Primary state outputs:
- `generation`

Common failure classes:
- ambiguous streaming cues
- stale DOM after submit
- route/tool mode overlays

Evidence expectation:
- state snapshot with cue summary
- if the only signal was transient, say so explicitly

## 7. latest-turn-read

Purpose:
- read the latest assistant turn in a structured way

Typical inputs:
- conversation DOM
- streaming/partial boundaries
- block parsing rules

Success signals:
- latest assistant turn found
- text and block summary extracted
- partial vs complete status classified honestly

Primary state outputs:
- `turn`
- partial `conversation`

Common failure classes:
- multiple candidate latest turns
- streaming partial ambiguity
- collapsed or virtualized turn list
- DOM drift in content blocks

Evidence expectation:
- turn snapshot and parsing note summary
- route/overlay note when latest-turn continuity could be ambiguous

## 8. support-capture

Purpose:
- emit a durable artifact set that can support or falsify a support claim

Typical inputs:
- current surface/workflow state
- relevant probe, fixture, or action artifacts

Success signals:
- support bundle or equivalent manifest written
- artifact refs attached to support truth

Primary state outputs:
- `support`
- `evidence`
- `action_outcome` where relevant

Common failure classes:
- partial capture with missing refs
- stale path assumptions
- no structured manifest

Evidence expectation:
- this workflow exists to produce evidence, so a missing artifact is itself a failure outcome
- route/history witness and transient-cue evidence when those affect interpretation

## Catalog rule

When a new workflow is added to the canon, extend `docs/canon-keys.md`, `docs/workflow-model.md`, and this file together.
