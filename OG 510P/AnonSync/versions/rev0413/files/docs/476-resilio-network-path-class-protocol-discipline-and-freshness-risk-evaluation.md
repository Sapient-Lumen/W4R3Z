# Resilio network path class, protocol discipline, and freshness risk evaluation

## Why this pass exists

The archive already had reachability notes, freshness-basis work, and some runtime/service material.
Those were necessary, but another current Resilio pass still exposes a more ordinary operator seam.
The problem is no longer only `can these peers connect`.
It is now:

- what exact **path class** am I binding here?
- what exact **access protocol** is authoritative for mutation and observation?
- what exact **detection grade** can this location honestly support?
- what exact **admission risk** am I accepting if I sync against this remote path anyway?

That is where current official Resilio docs stay candid yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid about network-path reality.

Examples the docs still openly describe include:

- **SMB is still a special path class, not just another folder**: the current `Sync and SMB file shares` article still says Sync can work with SMB/CIFS/Samba shares, but only with limitations and peculiarities.
- **Write authority is still runtime-account-sensitive**: the same article still says both Sync and the user who runs it need full permissions to the synced folder, otherwise delivery can cease.
- **Watcher coverage is still materially conditional**: current SMB docs still say file update notifications may be unavailable on SMB shares and that only SMB 3.0+ supports notifications; otherwise Sync detects changes only during full folder rescan.
- **Freshness ceilings are still openly downgraded for network storage**: current change-detection docs still say some storages such as NFS or SMB2 mounted shares are not even supposed to provide working filesystem notifications, with scheduled scan every 600 seconds by default filling the gap.
- **Locks are still implementation-dependent**: current SMB docs still say lost network connection or a crashed app can leave files locked and inaccessible, with behavior depending on the SMB service or daemon implementation.
- **Mixed protocol access is still candidly called dangerous**: the same article still says many Samba setups cannot safely handle third-party apps touching the same files outside Samba, and that a common NAS pattern can lead to files getting lost or corrupted.
- **Service-mode path workarounds still degrade freshness**: current Windows service troubleshooting still says mapped drive letters are unavailable to the service, UNC entry is the workaround, and the side effect is that file update notifications will not arrive so Sync learns about changes only during rescan or upon restart.
- **Service identity still changes the effective path contract**: the same troubleshooting guide still says switching to Local System can solve access issues but moves Sync into a different storage folder, requiring re-add / re-share / reconnect work.
- **The current v3 line is still active**: current official docs still list Sync v3 through `3.1.2.1076`, which means these network-path truths still matter as current product obligations rather than abandoned legacy behavior.

That candor matters.
Resilio is not pretending that a remote mount is identical to a local disk.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many articles and too many path classes.

### 1. Path class truth still leaks across troubleshooting and architecture notes

Current docs are candid that SMB shares are special and that service-bound UNC workarounds behave differently.
But the operator still has to combine:

- the SMB article
- the Windows service troubleshooting page
- the generic freshness article

just to answer one ordinary question:

- what exact kind of path am I attaching here?

That is too much reconstruction for one ordinary path verdict.

### 2. Protocol authority still hides behind cautionary prose

Current SMB docs still openly warn that a direct-on-NAS access pattern mixed with SMB access can damage or roll back files.
That is a strong product truth.
But the ordinary answer to:

- which protocol is allowed to mutate this namespace?
- who is allowed to touch it outside that protocol?

still lives in warning prose instead of one reviewed page.

### 3. Freshness truth still separates route from detection

Current docs are candid that a path may be reachable yet not promptly watchable.
A UNC workaround can work while losing notifications.
An SMB2 or NFS mount can exist while relying on rescan.
But the ordinary answer to:

- how fresh can this path ever be?

still requires hopping between detection docs and path-specific troubleshooting.

### 4. Admission fitness still hides behind failure recovery

Current docs still teach the operator how to work around missing mapped drives, permission denial, or missing notifications.
What they do not provide as one stable public contract is:

- should this remote path be admitted at all?
- under what runtime account?
- with what freshness and corruption ceiling?
- with what proof that the chosen protocol is authoritative?

That is still too much folklore for an ordinary bind decision.

## What AnonSync should do instead

AnonSync should keep the candor and reject the article sprawl.
The product should split this seam into four page families:

1. **Network path class**
   - local vs mounted-SMB vs UNC-under-service vs unknown path class
   - watcher grade and default freshness ceiling
   - runtime identity and storage-root implications
   - strongest incompatibility or caution

2. **Protocol discipline**
   - authoritative mutation lane
   - forbidden mixed-access patterns
   - direct-vs-shared access witness
   - corruption / rollback risk and mitigations

3. **Detection grade**
   - notifications present / partial / absent
   - rescan cadence, restart dependency, and publication ceiling
   - lock or watcher caveats
   - current proof basis

4. **Network subject admission**
   - permission test results
   - locking assumptions and daemon caveats
   - service-account consequences
   - honest admit / do-not-admit decision with receipt

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that SMB/network paths, permission models, watcher coverage, service identity, and mixed access all materially change the sync contract. But it is not worth cloning the way ordinary answers to `what path class is this`, `which protocol is authoritative`, `how fresh can this location ever be`, and `should this path be admitted at all` still sprawl across the SMB article, service troubleshooting, change-detection notes, and older fix history instead of one stable page family.

## New replacement pages added in this revision

- `477` Network path class
- `478` Protocol discipline
- `479` Detection grade
- `480` Network subject admission
