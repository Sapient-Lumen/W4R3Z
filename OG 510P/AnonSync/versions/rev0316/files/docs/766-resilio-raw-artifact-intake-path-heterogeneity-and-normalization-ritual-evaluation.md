# Resilio raw-artifact intake, path heterogeneity, and normalization-ritual evaluation

## Why this seam matters

Another current official Resilio pass exposes a tighter non-clone reason than `pick the right artifact family` or `build a better manifest`.
Current official docs are also candid that **raw evidence does not arrive in one stable shape**:

- the current `Collecting debug logs manually` guide still says log files are named `sync.log` and `sync.log.<some number>.zip`, and that their storage path changes by desktop platform, service account, package mode, config mode, and NAS/Android side routes
- the current `How to collect logs on NAS manually?` guide still tells the operator to copy the whole Sync internal-data folder from the NAS and then manually clean it up, leaving only `*.log`, `*.log.zip`, and `*.journal`, before packing and sending it
- the current `Collect debug logs on mobiles` guide still routes collection through the `SNC.DBG.LOGS` action and then to the hidden `.synclogs` folder in device storage
- the current `Collecting crash reports, mini-dumps and core dumps` guide still spreads crash material across platform-specific filenames and locations, including `.dmp`, crash-report folders, and gzipped core dumps
- the current `Collecting core dump on NAS devices` guide still says the operator may need to move the produced dump into a shared/public folder just to download it through the NAS WebUI
- the current `Resilio Sync 3.0 change log` still shows the live v3 line through `3.1.2.1076`

That candor is useful.
Resilio is not pretending that every evidence member starts from the same path, naming scheme, or preparation state.

The non-clone problem is still **raw-artifact intake ownership**.
One ordinary operator answer is still reconstructed from platform guides, hidden folders, ad hoc cleanup, and remembered file-shape folklore:

> what raw materials were actually harvested, what class does each file belong to, which incident/witness/row it came from, what got pruned or renamed during cleanup, and what claim ceiling remains because the packet began as heterogeneous scavenged files rather than one product-owned intake object?

## What current official docs still get right

### 1) Raw evidence really is heterogeneous

Current docs still admit that:

- one incident can produce plain logs, rotated zip logs, journals, crash reports, mini-dumps, core dumps, or profiler-adjacent artifacts
- raw artifacts may begin in hidden, service-owned, package-owned, or public-download staging paths
- different platforms expose different names, extensions, and extraction rituals
- some capture flows yield a whole folder first and only later a narrowed evidence subset

That is better than pretending every support-worthy artifact is just `the log file`.

### 2) Preparation work changes the evidentiary story

Current docs still imply this by requiring the operator to:

- copy a whole NAS internal-data folder and then remove non-log material
- move a dump into a downloadable/public NAS folder
- harvest mobile logs from a hidden folder after a magic-string action
- compress or send gzipped core dumps on some platforms

That is strong evidence that **intake normalization** is a real product need, not support trivia.

### 3) Provenance can easily be lost during cleanup

Once the operator manually renames, prunes, zips, moves, or repacks files, the current docs still do not leave one durable object saying:

- what each raw file originally was
- what witness/platform/path produced it
- what cleanup or narrowing changed it
- what exact normalized member later satisfied the evidence plan row

## Where the current contract still fails

### 1) Raw intake is still not a first-class object

Current docs still do not leave one product-owned record saying:

- which raw artifacts were discovered
- which artifact family each belongs to
- whether the artifact is original, copied, extracted, compressed, renamed, or pruned
- which witness/participant/row produced it
- whether any provenance is already uncertain

So operators improvise with filenames and temporary folders.

### 2) Cleanup and normalization are still folklore

The current guides still force several manual acts without one review surface that says:

- what should be kept versus discarded
- whether keeping an entire folder would over-disclose unrelated internals
- whether pruning journals, dumps, or service-state files narrows the diagnostic question too far
- whether renaming or repacking a member preserved enough provenance for later review

### 3) Heterogeneous artifacts still blur before manifest review

The manifest-stage truth is useful, but a later manifest cannot fully explain:

- whether a member was born as a raw original or as a cleaned derivative
- whether a missing member was never captured or merely discarded during cleanup
- whether two files are duplicates, same-class rotations, or contradictory witnesses
- whether path relocation changed audience/privacy risk

### 4) Later receipts still risk overstating package clarity

Even when a packet is exported, the current operator still lacks one durable receipt that says:

- what raw sources existed before normalization
- what transformations happened
- what was intentionally excluded
- what provenance uncertainty still caps the claim

## What AnonSync should do instead

AnonSync should keep the candor and reject scavenger-hunt intake.
The product should own four ordinary page families for this seam:

1. **Raw evidence intake page**
   - discovered raw members
   - source path / witness / platform provenance
   - artifact-family typing
   - original vs copied vs extracted status

2. **Artifact normalization review page**
   - keep / prune / rename / extract / recompress review
   - provenance preservation
   - duplicate / rotation grouping
   - over-disclosure warnings

3. **Packet assembly review page**
   - normalized members
   - source-to-member lineage
   - duplicate and contradiction handling
   - sensitivity split before manifest/export

4. **Intake normalization receipt page**
   - raw-source inventory
   - normalized-member inventory
   - transformations performed
   - residual provenance ceiling and reopen boundary

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that raw evidence is platform-specific, path-specific, and sometimes messy. But it is not worth cloning the way the operator still has to scavenge, prune, move, rename, and repack those artifacts by hand without one durable intake object that preserves provenance from raw harvest to reviewed packet.

## New replacement pages added in this revision

- `767` Raw evidence intake page
- `768` Artifact normalization review page
- `769` Packet assembly review page
- `770` Intake normalization receipt page

