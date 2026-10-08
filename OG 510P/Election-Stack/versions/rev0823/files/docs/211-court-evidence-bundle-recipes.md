# 211 — Court evidence bundle recipes (bounded, claim-first)

**Track:** A (Deployable core)


This document defines a **bounded** pattern for assembling court-usable evidence packets that remain verifiable offline.

Goal: when you need to prove *one specific claim* (or disprove one allegation), you should be able to ship a small packet whose `manifest.json` (an `EvidenceBundleManifest`) makes the contents auditable, mirrorable, and resistant to post-hoc story edits.

## 211.1 Principles (keep it small)

- **Claim-first:** an evidence bundle is for *one* claim (or one allegation family). If you need more, ship more bundles.
- **Claim card included:** ship a small `claim.md` (see `217`) so humans can’t widen the scope boundary post-hoc.
- **Loud failure > silent ambiguity:** if an input is missing, the bundle should prove *that it is missing* (receipts + gossip + coverage/missingness artifacts).
- **Bundle-local completeness:** every byte required for offline verification MUST be listed in `manifest.json`.
- **Transformation accountability:** if any evidence-relevant exhibit is redacted/transformed for publication, include `redaction-log.md` per `DOC:docs/225-redaction-logs-and-transformation-accountability.md`.


## 211.1.1 When courts are slow or institutions fail

This bundle format is named “court evidence,” but the durability requirement is broader:
**evidence must survive the window when legitimacy is decided.**

- If courts refuse to hear a challenge, or act months later, the packet remains verifiable without vendor services.
- If public channels are compromised, the packet’s manifest digest + witness/monitor receipts let third parties reconstruct what was published and when.

Treat “filed in court” as one use case, not the only one.
The historical record is an adjudicator too.

## 211.2 Bundle root: EvidenceBundleManifest

The packet root `manifest.json` MUST validate against `schemas/EvidenceBundleManifest.json` and MUST include at least:
- the content-addressed `objects/` entries required for verification
- any human-oriented copies under `envelopes/` (optional) referenced by digest

Production bundles SHOULD sign the manifest with a jurisdiction-controlled key (or a neutral packager key with publicly declared custody).

## 211.3 Minimal recipes (by catastrophe class)

These are **minimum viable** bundles: small packets that still allow independent parties to reach the same conclusion.

### A) Publication suppression / missingness (catastrophe class 2–3)

Include:
- `hfv.publication.contract`
- `hfv.publication.trigger_event`
- `hfv.publication.suppression_report`
- `hfv.coverage.publication_report`
- `hfv.coverage.liveness_beacon` (at least two independent watcher identities)
- If the incident involves public comms: `hfv.public.notice` (and if the claim depends on what a public surface served, record a bounded request context per `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md` in a capture note or parity snapshot notes) + `hfv.public.notice_signing_keyset`

### B) Fork / equivocation (catastrophe class 1–2)

Include:
- the conflicting envelopes (same `kind`, divergent `payload_digest` / checkpoint chain)
- receipts + gossip summaries for both views
- the minimal witness set policy artifacts that explain quorum expectations
- a `hfv.public.notice` announcing the fork finding and pointing to the bundle digest

### C) Cross-register consistency breach (impossible turnout)

Include:
- `hfv.results.cross_register_consistency_report`
- the referenced `VRDBSnapshot` payload digest and the referenced results payload digest (CRO or ENR)
- receipts + gossip summaries for each of the above
- a `hfv.public.notice` that states the constraint, the scope, and the computed status

### D) Official-communications impersonation / channel compromise

Include:
- `hfv.public.notice_signing_keyset` (the precommitted allow-list)
- at least one genuine `hfv.public.notice` and the disputed impersonated artifact (if publishable)
- an `hfv.public.surface_parity_snapshot` showing what different audiences saw
- `hfv.coverage.liveness_beacon` entries showing the pointer digests observers observed



### E) Stale pointer / replay-by-proxy (cache split-view)

Use when audiences report different “current” values for pointer surfaces (/.well-known, directory, feed, keyset).

