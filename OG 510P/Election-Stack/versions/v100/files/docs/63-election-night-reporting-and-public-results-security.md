# Election Night Reporting (ENR) & public results publishing

**Track:** A (Deployable core)


This document hardens **unofficial results publishing** (often called Election Night Reporting / ENR).
Even when the underlying tally is sound, ENR compromise can trigger a legitimacy crisis.

## Design goals

- Treat ENR as **unofficial** by default; make the “not certified” status unavoidable.
- Make ENR tampering **detectable** and **provable** (court-proof evidence).
- Make ENR outages survivable without creating selective “some voters see one thing, others see another.”

## Threat model (ENR-specific)

- Website takeover, CDN compromise, or CMS compromise
- API poisoning (results endpoint altered)
- Credential theft for official social accounts
- DDoS / selective denial (regional or demographic targeting)
- “Slow drift” attacks (small edits that look like benign corrections)
- Disinformation amplification: real-looking screenshots/HTML snippets circulating faster than corrections

## Architecture (recommended)

1. **Keep ENR separate from election management systems (EMS).**
   - ENR should ingest *exported* summary data from a protected tabulation environment.
   - Never allow internet exposure to move “inward” toward the EMS.

2. **Digitally sign every ENR update**, and publish signatures and hashes.
   - Each update is a content-addressed `ENRUpdate` object (see schema).
   - Publish: update JSON + detached signature + previous update hash (hash chain).

3. **Anchor ENR updates into the public bulletin board (PBB)** (preferred).
   - Include an `enr_update_hash` as a log entry type and/or include in witness checkpoints.
   - Optional: cross-anchor update hashes into independent public logs (see `57-*`).

4. **Publish a single authoritative “status banner”**
   - “Unofficial results; certification window; why totals change.”
   - Must appear identically across website and API.

5. **Multi-channel publication (avoid single-point UI capture)**
   - Website + API + downloadable signed bundles.
   - Publish an immutable “results evidence bundle” after each reporting interval.

## Minimum controls

- Strong account security: hardware keys, least privilege, separate publish roles
- Content pipeline with staged approvals (two-person rule for “major changes”)
- Immutable logging (append-only logs for result publishing actions)
- DDoS readiness: anycast/CDN for static content, rate-limited APIs
- Monitoring: alert on unsigned updates, hash-chain breaks, unexpected deltas

## Evidence bundle (recommended)

After each reporting interval, publish a `ResultsReleasePackage`:

- election id, EPB hash
- latest witness-quorum checkpoint (STH + cosignatures)
- list of ENR updates since last package
- notarization records (optional)
- human-readable summary and “what changed” diff

## References

- EAC: Checklist for Securing Election Night Results Reporting (ENR)
- NIST: Security of Election Night Reporting topic + ENR use case materials
- IFES: Cybersecurity of Election Results Management Systems briefing