# Surface mismatch page: direct-link, missing action, and browser-blocker diagnosis interface spec

## Purpose

The archive already had import fallback and control-launch doctrine.
This document makes one narrower diagnosis page concrete.

The page exists to answer one ordinary operator question:

> what exactly mismatched between this action and this surface — direct-link support, protocol registration, browser health, role, policy, or artifact validity?

## Core decision

Every seat that supports browser-mediated or cross-channel entry must expose one first-class **Surface mismatch** page.
That page is the semantic home of:

- mismatch class
- current surface facts
- expected fast path
- blocker diagnosis ladder
- typed fallback tools
- after-repair retest plan

The product must not force the operator to infer the answer from absent buttons, pop-up blockers, browser prompts, or generic `paste manually` advice.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. mismatch strip
2. current-surface facts card
3. attempted fast-path card
4. diagnosis ladder
5. typed fallback tools
6. retest and residue card
7. recent mismatch receipts

### 1) Mismatch strip

Show:

- current surface kind
- attempted action or artifact
- mismatch class
- strongest next-safe action

Allowed mismatch classes:

- `direct-link unsupported on this surface`
- `protocol registration missing`
- `browser blocked external app handoff`
- `browser compatibility issue`
- `extension or content blocker interference`
- `trust or session gate not met`
- `action hidden by role or policy`
- `artifact malformed or unsupported`

### 2) Current-surface facts card

Show:

- surface kind and endpoint
- current trust/session posture
- whether the runtime is healthy
- whether the surface is first-class, fallback-only, or degraded
- whether the action should normally exist here

This card should answer `what exactly is this surface supposed to be capable of?`

### 3) Attempted fast-path card

Show:

- attempted accelerator (`browser-open`, `protocol-url`, `share affordance`, `QR handoff`, `file import`, `other`)
- whether the artifact itself appears healthy
- whether the fast path depends on browser, OS, extension, or role state
- whether the same action exists in a typed non-accelerated lane

This card should answer `what shortcut failed, and what did it depend on?`

### 4) Diagnosis ladder

Render diagnoses from most likely to least likely, with each rung stating:

- diagnosis label
- evidence for it
- what it is not
- smallest confirming check
- safest corrective action

A good ladder makes these distinctions explicit:

- `the artifact is fine, but this surface cannot consume it`
- `the artifact is fine, but the browser blocked the handoff`
- `the action exists, but rendering or extension interference hid it`
- `the action is legitimately unavailable because role/policy blocks it`
- `the artifact itself is broken or unsupported`

### 5) Typed fallback tools

Always show:

- open typed import lane
- open action-availability page
- create reviewed handoff
- retry after trust/session repair
- clear local mismatch residue and retest

The fallback tools must preserve semantics.
They may not collapse everything into one opaque text box.

### 6) Retest and residue card

Show:

- what state will be rechecked after repair
- whether the same action will reappear here or only after channel switch
- what residue may remain (browser permission memory, extension state, stale session, stale draft, stale tab)
- which receipt will prove the mismatch was resolved or accepted as structural

### 7) Recent mismatch receipts

Show recent receipts with:

- mismatch class
- attempted fast path
- diagnosis chosen
- correction applied or fallback chosen
- resulting action lane

## Acceptance criteria

This spec is satisfied when:

- direct-link unsupported, browser-blocked, role-blocked, and malformed-artifact states are visibly different answers
- a missing affordance is not automatically treated as a policy denial
- typed fallback tools stay on the diagnosis page
- repair and retest produce receipts instead of relying on operator memory
