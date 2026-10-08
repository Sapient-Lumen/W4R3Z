# Recovery horizon receipt page: available-until, proof floor, and expiry risks interface spec

## Purpose

This page defines the durable receipt emitted after any decision or action that materially relied on current recovery horizon.

The receipt exists to answer a later reader's question:

> what evidence horizon did the product believe existed at decision time, how long was it expected to remain usable, and what weakening cliffs were already known?

## Core decision

Every non-trivial recovery decision, preservation step, or retention mutation must emit one first-class **Recovery horizon receipt**.
That receipt records:

- byte-witness horizon used
- event-witness horizon used
- access surface used
- available-until estimate
- known exclusions and cliffs
- strongest safe sentence at decision time
- weaker sentence forecast after expiry

## Receipt sections

The receipt always renders the same sections in the same order:

1. receipt strip
2. horizon basis card
3. access basis card
4. expiry-risk card
5. proof-floor card
6. follow-up card

### 1) Receipt strip

Show:

- receipt ID
- subject path
- decision kind (`inspect-horizon`, `preserve-witness`, `change-retention`, `cleanup-residue`, `decline-recovery`, `recover-now`)
- strongest safe summary sentence
- available-until estimate

### 2) Horizon basis card

Show:

- byte witnesses considered
- event witnesses considered
- policy basis for horizon (`default`, `custom`, `manual-preserve`, `unknown`)
- whether capture exclusions were present

### 3) Access basis card

Show:

- acting seat and surface
- alternate seat if the evidence existed elsewhere
- whether access was direct, filesystem-only, remote-nominated, or unavailable
- whether hidden residue survived beyond UI or app lifecycle assumptions

### 4) Expiry-risk card

Show:

- nearest known cliff
- what fact would weaken at that cliff
- whether loss would be true deletion or only access degradation
- preservation actions offered before close

### 5) Proof-floor card

Show:

- strongest safe sentence at decision time
- forbidden stronger sentence
- weaker future sentence after the nearest cliff
- remaining gaps in byte, actor, or access proof

### 6) Follow-up card

Show the strongest next honest step, for example:

- `Preserve joined receipt before actor horizon closes`
- `Export byte witness before mobile retention expires`
- `Complete cleanup only after explicit residue decision`
- `Re-check horizon after retention mutation applies`

## Non-negotiable rules

### Rule 1 — receipts must preserve the horizon that justified the action

A later reader should not need the now-expired live state to understand why the product acted.

### Rule 2 — expiry risk belongs in the receipt itself

Receipts must preserve not only what was true, but also what was already known to be near loss.

### Rule 3 — access posture must remain typed

A receipt must distinguish evidence that was directly reachable from evidence that only theoretically survived elsewhere.

## Honest outputs

The receipt may say:

- `At decision time, byte witnesses remained on two desktop seats for an estimated 17 days; actor evidence was expected to weaken sooner.`
- `Retention was lowered after preserving one manual export; future large-file versions above the new ceiling are no longer expected.`
- `App removal alone would not have erased hidden residual archive bytes, so cleanup was reviewed and applied as a separate decision.`
