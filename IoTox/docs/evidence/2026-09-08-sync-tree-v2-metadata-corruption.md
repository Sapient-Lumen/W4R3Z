# Tree-v2 signed-metadata corruption and exact restoration — 2026-09-08

## Result

IoTox rev0050 passes the first source-linked signed-metadata corruption gate on
the founding Sandwurm/Cloud-Hypervisor/KVM/ext4 stack. One networkless VM ran
three real IoTox daemons over an internal loopback Tox mesh with all six
directed read/write shares. The campaign created all five live namespace-local
signed metadata families, then corrupted and restored them one at a time in
this fixed order:

1. current mutable branch pointer;
2. referenced immutable branch record;
3. referenced immutable manifest;
4. signed workspace state; and
5. signed maintenance state.

For every family, a same-size final-byte XOR `0x01` followed by file and
parent-directory `fsync` caused live `sync-repair` to refuse with
`error=protocol-error` and exit 4. The exact corrupt bytes remained in place.
After a clean daemon stop, a fresh Agent process refused startup with exit 3
and the expected family classification; the corrupt bytes again remained
unchanged. Only external in-place restoration of the exact original bytes,
with file and parent-directory `fsync`, allowed the same identity and worktree
to reopen.

After the fifth restoration, the other two nodes returned. All three nodes
converged to branch counts `[3,3,3]`, retained the same five-file/one-directory/
16,411-byte tree, and passed final metadata and content repair. The result is
fail-closed detection plus exact operator restoration. It is not automatic
metadata repair.

## Bound build and topology

```text
source Git commit:       08e4179f7cfeb6448afa2cf5e7b908deb7d3db80
product:                 IoTox 0.50.0 rev0050
binary SHA-256:          449107ef7152547ededabd378c6298cda2963169527e2912f79676209fcef5bf
proof ID:                run.mixJ9VUp
substrate:               Cloud Hypervisor / KVM, 2 vCPU, 2 GiB
guest filesystem:        ext4
guest network class:     none
IoTox transport:         loopback-only inside the networkless VM
nodes / directed shares: 3 / 6
campaign elapsed:        26,429 ms
final tree SHA-256:      1d1c86ea77eadc494258669412902108a02e1e1846ebf7b939bbc6967a12016d
final tree shape:        5 files / 1 directory / 16,411 bytes
final branch counts:     3 / 3 / 3
repair-verified nodes:   3
```

The exact per-family receipt is:

| family | bytes | original SHA-256 | corrupt SHA-256 | live repair | cold startup |
| --- | ---: | --- | --- | --- | --- |
| branch pointer | 472 | `5a617a71bf72bb9260a1ba03e1e021803ce2447b7b65a0db169305978bbe1ada` | `0cf16d1beae3d90d1979d0c165c5422e57e6a802d14cf81d8dab0bdce1de3c40` | protocol error / exit 4 | family-classified / exit 3 |
| immutable branch record | 472 | `5a617a71bf72bb9260a1ba03e1e021803ce2447b7b65a0db169305978bbe1ada` | `0cf16d1beae3d90d1979d0c165c5422e57e6a802d14cf81d8dab0bdce1de3c40` | protocol error / exit 4 | family-classified / exit 3 |
| manifest | 619 | `c7243b0b38ac35492e2a5e7155ec945b9202fcb86271496eba34a579421825ef` | `44dabaf78e34b76dfc70f6722c5afb0ebf8e3a14cda37d266157e02d6b90dac0` | protocol error / exit 4 | family-classified / exit 3 |
| workspace | 13,592 | `466e53d152fc56d3a7d30432eb72eb8aa1b0fbc5f9d3c1ede0c5fca83ef80ae1` | `213e7c4af929cafa79cfc3efcc0f645d62face37bbdedbf91da0b9324cb97d3b` | protocol error / exit 4 | family-classified / exit 3 |
| maintenance | 248 | `f1337ac0c078806f8aa51fdd157c125e7072cf192cbadf3626df9956b00475d5` | `b8da7e665a5b6a6273ff867bed106554a6172d53e09834088c5c26201ce9e597` | protocol error / exit 4 | family-classified / exit 3 |

The pointer and immutable record deliberately have identical bytes and hashes:
the current pointer is an authenticated copy of the selected record. The gate
still targets their different paths and requires the error to identify the
corrupt family at the point where it is loaded.

## Method and integrity boundary

The campaign seeded five files and one directory, checkpointed and pinned the
namespace so workspace and maintenance records were present, and required the
three-writer graph to converge before mutation. Peers A and B were then stopped
so no ordinary replication race could overwrite or obscure node C's local
corruption.

Each target was changed in place without changing inode length. The harness
captured the original and corrupt hashes, fsynced the modified file and exact
parent, and checked byte equality after both refusal paths. It did not delete,
rename, quarantine, or substitute the record. Exact restoration reused the
captured original test bytes, wrote them in place, fsynced the file and parent,
then restarted the same identity and verified the worktree plus all five
metadata roots.

