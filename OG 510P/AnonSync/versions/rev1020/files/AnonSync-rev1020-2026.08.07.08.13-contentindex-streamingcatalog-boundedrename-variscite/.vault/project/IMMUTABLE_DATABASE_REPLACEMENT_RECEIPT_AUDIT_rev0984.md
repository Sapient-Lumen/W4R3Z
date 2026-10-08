# Immutable database-replacement receipt audit — rev0984

## Product reason

Rev0983 could durably install a detached primary-replica database and then
advance its recovery epoch, but a process or machine failure between those two
commits left the operator to identify and finish the transition manually.
Rev0984 closes that bounded offline crash window without turning immutable
backup creation into a restore engine and without inventing an online raw
SQLite-family swap protocol.

The shipping command is now:

```text
anonsync_sync database-recovery-replace \
  --manifest ABSOLUTE_JSON \
  --snapshot ABSOLUTE_SQLITE \
  --rollback ABSOLUTE_SQLITE \
  --receipt ABSOLUTE_RECEIPT \
  --expected-current v1:INCARNATION:EPOCH:CUTPOINT
```

It still requires the service to be stopped and claims the same deployment
singleton before opening the candidate, rollback, receipt, or active database.

## One immutable receipt, not a mutable stage journal

The receipt is a bounded create-new file. It is never rewritten and never says
that an effect happened. It binds:

- the deployment identifier and manifest digest;
- SHA-256 digests of the selected manifest, active database, candidate,
  rollback, and receipt pathnames;
- the exact operator-approved displaced database expectation;
- complete candidate and rollback artifact digests, SQLite geometry, and causal
  cutpoints;
- a domain-separated action digest; and
- a separately domain-separated checksum of the complete canonical record.

The digest domains include explicit NUL bytes. Compile-time assertions protect
that framing, and the process oracle independently recomputes both digests from
the published bytes. The canonical record is at most 8 KiB, mode 0600,
single-linked, no-follow opened, and independently reopened after publication.
Absolute path strings are not stored in the receipt.

The receipt is evidence that one exact action was admitted. It is not database
effect authority. Progress is classified only from the active database's exact
logical cutpoint.

## Exact restart classifier

After candidate, receipt, and rollback reproof, the active database must be
exactly one of three states:

1. **displaced database current** — publish or re-prove the rollback, install
   the candidate, and advance its recovery epoch;
2. **candidate installed, epoch pending** — do not copy the database again;
   advance exactly once; or
3. **recovery epoch advanced** — perform no mutation and independently re-prove
   the completed result.

Any fourth state fails closed as unknown continuity. The owner also rejects two
ambiguous action shapes before publishing receipt or rollback state: candidate
and displaced cutpoints may not be identical, and the displaced database may
not already be the candidate's exact recovery successor. A candidate whose
recovery epoch or state generation is `UINT64_MAX` is rejected at the same
pre-admission boundary because it has no representable recovery successor.

A receipt-only restart may recreate the rollback only while the active database
is still the exact operator-approved displaced state and the recaptured bytes
match the immutable receipt. A missing rollback after the active database has
advanced is terminal; the receipt cannot manufacture rollback authority from a
different database.

## Effect order and reproof

For a new action the durable order is:

1. validate the complete candidate, rollback, and receipt namespace geometry;
2. detached-capture and fully verify the candidate;
3. capture the exact displaced database under a bracketed forensic source
   cutpoint;
4. reject ambiguous restart shapes;
5. publish and reopen the immutable receipt;
6. re-prove the rollback output family and publish the displaced logical
   database create-new;
7. release the resident displaced image;
8. independently reopen and verify the durable rollback;
9. re-prove the receipt and classify the active database;
10. perform only the missing SQLite and recovery-epoch effects;
11. close the writer and independently reopen the exact final database;
12. release the resident candidate and rollback images, then recapture and
    fully re-attest each selected pathname one at a time against the receipt;
13. re-prove the immutable receipt and reopen the final database again,
    requiring the same cutpoint around the artifact reads.

