# 196 — Core glossary and terms of art

**Track:** Shared

This glossary defines **project-local meanings** of a small set of recurring terms.
It is intentionally short: if you need paragraphs to define a term, the term probably needs a dedicated spec.

## 196.1 Evidence primitives

- **Evidence object:** a JSON payload with a schema under `schemas/` (catalog: `EVIDENCE_OBJECT_CATALOG.md`).
- **EvidenceEnvelope:** the signed (or signable) wrapper around an evidence object (`173`, `176`).
- **Payload digest:** `sha256(JCS(payload))` recorded as `payload_digest` (`176`).
- **TBS digest:** “to-be-signed” digest for an envelope, computed over canonical fields (`176`).
- **Detached payload:** payload stored under `packet/objects/sha256-<hex>.json` and referenced by `payload_pointer` (`173`).

## 196.2 Publication and verification surfaces

- **Evidence packet:** a directory containing `manifest.json`, `envelopes/`, `objects/`, and optional notes (`173`, `92`).
- **Evidence API surface:** the minimum set of envelope kinds and registries a verifier must implement (`179`).
- **Verifier profile:** a small, stable capability claim (profile ID) a verifier can publish to indicate which kind sets it supports (`179`, `docs/VERIFIER_PROFILES.md`).
- **Publishable verifier output:** a privacy-safe report that can be cited publicly without leaking operator internals (`193`).
- **Comparability pins:** optional sha256s of stable registry bytes included in reports so two reports can prove they used the same rules (`99–100`, `tools/public_surface_pins.py`).

## 196.3 Comms as evidence

- **PublicNotice:** the canonical “official statement” envelope kind (`186`, schema: `schemas/PublicNotice.json`).
- **OfficialChannelDirectory:** a content-addressed directory of declared official public channels for a jurisdiction/election (published as evidence; `203`).
- **Rumor control:** Public notices that correct false claims using “myth → fact → how to verify” (`186`, `195`).
- **Status board:** a human-facing index over `PublicNotice` digests, not an authority separate from notices (`195`).
- **Parity:** the requirement that declared official channels show the same notice digests (anti targeted suppression) (`104`, `194`, `195`).
- **Stale pointer:** when caches/CDNs/proxies serve an older discovery payload (feed/directory/well-known) so users see outdated digests; treated as a split-view-adjacent risk and handled via explicit cache posture + parity snapshots (`205`, `201`).
- **OfficialSurfaceSecuritySnapshot:** a content-addressed snapshot of DNS/TLS/email anti-spoofing posture (CAA/DNSSEC/CT/DMARC/SPF/DKIM) published as evidence to make comms hardening auditable (`199`).
- **CAA / DNSSEC / CT monitoring / SPF / DKIM / DMARC:** standard domain/certificate/email controls used to reduce spoofing and detect mis-issuance (`37`, `199`).

## 196.4 Transparency and anti-equivocation

- **Transparency log:** an append-only public record of commitments (core primitive: `04`).
- **Witness gossip:** multi-vantage cross-checking to detect split-view and selective disclosure (`23`, `100`).
- **Receipt:** a verifiable acknowledgement/commitment from a transparency system or witness tier (`180–185`).
- **Selective disclosure:** withholding or showing different evidence to different audiences; treated as an attack surface (`180`, `100`, `104`).

## 196.5 Process terms

- **Track A/B/C:** deployable core vs research annex vs North Star (`START_HERE.md`, `154`).
- **Claims contract:** what this archive asserts and what must be provable (`166`, `159`).
- **Non-claims:** explicit boundaries to prevent accidental overreach (`167`).
- **Epistemic tag:** a statement label (OBSERVED/MEASURED/REPORTED/INFERRED/UNKNOWN) plus confidence to prevent interpretation drift (`218`).
- **Proof obligation (PO):** a named, checkable thing that must be provable to justify a claim (`159`, `164`).
- **Release gate:** the checks that prevent silent drift and broken examples (`162`, `scripts/`).
## 196.6 Precinct closeout evidence

- **Poll / results tape (“poll tape”):** the printed closeout tape produced by a precinct scanner/BMD system, commonly used as a local, human-readable snapshot at close.
- **Precinct closeout micro-packet:** a small evidence packet containing poll-tape photos (and optionally seal/container photos + a closeout note) published and bound to a PublicNotice digest (`197`).
- **PrecinctCloseoutIndex:** content-addressed mapping of reporting unit ids → closeout packet manifest digests; chained updates make rollbacks detectable (kind `hfv.results.closeout_index`, `198`).
- **Closeout index:** a published mapping of reporting unit ids → closeout packet manifest digests, used to detect selective omission (`198`).

- **Well-known discovery** — A domain-first bootstrap surface (e.g., `/.well-known/election-stack.json`) that points to the latest directory/feed digests so outsiders can start from a single official domain (docs/204).
