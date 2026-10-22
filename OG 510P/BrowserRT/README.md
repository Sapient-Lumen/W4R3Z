# BrowserRT

## Keep local browser work coherent when something goes wrong

A browser application that processes a large local archive needs more than a way to start a worker. It must decide how much work to admit, who owns the bytes being passed around, what happens when storage falls behind, and whether a cancelled operation changed anything before it stopped. BrowserRT builds runtime components around those questions. Its purpose is to make substantial browser-local work easier to coordinate and its failures easier to interpret, rather than treat the page as a thin screen in front of a server.

A browser IDE, local data workbench or media application could use that kind of foundation. Those are intended uses, not demonstrated deployments. The supplied work progresses from a broad “browser userspace kernel” ambition toward a smaller kernel kit and then a sharper storage question: **before a write, was it admitted; during the write, who coordinated it; after failure, what remains and what can safely happen next?** The [product contract](versions/rev0202/contents/docs/20-architecture/product-contract-matrix-rev0151.md) states that narrowing explicitly.

## The work is not just a worker pool

The [early overview](versions/rev0005/contents/README.md) distinguishes a resource runtime from a worker-pool wrapper. Worker count alone cannot describe storage pressure, memory ownership, a queued interactive action or the cost of moving a large payload. The design therefore separates small control messages from the data they refer to. An envelope carries an operation, priority, deadline, lane and payload reference; the referenced bytes can be transferred or kept in a content-addressed store.

The [ownership contract](versions/rev0202/contents/docs/10-contract/memory-ownership.md) distinguishes owned, transferred, shared, borrowed, persistent and GPU-resident data. This is a design vocabulary, not a claim that every listed ownership mode has an equally complete enforcement mechanism. In the implemented transfer helper, a reference describes an `ArrayBuffer` and a transfer list identifies the buffer to move. Creating that description does not itself transfer the bytes; the worker message performs the transfer. The intended discipline is to know which context can still use the data rather than accidentally copy a giant JavaScript object graph between contexts.

The [compact runtime implementation](versions/rev0202/contents/src/runtime-core-public.mjs) makes boundedness concrete. A channel has a fixed queue capacity and an explicit overflow policy: fail, discard the oldest queued item, or reject the newest. Lossy policies count the loss rather than quietly pretending every send was retained. These are different application choices: replacing a stale preview can be reasonable, while silently dropping a requested save would not be. The bound is on queued items, not a universal bound on payload bytes or every outstanding waiter.

Trace collection is bounded too. Its ring-like history drops the oldest event when capacity is reached and retains a dropped-event count. That makes an incomplete trace distinguishable from an apparently complete history, though the events remain local observations rather than authenticated proof of what a browser did.

## Two entrances, with different responsibilities

The [package export map](versions/rev0202/contents/package.json) exposes both the main entry and `browserrt/runtime-core`. They should not be treated as interchangeable.

The [main public entry](versions/rev0202/contents/src/public-api.mjs) loads the fuller runtime when `boot()` is called. That runtime includes worker-agent creation and OPFS/coordination factories alongside its larger diagnostic machinery. The smaller runtime-core entry provides reference and envelope helpers, bounded channels, a memory-backed block store, admission and scheduling components, storage-lane adaptation, and storage diagnostics. Its capability report detects available browser surfaces; a flag such as “accelerated” does not establish an implemented or benchmarked GPU application. The smaller entry also does not turn its memory store into persistent browser storage.

Read the [runtime-core consumer](versions/rev0202/contents/examples/runtime-core-consumer.mjs) as a worked composition. It fills a capacity-one channel and attempts an overflow, admits a small payload while rejecting a much larger request, then schedules a block write, verification and read through a storage lane. Another case supplies an already-aborted signal and checks that the memory store has not mutated. These examples give the abstractions something specific to do. Their carried outcomes are not a new performance result or proof of behavior in every browser.

The separation is also a response to the project's own growth. A developer needing admission, a small queue and memory-backed experimentation need not pull every demonstration and recovery apparatus into the entry they inspect. Linked rev0202's six-file runtime-core dependency closure is the scope of its size reduction; `product-wedge.mjs` still exists elsewhere in the supplied source and package list.

## Admission is a policy decision, not a storage reservation

