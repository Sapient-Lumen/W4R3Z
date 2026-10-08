# Adapter-binding trust-policy promotion refactor — rev0339

## What changed

Rev0338 made external attestation executable: a producer could no longer promote evidence by writing a `verified_external_attestation` label. Rev0339 closes the next replay risk: a valid signature is now useless unless it is bound to the exact adapter scope it is being used to satisfy.

The signed evidence payload now carries an `adapter_binding_hash`. That binding is derived from the case, adapter id, adapter type, route, source, model class, scope, and required outputs. Adapter execution rejects externally observed promotion-grade evidence when the evidence hash or signed payload hash does not match the live adapter packet.

## Why this was the riskiest next edge

A detached signature proves only that someone signed a payload. Without a scope binding, the same signed evidence can be replayed into a different case, route, source, or model check. That would reopen the old category error in a more sophisticated form: true evidence for one burden could be treated as authority for another.

Rev0339 makes the relation explicit:

`adapter packet -> adapter binding hash -> evidence payload -> signed payload -> verifier result -> replay ledger -> promotion gate -> held or finalizable output`

The proof object must now satisfy both cryptographic verification and semantic placement.

## Runtime changes

- `tools/verify_external_attestation.py` requires `adapter_binding_hash` in the signed canonical JSON payload.
- Trust-store entries may restrict keys to allowed adapter-binding hashes.
- Trust policy now fails closed for revoked keys, expired entries, inactive keys, and missing transparency-log metadata when transparency is required.
- `tools/execute_decision_adapters.py` computes the live adapter binding and blocks cross-case or cross-route replay.
- Replay ledgers and promotion packets carry both the live adapter binding and any evidence-supplied binding.
- Decision-output hashes now include the adapter binding surface, so output packets cannot hide a placement change.

## Audit/refactor performed

The verifier audit now covers:

- valid signed evidence;
- no configured trust store;
- tampered payload;
- forged verified status;
- expired attestation;
- revoked key;
- transparency-required policy without a transparency proof;
- valid evidence replayed against the wrong route.

The replay and promotion audits now count adapter-binding hashes and binding mismatches. The output audit requires every materialized adapter record to expose the live adapter-binding hash. The semantic-audit runner now keeps shared caches but isolates expensive audits so a long-lived worker does not retain all intermediate graphs.

## Current state

The release still holds all 122 cases because the built-in evidence is schema/test evidence, not externally observed implementation evidence. This is deliberate. Rev0339 proves that even a valid local signature cannot cross into promotion unless it is bound to the specific adapter it answers and is accepted by the configured trust policy.

Current release facts:

- Cases checked: 122
- Adapter records checked: 1,724
- Schema-satisfied adapter records: 1,672
- Explicit no-go or blocker records: 52
- Structurally finalizable cases before promotion: 83
- Externally observed adapter records: 0
- Promotion-eligible adapter records: 0
- Finalized cases: 0
- Held cases: 122
- Adapter binding hashes recorded: 1,724
- External evidence adapter-binding hashes: 0
- Adapter binding mismatches: 0

## What remains production-risky

Rev0339 still does not provide a production trust root, transparency-log inclusion verification, timestamp authority, revocation feed, key-rotation ceremony, or human reviewer authorization workflow. It creates the narrow executable seam where those systems can attach without weakening the truth boundary.

The next highest-value pass should add one small sample external-evidence bundle with a trusted test key, a transparency-log stub, and one deliberately promotable non-doctrinal toy case. That would prove the positive path without pretending the archive has live-law authority.
