# Revision notes — rev0974

## Product move

Rev0974 adds an exact, deletion-free physical payload-retention planner to the
retained C++ service:

```text
anonsync_sync retention-plan --socket ABSOLUTE_SOCKET \
    [--after LOWERCASE_SHA256] [--limit 1..1024] \
    [--source-cutpoint \
      v4:exact:OPERATION_SET:EVIDENCE_SET:PIN_SET:PAYLOAD_SNAPSHOT]
```

The command explains every physical payload object's current, historical,
inactive-evidence, and explicit-pin roots. It does not collect bytes.

## Exact owner observation

- The planner validates one digest cursor, a 1..1,024 page limit, and an optional
  current exact-v4 source token.
- A first SQLite snapshot permits early operation/evidence/pin stale rejection.
- One complete rooted payload snapshot is bracketed by a second SQLite snapshot.
- Payload-snapshot drift fails closed.
- Physical entries are digest ordered; the cursor must name one current object.
- Complete-scope reachability and three disposition partitions are checked
  against exact payload count and bytes before publication.
- Missing referenced or pinned content remains visible in the aggregate even
  though page entries enumerate physical objects only.

## Root reasons and dispositions

The shared owner vocabulary has four overlapping root flags:
`current_visible`, `superseded_active`, `inactive_evidence`, and `explicit_pin`.
Each physical object has one disposition:

- `current_or_explicit_pin`;
- `retained_history_or_evidence`; or
- `unreferenced_by_retained_file_operations`.

Unreferenced is a diagnostic fact, not reclaim authority.

## Operator and status surfaces

- `retention-plan` uses the existing mutex-linearized historical action lane.
- Strict local framing carries the complete plan query and remains PID-bound,
  owner-only, and drain-sealed.
- Equal requests coalesce; different pending queries reject.
- The local response is `anonsync.local-retention-plan.response.v1`.
- Live and terminal service reporting advance to
  `anonsync.peer-service.status.v19`.
- One completed plan is retained in stable history status; generic `last_step`
  drops the duplicate page.
- The canonical JSON explicitly reports no reclaim, quota, grace, or
  writer-fenced collection authority.

## Audit/refactor corrections

The root key, root-mask vocabulary, disposition mapping, canonical reachability
serializer, source-token codec, action lane, and status result path are shared
with existing historical ownership rather than duplicated as a collector.

The first plan status boundary was dead for valid input: the largest accepted
1,024-entry page encoded to 245,443 bytes under a 256 KiB limit. The limit is now
224 KiB. A focused maximum-page regression proves deterministic prefix
truncation, exact digest continuation, and remaining one-megabyte local-response
headroom.

The real configured-service regression pins a predecessor and proves that the
same retained daemon reports the exact physical object with an explicit-pin root
and `current_or_explicit_pin` disposition while all collection-authority flags
remain false.

## Cloudtainer divergence audit

A second unsealed rev0974 policy prototype and its orphaned registry runner were
stopped and removed before authoritative validation. It used payload-object
mtime as an age policy and introduced a parallel planner/codec surface. None of
its results are retained. Rev0974 deliberately ships only exact root
explanation; it does not guess causal chronology or select deletion candidates.
The audit also tightened the public dispositions to
`current_or_explicit_pin`, `retained_history_or_evidence`, and
`unreferenced_by_retained_file_operations`.

## Compatibility and nonclaims

Reconciliation protocol generation 2 and SQLite schema v6 are unchanged. The
new operation is local owner diagnosis and is not transmitted to peers. Direct,
Tor, and I2P routes continue to enter the same authenticated synchronization
semantics.

Rev0974 does not add garbage collection, automatic retention, quota eviction,
age/count/byte policy, grace windows, in-flight or pass-snapshot roots,
collection quarantine, Archive chronology, remote-history policy, or deliberate
version loss. Diagnostic corruption quarantine remains separate.

Exact rev0974 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 441 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 305/305 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed across bounded serial shards with leak detection and halt-on-error. One superseded combined sanitizer shard let the unchanged service lifecycle oracle reach its 30-second runtime cap after four of five cycles; the isolated authoritative rerun passed in 12.79 seconds with no sanitizer diagnostic. Focused sanitizer proof passed the 320-check SQLite-owner suite in 3.33 seconds at 556,136 KiB peak RSS, the 441-check folder-owner suite in 21.71 seconds at 1,412,208 KiB peak RSS, and the 155-check local-control suite in 0.63 seconds at 98,620 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0973 parent SHA-256 matched 62d265f026db82c946fe86df8700c6019826afc86604242716e9af564b84f7cd and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 18/18 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,336,658 bytes with SHA-256 1eb35263f32e14bb15be047a6bcadc88eb7aaac6bd5bcb9fd0898bf593b3377b. Validation excluded the rejected duplicate age-based planner prototype and every interrupted or timing-only non-authoritative run.
