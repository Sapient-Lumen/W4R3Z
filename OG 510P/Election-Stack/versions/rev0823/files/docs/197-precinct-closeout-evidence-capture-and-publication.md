# 197 — Precinct closeout evidence capture + publication (poll tapes, seals, and snapshots)

**Track:** A (Deployable core)

This doc defines a **minimal, deployable** lane for capturing and publishing *precinct closeout* evidence
so that later disputes have a stable, independently verifiable substrate.

It deliberately does **not** attempt to replace chain-of-custody law, canvass procedures, or RLAs.
Instead it makes common closeout artifacts **hash-addressable**, **mirrored**, and **bound to public notice** so
tampering, selective deletion, and “fake screenshot” attacks become harder to sustain.

See also:
- `63-election-night-reporting-and-public-results-security.md` (ENR hardening)
- `195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md` (public surfaces as verifiable indexes)
- `198-precinct-closeout-index-and-omission-detection.md` (closeout index for omission detection)
- `186-incident-communications-as-evidence.md` (incident comms as evidence objects)
- `177-observer-kit-offline-verification-walkthrough.md` (offline verification)
- `43-evidence-bundles-and-court-proofing.md` (bundle structure)

---

## 197.1 Threat model (what this lane addresses)

This lane is meant to reduce impact from:

- **ENR-only compromise**: website/API/social accounts publish altered “unofficial” numbers.
- **Selective deletion / suppression**: some precinct artifacts vanish, especially from contested areas.
- **Screenshot laundering**: images of “results” circulate without provenance or stable identifiers.
- **Slow drift edits**: “minor corrections” accumulate without a public change log.
- **Time ambiguity**: unclear when a photo was taken vs. when it was posted.

This lane is **not sufficient** against:
- ballot substitution without paper controls,
- coercion / voter intimidation (see Track B/C),
- legal disputes that require statutory chain-of-custody documentation.

---

## 197.2 Minimal closeout evidence set (recommended)

A jurisdiction SHOULD publish a *precinct closeout micro-packet* for each reporting unit (precinct / tabulation center),
containing only a few artifacts:

1. **Poll tape / results tape photos** (one or more angles; readable).
2. **Seal / container evidence** (photos of seal numbers on ballot containers, memory media, etc., if used).
3. **Closeout summary note** (short text): reporting unit id, close time window, who captured, and any anomalies.

Optional but useful:
- **Short video pan** over the tape and environment (to reduce “single-frame” ambiguity).
- **Witness cosignatures** (see `142-witness-network-operations.md`) for high-salience jurisdictions.

> Design rule: keep the set small enough that publication is routine, not heroic.

---

## 197.3 Packaging pattern (EvidenceBundleManifest + envelopes)

Use a standard evidence packet layout (see `177` / `43`):

- `manifest.json` — `EvidenceBundleManifest`
- `objects/` — content-addressed media (e.g., `sha256-<hex>.jpg`)
- `envelopes/` — `EvidenceEnvelope` objects that describe and bind the media

Recommended naming inside the manifest:

- `PrecinctCloseout: poll_tape_photo_01`
- `PrecinctCloseout: seal_photo_01`
- `PrecinctCloseout: closeout_note`

### Envelope guidance (tight)

For each media object, emit an `EvidenceEnvelope` with:

- `kind`: `hfv.media.capture` *(implementation-defined; do not treat as a public registry addition without ADR)*
- `track`: `A`
- `subject`: at minimum `{ election_id, jurisdiction_id, reporting_unit_id }`
- `payload_schema`: use a local schema URI *or* `schemas/EvidenceEnvelope.json` with detached payload pointers
- `payload_digest`: sha256 over canonicalized payload describing the capture (pointer + minimal metadata)

Keep payload metadata minimal:
- capture timestamp (best effort)
- device / capture operator id (best effort)
- “what this is” label (poll tape, seal, etc.)
- any anomalies (e.g., “tape torn; second photo taken”)

---

## 197.4 Binding to a public surface (PublicNotice + parity)

A closeout micro-packet is only useful if the public can find it and detect selective omission.

Minimum pattern:

1. Publish the packet (or its manifest + objects) at a stable public URL (jurisdiction site + mirrors).
2. Publish a **PublicNotice** entry whose payload includes:
   - reporting unit id
   - packet manifest digest (`sha256:<hex>`)
   - mirror URLs
   - an incrementing closeout index for the election (optional but helpful)

3. Mirror the **PublicNotice digest** across official channels (website, status board, social, press email)
   using the parity monitoring patterns in `195` / `194`.

4. (Recommended) Update a **PrecinctCloseoutIndex** and bind it to the same surface so missing precincts are measurable (`198`).

This makes “the thing the public should trust” a short digest that is hard to counterfeit at scale.

---

## 197.5 Verification (what an observer can prove)

Given:
- a closeout micro-packet directory (or downloaded copy), and
- the corresponding PublicNotice digest (from multiple channels),

an observer can verify:

- the packet’s internal integrity (object hashes match filenames / manifest)
- envelopes bind the declared payload digests
- the packet manifest digest matches what the public notice claimed
- mirrors are serving identical bytes (or detect divergence)

See `177-observer-kit-offline-verification-walkthrough.md` for the offline procedure.

What this does *not* prove:
- that the tape reflects a correct tally (audits handle that),
- that the photo was taken at the claimed time (though witnesses + multiple angles help),
- that *every* precinct’s packet exists unless you also publish a closeout index (`198`, recommended).

---

## 197.6 Minimal checklist (operator view)

Operator-ready checklist: `artifacts/checklists/precinct-closeout-evidence-capture-checklist.md`.


For each reporting unit:

- Capture poll tape photos (readable; multiple angles if needed).
- Capture seal/container photos (if applicable).
- Write the closeout note (unit id, time window, anomalies).
- Package into a micro-packet (manifest + objects + envelopes).
- Publish to primary site + at least one mirror.
- Issue a PublicNotice digest referencing the packet manifest digest.
- Ensure parity: the digest appears consistently across official channels.

If anything fails, publish a PublicNotice describing the failure mode (missing photo, late upload, etc.).
Failing loudly is better than silent gaps.

---

## 197.7 Source anchors (informative)

- `xref: cisa_rumorcontrol_page` (rumor-control as a public practice; see also `195`)
- `source: eac_enhancing_election_security_public_comms_2024_pdf` (public comms as security surface)
- `source: stark_gentle_introduction_rla_2012_pdf` (audits remain the correctness backstop)
