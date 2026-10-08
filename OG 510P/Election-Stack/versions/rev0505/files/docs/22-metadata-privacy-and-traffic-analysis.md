# Metadata privacy & traffic analysis (paranoid)

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

Even if ballots are perfectly encrypted and the Public Bulletin Board (PBB) is perfectly auditable,
**network metadata can still destroy privacy and enable targeted suppression**:
- who voted (or attempted to vote), when, and from where;
- correlation between eligibility token issuance/spend and ballot posting;
- selective disruption of specific precincts, ISPs, or demographics by timing.

This doc defines *minimum* mitigations so the system does not accidentally become a turnout‑surveillance
and targeting tool.

## Non-negotiable goals
1. **Ballot secrecy**: the ciphertext reveals no vote content (crypto layer).
2. **Unlinkability**: eligibility/authorization is not linkable to a posted ciphertext.
3. **Metadata minimization**: the PBB learns as little as possible about voter network identity.
4. **Suppression resistance**: attacks that rely on observing *whether* a vote was cast are made harder.

## Threats (metadata attackers)
Assume an attacker can be any of:
- ISP / carrier / enterprise observer;
- hostile federation node / witness collecting IPs and fingerprints;
- insider with access to access logs;
- global passive observer for limited windows.

## Required mitigations (MUST)
### A. Uniform message shapes
- Clients MUST submit fixed-size envelopes (padding) for vote submissions.
- Clients MUST avoid variable-length metadata fields (user-agent strings, locales, fonts, etc.).
- Servers MUST reject unexpected fields and MUST not log request headers beyond what is required for DoS controls.

### B. Decouple eligibility from submission
- Eligibility tokens MUST be unlinkable to voter identity at the PBB.
- Token issuance and token spend MUST be separated in time and infrastructure.

### C. Log-level privacy hygiene
- PBB nodes and witnesses MUST implement retention limits for raw network identifiers.
- Operational dashboards MUST aggregate and delay publication of turnout metrics.
- Publishing “who has voted” signals at fine time/geo resolution is forbidden unless jurisdiction-approved and privacy‑reviewed.

## Strongly recommended mitigations (SHOULD)
### D. Submission relays + cover traffic
For any remote (unsupervised) flow:
- Provide an official **relay network** (multiple independent operators) that forwards submissions to the PBB.
- Relays SHOULD emit cover traffic at a constant rate during the voting window.
- Clients SHOULD add a bounded random delay before relay submission.

> If you do not deploy relays/cover traffic, explicitly document that the system provides
> content secrecy but **not traffic-analysis resistance**.

### E. Batch commitments
To reduce timing correlation, a relay can batch submissions and commit them as a group:
- collect N submissions or wait T seconds (whichever first),
- post a batch commitment to the PBB,
- later publish per-submission inclusion evidence.

Tradeoff: delays receipts; integrate with `14-receipts-and-state-machine.md`.

## Red-team checks (minimum)
- Correlate token issuance and ciphertext posting using timing alone.
- Attempt “turnout oracle” attacks: determine whether a specific person voted.
- Attempt targeted suppression-by-fingerprint (device class, ISP, geography) and confirm detectability.