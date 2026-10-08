# Manual claim page: key, link, QR equivalence, and no-approval warning interface spec

The archive already separates delivery carrier from authority-bearing artifact and already gives strong intake-review doctrine.
What it still lacked was one ordinary page for the operator who is pasting, scanning, or importing something manually:

> what did I just bring in, which carriers are equivalent, and does this path include approval, remembered requester identity, or none of that at all?

Current Resilio docs still make this seam obvious enough to justify a replacement page.
They still distinguish raw keys from links, still treat QR as another way to deliver share capability, still show only minimal browser preview before local parse, and still let mobile and desktop flows route through manual add/paste/scan steps.
That is exactly the kind of truth a product should own on one page.

## Page promise

The Manual claim page should make five answers adjacent:

1. artifact parsed now
2. carrier equivalence now
3. approval model now
4. target-bind implications now
5. strongest honest next action

The page exists so `Paste key or link` stops being a semantic blind spot.

## Fixed page order

Every manual-claim page should render the same sections in the same order:

1. **Intake snapshot**
2. **Parsed artifact and carrier equivalence**
3. **Approval / requester consequences**
4. **Bind and arrival review**
5. **Action ladder**
6. **Receipt promise**

### 1) Intake snapshot

This section should show:

- ingestion carrier used (`paste`, `scan`, `open-wrapper`, `import file`, etc.)
- artifact families successfully parsed
- whether parse is complete, partial, or carrier-only preview
- whether the subject is already known locally
- whether further local review is required before any bind or approval request

The operator should be able to answer: **what exactly did the product parse from what I brought in?**

### 2) Parsed artifact and carrier equivalence

This section should show:

- canonical artifact identity if known
- whether pasted text, QR, and browser wrapper are equivalent views of one artifact
- whether the current artifact is raw capability material, approval-capable claim material, or local preview only
- what the current carrier omitted or wrapped

The operator should be able to answer: **which parts are the same authority object and which parts are only delivery clothing?**

### 3) Approval / requester consequences

This section should show:

- whether this artifact ever produces a requester approval step
- whether a requester identity is expected later
- whether the artifact is auto-admitting by design, only pending target choice, or blocked on approval policy
- whether the current operator should treat the artifact as high-risk because it bypasses requester review entirely

The operator should be able to answer: **does this path include identity review, remembered-requester logic, or no approval lane at all?**

### 4) Bind and arrival review

This section should show:

- candidate bind path or target seat
- whether target choice remains open
- whether existing bytes or prior subject identity create merge / reuse / duplicate risk
- whether this path is local-only preview, live claim preparation, or already committed bind

The operator should be able to answer: **what local consequence would follow if I continue from this parsed artifact?**

### 5) Action ladder

Example actions:

- `Continue to target review`
- `Require claim page with requester review`
- `Treat as raw capability and show elevated warning`
- `Abort and clear intake`
- `Compare against existing local subject`
- `Open full offer / claim detail`

The primary action should be the safest truthful action, not the shortest label.

### 6) Receipt promise

A manual-claim receipt should preserve:

- ingestion carrier used
- parsed artifact family
- carrier-equivalence verdict
- approval-model verdict
- target/bind consequence preview
- next action taken

The operator should be able to answer: **what exactly was imported, and what semantic lane did it put me into?**

## Compact row contract

A trustworthy compact row should preserve the following order:

1. intake carrier
2. artifact phrase
3. approval phrase
4. bind phrase
5. next honest action

Example:

```text
Pasted text   parsed as raw capability string for subject Project Alpha   no requester-proof lane implied by this artifact; treat as elevated-risk claim path   target not chosen yet, existing local bytes need review   Review
```

## What this page must never imply

The page must never imply that:

- every imported artifact will later produce an approval request
- browser preview is equivalent to authoritative local parse
- QR always means `mobile-safe` or `low-risk`
- raw capability material and reviewed claim material are interchangeable
- target-path choice is a cosmetic detail once parsing succeeded

## Result

This page is how AnonSync borrows Resilio's carrier flexibility without cloning the weaker habit of letting manual paste/scan/import become a generic intake box that hides approval differences and bind consequences.