The fuller runtime's [storage factories](versions/rev0202/contents/src/browserrt.mjs) can compose an OPFS provider, browser-storage diagnostics and a Web Locks guard. OPFS is the browser's origin-private file system: this is application-local storage, not a user's arbitrary directory tree. The browser's [file-system standard](https://fs.spec.whatwg.org/) supplies the underlying handles and operations; BrowserRT adds decisions and records around their use.

A postured store means a store created through these additional checks. It can refuse a write path when estimated free space, requested headroom or coordination policy does not satisfy the caller's requirements. Per-write checks matter because conditions can change after construction. The postured path also resists silently weakening those selected guards through a per-operation override; the lower-level raw provider remains a different choice with different responsibilities.

This distinction is useful for an application preparing a large import. It can explain “this work was not admitted” before treating a later storage exception as a partly completed save. But an estimate is not reserved space, and an accepted request is not a guarantee against quota failure or eviction. The point is to make the application's policy and the observed boundary explicit, not to give a browser-local library control over the browser's storage lifecycle.

## A failed write can leave useful bytes behind

The [OPFS block store](versions/rev0202/contents/src/opfs-block-store.mjs) names blocks by the SHA-256 of their contents. For a non-duplicate put, including a corrupt-block repair, it writes a uniquely named temporary file, checks the bytes against the intended hash, then publishes to the canonical `.blk` path. Publication copies verified bytes; it is not an atomic database transaction or a universal atomic rename guarantee.

That design gives rollback a subtle responsibility. Suppose a final file already contains the correct bytes, but a late abort or a trace observer's exception causes the call to reject. Deleting the file merely because the call failed would discard a valid content-addressed block. The [rev0100 change](versions/rev0100/contents/docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md) therefore makes eligible failed-write cleanup inspect the final block first. A matching block is preserved; invalid or partial owned output remains a cleanup candidate.

Three things are now separate: the caller received success, the addressed bytes exist and verify, and the application committed its higher-level operation. A failed `put()` can leave the second true without making the first or third true. An application can inspect that state and make an idempotent decision instead of assuming either “nothing happened” or “the save succeeded.” This is a useful failure model precisely because it does not promise transaction semantics the block store cannot supply.

## Recovery must cooperate with live writers

Temporary files introduce another problem: one provider instance's abandoned-looking file may be another instance's active write. The [rev0125 account](versions/rev0125/contents/README.md) deliberately begins with the unsafe case. A second raw provider can remove a live staged temporary file and cause its writer to fail before publication.

Here “raw” means unguarded, not unstaged.

The repair is in the [guarded provider](versions/rev0202/contents/src/opfs-web-lock-guarded-block-store.mjs): `recoverStagedWrites()` acquires the same exclusive Web Lock used by guarded writes. Cooperating instances using the same coordination identity serialize cleanup behind an active put. This does not make an uncooperative raw writer safe, and a lock name must actually identify the shared resource. The cleanup operation is part of the write protocol, not an unrelated maintenance job.

Cancellation has a similarly important boundary. The [W3C Web Locks draft](https://www.w3.org/TR/2025/WD-web-locks-20250924/#dom-lockoptions-signal) distinguishes aborting a pending request from work after a lock has been granted: the request signal is ignored after grant. BrowserRT therefore carries cooperative cancellation into the provider separately. A pending-lock abort and a provider abort after mutation require different interpretations. “Cancelled” is not a sufficient description of the storage state.

The runtime's [recovery guidance](versions/rev0202/contents/src/browser-storage-recovery-guidance.mjs) classifies these cases and supplies next-step advice. Pre-mutation policy rejection, lock contention, provider quota failure and an interrupted write do not all warrant the same retry. Some cases require settlement and digest or prefix checks before proceeding. The guidance is data returned to a caller, not an automatic recovery agent, a durability guarantee or a proof that a user followed the advice.

## Read the tests for the distinction they protect

The testing work is substantive when it exposes a false inference. The [rev0054 contrast slice](versions/rev0054/contents/docs/40-validation/kernel-kit-readiness-contrast-slice.md) removes reload/readback, handoff-import and exact-command evidence on purpose. The degraded object must fail readiness, while the report of that expected failure can itself be valid. A valid report about a failed case is not a ready application.

The rollback and staged-recovery probes likewise distinguish a rejected call from missing bytes, and a candidate for cleanup from a live writer's temporary file. Their source-level and simulated-browser checks are useful at those boundaries. They do not establish survival of browser termination, power loss, eviction or every browser's implementation. Focused browser observations and the broader browser-light release path remain separate evidence categories.

Finally, keep the two revision labels. The [linked rev0202 receipt](versions/rev0202/contents/REV0202-LINKED-REVISION-RECEIPT.json) belongs to a July recovery-guidance refactor while the packaged runtime identifies as rev0125 / 0.0.125. The refactor replaces repeated classification branches with compact tables and reduces the recorded runtime-core closure from 129,576 to 128,028 bytes. That is a supplied source-size observation, not a speedup or a newly published package.

BrowserRT is worth reading as a collection of working runtime components and increasingly precise failure distinctions. Its most productive ambition is not that a page can become an operating system by declaration. It is that a local application can stop guessing which work was admitted, which bytes survived, which actors were coordinated and which recovery action the available evidence supports. Read beside [Lacuna](../Lacuna/README.md), where accepted narrative state is distinct from plausible possibilities, and [TimeSync](../TimeSync/README.md), where a compact result must retain the conditions limiting its use. Those are comparisons of reasoning, not shared runtime mechanisms.

*Reading introduction by Lumen, 21 October 2026 (UTC−04:00).*

## Version shelf and preservation

### The five snapshots

| Archive label | Filename date | Reading guide | Focus |
| --- | --- | --- | --- |
| rev0005 | 2026-05-24 | [Test Observatory Scaffold](versions/rev0005/README.md) | Test selection, surface inventory, timing history, and a carried Node worker proof |
| rev0054 | 2026-06-01 | [Readiness Contrast Workbench](versions/rev0054/README.md) | Make intentionally weaker handoff evidence fail visibly |
| rev0100 | 2026-06-10 | [Preserve valid blocks during rollback](versions/rev0100/README.md) | Check final content-addressed bytes before failed-put cleanup |
| rev0125 | 2026-06-18 | [Guarded staged recovery](versions/rev0125/README.md) | Serialize staged cleanup with writes using the same exclusive Web Lock |
| rev0202 | 2026-07-08 | [Recovery-guidance table refactor](versions/rev0202/README.md) | Linked rev0202, still packaged runtime rev0125 / 0.0.125 |

### What is worth reading

- **Start with the testing discipline.** [rev0005](versions/rev0005/contents/README.md) explicitly describes an early scaffold. Its manifest-addressable checks, impact map, and timing records precede the planned browser, storage, and GPU features. Capability names in the source are not proof that all those capabilities were implemented.
- **Read the negative case alongside the happy path.** [rev0054's contrast slice](versions/rev0054/contents/docs/40-validation/kernel-kit-readiness-contrast-slice.md) deliberately removes reload/readback, handoff-import, and exact-command evidence. The purpose is to expose missing evidence rather than infer readiness from a reassuring report.
- **Follow the storage boundary carefully.** [rev0100's rollback slice](versions/rev0100/contents/docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md) treats a valid block left after a failed call as a possible idempotent side effect, not an acknowledged application commit. [rev0125](versions/rev0125/contents/README.md) then distinguishes raw, uncoordinated staged cleanup from recovery through a shared guard.
- **Keep the latest archive's two identities visible.** The [rev0202 README](versions/rev0202/contents/README.md) and [linked revision receipt](versions/rev0202/contents/REV0202-LINKED-REVISION-RECEIPT.json) retain packaged runtime rev0125 / 0.0.125. Linked rev0202 refactors recovery guidance and tightens a runtime-core source-size budget; it does not promote the runtime or document a published npm release.

### Preservation and evidence

The [manifest](MANIFEST.json) records the five original archives and 4,448 extracted files, including archive/member SHA-256 hashes, sizes, and recorded modes. `versions/revXXXX/contents/` retains the member paths of that original ZIP. The surrounding README files are new editorial guides; the historical files remain separate.

Archive/member byte comparisons and static document/source inspection are curation checks. They are not a fresh execution of BrowserRT. Carried probe reports, timings, `passed` statuses, and historical browser observations remain claims and evidence supplied with the snapshots. No uploaded test suite, historical command, or project code was executed for this showcase review. Some later reports are explicitly compacted summaries, so a retained status does not imply that detailed observations remain in that file.

Browser-light release checks and focused managed-Chromium records should not be conflated with cross-browser coverage. The snapshots expressly withhold broad claims about production readiness, OPFS durability, fsync or power-loss recovery, quota/eviction survival, Web Locks fairness, and artifact authenticity. Read each snapshot's own non-claims for the precise boundary.

### Reading and reuse

Start with each editorial guide, then its original README, revision receipt, and referenced source/probe files. Commands, work orders, and agent instructions inside the archives are historical project material, not present-day instructions to run them.

No LICENSE, COPYING, or NOTICE file, package license declaration, or affirmative license grant was identified in this review. This showcase preserves the supplied material as received; the [current owner declaration](../../LEGAL-NOTICE.txt) records the contributor’s later declaration without replacing third-party rights. A finite privacy/credential-pattern review found no flagged matches, but that is not a complete privacy, provenance, licensing, or security clearance.
