# Design goals (non‑negotiable)

**Track:** A (Deployable core)

> **Read-first:** before treating anything here as deployment guidance, read `166-scope-and-claims-contract.md` and `167-non-claims-and-boundaries.md` (they are binding on interpretation).



## Goal hierarchy (from most important)
1. **Correct outcome with evidence.** If the system declares a result, there MUST exist public evidence sufficient for independent parties to validate the outcome, and for courts to adjudicate disputes.
2. **Software independence / recovery.** A software fault or compromise MUST NOT be capable of producing an undetectable change in outcome. Recovery MUST be possible (e.g., paper ballot of record + audits).
3. **Privacy.** Ballot secrecy SHOULD hold against powerful attackers, including compromised servers, observers, and some compromised clients.
4. **Coercion resistance (best-effort).** The system SHOULD reduce vote-selling/coercion, but MUST NOT claim coercion resistance for unsupervised remote voting unless specific assumptions are satisfied.
5. **Availability.** The system MUST degrade safely under DDoS or partial outages (safe failure mode).
6. **Transparency.** Critical artifacts (code, builds, logs, proofs) SHOULD be publicly auditable.
## Scope framing (three tracks)
This archive is organized into three tracks:
- **Track A (Deployable Core):** evidence-based elections that assume a paper ballot of record.
- **Track B (Remote Return Research Annex):** hard-mode experiments with explicit non-claims.
- **Track C (North Star):** fully electronic voting in its best imaginable form (attestable devices + transparent manufacturing).
See `154-project-scope-and-track-map.md`.


## Human legitimacy surfaces (must not be implicit)

Election integrity failures are often **legitimacy collapses**: moments when people cannot tell what happened.
So we treat human-facing surfaces as first-class:

- **Representation duty:** verification must be doable by independent representatives (monitors/witnesses/journalists/civil society), not only by individual voters.
- **Material floor:** when power/internet/devices fail, the recovery mechanism must still work (paper of record + physical custody + audits/recounts).
- **Crisis usability:** under pressure, officials must be able to publish uncertainty-safe, authenticated updates that become evidence (`219`, `186`, `194–195`).

Track A keeps these in scope without requiring fully electronic voting.


## Paranoid assumptions
- A nation-state can compromise *some* servers, some trustees, and parts of the supply chain.
- Voter devices are frequently compromised (malware, browser injection, hostile extensions).
- Some voters are coerced (family, employer, organized coercion) and may be recorded.
- Network-level attacks occur (BGP/route hijacks, TLS interception in some environments, censorship, DDoS).
- Insiders exist and may collude.
- “Emergency patches” are a primary supply-chain attack vector.

## Safety invariants (MUST hold)
- **No single point of outcome control.** No single component (server, trustee, build system, CA, CDN) can change the outcome without detection by independent verifiers.
- **Tamper-evident public record.** The set of cast ballots and the tally procedure must be publicly verifiable.
- **Defined kill-switch behavior.** Under detected anomalies, the system MUST be able to halt online return and fall back to a safe method (e.g., in-person or paper).
