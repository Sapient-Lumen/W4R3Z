# Public incident bulletin with digest references

**Track:** Shared / Public surfaces


## Purpose

When a high-stakes claim (or counter-claim) is in the public sphere, organizations often feel pressure to publish *something* quickly. The wrong move is to publish raw logs, private datasets, or vendor exports.

This document defines a **Public Incident Bulletin (PIB)**: a small, repeatable public update that:
- communicates what is known and what is not known,
- references **digest-first evidence surfaces** (AuLD / ICLD / HoldCapsule summaries) rather than raw artifacts,
- supports later third-party verification (see `289`) without forcing premature disclosure.

## Non-goals

- Replacing a full after-action report, court filing, or regulatory submission.
- Proving causality on day 0. A PIB is an **integrity and scope** update, not a complete narrative.

## PIB as an evidence surface

A PIB is itself an evidence surface:
- it is a dated public statement,
- it can be signed (SDS) and optionally timestamped/anchored,
- it creates an auditable sequence of public commitments.

### Minimal structure

A PIB SHOULD contain:

1) **Header**
- organization / scope label
- bulletin id (monotonic, e.g., `pib-2026-03-05-01`)
- published time (with timezone)
- severity + confidence + pii_risk tags (see `283`)

2) **Claim snapshot**
- the claim being addressed (1–3 sentences)
- what is *confirmed* vs *suspected* vs *unknown*
- explicit bounds: what the bulletin does not cover yet

3) **Evidence references (digest-first)**
- list of referenced digests:
  - AuLD ids (audit-log digest summaries) (`279`)
  - ICLD ids (incident command decision digests) (`280`)
  - HoldCapsule ids (preservation notices / scope) (`278`)
  - Controlled Disclosure Packet ids, if any (`282`)
- for each reference: include digest hash, scope label, and the minimum metadata needed for an external verifier to request access under controlled disclosure

4) **Actions underway**
- preservation steps taken (hold issued? vendors notified?)
- next verification step (e.g., “external verifier engaged”, “timestamp receipts pending”)

5) **Disclosure commitments**
- what will be published next, and under what conditions
- what will only be provided via controlled disclosure (and why)

6) **Signature / receipts (optional but recommended)**
- Signed Digest Statement (SDS) for the PIB digest (`285`)
- Timestamp Receipt (TSR) (`287`)
- Transparency-log anchoring pointer(s) (`284`)

## Patterns and pitfalls

### Pattern: public narrative, private payload

Publish:
- bounded facts, explicit unknowns, and *digests + receipts*.

Keep private until controlled disclosure:
- raw logs, detailed timelines that reveal vulnerabilities,
- personal data, credential material, vendor support transcripts.

### Pitfall: “trust us, we looked”

Avoid claims that cannot be verified later. Instead:
- commit to producing specific digest evidence surfaces,
- include a verifier contact channel and a “how to request” pointer to `289`.

### Pitfall: over-redaction

A PIB can be “safe” and still useless. If everything is “cannot disclose”:
- publish **scope**, **time bounds**, and **digest receipts** at minimum.

## Operational checklist (10 minutes)

- [ ] Draft PIB in the minimal structure above.
- [ ] Compute PIB digest and issue an SDS (`285`).
- [ ] If available, obtain a TSR (`287`) and/or anchor the digest (`284`).
- [ ] Ensure any referenced AuLD/ICLD/HoldCapsule digests exist and are internally consistent (`281`, `288`).
- [ ] Route through the disclosure/redaction pipeline (`282`) for a final pass.

## Artifacts

- `artifacts/templates/hfv.public_incident_bulletin.v1.json`
