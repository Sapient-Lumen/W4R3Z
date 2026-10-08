# Import artifact page: handoff health, typed preview, and seat target interface spec

## Purpose

`238` established the semantic contract for browser handoff and fallback intake.
This document makes it concrete as one page.

The page exists to answer one ordinary operator question:

> what artifact did the product just receive or fail to receive, how healthy was the handoff, which seat should own the import, and what will happen if I continue?

## Core decision

Every seat must expose one first-class **Import artifact** page.
It is the canonical intake lane for:

- deep-link handoff
- typed paste
- QR scan result
- imported artifact file
- browser-local handoff repair

Fast paths may land here already prefilled.
They do not replace the page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. source and handoff verdict
2. artifact preview
3. target seat chooser
4. consequence preview
5. fallback tools
6. import receipts
7. expert details drawer

### 1) Source and handoff verdict

Show:

- source kind (`deep link`, `paste`, `qr`, `file`, `unknown`)
- source app or browser when known
- one handoff health verdict
- whether local runtime ownership was acquired

Allowed handoff verdicts:

- `handoff succeeded`
- `protocol registration missing`
- `browser blocked scheme`
- `web control cannot consume direct link`
- `artifact malformed`
- `artifact unsupported`

This verdict must distinguish transport failure from artifact invalidity.

### 2) Artifact preview

Show typed preview rows such as:

- artifact class
- issuer / origin hint
- target subject or family
- expiry or freshness
- authority / capability summary
- parse confidence

The preview must remain available before any adopt/claim/import action.

### 3) Target seat chooser

If more than one local seat/runtime can receive the artifact, show explicit target rows:

- seat name
- current readiness
- why this seat is eligible or ineligible
- whether it matches the handoff's original target intent

This chooser is required because the browser's chosen handoff target is not always the only honest destination.

### 4) Consequence preview

Before apply, show:

- what subject will be created or changed
- whether this is inspect-only, inbox-only, adopt, claim, join, or update
- whether future-arrival or remembered-trust consequences exist
- whether any warnings or blockers remain

The apply button text must match the consequence.
It should say `Inspect only`, `Import to inbox`, `Adopt`, `Join`, or similar — not generic `Continue`.

### 5) Fallback tools

This section always remains visible and includes:

- paste artifact text
- rescan / reload handoff
- upload artifact file
- switch target seat
- clear broken handoff state

The fallback lane must not reduce the artifact to a generic opaque text box.

### 6) Import receipts

Show recent intake receipts with:

- source kind
- handoff verdict
- target seat
- artifact class
- final action taken
- result state

### 7) Expert details drawer

Hide raw parse, raw handoff metadata, and low-level protocol diagnostics behind an expert drawer.
These details are valuable, but they are not the page's semantic center.

## Empty and failure states

If no artifact is present, the page should still be usable.
It should render a ready intake lane rather than a dead blank state.

If the artifact is malformed, the page should preserve:

- source kind
- parse confidence
- strongest likely class if any
- exact reason it could not be typed
- safe next actions

## Acceptance criteria

This spec is satisfied when:

- browser/OS handoff failure and malformed artifact are visibly different answers
- deep-link, paste, QR, and file import all converge on one typed page
- the operator can choose the destination seat explicitly when needed
- the page preserves typed preview before any live adoption or claim
- the product leaves an intake receipt regardless of fast path or fallback path
