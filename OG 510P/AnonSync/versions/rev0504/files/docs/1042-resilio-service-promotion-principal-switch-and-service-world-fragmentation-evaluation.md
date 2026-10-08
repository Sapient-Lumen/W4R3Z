# Resilio service promotion, principal switch, and service-world fragmentation evaluation

## Why this pass exists

The archive already had launch-profile, same-host namespace, mutation-durability, route/exposure, and service-promotion sketch language.
What it still did not own cleanly enough was one narrower but very ordinary operator seam:

> when I turn an interactive install into a service seat, or change which principal the service runs under, am I still operating the same seat, the same storage world, and the same watched paths — or did I create a different runtime that only looks like continuity because a browser tab reopened?

Current official Resilio docs still make that seam materially real.
They still say all of the following at once:

- the Windows service installer can either **migrate settings and uninstall the existing client** or do a **clean installation**
- the service can run as **current user**, **Local Service**, or **Local System**
- mapped drive letters are not available to the service because they are created at interactive logon rather than for services
- the UNC-path workaround for that problem loses immediate file-update notifications, so Sync falls back to discovery during **rescan** or **restart**
- switching the service to **Local System** can widen folder access, but it also creates a different service storage folder, shows an empty-looking world, and requires the operator to **re-add / re-share / reconnect** folders
- running the service in config mode works only by placing `sync.conf` in the **service storage folder**
- without a config file, service WebUI is still bound to **127.0.0.1** by default and widening access requires explicit settings or config plus a restart
- uninstall guidance still publishes different service storage roots for local-user, LocalService, and LocalSystem service seats

That is good candor.
It is also a strong reason not to clone the present contract.
One ordinary operator answer — `did I background the same seat, or did I create a different principal/world and lose continuity?` — still depends on combining:

- service-install instructions
- service troubleshooting notes
- config-mode rules
- general preferences / listener notes
- uninstall storage-path notes

AnonSync should keep the distinctions and refuse the archaeology.

## Hard product decisions locked by this pass

1. **Service promotion is a continuity-bearing cutover, not a startup convenience toggle.** `Run as service` is never allowed to read like `same seat, but quieter` without continuity proof.
2. **Principal change is a world switch unless storage-world continuity is proven.** Wider path access under Local System does not, by itself, prove same-seat continuity.
3. **Reach, observation grade, and continuity are separate truths.** A service seat may see more paths, fewer mapped drives, weaker notifications, or wider WebUI exposure without any of those facts proving or disproving lineage by themselves.
4. **Empty state needs attribution.** An empty-looking WebUI after service cutover must be labeled as `clean branch`, `different storage world`, `migration incomplete`, or `unknown` — never left to feel like silent data loss.
5. **Receipts must preserve the actual cutover verdict.** The durable record must keep principal, storage root, migrated-roster proof, observation-grade delta, and reconnect obligations together.

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **Migrate versus clean is admitted as a real branch.** The current service-install article still says the installer can migrate existing shares or perform a clean service installation.
- **Runtime principal is admitted as semantic, not cosmetic.** The same service-install docs still say service can run as current user, Local Service, or Local System.
- **Mapped-drive loss is candidly documented.** The current troubleshooting article still says mapped letter drives are unavailable to the service because interactive logon did not occur.
- **Observation downgrade is admitted as real.** The same troubleshooting docs still say the UNC workaround loses system notifications and therefore detection falls back to rescan or restart.
- **Local System widening is admitted as mixed truth.** The docs still say Local System can access more folders, but it also opens a new storage folder and shows no old shares until re-add / re-share / reconnect.
- **Service config authority is admitted as storage-local.** Current config-mode docs still say service config mode only works when `sync.conf` is placed in the service storage.
- **Service WebUI exposure is admitted as launch/config shaped.** Troubleshooting docs still say the default listener is loopback-only and widening to LAN requires settings or config plus restart.
- **Service storage roots remain principal-specific.** Current uninstall guidance still publishes distinct service storage locations for local-user, LocalService, and LocalSystem variants.

That is useful product honesty.
Resilio does not pretend that `install as service` is one flat verb.

## Where current Resilio still stays too article-shaped

### 1. Service promotion still reads too much like backgrounding

The ordinary operator should not have to reconstruct from installer prose, troubleshooting text, and storage-path notes whether a cutover means:

- same seat, same principal, same service-visible storage world
- same subject inventory, but a different runtime class
- wider filesystem reach but different storage world
- clean service branch with deliberate reconnect later
- same machine, different listener scope, different observation grade

Yet that is still roughly how present-day Resilio explains it.

### 2. Principal widening can still masquerade as continuity

Current official docs are candid that switching to Local System may solve permission trouble.
But they are equally candid that doing so can surface a different storage root with no old folders visible.
That means `can now reach the path` and `is still the same seat` are separate questions.
AnonSync should not clone any contract where one answer silently impersonates the other.

### 3. Observation-grade loss still hides inside workaround prose

Mapped-drive failure, UNC-path fallback, and notification loss materially change how quickly and confidently the service sees updates.
Current docs preserve that truth, but only as troubleshooting side effects.
That is too weak.
The cutover itself should publish the new observation grade before the operator keeps going.

### 4. WebUI reopening can still over-signal continuity

The service starts, the browser opens, and a WebUI appears.
But current docs also show that the control surface may belong to a different principal, different storage world, and different listener posture than the prior interactive seat.
That means `WebUI opened` is not strong enough evidence for `same node continued`.

### 5. Cleanup and uninstall knowledge still carries continuity truth

Current uninstall docs still matter because they reveal which storage roots belong to which service principals.
That is telling.
If removal docs are still required to reason about service-world lineage, the product has not truly owned the runtime contract in one ordinary page family.

## The tighter non-clone decision

Borrow Resilio's candor that service install mode, runtime principal, storage root, mapped-drive access, notification grade, and listener posture are materially different truths.
Do **not** clone a product contract where operators still have to merge install, troubleshooting, config, preferences, and uninstall articles to answer whether a service cutover preserved the same seat, created a clean branch, widened reach while downgrading observation, or silently switched storage worlds.

## What AnonSync should do instead

AnonSync should treat **service promotion and principal continuity** as a first-class reviewed object.
Every serious service-install, service-user switch, clean-vs-migrate cutover, or service-storage rebind should answer five things in one place:

1. **continuity class** — same seat, same seat with follow-up, clean branch, different storage world, or blocked
2. **principal delta** — what changed in runtime identity, namespace reach, and write authority
3. **storage-world verdict** — which state root now governs the service seat
4. **observation and exposure delta** — mapped-drive visibility, notification grade, rescan dependence, and WebUI audience
5. **safe language** — what the product may and may not say about migration success and continuity

## New page obligations from this pass

The archive now needs five more workflow-owned pages:

- **Service promotion contract sheet**
- **Principal switch review**
- **Service world preview**
- **Service cutover proof**
- **Service lineage receipt**

Those pages should sit beside launch-profile, same-host namespace, mutation-durability, and route/exposure pages — not underneath a troubleshooting lane.
