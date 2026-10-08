# Trust-anchor rotation, delegated authority, and recovery paths are world contracts, not static provenance

Recent trust-management practice adds another missing layer to Concord's long-horizon stewardship worlds: **it matters whether successors inherit a system that can rotate trust anchors, narrow or revoke delegated authority, and recover from signer compromise without freezing the archive or silently replacing the root of trust by fiat**.

- `RS-GR-332` shows that NIST treats trust anchors, key-inventory management, backup, compromise, recovery, and cryptoperiod planning as part of core key management rather than as optional cleanup.
- `RS-GR-333` shows that live trust-anchor rollover can require long prepublication windows, vendor / package-maintainer distribution work, and readiness for accelerated rollover rather than an instant key swap.
- `RS-GR-334` shows that authenticated automated trust-anchor updates need explicit revocation, hold-down, and recovery semantics, and that some compromise cases still require manual or other out-of-band intervention.
- `RS-GR-335` shows that modern update-trust frameworks keep root keys offline, rely on threshold trust, allow revocable delegated roles, and require out-of-band root recovery if a threshold of root keys is compromised.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **trust-anchor rotation windows, delegation / threshold topology, or emergency recovery paths** — not because the underlying Golden-Rule disposition improved.

## Why this matters for Concord

A future-facing benchmark should not report that an institution “preserves provenance for successors” when the world mainly changed its **trust-root lifecycle architecture**.

There is a real institutional difference between:
1. a world with one static trust root and no declared replacement horizon;
2. a world that plans a future rollover but has no propagation or standby model;
3. a world with automated in-band trust-anchor update but no explicit compromise or revocation path;
4. a world with thresholded delegated authority but no clearly published emergency out-of-band recovery route; and
5. a world that looks durable only because successors inherit a rotation-ready trust chain instead of one brittle long-lived signer.

Those are not provenance-aftercare details.
They change whether future inheritors receive a living trust institution or a static signature shell that fails the first time authority has to rotate.

## Minimal implementor handoff

If Concord adds archive, attestation, repository, or successor-trust lanes, publish at least:

1. the declared lifetime / cryptoperiod or replacement horizon for each trust anchor or root signer;
2. whether trust-anchor updates are manual, automated in-band, vendor-distributed, or otherwise staged through a declared propagation path;
3. the delegation graph, threshold policy, and revocation rights for subordinate signers or roles;
4. the compromise response path, including what requires out-of-band recovery and who is authorized to perform it;
5. whether headline results survive one same-behavior comparison where only trust-anchor rotation / delegation / recovery semantics change.

Without that compact contract, future inheritors can mistake rotation-ready trust governance for the same thing as deeper reciprocity toward successors.
