# 43 — Evidence bundles and court-proofing (operational, claim-first)

**Track:** A (Deployable core)


This document defines operational requirements for producing **court-usable** evidence bundles that remain verifiable under adversarial conditions (including litigation and disinformation campaigns).

The primary constraint is *use*, not existence: bundles must be small enough to be filed, copied, mirrored, and explained to humans under time pressure.

## Requirements (Track A posture)

- **Claim-first:** each bundle supports *one* claim (or one allegation family). If you need more, ship more bundles. (See `docs/211`.)
- **Content-addressed + immutable:** the bundle root MUST be an `EvidenceBundleManifest` whose entries are keyed by digest (`schemas/EvidenceBundleManifest.json`).
- **Offline-verifiable:** a third party MUST be able to verify the bundle without vendor services (observer kit / verifier; `docs/177`, `docs/188`).
- **Digest-first presentation:** the bundle MUST include a one-page cover sheet that states the claim boundary and the bundle digest so the filing can be referenced without screenshots or “trust me” narratives.
- **Provenance + custody are explicit:** the bundle MUST include (or be accompanied by) a short admissibility worksheet describing authentication, chain of custody, and tool provenance (`artifacts/templates/court-admissibility-worksheet.md`).
- **Transformation accountability:** if any exhibit is redacted/transformed for publication, include a redaction/transformation log (`docs/225`).
- **Mirrorability:** if the bundle is public, it SHOULD be mirrored by independent parties and referenced by digest in a `PublicNotice` (or equivalent signed statement) so authenticity is faster to verify than to fake.
- **No legibility theater:** avoid giant scans/opaque portals. If something cannot be made operationally usable, publish the missingness as evidence (`docs/187`, `docs/210`).

## Bundle anatomy (minimum)

Every Track A bundle SHOULD include:

1) `manifest.json` (the `EvidenceBundleManifest`) and the referenced `objects/` (content-addressed)
2) `claim.md` (bounded claim card; `docs/217`)
3) `notes/README.md` (one-page cover sheet; `artifacts/templates/court-cover-sheet.md`)
4) `notes/admissibility.md` (1–2 page worksheet; `artifacts/templates/court-admissibility-worksheet.md`)
5) a replayable verifier output artifact where feasible:
   - `hfv.verifier.packet_verification_report` (bundle- or packet-scoped)

Depending on the claim, include only the *minimal* evidence objects required to verify it:

- **Publication/comms evidence:** `hfv.public.notice`, publication contracts/trigger events, coverage/suppression reports, parity snapshots, capture notes.
- **Results/audit evidence (paper floor):** results objects + correction discipline, precinct closeout evidence, audit artifacts, custody anchors.
- **Governance surfaces:** witness/monitor policies relevant to quorum, liveness+dissent, and independence.
- **Tool provenance:** verifier binary hash/build identity, policy profile digest pins, and any test vectors needed to reproduce checks.

If the claim is about a cryptographic protocol step (Track B/C work), include the specific proofs and parameter bundles required by that claim — but keep the packet claim-first and bounded.

## Filing and publication (tight)


- If you will file or cite the bundle, treat **admissibility** as a first-class requirement: courts differ, and “hash matches” is not self-explanatory. Keep the worksheet bounded but explicit.
- Keep jurisdiction-specific admissibility planning bounded: track which venues have a filled matrix/worksheet (and where those artifacts live) in `artifacts/registries/admissibility-jurisdiction-index.csv`.
- If you publish the bundle, publish a digest-first pointer (PublicNotice/feed entry) and ensure mirrors agree on bytes/digests.
- Prefer multiple small bundles over one large “everything dump.”

See also: `docs/211-court-evidence-bundle-recipes.md` for **bounded, claim-first** recipes aligned to the catastrophe ordering.


## Schemas

- `schemas/EvidenceBundleManifest.json` — the manifest is the root of the bundle.

## Related templates (court usability)

- `artifacts/templates/court-cover-sheet.md`
- `artifacts/templates/court-admissibility-worksheet.md`
- `artifacts/templates/crypto-primer-one-page.md`
- `artifacts/templates/expert-declaration-outline.md`
- `artifacts/templates/jurisdictional-admissibility-matrix.md`