The adjacent refactor centralizes exact optional-file absence classification.
A failed receipt or rollback open is treated as absence only when a fresh
`symlink_status` observation reports exact `ENOENT`/`not_found`; permission,
I/O, symlink, type, mode, link-count, and other failures are rethrown. The same
refactor releases the complete resident displaced image before reopening the
published rollback, avoiding an unnecessary candidate + displaced + rollback
three-image peak. Final success likewise releases the retained candidate and
rollback images before recapturing those pathnames sequentially, so pathname
reproof does not reintroduce the third-image peak.

This final artifact proof is deliberately pathname-based and fail-closed, but
it is not an atomic reservation of three independent filesystem names. The
deployment singleton serializes cooperating AnonSync owners. A noncooperating
same-UID or privileged writer can still replace a name immediately after an
observation; rev0984 reports that limitation rather than claiming hostile-local-
writer atomicity.

## Executable crash-cutpoint proof

The real process oracle exercises the shipping executable across independent
processes. In addition to the ordinary action, it:

- recomputes the action and record digests with the explicit-NUL domains;
- proves private, single-link, bounded receipt publication and path binding;
- rejects damaged, nonprivate, and hard-linked receipts without database
  effects;
- proves completed-action replay is mutation-free;
- logically reconstructs the exact candidate-installed/epoch-pending cutpoint
  and proves only the epoch transition runs;
- reconstructs the exact receipt-only/displaced cutpoint, removes the rollback,
  and proves exact rollback recreation followed by ordinary completion;
- proves a missing rollback cannot be recreated after completion;
- constructs an active state outside all three admitted cutpoints and proves
  fail-closed unknown continuity; and
- returns to an admitted cutpoint and proves recovery still succeeds.

## Authority and nonclaims

Rev0984 replaces only the primary replica database. It does not restore payload
bytes, folder-catalog state, effect receipts, membership, anchors, credentials,
configuration, synchronized files, or network state. The rollback remains a
logical standalone SQLite artifact, not raw main/WAL/SHM inode identity.

The receipt is not a signature, trusted clock, external monotonic counter, or
anti-rollback anchor. Whole-deployment rollback can restore the database and
receipt together. Unknown continuity therefore still resets retained-mark age.
This is one bounded offline restart protocol, not a complete share-backup or
retention-collection design. It does not exclude a noncooperating same-UID
process from replacing candidate, rollback, or receipt names; the singleton
serializes only cooperating AnonSync owners.

## Release boundary

Exact rev0984 active source passed a fresh GCC 14.2 Debug graph (536/536 configured build edges), all 262/262 registered tests in an indexed final-source replay (261/261 immutable-preseal tests plus the final documentation-sensitive structural audit), and an independent 41/41 product replay. Focused GCC proofs passed 334 SQLite-owner checks, 38 deployment-binding checks, 102 snapshot-seal checks, 53 SQLite live-backup/replacement checks, 470 folder-owner checks, and the shipping database backup, recovery, replacement, and restart oracle passed 598 checks. Source audits passed 24/24 bounded-reader checks, 41/41 database-replacement checks, and 404/404 structural authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed with leak detection and halt-on-error, including the direct 470-check folder-owner proof at 1,481,008 KiB peak RSS, and focused sanitized proofs passed the same 334, 38, 102, and 53 checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0983 parent SHA-256 matched 64ef96593d809861275fe7b9ec5fbf67554a25c23b6e543de70cfe9fd59519b6 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 12/12 changed active files and the complete 583-file projection byte-for-byte and by mode. The final active implementation projection contains 583 files / 27,098,385 bytes with SHA-256 48c4b04bb58f482b3dc8dc853ba951d78941ccbea552ddbb3e442a0b2ede2419. Validation excluded overlapping Ninja invocations, vanished build trees, divergent source authorities, interrupted nonterminal runs, and every result not bound to the frozen exact C++ source or the final prose-and-audit seal. The final wrapper directory and ZIP remain publication-gated on the exact manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

Archive: `AnonSync-rev0984-2026.08.03.12.22-receiptresume-pathreproof-successorfence-grandidierite.zip`
