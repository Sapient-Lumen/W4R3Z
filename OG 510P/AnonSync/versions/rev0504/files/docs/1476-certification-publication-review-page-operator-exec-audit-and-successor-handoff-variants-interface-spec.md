# Certification publication review page: operator, executive, audit, and successor-handoff variants interface spec

## Purpose

This review page helps the operator choose the correct publication variant instead of reusing one packet for audiences with different decision rights.

## Review question

> what exact version of the certification is safe for this audience to rely on, and what must be downgraded, hidden, or made explicit before publication?

## Fixed review branches

1. **Working-operator branch**
2. **Executive branch**
3. **Audit branch**
4. **Successor-operator handoff branch**
5. **External partner / customer branch**
6. **No-safe-publication branch**

### 1) Working-operator branch

Show:

- active certification sentence
- exact scope and exclusions
- freshness and revocation triggers
- linked receipts, timelines, and open blockers
- next permitted operational action
- next forbidden overclaim

Use when the audience may perform follow-on operational decisions.

### 2) Executive branch

Show:

- bounded high-level sentence
- why the sentence is bounded
- explicit exclusions summarized compactly
- freshness horizon
- required follow-up owner
- no raw log or forensic detail by default

Hard rule:

An executive packet may compress detail, but it may not widen the claim envelope.

### 3) Audit branch

Show:

- precise certified scope
- exclusions and why they are excluded
- evidence lineage ids
- witness freshness basis
- revocation and supersession chain
- redaction note if artifacts are withheld

Hard rule:

An audit packet may never rely only on dashboard prose.
It must include traceable lineage identifiers.

### 4) Successor-operator handoff branch

Show:

- working-operator packet fields
- unresolved obligations
- recall obligations still active
- next rereview time
- world attribution and path / service / config caveats
- stale packet handling instructions

Hard rule:

`shared for awareness` is weaker than `delegated custody accepted`.
The handoff branch must keep that difference explicit.

### 5) External partner / customer branch

Show:

- narrow safe sentence
- explicit service or data-impact implication
- actions the audience may take now
- actions still blocked
- how they will be told if the sentence is recalled

Hard rule:

This branch must never leak a stronger internal sentence just because internal operators can tolerate nuance.

### 6) No-safe-publication branch

Use when any of the following is true:

- source certification is not active
- exclusions are not yet explicit
- freshness already failed
- recall channel is missing
- world attribution is unknown
- the audience wants a stronger claim than the evidence allows

Decision sentence:

> No audience-safe publication yet. Keep this as internal operator truth only until [missing requirement] is satisfied.

## Cross-branch invariants

- one audience packet may not silently impersonate another
- stronger source truth may be deliberately downgraded, but weaker packets may not imply stronger source truth
- every published packet must name its supersession source
- every packet must preserve at least one explicit `do not infer` sentence
