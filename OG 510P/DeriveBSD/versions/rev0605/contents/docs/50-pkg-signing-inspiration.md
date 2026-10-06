# Repo signing inspiration: FreeBSD pkg-repo(8)

FreeBSD pkg signs repository metadata (pkg-repo(8)). DeriveBSD learns the operational pattern:
- distribute pubkeys
- verify before install
- treat transport/mirrors as untrusted

DeriveBSD extends this to:
- artifact digests
- provenance attestations

Last updated: 2026-02-23
