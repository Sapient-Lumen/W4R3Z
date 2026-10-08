# Rev0819 audit

## Boundary selected

Rev0819 re-audits atomic JSON publication because rev0818 had correctly bound
creation, write, rename, and durability to descriptors, but failure cleanup
quietly stepped back to pathname authority. The governing invariant is:

> Observing that a name denotes inode X does not authorize a later deletion of
> that name unless the delete operation itself is conditionally bound to X.

POSIX `unlinkat` has no expected-device/inode precondition. A separate
`fstatat` check and `unlinkat` therefore form a check/use race.

## Severe defect reproduced and corrected

The sealed-parent harness interposes rev0818's `unlinkat`. Between the identity
check and the real delete, it renames the writer-created inode away and installs
a foreign file at the checked name. Rev0818 deletes the replacement. Rev0819
performs no pathname deletion.

Failure cleanup now uses only the exact retained object capability:

- POSIX: best-effort `fchmod(fd, 0600)`, `ftruncate(fd, 0)`, and `fsync(fd)`;
- Windows: best-effort truncate and flush through the retained handle while it
  is still open; and
- all platforms: a typed `TemporaryArtifactMayRemain` residue fact rather than
  inferred or guessed cleanup authority.

The allocation-free progress owner records possible residue immediately after
exclusive temp creation. Namespace publication consumes that state permanently.
The residue classification is orthogonal to the existing publication outcome,
so callers can separately decide retry/recovery policy and operator cleanup.

## Proof surface

- pure state/API model: 24/24;
- race/path runtime corpus: 28/28;
- exception/process-exit cutpoint corpus: 144/144;
- unlink-authority regression: 12/12;
- focused stress: 100/100 executions (25 × four tests);
- structural audit: 32/32;
- complete project CTest accounting: 97/97 in four disjoint exhaustive ranges;
- all-target Debug build plus final `ninja: no work to do`;
- GCC 14 and Clang 17 warning-as-error lanes; and
- focused Clang 17 ASan/UBSan lane with leak detection disabled.

## Broader audit

A repository-wide lexical inventory found 480 pathname-deletion candidates in
`src/`, including 92 crudely classified as runtime. These counts are triage,
not verdicts. The most valuable next reviews are SQLite snapshot staging and
replay-ledger journal/temp deletion because those paths combine durable state,
crash recovery, sidecars, and names that can outlive their original owner.

## Explicit limits

Rev0819 deliberately prefers possible private residue over deletion of an
unrelated object. It does not implement a reaper. Descriptor sanitation is best
effort, not a proof against a failing filesystem or closed Windows handle. The
cutpoint corpus does not emulate arbitrary power loss, torn writes, controller
reordering, kernel/filesystem defects, or every syscall failure. Windows was
not executed in this Linux cloudtainer. No distributed convergence,
confidentiality, anonymity, or key-lifecycle property is claimed here.
