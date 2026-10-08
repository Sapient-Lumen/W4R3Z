# Revision notes — rev1004

## Bounded terminal target verification

Rev1004 turns the receiver's one unbounded staged-target SHA-256 pass into a
restart-safe **32 MiB per owner-call** continuation. The staged prefix must
already be complete and durable. A fixed-width, checksum-framed two-slot journal
then binds provider-independent SHA-256 computation progress to:

- the exact payload-store identity digest and private identity inode;
- the target content SHA-256 and exact total size;
- the exact complete staged-prefix inode observation;
- a nonzero monotonic generation;
- the verified byte offset; and
- a canonical `ResumableSha256Checkpoint`.

The journal is computation progress, never publication authority. A nonterminal
slot always has `verified_offset_bytes < total_size_bytes`; the terminal digest
is produced only in the current process after reading the final bytes from the
exact staged descriptor. Publication still requires the independently trusted
whole-content digest, exact pathname and inode reproof, an exclusive store
lease, a complete final namespace scan, and no-replace rename of that exact inode
under its digest name.

## Crash, damage, and legacy behavior

The newest journal slot is overwritten only after the older valid slot exists.
A torn newest write therefore falls back to the prior checksum-valid generation
and loses at most one 32 MiB verification step. Conflicting equal generations,
foreign store identity, target mismatch, extent mismatch, or staged-inode drift
make the journal unusable.

A missing rev1003 journal, a malformed journal, or a journal bound to stale
metadata does **not** trigger a complete compatibility reread and does not
truncate received bytes. Verification restarts from SHA-256 offset zero and the
current call still reads no more than 32 MiB. Only a physical tail beyond the
basename-committed prefix may be truncated. A final digest mismatch removes the
invalid complete staged owner and its computation journal without publishing a
false payload.

## Generation-8 wire handoff

Generation 8 makes the receiver-local terminal phase explicit. When the final
payload range reaches the exact total size, the source does not advance the
operation cursor. It returns the same operation with a continuation whose
`next_offset_bytes == total_size_bytes`. Later terminal turns repeat that exact
operation but carry no payload ranges and do not reopen source payload
authority. The receiver advances only its local bounded SHA-256 continuation;
the operation is admitted and the cursor advances only after final local
publication.

The ordinary range API rejects the zero-byte terminal sentinel. A separate
`continue_staged_payload_prefix_verification_or_throw()` entry point makes the
no-network-byte phase mechanically distinct and reports zero accepted range
bytes.

## Adjacent audit and refactor

The end-to-end audit found a serious first-cut protocol defect: generation 7
could advance the source operation cursor when the final bytes arrived even
though the receiver still had unfinished local verification. A crash or next
turn could then lose the obligation. Generation 8 preserves that obligation on
the wire until publication.

The audit also removed dead helpers from an abandoned per-range checkpoint
model, removed an unused test-only filesystem helper that produced a clean-build
warning, and discarded a timestamp-stale object tree that had hidden the real
48 MiB terminal-turn regression. A fresh Clang product build then found the new
codec test in the sanitizer compile inventory but not the final-link inventory.
The target now receives both flags, and the focused source audit parses the
link inventory explicitly.

## Product boundary

Rev1004 bounds terminal byte work and memory, but it does not yet make the
multi-terabyte path efficient enough. Each incomplete 32 MiB terminal step
currently requires another payload-cold peer turn and another exact staged-prefix
namespace observation. On a multi-terabyte file, that can amplify high-latency
round trips and repeated directory traversal even though source payload bytes
are never retransmitted. Source-side target-manifest construction can also still
read a complete source in one owner call.

Rev1004 does not add a durable/global chunk index, target-scale soak evidence,
identity-preserving rename/move, complete directory semantics, Android support,
selective placeholders or automatic eviction, ENOSPC qualification, or live
public Tor/I2P performance proof.

## Release cutpoint

Validation: `Exact rev1004 source passed a fresh GCC 14.2 Debug complete graph with 555/555 configured build edges, followed by exact-source CMake regeneration and bundled-SQLite no-work re-attestation; all 288/288 registered tests and an independent isolated 48/48 product replay passed. Focused GCC proofs passed 20 terminal-state-codec, 696 payload-store, 4,999 reconciliation-protocol, 194 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 38/38 bounded terminal-verification-continuation checks and 567/567 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph compiled its 266-edge configured dependency set across bounded resumptions; the first final link exposed that the new codec test was present in the sanitizer compile inventory but absent from the final-link inventory, the target graph was corrected, 28 exact-source relink edges and a no-work re-attestation passed, and all 48/48 registered product commands passed serially with leak detection and halt-on-error. Focused sanitizer proofs passed the same 20 terminal-state-codec, 696 payload-store, 4,999 protocol, 194 reconciliation-service, and 536 folder-owner checks; payload-store, reconciliation-service, and folder-owner peak RSS was 648,772 KiB, 780,832 KiB, and 1,694,640 KiB. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1003 parent SHA-256 matched 58be646d3714895037e2dd1f928aa81e2fd200614eb9dfa75a5fdde16a424b53 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 36/36 changed wrapper files, all 35/35 changed project files, all 32/32 changed active files, and the complete 618-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 618 files / 28,499,104 bytes with SHA-256 7b4499a95932e5d3ec3452c9982c3dc8f3f2a3e15b79962f90b953144ac709e9. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes both remount-vanished unsealed worktrees and their builds, obsolete pre-generation-8 evidence, the first aggregate sanitizer run invalidated by concurrent memory-heavy tests, the CTest wrapper invocation that stalled despite a passing direct proof, and the pre-correction sanitizer final-link failure.`

Archive: `AnonSync-rev1004-2026.08.05.16.01-terminalcontinuation-zerobytepulse-inodejournal-cordierite.zip`

Codename: `cordierite`
