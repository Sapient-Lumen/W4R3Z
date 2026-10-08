# Rev0947 online research and speculation

Checked on 2026-07-30. Sources are primary or official documentation. Research
informs design choices; it is not substituted for AnonSync runtime evidence.

## SQLite WAL commit cost

SQLite's WAL documentation describes commits as appends to the write-ahead log
and checkpoints as transfers back to the database. The `PRAGMA synchronous`
documentation states that `FULL` synchronization in WAL mode adds durability
work at transaction commit. This supports rejecting the prototype that opened
one immediate transaction per observed file: on many-small-file trees, the
journal could create thousands of avoidable commit/synchronization boundaries.

- https://www.sqlite.org/wal.html
- https://www.sqlite.org/pragma.html#pragma_synchronous

Speculation: one transaction per complete scan segment is the right bridge for
current scale. A future chunked journal should not be selected by row count
alone; it needs an explicit filesystem-authority reproof boundary so durable
cursor progress cannot outrun the rooted traversal proof.

## Watchers versus repair scans

Linux inotify documents queue overflow, watch invalidation/unmount behavior,
name-based event races, and limitations for some remote filesystems. Syncthing's
official tuning and FAQ material treats filesystem watching as a way to avoid
unnecessary periodic scan work, while retaining scans as repair behavior.

- https://man7.org/linux/man-pages/man7/inotify.7.html
- https://docs.syncthing.net/users/tuning.html
- https://docs.syncthing.net/users/faq.html

This matches AnonSync's current authority split: watcher events wake and rebuild,
but do not prove absence or epoch completion. Speculation: target-scale Linux
operation should evolve toward event-assisted dirty-subtree indexing plus a
rotating complete scrub, not toward “watcher-only” correctness.

## Persistent indexes and monotonic updates

Syncthing's Block Exchange Protocol persists folder indexes across connections
using index identifiers and monotonically increasing sequence numbers, allowing
subsequent index updates rather than complete retransmission. Its synchronization
documentation also describes block hashes, local block reuse, and temporary file
assembly.

- https://docs.syncthing.net/specs/bep-v1.html
- https://docs.syncthing.net/users/syncing.html

AnonSync's scan journal is intentionally smaller in purpose: it proves fair local
repair scheduling and deletion safety, not a durable whole-tree metadata index.
Speculation: the next index should unify exact path observation metadata,
subtree generation/change sequence, payload digest/size, and scrub state, while
keeping the descriptor-rooted scanner as rebuild authority. Reusing the scan
journal itself as that index would overload a short-lived epoch structure with
long-lived truth.

## Recovery and retention are product semantics

Syncthing exposes several file-versioning policies, and Resilio exposes Archive
retention for replaced/deleted versions. These are ordinary-user recovery
features, not invisible garbage-collector internals.

- https://docs.syncthing.net/users/versioning.html
- https://help.resilio.com/hc/en-us/articles/204754419-File-versioning-and-recovery

Speculation: AnonSync should design retention, restore, and payload garbage
collection together. Reachability must include current catalog entries, retained
versions, in-flight transfers, active snapshots/batches, and quarantine. A
collector added before a visible retention/restore contract could destroy the
very recovery behavior required to replace Resilio.

## Resilio parity surfaces

Resilio documents selective/full/disconnected synchronization modes, placeholder
behavior, Owner/Read-Write/Read-Only permissions, and encrypted folders for
untrusted storage peers.

- https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes
- https://help.resilio.com/hc/en-us/articles/205471375-User-Management
- https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

These sources reinforce that byte convergence is not sufficient replacement
parity. Speculation: after the first named workflow is measured, the highest
value surface is likely one of changed-block large-file transfer, selective sync,
or recovery/version UX—not a new internal proof taxonomy.

## Changed-file transfer

Syncthing documents fixed-size blocks, block hashes, local block reuse, and
retrieval of missing blocks. Rsync's original algorithm and technical report
show the broader value of rolling checksums and delta transfer while also making
clear that discovering reusable content has its own disk and CPU cost.

- https://docs.syncthing.net/users/syncing.html
- https://rsync.samba.org/tech_report/

Speculation: AnonSync can first add a manifest of fixed-size SHA-256 blocks over
its existing authenticated range protocol. Reuse should search the predecessor
file and retained local payloads before requesting ranges, then verify each block
and the final whole-file digest. Variable or content-defined chunking can follow
only if the measured uninstall workload benefits.

## Product prioritization conclusion

The fair scan epoch corrects a real liveness and deletion-safety defect, but it
does not answer how large or dynamic the target tree is. The next session should
capture one owner's actual Resilio workload and make its success criteria an
executable qualification matrix. Research examples are useful comparators; they
cannot choose AnonSync's product priorities in place of that measurement.
