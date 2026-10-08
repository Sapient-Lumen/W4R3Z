# Resilio resource budget, throttling, and hidden contention fragmentation evaluation

## Why this pass exists

The archive already had strong language for reachability, eligibility, completion, activation, and hidden internal work.
What it still did not own with one explicit current Resilio memo was the narrower but highly practical operator seam:

> what is actually constraining throughput right now, which budget owns that slowdown, and who is being starved or preempted while the interface still looks generally alive?

Current official Resilio docs are still useful here precisely because they are candid about the pieces.
They still say all of the following:

- `Sync Preferences` still exposes global receiving/sending rate limits and a weekly scheduler, and still says those global rate limits apply to internet connections by default unless `rate_limit_local_peers` is enabled in power-user preferences.
- `Running Sync on schedule` still says scheduled `Paused` means upload and download rates go to zero while zero-sized files, deletions, rescans, and indexing still continue, and paused peers may still upload to non-paused peers.
- `Power user preferences` still exposes `disk_low_priority`, `disk_worker_per_job`, `worker_threads_count`, `rate_limit_local_peers`, `free_space_warning_threashold`, and `folder_rescan_interval`, plus other knobs that materially change which resources are scarce and how work competes for them.
- `File download priority` still says prioritization only applies to the active queue up to 50,000 files, that higher-priority files can suspend lower-priority downloads, that some internal exceptions remain, that queue rebuilds can affect performance, and that the UI queue may still appear alphabetical rather than in true priority order.
- `Out of memory` still says Sync keeps the whole file tree in memory, retains deleted entries in the database, and may only truly shrink RAM usage by removing a biggest folder from Sync and sharing it again.
- `Some internal tasks are taking time to complete` still says resource pressure may come from hidden disk and network work such as block checking, hashing, merging, reading, and writing.

That is valuable candor.
It is also a strong non-clone signal, because the ordinary operator answer about `what is slow, why, and who is paying for that slowdown?` still bottoms out in several different settings pages, troubleshooting notes, and queue caveats rather than one product-owned resource contract.

## What current Resilio still gets right

Current official docs still deserve credit for several things AnonSync should borrow more strongly:

- **They admit that throughput is multi-budget.**
  Bandwidth, disk, CPU, memory, and queue shape are not collapsed into one fuzzy `performance` story.
- **They admit that `paused` does not mean frozen.**
  Some publication and indexing lanes keep moving even when transfer rates are zero.
- **They admit that prioritization can preempt earlier work.**
  Higher-priority items can suspend lower-priority work rather than politely waiting their turn.
- **They admit that the visible queue is not the whole truth.**
  The UI can sort alphabetically while actual scheduling obeys other rules and internal exceptions.
- **They admit that hidden internal work can be the bottleneck.**
  Slowness is not always `the network`; hashing, merging, and reads/writes can dominate.
- **They admit that memory pressure is structural.**
  The whole tree and deleted state remain in memory/database, so scale debt is real rather than cosmetic.

## Where the contract still fractures

The trouble is not that Resilio lacks knobs.
The trouble is that the operator still has to assemble the budget truth manually.
A serious operator usually needs one owned answer to these questions:

1. which lane is rate-limited right now: upload, download, LAN, WAN, indexing, hashing, merge, disk write, memory pressure, or free-space stop?
2. which policy plane imposed that limit: global default, weekly schedule, share-local override, power-user setting, runtime pressure, or queue exception?
3. who is paying the price: one share, all shares, only LAN peers, only internet peers, only low-priority downloads, or the entire runtime?
4. what stronger sentence is false: `paused means no mutation`, `priority order is exactly what the list shows`, `full bandwidth available means nothing else is constraining progress`, or `slow right now means the network is the bottleneck`?

Current official docs still do not give that as one first-class page family.
Instead, the operator must reconstruct it from Sync Preferences, scheduler docs, file-priority docs, power-user settings, and troubleshooting pages.

## Hard AnonSync decisions locked in here

1. **Resource budget becomes a first-class contract object.**
   The system may not hide slowdown cause behind a single `performance` summary.
2. **Budget lanes stay separate.**
   WAN bandwidth, LAN bandwidth, disk service, CPU/indexing, memory pressure, and free-space floor must not be flattened into one bar.
3. **Budget provenance is mandatory.**
   Every meaningful limit must say whether it came from policy, schedule, share-local priority, runtime pressure, or internal exception.
4. **Starvation risk gets its own warning surface.**
   Preemption, full active queue, hidden rebuilds, and long-lived low-priority suspension are first-class hazards.
5. **Visible order never stands in for actual execution order.**
   A list may be human-sorted while the scheduler uses a different queue truth.
6. **Receipts must preserve the bottleneck claim ceiling.**
   The system must record when it proved only `download queue saturated under this budget` rather than the stronger sentence `the network was the only limiting factor`.

## Borrow, then refuse the fragmentation

AnonSync should borrow Resilio's practical honesty that resource contention is real and multi-plane.
AnonSync should refuse the weaker contract where the operator still has to memorize five help pages to answer one performance question.

The better product shape is:

- one explicit **Resource budget contract sheet** for all major lanes and owners
- one explicit **Resource budget review** for planned throttles, priorities, and schedule cells
- one explicit **Starvation and suspension warning** whenever priority or queue shape can strand work
- one explicit **Resource pressure proof** that names the current bottleneck and claim ceiling
- one durable **Resource budget receipt** proving exactly which budget plane, fairness rule, and stronger sentence were blocked