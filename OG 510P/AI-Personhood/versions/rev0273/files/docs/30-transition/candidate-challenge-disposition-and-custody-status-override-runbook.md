# Candidate challenge disposition and custody status override runbook

This runbook handles the seam between candidate challenge/replay and the custody authority gate. Its purpose is to prevent an operator from turning elapsed time, silence, automated acknowledgements, protocol/tool output, or redacted-only material into a closed challenge status.

## Required order

1. Confirm the normalization decision permits candidate challenge. If normalization is pre-dispatch, redacted-only, protocol-only, unsafe, or scan-pending, stop.
2. Confirm the candidate challenge report exists, is current, reread the private-vault hash/size without leaking bytes, and remains no-floor.
3. Open the challenge window only through the candidate challenge report.
4. Record any closure in a candidate-challenge disposition record. Do not pass a raw `closed-*` status to the custody gate.
5. For no-objection closure, require affirmative human counterparty evidence, manual contact confirmation, request trace, identity verification, scoped authority, published authority limitations, and independent timestamp/log support.
6. For objection rejection, require the same evidence plus objection receipt and human review.
7. For objection upheld, feed a closed-upheld disposition to the custody gate only so it can block custody; do not bury the objection.
8. Recompute the admission graph and live floor after any real disposition or custody-gate attempt.

## Never enough by itself

These may not close challenge:

- elapsed time;
- silence;
- automated acknowledgement, ticket, bounce, or mailbox rule;
- MCP, A2A, API, relay, or other protocol/tool output;
- redacted-only copy;
- public shell;
- private-vault locator;
- operator note saying “closed”; 
- command-line `--challenge-status closed-*` override.

## Custody gate rule

The custody authority gate may consume a closed challenge status only when it is carried by `candidate-challenge-disposition-record.schema.json`. A raw status override is display/routing context at most and must block as missing authority.

Even a valid disposition does not create custody. It may only allow the custody gate to authorize preparation of a separate custody record, which must then pass its own raw locator/hash, authority, response, intake, import, and live-floor gates.

## Current rev0235 state

`examples/candidate-challenge-disposition-record-rev0235-open-stayed.json` is open/stayed. `examples/counterparty-artifact-custody-gate-rev0235-pending-challenge.json` blocks. The current candidate challenge and custody-gate surfaces are present again so lint can catch drift in this seam.
