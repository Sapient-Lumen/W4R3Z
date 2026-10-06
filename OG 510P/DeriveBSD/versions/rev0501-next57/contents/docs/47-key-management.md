# Key management (signing, rotation, revocation)

DeriveBSD is signature-heavy. This doc defines the minimal viable key story.

## Key classes
- Root trust keys (rarely used): authorize intermediate keys
- Signing keys: sign artifacts/attestations
- Host identity keys (optional v1)
- Secrets sealing keys (optional)

## Rotation + revocation
Policy must express:
- trust key for certain target kinds only
- distrust after cutoff date
- allow rollover windows

See `rfcs/RFC-0003-cache-signatures.md` and `rfcs/RFC-0034-trust-policy-schema.md`.
Last updated: 2026-02-23
