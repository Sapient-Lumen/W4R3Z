# Filesystem shape audit page — link, metadata, invalid-name, and bundle-risk rollup interface spec

## Purpose

The archive already has deeper specs for portability, alias edges, and metadata fidelity.
What it still lacked was one ordinary rollup page for the operator who needs the answer before trouble starts:

> does this subject contain filesystem shapes that will preserve faithfully, downgrade, fork into conflicts, decompose visibly, or require review before cross-seat use?

This page exists so operators do not have to reconstruct shape risk from several specialist pages and support articles.

## Core rule

A serious sync product should expose a first-class **filesystem shape audit** that rolls up the highest-risk object-shape facts into one page while still linking to deeper specialist pages when needed.

The audit must be able to summarize at least four families together:

1. alias edges and special links
2. metadata-channel / xattr fidelity
3. invalid-name / portability rewriting risk
4. bundle / package cohesion risk

## Fixed review order

Every serious filesystem-shape audit page should render the same sections in the same order:

1. **Overall fidelity verdict**
2. **Risk family rollup**
3. **Affected object examples**
4. **Required policy or migration actions**
5. **Receipt and validation horizon**

### 1) Overall fidelity verdict

This section should answer:

- whether the subject is `portable`, `portable-with-warnings`, `shape-changing`, or `blocked`
- which target profile the verdict is relative to
- when the verdict was last validated

The operator must be able to answer: **is this subject safe to move between my current seats without hidden shape changes?**

### 2) Risk family rollup

This section should summarize at least:

- alias-edge risk
- metadata fidelity risk
- invalid-name risk
- bundle cohesion risk

Each family should show:

- severity
- count of affected objects
- dominant reason
- drill-in destination

The operator must be able to answer: **what category of shape problem is actually present here?**

### 3) Affected object examples

This section should show concrete examples with columns such as:

- path
- risk family
- predicted downgrade or rewrite
- recommended next action

The operator must be able to answer: **which exact objects are dangerous, not just which abstract rule exists?**

### 4) Required policy or migration actions

This section should show:

- block until moved
- permit with reduced fidelity
- change metadata policy
- split target folder / add separate subject for link targets
- rename for portability
- keep local-only

The operator must be able to answer: **what should I do about the risky shapes I found?**

### 5) Receipt and validation horizon

This section should show:

- last audit receipt
- target profile used
- expiry / revalidate trigger
- whether the result is complete or sample-based

## States

Use a small stable vocabulary:

- `portable`
- `portable-with-warnings`
- `shape-changing`
- `reduced-fidelity accepted`
- `blocked until review`

## Main surface

A compact **Filesystem shape audit** card should show:

- overall fidelity verdict
- total risky object count
- top two risk families by severity
- primary action: `Inspect filesystem shape`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Verdict strip

Shows:

- subject
- target profile
- fidelity verdict
- validation time

### Pane B — Risk family rollup

Columns:

- family
- severity
- affected count
- dominant reason
- drill-in

Families should at least include:

- alias edges
- metadata channels
- invalid names / normalization
- bundle cohesion

### Pane C — Affected examples

Shows representative and highest-risk paths.

### Pane D — Actions

Rows may include:

- `Open link-edge review`
- `Open metadata fidelity review`
- `Rename for portability`
- `Split into separate subject`
- `Accept reduced fidelity`
- `Block propagation`

### Pane E — Receipts

Shows:

- last audit receipt
- accepted reduced-fidelity receipts
- pending review items

## CLI parity

Minimum commands:

- `anonsync shape-audit show <subject>`
- `anonsync shape-audit validate <subject> --target-profile <profile>`
- `anonsync shape-audit review <subject> --family <family>`
- `anonsync shape-audit receipt <receipt-id>`

## Acceptance criteria

A user can:

- see one rollup verdict for filesystem-shape fidelity on the current target profile
- identify the dominant risk family without reading several specialist docs first
- inspect concrete affected paths and predicted downgrade classes
- pivot into deeper alias-edge or metadata pages when needed
- prove later which audit verdict and target profile were accepted
