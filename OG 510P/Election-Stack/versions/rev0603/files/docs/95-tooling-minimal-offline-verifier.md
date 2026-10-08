# 95 — Minimal Offline Verifier Tooling

**Track:** A (Deployable core)


This pack includes `observer-kit/tools/offline_verifier.py`:
- validates file hashes in `manifest.json`
- validates signatures over the manifest using `public_keys.json`
- uses RFC8785-JCS canonical bytes for manifest signing (see `92`)
- prints a human-readable verification summary

It is intentionally minimal and does not attempt to verify full ballot cryptography.
Instead, it provides a reliable “bundle integrity + provenance” check and creates a stable base for full verifiers.

Full cryptographic verification SHOULD be done by separate, independently audited verifier tools; see `94-independent-verifier-diversity.md`.