# Fetch phase design (pinned inputs, hostile network)

DeriveBSD separates fetch from build:
- Fetch: constrained network access, allowlists, pinned hashes (Lock).
- Build: jail with no network (ADR-0008).

## CA handling
FreeBSD libfetch supports configuring CA bundles via:
- `SSL_CA_CERT_FILE`
- `SSL_CA_CERT_PATH`

Policy can require explicit CA bundle provenance (e.g., pinned `ca_root_nss`).

Last updated: 2026-02-23
