# Rev0953 audit summary

Rev0953 corrects two composition defects on the shipping folder-convergence
path.

First, remote-only exact-digest work no longer requires a complete private
payload namespace snapshot. One pass-scoped targeted-access capability amortizes
identity reconciliation and rooted setup, while every probe or selection still
uses a fresh nonblocking shared lease and exact marker/root reproof. The selected
descriptor is hashed only by the existing atomic publisher. This point lane does
not attest unrelated entries or complete namespace capacity; the full snapshot
remains the sole health/inventory oracle.

Second, a completed remote sweep can publish scheduling progress only while a
replica `BEGIN IMMEDIATE` guard proves the expected complete visible-state digest
and a nested short catalog `BEGIN IMMEDIATE` transaction re-proves the exact
catalog, authenticated scan, and prior remote-work heads. Any miss reports
`authority_cutpoint_changed`. The final `sync-once` predicate also compares the
pass's published remote fairness cursor with the final durable cursor, preventing
scheduling-only movement from being hidden behind equal content digests.

The implementation refactors required and optional POSIX regular-file component
opening through one fail-closed path, centralizes full-snapshot versus targeted
payload selection, and gives ordinary and idle completion one terminal helper and
one settlement predicate. Runtime tests bind explicit namespace-health nonclaims,
publication-time corruption detection, one-access amortization, complete-snapshot
reuse, cross-owner movement, exact terminal diagnostics, and cursor mismatch.
The lexical source audit passes 75/75 checks; it is a regression tripwire, not a
semantic, cryptographic, filesystem, concurrency, or crash proof.

The two SQLite databases remain separate durable owners. The fence proves one
real writer-serialized observation at catalog scheduling publication but is not a
cross-database/filesystem transaction. Targeted lookup is not a durable payload
index. Complete projection restoration, per-candidate exact-name probes,
restart-cold local/snapshot payload walks, process-local verification cache,
append-only history, whole-file changed transfer, and missing retention/restore/
garbage-collection ownership remain open.

See `TARGETED_REMOTE_PAYLOAD_ACCESS_AUDIT_rev0953.md` and
`TERMINAL_CROSS_OWNER_SETTLEMENT_FENCE_AUDIT_rev0953.md`.
