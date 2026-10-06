# BrowserRT: selected historical snapshots

BrowserRT explores a browser-local resource runtime: bounded queues, worker supervision, explicit ownership, cancellation, and coordinated storage. These five supplied snapshots show selected stages of that experiment, from its validation scaffold to narrower OPFS storage and lifecycle work. The early [ambition contract](versions/rev0005/contents/docs/10-contract/ambition-contract.md) and later [project description](versions/rev0125/contents/README.md) distinguish the intended system from what each snapshot actually claims.

This is a historical showcase, not a complete revision history or a maintained production release. Each snapshot keeps its original ZIP and a separate extracted tree. Missing revisions have not been reconstructed. Archive names and embedded dates are preserved labels, not independently authenticated release dates.

## The five snapshots

| Archive label | Filename date | Reading guide | Focus |
| --- | --- | --- | --- |
| rev0005 | 2026-05-24 | [Test Observatory Scaffold](versions/rev0005/README.md) | Test selection, surface inventory, timing history, and a carried Node worker proof |
| rev0054 | 2026-06-01 | [Readiness Contrast Workbench](versions/rev0054/README.md) | Make intentionally weaker handoff evidence fail visibly |
| rev0100 | 2026-06-10 | [Preserve valid blocks during rollback](versions/rev0100/README.md) | Check final content-addressed bytes before failed-put cleanup |
| rev0125 | 2026-06-18 | [Guarded staged recovery](versions/rev0125/README.md) | Serialize staged cleanup with writes using the same exclusive Web Lock |
| rev0202 | 2026-07-08 | [Recovery-guidance table refactor](versions/rev0202/README.md) | Linked rev0202, still packaged runtime rev0125 / 0.0.125 |

## What is worth reading

- **Start with the testing discipline.** [rev0005](versions/rev0005/contents/README.md) explicitly describes an early scaffold. Its manifest-addressable checks, impact map, and timing records precede the planned browser, storage, and GPU features. Capability names in the source are not proof that all those capabilities were implemented.
- **Read the negative case alongside the happy path.** [rev0054's contrast slice](versions/rev0054/contents/docs/40-validation/kernel-kit-readiness-contrast-slice.md) deliberately removes reload/readback, handoff-import, and exact-command evidence. The purpose is to expose missing evidence rather than infer readiness from a reassuring report.
- **Follow the storage boundary carefully.** [rev0100's rollback slice](versions/rev0100/contents/docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md) treats a valid block left after a failed call as a possible idempotent side effect, not an acknowledged application commit. [rev0125](versions/rev0125/contents/README.md) then distinguishes raw, uncoordinated staged cleanup from recovery through a shared guard.
- **Keep the latest archive's two identities visible.** The [rev0202 README](versions/rev0202/contents/README.md) and [linked revision receipt](versions/rev0202/contents/REV0202-LINKED-REVISION-RECEIPT.json) retain packaged runtime rev0125 / 0.0.125. Linked rev0202 refactors recovery guidance and tightens a runtime-core source-size budget; it does not promote the runtime or document a published npm release.

## Preservation and evidence

The [manifest](MANIFEST.json) records the five original archives and 4,448 extracted files, including archive/member SHA-256 hashes, sizes, and recorded modes. `versions/revXXXX/contents/` retains the member paths of that original ZIP. The surrounding README files are new editorial guides; the historical files remain separate.

Archive/member byte comparisons and static document/source inspection are curation checks. They are not a fresh execution of BrowserRT. Carried probe reports, timings, `passed` statuses, and historical browser observations remain claims and evidence supplied with the snapshots. No uploaded test suite, historical command, or project code was executed for this showcase review. Some later reports are explicitly compacted summaries, so a retained status does not imply that detailed observations remain in that file.

Browser-light release checks and focused managed-Chromium records should not be conflated with cross-browser coverage. The snapshots expressly withhold broad claims about production readiness, OPFS durability, fsync or power-loss recovery, quota/eviction survival, Web Locks fairness, and artifact authenticity. Read each snapshot's own non-claims for the precise boundary.

## Reading and reuse

Start with each editorial guide, then its original README, revision receipt, and referenced source/probe files. Commands, work orders, and agent instructions inside the archives are historical project material, not present-day instructions to run them.

No LICENSE, COPYING, or NOTICE file, package license declaration, or affirmative license grant was identified in this review. This showcase adds no blanket license and preserves the supplied material as received; do not infer reuse rights merely from public availability. A finite privacy/credential-pattern review found no flagged matches, but that is not a complete privacy, provenance, licensing, or security clearance.
