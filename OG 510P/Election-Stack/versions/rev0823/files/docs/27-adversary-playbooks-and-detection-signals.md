# Adversary playbooks & detection signals

**Track:** A (Deployable core)


The point of paranoia is to assume attackers choose the *cheapest* effective path.

Each scenario includes: expected signals, required evidence, and response trigger.

## A. Silent ballot dropping (selective censorship)
- Attack: accept intake, never include; or block submissions by region/ISP.
- Signals: spike in “PENDING but not RECORDED by deadline”, geographic clustering.
- Evidence: signed IntakeReceipt + missed inclusion deadline; witness logs.
- Response: invoke fallback; extend voting; public incident bulletin.

## B. Split-view equivocation
- Attack: show different STHs to different clients.
- Signals: witness gossip detects inconsistency; ForkProof published.
- Evidence: ForkProof + signed STHs.
- Response: treat PBB as compromised; freeze; switch to recovery.

## C. Log signing key compromise
- Attack: sign fraudulent STHs/receipts.
- Signals: cross-witness divergence; anomalous signing patterns.
- Evidence: witness comparison; HSM audit trails.
- Response: revoke key; rotate log_id; publish incident report.

## D. Colluding trustees (threshold attack)
- Attack: collude to decrypt or bias tally.
- Signals: missing/failed public proofs; ceremony anomalies.
- Evidence: proof failures (public).
- Response: replace trustees; rerun tally; rely on paper audit.

## E. Supply-chain compromise (update attack)
- Attack: backdoored client/verifier release.
- Signals: provenance mismatch; hash mismatch; suspicious dependency change.
- Evidence: provenance attestations; reproducible build logs.
- Response: revoke release; publish IOCs; reissue if needed.

## F. Client malware / coercion
- Signals: weak/none without extra mitigations.
- Response: supervised override; do not overclaim security.

## G. Forged public artifacts / synthetic “official” statements
- Attack: circulate fake receipts, screenshots, or deepfaked statements claiming compromise or victory; or hijack/impersonate official channels (social handles, lookalike domains).
- Signals: high-velocity media without matching bundle IDs/checkpoints; mismatched hashes; outlets quoting unverifiable artifacts.
- Evidence: signed `PublicNotice` envelopes (hash-first); verifier reproduction logs; audience-parity monitoring.
- Response: publish a minimal rumor-control packet (hashes + reproducible checks), then narrate.
