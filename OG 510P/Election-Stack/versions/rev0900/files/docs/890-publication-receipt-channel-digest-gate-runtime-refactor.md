# 890 — Publication-receipt channel-digest gate runtime refactor

**Track:** Shared / Verifier / Release gate

rev0860 wires `scripts/check_publication_receipt_channel_digests.py` into the release-gate inventory and refactors it to use the repository in-process CLI harness.

The gate remains narrow: trust-chain publication receipts must retain per-channel observed subject digests, and the current verification-policy receipt must keep digest/id aliases coherent. Removing channel observed digests from trust-keyset, governance, status, signer-authorization, or policy receipt fixtures must fail closed.

Audit: `artifacts/reports/publication-receipt-channel-digest-gate-refactor-rev0860.json`.

Boundary: these are synthetic fixtures. They do not prove real public-channel control, legal delegation, or production signer authority.
