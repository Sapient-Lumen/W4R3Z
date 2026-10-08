# Resilio same-host multi-instance, port namespace, storage world, and claim-collision evaluation

## Why this pass exists

The archive already had stronger language for invocation profiles, service promotion, storage worlds, hidden service material, and directory admission.
What it still did not own tightly enough was one ordinary but dangerous operator seam:

> if I start another runtime on the same host, what exactly must be distinct, what can still collide, and when does a second bind stop being `another instance` and become corruption of the first instance's continuity-bearing state?

Current official Resilio docs still make that seam materially real.
They now say all of the following at once:

- on Linux, one can start multiple instances of Sync, but the second and subsequent instances require manually assigned ports for data transmission and reception
- the Linux runtime's storage, identity, and license can default into the current working directory unless `--storage` and related parameters are made explicit
- config mode can create a new settings world at a non-default `storage_path`, and a listening port value of `0` allocates a random port
- Linux package installs run the service under `rslsync` by default with minimal privileges, while a separate documented path runs under the current user instead
- update guidance for non-default `/config` or `/storage` launches says you must restart with the same command line parameters and the same user to preserve the same storage-root continuity
- `Service files missing` still says adding the same folder from Sync A and then Sync B on the same computer, or reusing one external disk as storage for two instances, can corrupt the first instance's internal files and make further synchronization impossible

That is good candor.
It is also a strong reason not to clone the present contract.
One ordinary operator answer — `am I safely starting a second namespace, or am I about to double-claim the same storage or subject path and damage continuity?` — still depends on combining:

- Linux multi-instance notes
- command-line storage/identity notes
- config-mode storage-path notes
- service-user packaging notes
- update-path continuity notes
- a later repair article about `.sync` corruption

AnonSync should keep the distinctions and refuse the archaeology.

## Hard product decisions locked by this pass

1. **A same-host multi-instance plan is a namespace contract, not a power-user convenience.**
2. **Port separation, storage-root separation, identity storage, and control-surface audience are separate truths and all must be reviewed.**
3. **Subject-path ownership on one host is exclusive until explicitly detached, migrated, or branch-reviewed.**
4. **Reusing removable or external storage across runtimes is a host-ownership handoff, not a casual restart shortcut.**
5. **Receipts must preserve the blocked stronger sentence whenever the product refuses `safe to run both`.**

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **Multi-instance is admitted, not denied by folklore.** The Linux guide still says multiple instances can run on one host.
- **Runtime namespace needs explicit port discipline.** The same guide still says later instances require manual port assignment.
- **Storage world is real.** The same Linux and config-mode docs still say storage path determines where settings, identity, and license live, and that a non-default `storage_path` creates new settings there.
- **Runtime principal is real.** The Linux package guide still distinguishes the default `rslsync` service user from a current-user service mode.
- **Continuity depends on same-user / same-parameter relaunch.** Current update guidance still says non-default `/config` or `/storage` launches must restart with the same parameters and the same user to preserve the same storage folder and configuration.
- **Same-path dual claim is openly called destructive.** `Service files missing` still says Sync A and Sync B can corrupt the former instance's internal files if they add the same folder on the same computer.

That is useful product honesty.
Resilio does not pretend that `another instance` is merely another window.

## Where current Resilio still stays too article-shaped

### 1. Instance namespace still reads like launch technique instead of reviewed host topology

Current docs admit multiple instances, but the ordinary operator still lacks one owned answer to:

- which runtime namespace already owns which listener, storage root, identity store, and control audience
- which parts are distinct enough to coexist
- which parts are forbidden to share

### 2. Storage-world separation and subject-path collision are still explained in different places

The storage docs explain how new worlds are created.
The repair docs explain how same-path double claim can corrupt hidden state.
But the product does not make that one reviewed decision before damage.

### 3. Default working-directory storage is too easy to under-read

The Linux guide still says `.sync` storage is created in the current directory unless `--storage` is set.
That is not a tiny CLI footnote.
It means launch location can silently define continuity-bearing world placement.
AnonSync should never hide that in command help alone.

### 4. Principal continuity and namespace continuity still blur

Current Linux package docs distinguish `rslsync` service mode from current-user mode.
Current update docs separately insist on the same user for preservation.
The operator still has to infer that principal change can also be a different state namespace.

### 5. Collision only becomes legible after the repair article

The strongest current warning about the same-folder double-claim shows up in `Service files missing`.
That is too late.
AnonSync should block or narrow the plan before corruption rather than educate after it.

## The tighter non-clone decision

Borrow Resilio's candor that multiple same-host runtimes are possible, that later instances need explicit port/storage discipline, that runtime user and storage root change continuity, and that double-claiming one subject path can corrupt the first instance's hidden state.
Do **not** clone a product contract where the operator still has to merge Linux notes, config/storage comments, update ritual, and repair prose to answer whether a second runtime is a safe namespace or a destructive collision.

## What AnonSync should do instead

AnonSync should treat **same-host multi-instance bringup** as one first-class reviewed family.
Every serious second-runtime launch, portable-binary bringup, service/user split, external-disk reuse, or CLI-storage override should answer five things in one place:

1. **runtime namespace** — which listener, storage root, identity store, and control audience this runtime would own
2. **principal and continuity basis** — which user/service principal anchors the namespace
3. **subject-path ownership** — whether any existing local subject is already claimed by another runtime world
4. **safe branch vs reattach** — whether the new plan creates a distinct branch, continues an existing world, or collides destructively
5. **safe language** — what the product may and may not say about `run another instance`, `reuse this storage`, and `add the same folder`

## New page obligations from this pass

The archive now needs five more workflow-owned pages:

- **Instance namespace contract sheet**
- **Second-instance bringup review**
- **Same-path claim-collision warning**
- **Shared external-storage review**
- **Instance lineage receipt**

Those pages should sit beside invocation-profile, storage-world, service-promotion, and directory-admission pages — not underneath Linux notes and repair articles alone.
