# rev0881 compact audit record

## Mission fit

AnonSync's load-bearing mission remains exact authority accounting: canonical
evidence owns identity and causality; local filesystem, clock, namespace,
transport, retry, and summary observations may constrain action but may not
silently manufacture history. Rev0881 corrects places where a local capability
or stale in-memory copy could be mistaken for current durable authority.

## Corrected receiver frontier

Canonical replicated path validity is now separate from receiver-local filename
capability. A portable-valid component that is provably longer than the retained
root can represent returns typed `DestinationPathBlocked`/
`EffectPathBlocked` before effect insertion, payload retention, generation
advance, causal admission, or namespace mutation. The positive
`statvfs().f_namemax`/`_PC_NAME_MAX` minimum is a conservative preflight, not a
universal descendant theorem; indeterminate observations defer to the actual
descriptor-relative publication syscall.

File delivery explicitly advances to protocol v2. Pre-effect path/capacity
receipts bind the request, channel, generation, and cutpoint while forbidding an
effect ID or nested evidence receipt. Old v1 frames are rejected rather than
silently reinterpreted.

## Corrected sender frontier

Validated nonterminal receipts and pre-frame exceptions release the exact claim
through the owner under a positive bounded local retry policy. The receiver does
not supply sender time. One helper now owns the complete missing/stale/expired
contradiction matrix, removing duplicated exception paths.

The deeper finding was a normal-return callback race. Payload-source code ran
after an attempt had been minted and could mutate that attempt without throwing;
the service then built a frame from its stale C++ copy. Rev0881 adds
`SyncReplicaSqliteOutboxDispatchGuard`: after arbitrary callback code, the owner
opens `BEGIN IMMEDIATE`, fully restores state, proves exact claim/operation,
permits only bounded same-claim deadline renewal, observes owned time, revokes
expiry durably, independently re-attests staged state, and retains the writer
transaction through bounded local validation/encoding/digest construction.

Missing and stale identities do not sample or ratchet time. Expiry publishes a
clock-only revocation without fabricating retry release. Guard destruction rolls
back; guard commit is one-shot. Construction failure drops the guard before the
service attempts exact durable release, so it cannot deadlock against its own
writer slot.

The staged cutpoint sequence was refactored into one reusable independent
attestation function plus a commit wrapper. This reduces security-sensitive
copy/paste while preserving the precommit reload used by ordinary owner writes.

## Live context refactor

`SyncPosixMountNamespaceAuthority` retains the current thread's Linux mount
namespace handle and re-proves it against a fresh handle at each use; failure is
sticky. `SyncDirectoryAuthority` captures that capability before traversal.

Two divergent Linux boot-ID readers now delegate to one strict bounded
`sync_system_epoch_identity` observer. A proposed durable boot/mount equality
schema was removed because those identifiers are reboot-ephemeral and no
authorized rebind ceremony exists.

## Evidence hierarchy

Load-bearing fresh evidence is:

- one complete 191/191 CTest invocation;
- one complete 60/60 audit-named CTest invocation;
- 5,149/5,149 focused assertions in GCC Debug, Clang 17 Release `-Werror`, and
  GCC ASan/UBSan with bundled SQLite instrumented;
- 4,440/4,440 repeated authority assertions across 80 runs; and
- deterministic negative matrices for callback mutation, writer exclusion,
  renewal, stale/missing identity, exact expiry, malformed payload, and
  connection-local TEMP-trigger rollback.

The 477/477 selected source-audit checks are lexical architecture/package
hygiene only. They are not behavioral, concurrency, cryptographic, or formal
proof.

## Remaining severe boundaries

The newly returned frame is still only a local construction result. It may wait
in a queue until its claim expires or changes. Linux `send()` itself does not
prove remote delivery. A future transport owner must re-attest immediately
before first-byte dispatch or introduce durable frame ownership and explicit
crash/retry transitions. Holding a SQLite writer across unbounded network I/O
would be the wrong correction.

Unavailable boot identity still escapes as an adapter exception before durable
clock quarantine. Existing impossible staged paths lack an authorized repair
transition. The shipped executable still does not compose the newer owner stack.
Windows parity, restart/root rebind, indexed production ownership, full effect
vocabulary, complete retry/dead-letter policy, membership/key lifecycle,
compaction/rejoin, anonymity, externally signed provenance, and formal proof
remain open.
