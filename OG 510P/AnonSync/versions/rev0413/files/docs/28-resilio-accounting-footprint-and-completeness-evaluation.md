# Resilio accounting, footprint, and completeness evaluation

## Why this pass matters

Current official Resilio Sync docs are again useful for AnonSync precisely because they are candid about several byte-accounting truths that many products blur.
They still say all of the following:

- IgnoreList entries are not indexed and are not counted in the `Size` column in the main view
- IgnoreList lives in hidden `.sync`, is case-sensitive, and if edited after the folder was already added, the structure has already been stored in the database and passed to peers until disconnect
- every synced folder gets a hidden `.sync` directory that is critical for syncing and also contains `Archive`, `IgnoreList`, `StreamsList`, and in-flight `.!sync` files
- placeholder `.rsls` files are 0-byte stand-ins that save space, can later materialize bytes on demand, and can leave a mesh with placeholders only if every full copy is removed
- change detection can rely on filesystem notifications, scheduled rescans, or manual rescans; the scheduled rescan is 600 seconds by default, and if the interval is set to zero Sync will not rescan even on restart
- the power-user table still exposes `free_space_warning_threashold`, `folder_rescan_interval`, `max_file_size_for_versioning`, `parallel_indexing`, `enable_file_system_notifications`, `lazy_indexing`, and other knobs that directly affect what is resident, counted, or confidently known
- desktop list views can show additional columns such as `size` and `date synced`, but the meaning of those columns still depends on the surrounding support prose rather than an integrated accounting page

That is a strong product to learn from.
It is also a concrete reason not to clone the page contracts.

## What Resilio gets right

### 1) It admits that counted size is not the same thing as bytes on disk

Current docs still say ignored files are not counted in the main `Size` column and placeholders are 0-byte stand-ins.
That is important honesty.
A product that hides those facts would be worse.

### 2) It admits that hidden service material is real

Current docs still say `.sync` is critical, houses share ID and service files, contains Archive / IgnoreList / StreamsList, and temporarily contains `.!sync` during transfer.
That again is useful candor.

### 3) It admits that visibility can be provisional

Current docs still say watcher quality varies by storage, rescans are periodic by default, zero disables rescans entirely, and indexing/hashing settings affect what Sync can know cheaply versus only after more work.
That is the right kind of honesty.

### 4) It admits that sparse visibility is not full custody

Current placeholder docs still say `.rsls` files are 0-byte representations, not actual file content, and warn that all peers can end up with placeholders only if every full copy is removed.
That is exactly the kind of semantic distinction the UI should surface.

## Why we still should not clone it

The core problem is not lack of truth.
The core problem is **where the truth lives**.

Resilio still makes the operator reconstruct one ordinary answer from several separate article families:

- *how much of this subject is really resident on this seat?*
- *which bytes are counted in the visible size metric, and which are excluded or merely hidden?*
- *is this list complete, or is it provisional because watchers, rescans, or hashing have not caught up yet?*
- *what service, history, temp, or metadata residue still remains even after I think I have cleared the subject?*

Those should not be FAQ-navigation questions.
They should be ordinary product pages.

## The AnonSync borrow line

Borrow from current Resilio:

- explicit candor that excluded bytes are not counted
- explicit candor that placeholders are sparse stand-ins rather than real content
- explicit candor that hidden managed folders/files are real parts of the product's behavior
- explicit candor that watcher health, rescans, and hashing make some views provisional

Adapt into AnonSync:

- one first-class page for **subject footprint**
- one first-class page for **size-metric truth**
- one first-class page for **completeness confidence**
- one first-class page for **service residue / clearance review**

## The replacement principle

AnonSync should never force the operator to infer byte truth from a single column.
Every surface that shows `size`, `present`, `available`, `cleared`, or `empty` should be able to answer four questions directly:

1. what bytes are counted here?
2. what bytes exist here but are not counted here?
3. what bytes are only names/placeholders and not present content?
4. how confident is the product that this answer is current?

That is the tighter reason not to clone current Resilio page contracts in this part of the product.
