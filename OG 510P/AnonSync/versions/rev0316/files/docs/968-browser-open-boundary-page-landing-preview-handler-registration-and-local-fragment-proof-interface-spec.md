# Browser-open boundary page — landing preview, handler registration, and local fragment proof interface spec

## Purpose

This page exists because browser-open flows are where operators routinely over- or under-estimate disclosure.

It answers:

> when I open or issue an artifact through a browser, what part is local fragment parse, what part touches a service landing page, what preview facts become visible, and what handoff to the local runtime is actually happening?

## Core decision

Any serious browser-mediated artifact flow must expose a first-class **Browser-open boundary** page.

That page owns the boundary between:

- browser-visible state
- service-page-visible state
- local fragment-only state
- handler registration and transfer state
- post-handoff local runtime state

## Page layout

The page renders the same order:

1. artifact summary
2. URL / carrier partition
3. preview provenance
4. handler / transfer path
5. disclosure ceiling
6. safe next actions

### 1) Artifact summary

Show:

- artifact family
- visible human label
- embedded preview fields
- whether the preview is exact, approximate, or omitted

### 2) URL / carrier partition

Show a stable split between:

- server-addressed prefix
- local fragment or local-only payload
- fields that cross the network
- fields that remain local to the browser / device

The operator should not have to remember URL-fragment rules to know what crossed the network.

### 3) Preview provenance

For each shown preview field, mark one of:

- `rendered locally from fragment`
- `rendered by service page`
- `rendered by local app after handoff`
- `unknown provenance`

### 4) Handler / transfer path

Show:

- whether a browser page is merely displaying guidance
- whether it is triggering a registered handler such as a custom URI scheme
- whether the browser asked for confirmation
- whether the artifact can also be imported manually without browser assistance
- whether the chosen path changes disclosure or only convenience

### 5) Disclosure ceiling

Summarize with one safe sentence and one blocked stronger sentence.
Examples:

- safe: `artifact details after # remained local to the browser/device in this flow`
- blocked: `reject saying “no off-device infrastructure was contacted at all”`

### 6) Safe next actions

Permit actions such as:

- `Open locally via handler`
- `Copy for manual local import`
- `Choose no-preview artifact form`
- `Open disclosure proof`
- `Cancel`

## Rules

### Rule 1 — browser convenience must not hide disclosure shifts

A `one-click open` path may be safe, but the product must say whether it touched a landing page or only used local fragment parsing.

### Rule 2 — preview provenance is mandatory

If folder name or size is shown, the page must say whether those facts were derived locally or rendered by a service path.

### Rule 3 — manual import remains a first-class neighbor action

When a browser handoff exists, the product should still present a local/manual intake path if it materially narrows disclosure or operator confusion.

## Receipt fields

A browser-open boundary receipt should preserve:

- artifact ID
- browser / service / local partition
- preview fields and provenance
- handler path used
- strongest safe sentence
- blocked stronger sentence
- completion time

## Result

AnonSync should make browser-open truth obvious at the moment of open.
If the operator still has to know URL-fragment mechanics or custom-scheme behavior by folklore, the page has failed.
