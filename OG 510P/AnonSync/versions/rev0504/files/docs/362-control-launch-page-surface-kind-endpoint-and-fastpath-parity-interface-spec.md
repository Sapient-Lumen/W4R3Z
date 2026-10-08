
# Control launch page: surface kind, endpoint, and fast-path parity interface spec

## Purpose

The archive already had bringup, control trust, import artifact, and setup-readiness doctrine.
This document makes one missing ordinary page concrete.

The page exists to answer one ordinary operator question:

> what control surface did I just open, which runtime owns it, what endpoint am I talking to, what fast paths are available from here, and what fallback still works if a convenience path fails?

## Core decision

Every seat that exposes any control surface must own one first-class **Control launch** page.
That page is the semantic home of:

- current surface kind
- runtime owner
- endpoint and exposure scope
- fast-path availability
- typed fallback entry points
- recent entry receipts

The product must not ask the operator to infer these from browser tabs, tray icons, login prompts, or protocol-handler luck.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. launch verdict strip
2. current surface card
3. runtime owner card
4. endpoint and exposure card
5. fast-path parity card
6. recent entry receipts
7. expert details drawer

### 1) Launch verdict strip

The strip shows:

- seat name
- current surface kind
- one plain-language launch verdict
- strongest next-safe action

Allowed launch verdicts:

- `desktop control open`
- `local web control open`
- `headless web control open`
- `cli / tui control open`
- `degraded entry; runtime healthy`
- `entry open but limited capability`

The strongest next-safe action must name a real next step, such as `Inspect listener`, `Repair browser trust`, or `Open import lane`.

### 2) Current surface card

Show:

- surface kind
- how it was opened (`browser`, `tray`, `command`, `deep link`, `installer handoff`, `other`)
- whether this surface is first-class, fallback-only, or degraded
- whether this surface is expected for the current seat profile

This card should answer `what exactly am I using right now?`

### 3) Runtime owner card

Show:

- runtime owner or execution principal
- storage/state root handle
- whether this surface is talking to the expected runtime
- whether another local runtime could have answered instead

This card should make `the browser opened` and `the intended daemon answered` visibly different truths.

### 4) Endpoint and exposure card

Show:

- endpoint class (`loopback`, `lan`, `proxied`, `remote`, `not networked`)
- host and port or named local handle
- current exposure scope
- current trust posture
- last listener or endpoint mutation receipt

This card should answer `who can reach this thing besides me?`

### 5) Fast-path parity card

This card is mandatory.
It shows which convenience paths are actually available from this surface:

- browser-open artifact handoff
- protocol/deep-link handoff
- QR intake
- typed paste
- file import
- privileged admin / config actions
- upgrade or install actions

Each row shows:

- `available here`
- `not available here`
- `available through handoff`
- `blocked until trust repair`
- `blocked by seat policy`

The page must also offer the strongest typed fallback for any blocked fast path.
A failed accelerator may not dump the operator into folklore.

### 6) Recent entry receipts

Show recent control-entry receipts with:

- surface kind
- runtime reached
- endpoint used
- launch verdict
- fast-path blockers encountered
- resulting next action

### 7) Expert details drawer

Hide raw command lines, protocol registration details, browser metadata, and low-level endpoint diagnostics behind an expert drawer.
They are valuable, but they are not the page's semantic center.

## Narrow-width behavior

In narrow width the page may stack cards, but it may not hide:

- current surface kind
- runtime owner
- endpoint class
- fast-path availability versus fallback

## Acceptance criteria

This spec is satisfied when:

- an operator can tell from one page what surface is open and which runtime answered
- browser-open failure, unavailable-from-this-surface, and malformed artifact are visibly different answers
- a blocked accelerator still leaves a typed fallback path on the same page
- control entry emits a receipt rather than outsourcing memory to browser history or tray lore