The guest first publishes its receipt on guest-private ext4 owned by root and
mode `0700`. Only after local validation does the NixOS service copy the exact
receipt into the Sandwurm proof channel with `O_EXCL`, file `fsync`, and parent
directory `fsync`. The host verifier independently binds:

- clean 40-hex source revision and exact rev0050 product identity;
- source-linked binary digest;
- networkless direct Cloud Hypervisor launch and KVM guest evidence;
- ext4 state root, three nodes, six directed shares, and the ordered five-family set;
- canonical live repair exit 4 and cold startup exit 3;
- corrupt-byte retention and byte-exact restoration for every family;
- identity/worktree preservation, final tree digest, `[3,3,3]`, and three repairs;
- closed receipt schemas, duplicate-key rejection, bounded JSON loads, and exact compact-file digest closure.

The compact exporter does not copy extensible Sandwurm records verbatim. It
projects them into closed, content-free lifecycle summaries, copies the two
exact IoTox guest receipts, fsyncs every file and directory, and publishes the
finished root with `renameat2(RENAME_NOREPLACE)`. Its self-test injects a
nested sentinel secret into a raw Sandwurm fixture and proves that the compact
export cannot retain it.

The guest harness classifies each cold-start error before publishing the
receipt. Compact evidence retains the exact family, exit 3,
`startup_family_classified=true`, and a SHA-256 commitment to that startup log;
it deliberately does not retain the potentially private log itself. The host
verifier therefore authenticates the closed guest classification assertion and
log digest, but does not independently reparse the omitted startup log.

## Defect found by qualification

The first clean source-linked attempt, `run.BB5I3Ow1` at commit `1100a0b`,
failed closed before mutation. Virtiofs preserved the host UID on the mounted
receipt directory, so the rehearsal correctly rejected it as not
guest-owner-private even though its mode was `0700`.

Commit `08e4179` kept that ownership check and moved primary receipt creation
to the service's guest-private ext4 state directory. The service validates the
receipt there before durably publishing a no-replace copy to Sandwurm. The
accepted rerun then completed in 26.429 seconds. The rejected attempt is
diagnostic provenance, not qualification evidence.

## Compact evidence

The retained content-free proof is:

```text
proof root:               .sandwurm/exports/sync-metadata-corruption/run.mixJ9VUp
manifested files:         5
manifested bytes:         6,123
compact tree bytes:       7,323
source-proof-root SHA-256:b4d96db4abb5df65fb799f65407bd72c616797c84b3188c5efca795617a7e2eb
compact-manifest SHA-256: b0ac88a09ea54f860d575125a8fb79c27f483d9f7f4ba1f7e5a661b4eaf8ffa2
contains secrets:         false
```

The five manifested records are the closed live-chain summary, closed
prelaunch summary, closed live-launch summary, exact VM smoke receipt, and
exact metadata-corruption receipt. The separate `compact-export.json` is the
authenticated manifest and is not counted among its five payload records.
Both the raw root and compact root passed the strict verifier after export.

Reproduce from a clean checkout on the prepared Sandwurm host with:

```sh
./tools/iotox-sandwurm-lab.sh up-sync-metadata-corruption
./tools/iotox-sandwurm-lab.sh verify-sync-metadata-corruption \
  .sandwurm/lab/sync-metadata-corruption/RUN_ID
./tools/iotox-sandwurm-lab.sh export-sync-metadata-corruption \
  .sandwurm/lab/sync-metadata-corruption/RUN_ID
./tools/iotox-sandwurm-lab.sh verify-sync-metadata-corruption \
  .sandwurm/exports/sync-metadata-corruption/RUN_ID
```

## Nonclaims and next gates

This evidence covers one current live record from each of five signed tree-v2
families and one last-byte mutation per record on one honest virtual storage
stack. It does not prove automatic repair, quarantine, or peer replacement of
signed metadata. Recovery requires operator-supplied byte-exact originals; the
gate does not prove that those bytes came from an independent or trustworthy
backup.

It does not cover truncation, extension, record substitution, filename swaps,
permission/link/path attacks, exhaustive bit mutation, valid-old signed
rollback, multiple simultaneous corruptions, every historical record, or
policy, automation, attempt-journal, witness, health, projection-marker,
quarantine-inventory, or CAS-object corruption. CAS objects retain their
separate verified quarantine repair path.

Peers are stopped during mutation and restoration, so this is not a
replication-race result. It does not cover a cut during corruption/restoration,
remount or open-descriptor behavior, dishonest storage or firmware, physical
power loss, another filesystem/kernel/hypervisor, an independent failure
domain, long soak, or precious-data/sole-copy suitability. An attacker able to
modify these files can still cause denial of service; cryptographic integrity
does not establish freshness. Valid but old signed state remains the separate
rollback-witness problem.

The compact proof's cold-start family label is a checked guest-harness
assertion committed by `startup_log_sha256`, not an independently replayable
host-side log classification.

The next corruption frontier is valid-old and simultaneous signed-record
substitution, followed by the remaining effect-bearing durable families and
an authenticated operator restore ceremony. The broader storage frontier
still includes projection/remount open-descriptor cases, lying storage,
independent backup restore, cold/near-ceiling repetition, and the 24-hour
writable soak.
