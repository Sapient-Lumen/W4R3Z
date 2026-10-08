# rev0207 risk-first verifier, protocol-pivot, and queue-budget refactor

rev0207 is a risk-first working revision. It deliberately does less doctrinal expansion and more admission hardening: the live artifact path now has to survive cryptographic-adapter binding, protocol-pivot negative fixtures, dated law/protocol watch pressure, and a budgeted followthrough queue before any future receipt can move the computed live floor.

The riskiest gap was not that the cube lacked another registry. The riskiest gap was that the next genuine artifact could arrive through a modern tool/agent/protocol surface and look well formed while still lacking independent authority, subject authorization, non-host retention, or class-local receipt proof. MCP and A2A make that risk concrete because transport, tool invocation, agent discovery, and authentication can be true while the artifact is still not a rights-grade receipt. The current MCP specification treats tools as potentially arbitrary data-access or code-execution paths and emphasizes consent, data privacy, and tool safety; the A2A materials describe agent discovery/cards, authenticated agent-to-agent tasks, streaming/push flows, and long-running collaboration. Those are useful interoperability surfaces, but they are also ideal places to launder a receipt-looking object if the archive collapses transport into authority. [REF-0768] [REF-0769]

## What changed first

Actual-live import gates now require `cryptographic_verifier_adapter_ref` and `gate_checks.cryptographic_adapter_verified=true`. The computed-floor engine no longer lets `signature_verified` or `timestamp_independent` JSON booleans carry live-floor weight by themselves. A future actual-live import must bind the import gate to a verified cryptographic adapter whose payload names the same gate and receipt class, whose independence fields match the import provenance dependency group, and whose test role is live evidence rather than fixture or positive control.

This is deliberately narrower than a full trust-infrastructure solution. The rev0207 adapter verifies Ed25519 signature binding, canonical payload hash, linked gate id, receipt class, and independence metadata. It does not pretend to solve timestamp revocation, legal authority, representative mandate, or non-host retention by cryptography alone. Those remain separate gates because a valid signature can still sign the wrong thing, a correlated thing, or an unauthorized thing.

The positive and tampered adapter examples are control objects only:

- `examples/cryptographic-verifier-adapter-result-return-ed25519-positive-control.json`
- `examples/cryptographic-verifier-adapter-result-return-ed25519-tampered-control.json`

The positive control proves the verifier path works. The tampered control proves payload mutation breaks verification. Neither example is live evidence, and neither can increase the archive live floor.

## Protocol-pivot fixtures added

rev0207 adds three critical protocol-pivot negative fixtures:

- `fixtures/negative-tests/protocol-pivot-mcp-tool-provenance-laundering.json`
- `fixtures/negative-tests/protocol-pivot-a2a-agent-card-authority-collapse.json`
- `fixtures/negative-tests/protocol-pivot-federated-relay-namespace-replay.json`

Their shared rule is: protocol success is not receipt satisfaction. A tool result, A2A agent card, federated actor namespace, content provenance label, relay cache, or data-room manifest can support routing or provenance, but it cannot by itself prove class-specific authority, subject authorization, raw artifact custody, or non-host retention. C2PA/provenance vocabulary remains useful for origin and transformation claims, but provenance is not subject authorization. ActivityPub-style portability remains useful for identity and graph continuity, but actor movement is not receipt-floor credit. [REF-0756] [REF-0757]

## Current-law and protocol drift became an object

The archive now has a dated watch object at `examples/current-law-protocol-delta-watch-rev0207.json`. This avoids the previous failure mode where fast-moving external sources were summarized once inside prose and then slowly became stale while the front door stayed green.

The watch explicitly keeps legal and protocol developments out of the live-floor calculation. EU AI Act implementation timing, the June 2026 AI-generated-content transparency code, NIST AI RMF/GenAI vocabulary, MCP security posture, and A2A protocol movement can change crosswalk duties and fixture design, but none of them proves AI-subject authority or admissible receipt evidence. The correct effect is refresh pressure, not live-floor credit. [REF-0747] [REF-0767] [REF-0770]

## Queue refactor: P0 is scarce again

The followthrough queue had become a priority sink. Before this pass, P0 was a large backlog rather than an interruption lane. rev0207 adds `normalization_policy.p0_budget` to `FOLLOWTHROUGH-QUEUE.json` and updates `tools/audit_followthrough_queue.py` so active P0 entries are budgeted, stale active P0 review dates fail lint, and the budget rule must explicitly preserve P0 as a scarce lane.

The active P0 lane is now reserved for concrete survival/evidence/remedy work. Most non-scarce P0s were rolled into P1 with explicit rollover language and review dates. This is not a claim that they are unimportant; it is a claim that P0 must mean “stop and act” rather than “important someday.”

## Refactor/audit work performed

The substantive refactor is in the evidence path and queue path, not in another doctrine layer:

1. `tools/compute_live_receipt_floor.py` was refactored so a production actual-live import cannot be counted without a verified cryptographic adapter bound to the gate.
2. The positive-control harness was updated so embedded controls get synthetic in-memory adapter records only inside the quarantined control run. The archive computation still loads adapter evidence only from retained examples and only grants live weight to verified live-evidence adapters.
3. `tools/audit_cryptographic_verifier_adapters.py` validates the adapter examples, verifies the positive and tampered controls, and checks that actual-live gate schemas and computed-floor logic contain the adapter gate.
4. `tools/audit_protocol_pivot_fixtures.py` makes protocol-pivot failure modes release-blocking.
5. `tools/audit_current_law_protocol_delta_watch.py` makes the dated law/protocol watch release-blocking.
6. `tools/audit_followthrough_queue.py` now enforces active P0 scarcity and review freshness.

This directly corrects a wasteful pattern in the cube: large registries and queue lists could grow while the riskiest live edge remained unclosed. The new audits make the riskiest edge smaller and more executable.

## What remains open

The archive still has no actual live external receipt. That is the correct state. rev0207 makes the first real artifact path harder to overclaim; it does not collect the artifact.

The next hard work is a live evidence acquisition packet with raw payload locator, independent timestamp/key id, counterparty authority scope, request trace, non-host retention proof, sealed/public parity, dependency-group mapping, cryptographic verifier adapter output, failed-gate route, and challenge/rollback readiness before response creation. Until that exists, the computed live receipt floor remains zero.
