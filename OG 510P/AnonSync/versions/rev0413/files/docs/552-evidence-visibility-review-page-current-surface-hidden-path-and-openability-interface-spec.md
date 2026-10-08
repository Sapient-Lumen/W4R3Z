# Evidence visibility review page — current surface, hidden path, and openability

## Purpose

Give the operator one reviewed answer to:

- what evidence classes exist for this subject right now
- whether each class is visible on the current surface
- whether it is merely hidden, or actually unavailable here
- which stronger recovery or cleanup claims are still unsupported on this surface

## Inputs

- current seat identity
- current UI surface (`desktop app`, `web`, `android app`, `ios app`, `file browser`, `service shell`)
- subject identifier and share lineage
- witness inventory from prior scans:
  - live bytes
  - placeholders only
  - Archive candidates
  - History candidates
  - hidden service-state candidates
  - exported bundles / pinned receipts
- retention and cleanup history
- current safety posture (`read only`, `encrypted custody`, `detached`, `uninstalled app residue`, `service files missing`, etc.)

## Primary questions this page must answer

1. Which witness classes still exist?
2. Which witness classes are inspectable from **this** surface?
3. Which are hidden but reachable with a safe next step?
4. Which require a different seat or surface?
5. Which cannot currently be reached at all?
6. What is the strongest safe operator sentence **right now**?

## Layout

### A. Current-surface truth card
Top card with:

- current seat
- current surface
- subject / lineage
- strongest safe sentence, phrased narrowly

Examples:

- `Archive witness exists and is directly inspectable here`
- `Archive witness exists but is hidden-path only from this surface`
- `Recovery witness may exist on another seat; not inspectable here`
- `This surface cannot inspect Archive witnesses`

### B. Witness class table
Rows:

- witness class
- existence status
- access class
- next safe open step
- strongest claim allowed
- forbidden stronger claim

Access classes:

- `visible-now`
- `hidden-but-openable-here`
- `reachable-only-via-file-browser`
- `reachable-only-on-other-seat`
- `unavailable-on-this-surface`
- `unknown / not yet scanned`

### C. Claim ceiling pane
For each class, show:

- **allowed now**
- **blocked by**
- **what would raise the ceiling**

### D. Risk callout
If surfacing itself may change state, weaken proof, or require a different runtime, say so plainly.

## Required interactions

- `Open safely here`
- `Switch to better surface`
- `Route to better host`
- `Export current proof only`
- `Acknowledge surface limit`

## Guardrails

- Never let `exists somewhere` display as `recoverable here`.
- Never let `hidden path` display as `missing`.
- Never let `unavailable on iOS` quietly collapse into `no Archive`.
- Never let hidden service-state be exposed without warning when opening it may invite operator damage.

## Output

A reviewed classification of current evidence visibility that downstream recovery, cleanup, or attestation pages must inherit without reinterpreting.
