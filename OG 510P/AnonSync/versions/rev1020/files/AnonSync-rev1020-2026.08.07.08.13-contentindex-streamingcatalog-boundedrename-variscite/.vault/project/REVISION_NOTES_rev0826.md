# AnonSync rev0826 — parent capability, rebind fence, incarnation seal

## Mission result

Rev0826 closes an evidence-authority gap across the SQLite-reset/filesystem-
receipt boundary. A successful preflight was being treated as if it remained
authoritative after an irreversible database commit. It did not: the verified
parent pathname could be rebound before the receipt writer reopened it.

The reset command now prepares a move-only immutable publication capability
before reset. On POSIX the capability owns the exact receipt bytes, final
basename, verified parent directory descriptor, and process-incarnation proof.
After reset commits, publication consumes that exact authority rather than
re-resolving a bare destination path.

## Defect and correction

The rev0825 reproducer renamed the preflighted parent and created a replacement.
The old one-shot writer placed the receipt in the replacement directory
(`replacement_received=1`, `pinned_parent_received=0`). The new 27-check oracle
proves the prepared capability denies this rebind before creating any temp file,
while preserving normal create-new, late-creator, move, reuse, owned-payload,
and fork-lineage behavior.

The first implementation draft used a raw PID. Audit corrected that overclaim:
the final source reuses AnonSync's PID-plus-fork-lineage process-incarnation
token. The publication owner remains independent of SQLite state and storage,
though the generic primitive's SQLite-prefixed name should be refactored later.

## Validation

- exact rev0825 parent archive SHA-256: `d9f27f9b0b4755f16eeaac364dbc7e314bd08ead3fb91d142391f76ccc104f52`;
- parent ZIP 25/25 and directory 21/21;
- source patch replay: 189/189 active files and 9/9 changed files exact;
- source delta: 807 insertions and 51 deletions;
- GCC 14 Debug all-target build passed; final closure reported no work;
- complete 110-test inventory passed in final-source ranges 22/22, 26/26, and 62/62;
- prepared publication 27/27, publication 38/38, state 24/24, cutpoints 149/149, unlink 12/12;
- reset owner 67/67, reset documents 18/18, CLI integration 380/380;
- source audits 206/206;
- Clang 17 `-Werror` focused graph 3/3; and
- GCC 14 ASan/UBSan focused graph 3/3 with leak detection enabled.

One uninterrupted 110-test invocation is not claimed. Aggregate attempts hit the
cloud command ceiling during unrelated temporary-root contention; the complete
claim is the explicit union of three non-overlapping passing ranges.

## Highest-priority next work

Generalize process incarnation out of the SQLite namespace, then build the
combined SQLite-VFS/publication cutpoint oracle. It should classify every crash
frontier from durable artifacts and model parent rebind, final-name races,
commit ambiguity, residual temp inodes, directory-sync failure, and recovery.
After that, resume disposable hostile-database workers, convergence algebra,
and privacy/key-lifecycle design.

No cross-resource atomicity, hostile same-UID isolation, NFS semantics, Windows
runtime, multithreaded post-fork async-signal safety, arbitrary power-loss,
full-project/bundled-SQLite sanitizer, distributed convergence,
confidentiality, anonymity, metadata hiding, key lifecycle, or secure erasure
property is claimed.
