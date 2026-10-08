# 39 — Traffic analysis and metadata privacy

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

Even if ballots are encrypted and proofs are correct, **network metadata** can leak:
- whether and when a voter voted
- whether a ballot was spoiled vs cast
- potentially the voter’s selections (via message size / response patterns)

This can enable coercion, vote buying, retaliation, or targeted suppression.

## Threats

### T1 — Passive network observer
A network observer (ISP, Wi‑Fi operator, enterprise proxy, national censor) observes timing, sizes, and endpoints.

### T2 — Active traffic shaping adversary
An on-path attacker injects delays, resets, or selective drops to induce distinguishable client behavior (“oracle attacks”).

### T3 — “Confirmation page” side channels
UI flows can leak selections through request sizes or response lengths even without breaking TLS.

## Findings from the literature (high level)

- Recent work demonstrates high-accuracy classification of voter actions using only encrypted traffic metadata in real systems, and evaluates mitigations such as padding and timestamp equalization.
- Prior work shows confirmation/verification screens can break secrecy via length-based leakage.

## Normative requirements

### Minimize distinguishers
- The client MUST avoid making network requests whose size or timing depends on the voter’s selections.
- The server MUST avoid responses whose size depends on selections (including error strings that vary by contest/choice).

### Envelope format
- All client→PBB submissions MUST use a fixed-size outer envelope with:
  - padding to the configured size class
  - constant-time-ish processing (avoid obvious branching on ballot content)
- Where fixed-size is infeasible, the system MUST define discrete size buckets and MUST make bucket selection independent of vote content.

### Timestamp equalization / batching
- The PBB ingestion layer SHOULD support batching:
  - clients submit into a short window
  - the log publishes a batch commitment at fixed cadence
- When batching is enabled, verifiers MUST validate batch commitments and subsequent inclusion.

### Relay / multi-path submission (recommended)
To reduce single-observer metadata linkage:
- Clients SHOULD support submission via multiple relays operated by mutually distrustful parties.
- Clients SHOULD support multi-path retries (different ingress points) on censorship suspicion.

### Publication minimization
- Public logs MUST NOT publish per-voter IPs, TLS identifiers, or other high-entropy network metadata.
- Any operational telemetry MUST be aggregated and privacy-reviewed.

## Mitigation tradeoffs

- Padding + batching + cover traffic can reduce leakage but may increase latency and cost.
- Using anonymity networks can improve privacy but can harm reliability and may trigger blocking.

## Evidence artifacts

- `artifacts/checklists/traffic-analysis-mitigations.md`
- `schemas/BatchCommitment.json`