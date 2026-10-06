# Priority-0 external replay handoff and leak guard — 2026-06-15

## Decision

`rev0365` does not claim an external/operator-independent replay has been run. It resolves `OQ-0256` only by the allowed narrowing path: the compact hot cue remains a preflighted default, but no new burden retirement, deletion-like move, or independent-certification claim is allowed until an external response is collected and scored.

The risk was concrete: `rev0364` separated a responder packet from a scorer key, yet the public package still contained both. A future operator could accidentally hand the whole archive to the responder and call the result blind. This revision adds a responder-only handoff file, a blank response template, a scorer intake, hashes tying the files together, and a checker that fails if the responder-only file leaks scorer-only tokens.

## New handoff surfaces

- `assays/priority-zero-external-replay-responder-only-2026-06-15.json` — give this file to the external/operator-independent responder.
- `assays/priority-zero-external-replay-response-template-2026-06-15.json` — blank response template; responder fills only `responder_stage` before seeing scoring material.
- `assays/priority-zero-external-replay-scorer-intake-2026-06-15.json` — use only after a response exists.
- `assays/priority-zero-external-replay-handoff-2026-06-15.json` — records hashes, non-claims, gate narrowing, and successor routing.
- `tools/check_priority_zero_external_replay_handoff_contract.py` — validates leak separation, hash custody, response-template shape, scorecard arithmetic, and receipt/frontier routing.
- `tools/score_priority_zero_external_replay_response.py` — small local scorer helper for a completed response JSON.

## Finding

The main archive is auditable but is not blind input because it contains scorer material. The responder-only handoff is the smallest current object that can plausibly be given to an external responder without leaking the key. The external-response evidence row remains zero because no independent response exists in this package.

## Audit / refactor

The Priority-0 role-blind checker was also refactored from a current-tail checker into a historical-evidence checker. That prevents `rev0364` from forcing every later receipt to pretend the role-blind preflight is still the current tail. The new current checker is `tools/check_priority_zero_external_replay_handoff_contract.py`, which owns only the handoff/leak-guard invariants.

## Non-claims

This is not deletion authority, not a minimality proof, not an independent replay result, not a benchmark, and not a review court. It is a leak-sealed handoff plus an explicit narrowing of the compact gate.

## Successor

`OQ-0257` is the live task: collect a completed external/operator-independent response using the responder-only file and response template, then score it with the scorer intake. If the compact packet loses mission-heart recovery or OQ routing, narrow or reverse the compact gate.