Include:
- `hfv.coverage.liveness_beacon` (≥2 independent watchers) that record:
  - `payload_sha256` for each pointer surface (when parseable)
  - freshness headers (`etag`, `cache_control`, `age_seconds`, `last_modified`) (`docs/210`, `docs/205`)
- `hfv.public.surface_parity_snapshot` for each affected `surface_kind` (portable “who saw which bytes?” proof)
- `hfv.public.notice` that:
  - states the canonical digests clients should trust *right now*
  - cites the beacon + snapshot digests
  - states the remediation plan (purge/rotation + next update time)

For effective-state divergence across official channels (feeds/corrections mismatch), also follow `222`.

Keep it bounded: do **not** bundle long HTML/JSON bodies unless they are strictly necessary; hashes + receipts + comparable snapshots are the point.

## 211.4 Court packaging tips (tight)

- Include a one-page **cover sheet** (claim + bundle digest + how-to-verify). Template: `artifacts/templates/court-cover-sheet.md`.
- Put the **claim** and the packet digest in the cover page (a one-page `notes/README.md`).
- Include the verifier output as its own small packet where feasible:
  - `hfv.verifier.packet_verification_report`
- If physical custody artifacts exist (paper-of-record), anchor them:
  - include a custody packet digest and reference it from closeout evidence (see `docs/197–198`).



**Admissibility note:** evidentiary standards vary by jurisdiction.
Treat “court-friendly” as a research surface: document verifier provenance (tool hashes/build identity),
chain-of-custody assertions, and a short human-legible explanation of the verification procedure.
See `172.1.1` for the open question and the minimum collaboration needed with election-law practitioners.


## 211.5 Admissibility worksheet (jurisdiction-bound, minimal)

Courts differ. Do **not** assume “hash matches” is self-explanatory. For any bundle you expect to file or cite, include a *filled* worksheet (1–2 pages) that answers:

- **Authentication:** who can attest that this bundle is what it claims to be (custodian declaration, signature keys, publication method)?
- **Chain of custody:** how did the bytes move from source → packaging → filing (who handled it, when, and what controls)?
- **Tool provenance:** what verifier binary was used (hash, build identity, reproducibility status, where to get an identical build)?
- **Explainability:** a short, human-legible explanation of the verification step(s) performed (what was checked; what would cause failure).
- **Exhibits:** which items are human-facing exhibits vs machine-checkable objects (and how each exhibit maps to a digest in `manifest.json`).

Template: `artifacts/templates/court-admissibility-worksheet.md`.

**Crypto primer (keep it one page):** if the tribunal is not already comfortable with cryptographic verification,
include a short appendix that explains (in plain language) *what the verification actually establishes* and what it does **not** establish.
At minimum: what SHA‑256 digests are used for, what JCS canonicalization is, what a signature proves (and does not prove),
and how an opposing party can reproduce the verification.

Template: `artifacts/templates/crypto-primer-one-page.md`.

**Expert lane (optional):** where required, include a brief expert declaration that (a) describes the verifier tool provenance
and (b) explains the cryptographic checks at the level expected for the jurisdiction.

Template: `artifacts/templates/expert-declaration-outline.md`.

Keep this bounded: the goal is “minimum documentation that makes the bundle usable,” not a legal treatise.


### 211.5.1 Jurisdictional admissibility matrix (pilot planning)

Before a pilot (or any intended filing), maintain a *small* jurisdiction sheet that answers:
“**What would make this packet admissible and usable here?**”

Template: `artifacts/templates/jurisdictional-admissibility-matrix.md`.

Track progress (without embedding long jurisdiction memos) in: `artifacts/registries/admissibility-jurisdiction-index.csv` (store only bounded pointers/digests).

Keep it bounded:
- one page per jurisdiction / forum,
- link to bundle-local worksheets (`court-admissibility-worksheet.md`) rather than duplicating them,
- treat changes in law/rules as a refresh trigger (publish as a dated artifact).


## Relationship to other docs

- Evidence bundle operational requirements: `docs/43-evidence-bundles-and-court-proofing.md`
- Canonical packet layout and manifest rules: `docs/173-canonical-evidence-envelopes-and-packets.md`
- Publication contracts + suppression proofs: `docs/181`
- Missingness surface (liveness beacons): `docs/210`
