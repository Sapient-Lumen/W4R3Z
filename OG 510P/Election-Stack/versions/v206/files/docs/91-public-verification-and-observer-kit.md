# 91 — Public Verification & Observer Kit

**Track:** A (Deployable core)


## Goal
Make it possible for **any independent party** (journalists, candidates, observers, courts, universities) to verify:
1) what parameters were “official” (ballot definition, election public key, disclosure policy),
2) that the public bulletin board (PBB) log did not fork,
3) that a published tally/results package is consistent with the posted record,
4) that the public-facing Election Night Reporting (ENR) feed is not a “cheap legitimacy hack.”

This subsystem is intentionally designed to work:
- **offline** (after downloading a bundle),
- under **partial outage / censorship / CDN split views**, and
- with **verifier diversity** (multiple independent implementations).

## Threat model (observer kit)
- **Parameter substitution:** a voter is served a different ballot definition or election public key than “official”.
- **Split-view / equivocation:** different observers see different log histories.
- **ENR compromise:** results web/API is altered without touching the tally record.
- **Verifier monoculture:** a single verifier bug becomes a systemic blind spot.
- **Disinformation:** claims that “the system was hacked” (true or false) spread faster than evidence.

## Minimal publish set (MUST)
### A) Election parameters
- ElectionParameterBundle (EPB) object and hash.
- Ballot Definition CDF bundle and hash.
- DisclosurePolicy object and hash.

### B) PBB transparency record
- Quorum-witness checkpoints (Signed Tree Heads / Checkpoints).
- Witness public keys + policy document (who must sign what).
- ForkProof format (if equivocation is detected).

### C) Tally / results
- Election record / election record index.
- Tally proof package.
- ResultsReleasePackage (for each reporting interval) plus the final certified package.

### D) Operational evidence (privacy-safe)
- Event log exports in a common data format (or a mapping statement) for forensic auditing.
- `hfv.public.notice` PublicNotice envelopes for “proof-first” public statements (status/incident/correction/rumor_control).

## Observer workflow (high level)
1) Download the **ObserverKit Bundle** for the election/interval.
2) Verify bundle integrity (hashes + signatures).
3) Verify EPB is included in the PBB and covered by witness-quorum checkpoint(s).
4) Verify checkpoint chain (append-only) and absence of forks.
5) Verify tally/results package against the election record with ≥2 independent verifiers.
6) Verify ENR feed matches the signed ResultsReleasePackage (no drift).
7) Archive the bundle hash + checkpoint ID in independent venues (optional notarization).

## Operational recommendations (SHOULD)
- Publish bundles via multiple mirrors (gov site, university mirror, NGO mirror).
- Provide a “one-command” offline verifier for non-experts.
- Publish test vectors and known-good verifier builds.

See: `92-offline-verifier-bundle-spec.md`, `94-independent-verifier-diversity.md`.