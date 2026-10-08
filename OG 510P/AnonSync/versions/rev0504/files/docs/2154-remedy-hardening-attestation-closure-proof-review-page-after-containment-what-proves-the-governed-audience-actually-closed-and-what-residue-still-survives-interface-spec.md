# Remedy-hardening-attestation closure-proof review page — after containment, what proves the governed audience actually closed and what residue still survives?

## Purpose

This review page asks the one question containment cannot answer by itself:

**after we intercepted or narrowed the relapse, what proves the governed audience actually closed, and which stale carriers still survive?**

## Mandatory review prompts

The review must force explicit answers to at least:

1. Which audience slices are confirmed closed, and by what evidence?
2. Which audience slices are only inferred closed?
3. Which audience slices remain unknown or nonresponsive?
4. Which stale-carrier classes can still survive despite future access being blocked?
5. Which closure claim would become dishonest if a late-surviving copy were rediscovered tomorrow?

## Review buckets

### Confirmed-closed slices

For each slice, the page must show:

- slice name
- evidence class
- time of last confirming evidence
- whether the evidence proves byte retirement, merely disconnection, or only future-access blocking

### Unconfirmed or unknown slices

For each slice, the page must show:

- why closure is not yet proven
- whether the slice is expected to respond
- what residual stale carriers may survive there
- what stronger sentence stays blocked because of it

### Residual carrier review

The page must separately review at least:

- already-downloaded single-file copies
- disconnected local copies
- remote unlinked copies
- local-share derivatives
- forwarded/reshared artifacts
- hidden archive or placeholder-related residue where applicable

## Refusal rules

The review must refuse to bless a closure claim if:

- any required audience slice is still unknown and not explicitly tolerated by policy
- the proof only shows link expiry or approval revocation without recipient-side state evidence
- the proof only covers linked devices while the governed audience includes unlinked peers or recipients
- the survivor ledger is missing

## Output

The output must be one of:

- `closure proven for named slices only`
- `closure partly proven with explicit survivors`
- `closure blocked by unknown survivors`
- `closure claim collapsed`
