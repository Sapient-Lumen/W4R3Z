# Election Night Reporting (ENR) & public results publishing

**Track:** A (Deployable core)


This document hardens **unofficial results publishing** (often called Election Night Reporting / ENR).
Even when the underlying tally is sound, ENR compromise can trigger a legitimacy crisis.

## Design goals

- Treat ENR as **unofficial** by default; make the “not certified” status unavoidable.
- Make ENR tampering **detectable** and **provable** (court-proof evidence).
- Make ENR outages survivable without creating selective “some voters see one thing, others see another.”

- Use a compact, portable **results status vocabulary** (`unofficial` + `counts_status`) so the public cannot confuse “more complete” with “more official.” See `234-results-status-taxonomy-and-correction-discipline.md`.

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
   - Each update is a content-addressed `ENRUpdate` object (see schema; hashing/canonicalization contract: `235`).
   - Publish: update JSON + detached signature + previous update hash (hash chain).

3. **Anchor ENR updates into the public bulletin board (PBB)** (preferred; see `236`).
   - Include an `enr_update_hash` as a log entry type and/or include in witness checkpoints.
   - Optional: cross-anchor update hashes into independent public logs (see `57-*`).

4. **Publish a single authoritative “status banner”**
   - “Unofficial results; certification window; why totals change.”
   - Must appear identically across website and API.

5. **Multi-channel publication (avoid single-point UI capture)**
   - Website + API + downloadable signed bundles.
   - Publish an immutable “results evidence bundle” after each reporting interval.


## ENR as a verifiable public surface (digest-first)

ENR UIs are easy to counterfeit; **digests are not**.

For each reporting interval, the publisher SHOULD:

- Generate a `ResultsReleasePackage` payload and publish it as an `EvidenceEnvelope` (`kind: hfv.results.release_package`; `238`).
- Issue a **PublicNotice** whose payload includes that digest, a monotonically increasing interval counter,
  and mirror URLs (see `195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md`).
- Mirror the **PublicNotice digest** across official channels (site banner, status board, social, press list),
  and run parity monitoring so “some people see one thing, others see another” becomes detectable (`194` / `195`).

For disputed jurisdictions, also publish **precinct closeout micro-packets** (poll tapes / seals / closeout notes)
bound to PublicNotice digests (`197-precinct-closeout-evidence-capture-and-publication.md`).
This creates a small, independent substrate that survives ENR compromise and screenshot laundering.


## Minimum controls

- Strong account security: hardware keys, least privilege, separate publish roles
- Content pipeline with staged approvals (two-person rule for “major changes”)
- Immutable logging (append-only logs for result publishing actions)
- DDoS readiness: anycast/CDN for static content, rate-limited APIs
- Monitoring: alert on unsigned updates, hash-chain breaks, unexpected deltas

## Evidence bundle (recommended)

After each reporting interval, publish a `ResultsReleasePackage` as an `EvidenceEnvelope` (`kind: hfv.results.release_package`; `238`):

- election id, EPB hash
- latest witness-quorum checkpoint (STH + cosignatures)
- list of ENR updates since last package
- notarization records (optional)
- human-readable summary and “what changed” diff

## References

- EAC: Checklist for Securing Election Night Results Reporting (ENR). `xref: eac_enr_securing_results_checklist_pdf`
- NIST: Election Results Reporting Common Data Format (ERR CDF) (for machine-readable results objects). `source: nist_sp1500_100r2_err_pdf`
- NIST: CDF implementation guidance across BD/CVR/ERR/EEL (for identifier/geography pitfalls). `source: nist_gcr_24_058_cdf_implementation_guidance_pdf`
- IETF: JSON canonicalization (JCS) for deterministic hashing and signatures. `source: rfc8785_txt`
- Results-object canonicalization + chain-linking contract (CRO/ENRUpdate/RRP): `235`.
- NIST: Security of Election Night Reporting topic + ENR use case materials. `xref: nist_enr_security_enr_use_case_page`
- IFES: Cybersecurity of Election Results Management Systems briefing. `xref: ifes_results_management_cybersecurity_briefing_pdf`
