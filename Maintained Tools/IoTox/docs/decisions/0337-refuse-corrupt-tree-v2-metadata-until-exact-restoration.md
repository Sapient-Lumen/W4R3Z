# ADR 0337: Refuse corrupt tree-v2 metadata until exact restoration

- Status: accepted, implemented, and qualified on the founding Sandwurm/KVM/ext4 stack
- Date: 2026-09-08

## Context

Tree-v2 has five live namespace-local metadata families that can authorize or
describe synchronization effects:

1. the mutable current branch pointer;
2. its referenced immutable branch record;
3. its referenced immutable manifest;
4. the signed workspace state; and
5. the signed maintenance state.

The branch store already authenticated the first three while loading a
frontier. Agent startup, however, did not authenticate present workspace or
maintenance state for every configured tree-v2 namespace. Likewise,
`sync-repair` verified frontier closure and selected CAS objects but could
report success while a workspace or maintenance record was corrupt. Treating
bad signed metadata as absent, deleting it, or replacing it from a peer would
hide evidence and could erase the only retained frontier, pin, or writer
cutoff.

This is an integrity and availability boundary, not a backup or freshness
mechanism. A byte-invalid signed record can be detected locally. An older but
cryptographically valid record requires the separate witness design in ADR
0314.

## Decision

1. Agent startup authenticates the branch-pointer to immutable-record to
   manifest closure, every present signed workspace state, and signed
   maintenance state under the namespace transaction before the configured
   tree-v2 namespace can proceed to worker or network exposure.
2. `sync-repair` authenticates the same five semantic roots before verifying
   selected immutable content. It reports `metadata=verified` and whether the
   workspace and maintenance records are present only after this succeeds.
3. Errors carry a stable metadata-family context: branch pointer, immutable
   branch record, manifest, workspace state, or maintenance state. A failed
   immutable-record load is propagated rather than collapsed into a generic
   pointer-closure mismatch.
4. Startup, repair, and ordinary mutations do not delete, quarantine, rewrite,
   or overwrite corrupt signed metadata. They fail closed and leave its exact
   bytes in place for operator inspection.
5. Recovery requires an operator to restore byte-exact reviewed metadata
   externally. IoTox then authenticates it normally; restoration does not
   bypass signatures, namespace binding, or frontier closure.
6. A bounded qualification gate runs three source-linked nodes over a local
   Tox full mesh inside one networkless Cloud Hypervisor/KVM guest on ext4. It
   creates all five families, stops both peers, and applies one durable,
   same-size last-byte bit flip to each family in order. For each family:

   - live `sync-repair` must refuse with the family label and retain the exact
     corrupt bytes;
   - clean Agent shutdown must not change those bytes;
   - a fresh Agent process must exit nonzero with the same family label and
     retain the exact corrupt bytes;
   - external in-place restoration of the exact original bytes, followed by
     file and parent-directory `fsync`, must permit startup with the same
     identity, worktree, and verified metadata.

7. After all five cells, both peers return and the full mesh must converge to
   branch counts `[3,3,3]`, the unchanged five-file tree, and successful repair
   on all nodes. A strict verifier binds the clean source revision, binary
   digest, networkless KVM chain, ext4 filesystem, ordered family set, refusal
   and byte-retention claims, final convergence, and explicit nonclaims. A
   compact exporter retains only five content-free JSON records and enforces a
   2 MiB source-evidence ceiling.

## Consequences

Corrupt signed metadata can cause denial of service, but it cannot silently
become authoritative or be erased by a command whose name suggests repair.
The operator gets an exact family diagnosis and a conservative recovery
boundary. This deliberately favors evidence retention and rollback safety over
automatic availability.

The gate covers one present live record in each of five families and one
single-bit mutation per record. It does not cover truncation, extension,
record substitution, filename swaps, permission/link/path attacks, multiple
simultaneous corruptions, every historical record, or an older valid signed
state. It does not cover policy, automation, attempt-journal, witness,
health-record, projection-marker, quarantine-inventory, or CAS-object
corruption. CAS objects retain their separate verified quarantine repair path.

Peers are stopped while corruption and restoration occur. The gate does not
cover replication races, a cut during restoration, remount/open-descriptor
behavior, dishonest storage, firmware behavior, physical power removal,
independent failure domains, authenticated backup provenance, or precious-data
suitability. The original bytes used by the harness are operator-supplied test
input, not proof of an independent backup.

Construction, verification, and compact export use:

~~~sh
./tools/iotox-sandwurm-lab.sh up-sync-metadata-corruption
./tools/iotox-sandwurm-lab.sh verify-sync-metadata-corruption PROOF_ROOT
./tools/iotox-sandwurm-lab.sh export-sync-metadata-corruption PROOF_ROOT
~~~

Source-linked run `mixJ9VUp` at commit `08e4179` and binary SHA-256
`449107ef7152547ededabd378c6298cda2963169527e2912f79676209fcef5bf`
passes all five ordered cells, exact restoration, final `[3,3,3]`
convergence, and repair on all three nodes. Its strict compact proof is
`.sandwurm/exports/sync-metadata-corruption/run.mixJ9VUp`; see
[`../evidence/2026-09-08-sync-tree-v2-metadata-corruption.md`](../evidence/2026-09-08-sync-tree-v2-metadata-corruption.md).
