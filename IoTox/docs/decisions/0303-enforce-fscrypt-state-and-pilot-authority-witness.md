# ADR 0303: Enforce fscrypt state and pilot the authority witness

- Status: accepted and implemented for the construction-host first tier; authenticated remote service added by ADR 0305
- Date: 2026-09-02

## Context

ADR 0302 rejected a cosmetic per-file encryption wrapper. IoTox has many security-bearing durable
roots with distinct atomic-replace, guard, quarantine, and recovery protocols. Encrypting selected
codecs would miss equivalent authority and could change established crash ordering. Local signed
guards also cannot detect a coordinated replay of the complete matching disk state.

The first implementation therefore had to preserve existing filesystems semantics, close over every
configured path, and establish freshness as a separate transaction rather than calling encryption a
rollback defense.

## Decision

Add the inseparable Agent options `--require-state-protection fscrypt-v2`,
`--protected-state-root PATH`, and `--protected-state-policy-id HEX`. The last is the public 16-byte
master-key identifier, not key material. IoTox accepts neither a key nor a passphrase. Before
creating its
runtime tree or opening security-bearing stores, it descriptor-pins the normalized owner-private
root and requires:

- fscrypt policy v2 and a kernel-reported present exact master-key identifier;
- one `statx` mount identity throughout;
- owner-private directories and single-link regular files, with no special inodes;
- the same exact policy on every extant directory and regular file;
- component-wise no-follow containment of savedata, identity, authority ledger/guard/witness intent,
  command/diagnostic/alias stores, incarnation and route locks, route-worker roots, Ratox policy,
  every loaded sync namespace root, update policy/state/slots/quarantine, and file-backed Agent
  configuration; and
- runtime on tmpfs or inside the same protected root.

Absent descendants are permitted only below a verified existing parent so Agent-created files inherit
the policy. A wrong policy-ID pin, prefix siblings, `..`, configured symlinks, hard links, bind/mount
crossings, weak modes, foreign ownership/policy, absent keys, and plaintext roots fail closed. `run-check` performs a
side-effect-free inspection and `run` repeats it at the actual start boundary.

Because a complete closure is only useful if IoTox can preserve it, `StateStore::write_atomic` now
records every absent parent component it creates and seals each `0700` without changing pre-existing
directory permissions. The VM caught the previous `0755` diagnostic-store parent on first restart.

Implement the generic rollback-witness record and exact compare-and-swap backend contract, then use it
for the authority lane. The lane-global position is authority record count, not the ownership-epoch
sequence. Before local mutation the ledger durably writes a canonical intent containing the exact
owner-signed next record, old/new heads, random nonce, domain, device, epoch, and lane. It then moves
the external witness from committed to pending, performs the existing local guard/ledger transition,
commits the external witness, and durably removes the intent.

Recovery completes only the exact pending transition. A lost reply is queried and resolved
idempotently. Missing pending intent, wrong identity/domain/epoch/lane, unrelated local head,
whole-ledger rollback/deletion, fork, invalid signed record, or witness unavailability refuses. A
backend sharing the Agent's control/failure domain must report false and is rejected except behind an
explicit test-only configuration. There is no CLI switch that asserts independence.

Finally, perform authority reconciliation and all durable security opens before `RuntimeTree::prepare`
so a witness failure exposes no local control/FIFO/socket surface.

## Consequences

The optional first tier now gives a measurable encrypted-at-rest claim for a complete IoTox state
closure while leaving default deployments and every existing state codec unchanged. An ext4-fscrypt
NixOS VM proves correct/wrong/re-added keys, raw-media canary absence, tmpfs/no-swap placement, and
representative path/mount escapes. Twelve new owned checks bring the direct registry to 759 and cover
configuration refusal plus witness record/CAS/recovery/rollback behavior, including both lost-reply
boundaries and a pre-revocation whole-ledger/guard snapshot replay.

This does not close workstream 8. ADR 0305 subsequently selects and implements the authenticated
remote-service backend, but only authority mutations participate and same-host evidence does not
qualify operational independence. Application/Ratox
incarnations, terminal policy, route generation, sync/update state, and pre-effect command identity
still need witnessed lanes and the exhaustive crash/restore ceremony campaign. fscrypt leaks metadata,
does not protect an unlocked running kernel or establish freshness, and is not a backup.
