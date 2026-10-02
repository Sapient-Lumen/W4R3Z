# toxsync roadmap

## 2026-09-01 hardening checkpoint

The full standalone source, CLI, tests, package, and current IoTox embedding seam have been
re-audited without changing a wire/disk format. Exact retained-publication retry, scheduler online
accounting, exclusive key-pair creation, collision-resistant test workspaces, a backend-aware CLI
transaction, and a repeatable TSan lane are closed. The registry is 125 native checks plus three
CTest routes.

The remaining standalone work is evidence-led: power-loss injection at every durable boundary,
named filesystem/architecture coverage, longer scheduler/publication/GC soaks, and independent
review. Product authority, conflict policy, transport, and retention witnesses remain IoTox-owned
rather than migrating into the component.

## 0.7 / rev0010 — autonomous closure primitives

Completed in the library:

- bounded HEAD summary/query/receipt anti-entropy records;
- publication transactions that commit immutable content before a linked signed HEAD;
- restart-safe verified treepack activation with an atomic current-revision switch;
- external path sorting with bounded memory and bounded open-run count;
- cancellation checkpoints, lane backoff, and verified-goodput observation seams;
- retained byte compatibility for range-v1 and both flat and paged content-v2.

Completed by the IoToxsync embedding above the library:

- O(jobs) durable synchronization intents and restart recovery by immutable-store rescan;
- live request deadlines, retry-after, failover history, no-source/retry-exhausted terminal states,
  and connection-epoch invalidation;
- reconnect HEAD anti-entropy and receipts;
- bounded inventory work off the toxcore owner thread;
- one-binary publish and activate commands plus live activation jobs;
- accepted-HEAD retention reconciliation and bounded conservative garbage collection;
- measured useful-goodput input to the elastic lane controller;
- exact restart-safe per-peer HEAD obligations and operator-managed durable subscriber fanout.

Still open before unattended production use:

- namespace reader authorization and optional content encryption/key epochs;
- automatic subscriber discovery and membership policy;
- automatic publisher watcher/debounce and a consistent source-snapshot facility;
- small-circle/custodian membership policy;
- staging quotas and complete filesystem metadata semantics;
- real c-toxcore LAN/relay, target-board, flash, power, thermal, and Nix evidence.

## 0.5 / rev0008 — paged content fabric

Completed in the library:

- signed mutable HEAD records and strict acceptance policy;
- flat and paged v2 manifests with bounded random-access windows;
- sparse availability sketches and exact inventory bitmaps;
- allocation-stable dynamic and rarest-first multi-source schedulers;
- verified content-object ingest with zero-copy same-filesystem publication;
- checksum-protected pin journal, compaction, conservative mark/sweep, and dry-run;
- bounded reconstruction of flat and paged manifests;
- a bounded transport-neutral content-fabric session for page bootstrap, window scheduling,
  verified object ingest, restart rediscovery, and final reconstruction;
- fabric benchmark, formula-scale tests, sanitizers, and fuzz decoders.

Integrated into IoTox:

- explicit namespace-to-writer trust rather than friendship-as-authority;
- durable accepted-HEAD state and fork/rollback rejection;
- capability, inventory, HEAD, and range protocol frames;
- bounded exact inventory service and peer inventory cache;
- resource-derived logical range lanes over one Tox friendship, with one as the unmeasured default.

## 0.6 / rev0009 — elastic live IoTox worker

The transport-neutral receiver is now bound to the IoTox rev0010 event pump, exact inventories,
range completions, and a bounded reconstruction worker. The remaining hardening work is:

- measure source-linked c-toxcore LAN/relay behavior and feed observations into `LaneTuner`;
- persist active job intent while continuing to recover chunk progress through store rescans;
- use conservative sketches as discovery prefilters before exact inventories;
- feed useful-goodput, timeout, retry, and stall observations into lane policy;
- persist operator-visible session summaries without journaling per-chunk state;
- reconstruct, verify, treepack-unpack, and activate through one explicit local command.

## v2 hardening — evidence driven

- real c-toxcore LAN and relay measurements for one through four lanes;
- scrub/repair policy for corrupt local objects;
- pin/reference policy for baselines, current revision, rollback window, and operators;
- Merkle-paged or hierarchical roots only if root page tables become material;
- content encryption at rest only with a reviewed identity/key-rotation design;
- project-owned Ed25519 only if removing OpenSSL is worth the audit surface.

The range-v1 engine remains the minimum-complexity choice for stable-offset artifacts. v2 is
selected per namespace, not imposed globally.
