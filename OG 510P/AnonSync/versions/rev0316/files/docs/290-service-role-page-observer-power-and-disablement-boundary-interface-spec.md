# Service role page — observer power and disablement boundary interface spec

## Purpose

The archive already has disclosure objects and route-policy language.
What it still lacked was one explicit page for a second ordinary question that often follows immediately after visibility:

> what does this external service actually do for me, what can it never do, and what exactly changes if I disable or replace it?

This page exists so the product can answer `tracker`, `relay`, `landing page`, `telemetry`, `update service`, or `license service` with capability ceilings rather than mythology.

## Core rule

Every external service role must publish three separate truths:

1. **what it can observe**
2. **what it can influence operationally**
3. **what it can never do**

A service role page is not a marketing FAQ.
It is a capability ceiling and disablement review.

## Fixed review order

Every serious service-role page should render the same sections in the same order:

1. **Role and capability ceiling**
2. **Current dependence**
3. **Disablement / replacement review**
4. **Residual reliance and fallback**
5. **Receipt and operational notes**

### 1) Role and capability ceiling

This section should answer:

- service class under review
- whether the service is vendor-run, private operator-run, or peer-run
- what the service can observe
- what the service can influence (`discovery`, `relay`, `handoff`, `update-awareness`, `accounting`, etc.)
- what the service can never do (`read plaintext`, `mutate content`, `revoke local data`, `impersonate peer approval`, etc.)

The operator must be able to answer: **what powers does this service really have, and what powers does it categorically lack?**

### 2) Current dependence

This section should show:

- whether the current subject/seat actively depends on the service
- whether that dependence is `required`, `optional convenience`, `temporary fallback`, or `host-wide only`
- what feature is currently using the service
- whether a private replacement already exists

The operator must be able to answer: **am I relying on this service right now, or is it merely available?**

### 3) Disablement / replacement review

This section should show:

- what exact capability disappears if the service is disabled
- whether the service can be replaced by manual workflow, private infrastructure, or another direct path
- whether the service can be disabled per subject, per policy, or only host-wide
- whether the current disablement is reversible without continuity loss

The operator must be able to answer: **what breaks, what remains, and what replacement path is honest if I turn this off?**

### 4) Residual reliance and fallback

This section should show:

- any cached or already-issued state that still reflects earlier use
- whether new operations will still try to fall back to the service unless another policy changes
- whether earlier handoff or account relationships remain visible
- whether the service was only used for bootstrap and is now inactive

The operator must be able to answer: **does disabling the service truly remove current reliance, or merely stop future fresh use?**

### 5) Receipt and operational notes

This section should show:

- disablement / replacement receipts
- prior acknowledgments of role ceilings
- diagnostic notes for common failure or degraded cases
- exportable service-role summary for audit or support packets

The operator must be able to answer: **what proof shows how this service role is configured and what ceiling was accepted?**

## States

Use a small stable vocabulary:

- `not in use`
- `available convenience`
- `active fallback`
- `required now`
- `private replacement active`
- `disabled with residue`
- `disabled cleanly`

## Main surface

A compact **Service role** card should show:

- role name
- current dependence class
- strongest capability it has
- strongest capability it lacks
- primary action: `Inspect service role`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Capability ceiling strip

Shows:

- service role
- current dependence
- strongest observable facts
- strongest non-capability claim

### Pane B — Power table

Columns:

- service function
- active here
- operational influence
- content visibility
- hard limit / cannot-do

### Pane C — Disablement review

Rows may include:

- `disable tracker`
- `disable relay`
- `disable landing-page handoff`
- `disable update checks`
- `disable telemetry`
- `replace vendor service with private equivalent`

### Pane D — Fallback and residue

Shows:

- manual replacement path
- private replacement path
- residual account/contact state
- stale or cached use still in play

### Pane E — Receipts

Shows:

- disablement receipts
- replacement receipts
- prior role-ceiling acknowledgments

## CLI parity

Minimum commands:

- `anonsync service-role show <role>`
- `anonsync service-role preview-disable <role>`
- `anonsync service-role disable <role> --review <review-id>`
- `anonsync service-role replace <role> --with <private-role>`
- `anonsync service-role receipt <receipt-id>`

## Acceptance criteria

A user can:

- tell what an external service can and cannot do
- distinguish observation from operational influence
- see whether the current system actually depends on the service
- preview the cost of disabling or replacing it
- prove later that the accepted service ceiling or disablement choice was reviewed

