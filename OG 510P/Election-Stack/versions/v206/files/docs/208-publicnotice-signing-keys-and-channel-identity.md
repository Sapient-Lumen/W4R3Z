# 208 — PublicNotice signing keys and channel identity (verifiable comms root)

**Track:** A (Deployable core)

Docs `186`–`206` treat operational communications as evidence via **PublicNotice**. This doc tightens the *root of authenticity* for those notices:

> **Audiences need a pre-committed, verifiable answer to “which key(s) are allowed to speak as the jurisdiction?”**

If we do not pre-commit, an attacker can win with “credible fake” statements during the highest-friction moments.

## 208.1 New evidence object: PublicNoticeSigningKeyset

- **Envelope kind:** `hfv.public.notice_signing_keyset`
- **Payload schema:** `schemas/PublicNoticeSigningKeyset.json`

This object is a small, content-addressed list of public keys (or key references) authorized to sign **PublicNotice** envelopes for a specific election scope.

### Minimal rules (normative)

1) **Pre-commitment**
   - A jurisdiction SHOULD publish at least one `hfv.public.notice_signing_keyset` **before election day**.
   - It MUST be **receipted + gossiped** (per attachment registry) so it is hard to selectively bury.

2) **Key allow-list enforcement**
   - Verifiers SHOULD warn if a PublicNotice signature key is not present in the latest keyset for that election scope.

3) **Rotation + anti-rollback**
   - Keyset updates SHOULD include `previous_keyset_payload_sha256` to form a hash chain.
   - Rollback (serving an older keyset) is treated like a **public-surface split view**.

4) **Emergency key use**
   - If an emergency key must be used outside the keyset, the issuer MUST publish:
     - a PublicNotice explaining the emergency rekey, and
     - a new keyset that includes the emergency key.

## 208.2 Where the keyset digest lives (discovery anchors)

The keyset is only useful if audiences can *find* it under attack.

Recommended anchors:
- `hfv.public.official_channel_directory` MAY include `discovery.public_notice_signing_keyset_payload_sha256`.
- `hfv.public.well_known_discovery` SHOULD include `pointers.public_notice_signing_keyset_payload_sha256`.
- Digest cards (`206`) SHOULD include the keyset payload digest alongside the PublicNotice feed digest.

This makes “which key is official?” a small, portable verification step.

## 208.3 Failure modes this closes

- **Channel impersonation:** fake screenshots, fake accounts, fake “press releases”.
- **Channel compromise:** attacker posts via an official account, but cannot sign a matching PublicNotice.
- **Key confusion:** multiple plausible keys; the keyset makes authorization explicit.

## 208.4 Related

- `186` — Incident communications as evidence (PublicNotice)
- `195` — Rumor control + status boards (verifiable public surfaces)
- `203` — Official channel directory (where to look)
- `204` — Well-known discovery bootstrap
- `206` — Digest cards for low-bandwidth publication
