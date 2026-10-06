# Lessons from the example datacubes

This pass reviewed the three uploaded example cubes structurally and by key
startup, handoff, receipt, validation, and manifest surfaces. The goal is not to
clone them. The goal is to keep BrowserRT from repeating their failure modes.

## What they did right

### 1. They made reentry explicit

The strongest pattern is a small set of files that tell a future operator where
to start, what changed, what commands matter, and what is derivative. BrowserRT
keeps this pattern with `START_HERE.md`, `CONTEXT-PACK.md`, `REENTRY-CONTRACT.json`,
`SURFACE-STATUS.json`, and `REVISION-RECEIPT.json`.

### 2. They separated canon from derivative aids

DelayBasin in particular repeatedly marks compact packets as derivative. This is
worth copying. BrowserRT should never let a summary packet, context pack, or
operator card silently replace the contract docs or release manifest.

### 3. They used receipts and manifests

Hyperepo and SlopOS both make package identity and receipts first-class. This is
essential for a zip-passed revision loop. BrowserRT adopts an embedded
`RELEASE-MANIFEST.json` with file sizes and hashes.

### 4. They had validation commands

The example cubes do not merely describe structure; they add scripts and command
surfaces. BrowserRT starts with `make lint`, `make test`, and release verification
rather than prose-only discipline.

### 5. They preserved non-claims and status lanes

The good surfaces do not pretend every artifact is equally authoritative.
BrowserRT preserves explicit non-claims around performance, browser support, and
implementation maturity.

## What they did wrong or risked

### 1. Surface sprawl became a tax

SlopOS and DelayBasin show how a discipline system can become too large for fast
reentry. Hundreds of docs and checks can preserve memory, but they can also hide
the next actionable move. BrowserRT starts with few surfaces and requires a check
before adding recurring status/index/receipt families.

### 2. Derived truth can drift

Hyperepo's many receipt and browser evidence surfaces show a real problem: a
summary can be green while a stricter current receipt says something else.
BrowserRT's rule is: every derivative surface must name its stronger underliers,
and validation must fail when key currentness fields disagree.

### 3. Browser evidence can overclaim

Browser tests inside a cloudtainer are valuable, but they are not real-device
performance proof. BrowserRT must distinguish cloudtainer correctness, smoke
capability, regression evidence, and public performance claims.

### 4. Context packs can become too large

A context pack should reduce reentry cost. If it becomes a second archive, it has
failed. BrowserRT caps the context pack's role: current orientation, must-read set,
commands, non-claims.

### 5. Packaging can confuse currentness

The examples repeatedly guard against stale packaged surfaces. BrowserRT should
keep release identity in one manifest, one status surface, and one receipt. New
status surfaces must earn their existence.

## BrowserRT import rule

BrowserRT imports these practices:

- start surface;
- reentry contract;
- revision receipt;
- status lanes;
- release manifest;
- validation index;
- context pack;
- explicit non-claims.

BrowserRT refuses these practices for now:

- hundreds of check scripts before code exists;
- giant ledgers without immediate readers;
- multiple competing currentness summaries;
- performance language without trace evidence;
- external dependency or network reliance.

## Exact structural audit

The compact machine-readable audit is in
`artifacts/datacube-audit/EXAMPLE-DATACUBE-REVIEW.json`.
