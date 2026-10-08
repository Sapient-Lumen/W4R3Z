# Resilio recovery horizon, retention, and surface-decay evaluation

## Why this pass exists

The archive already had stronger doctrine for restore intent, recovery host choice, witness locality, and archive/history joins.
What it still did not own tightly enough is a quieter but equally ordinary operator question:

- how long do the recovery bytes and event witnesses stay meaningfully available
- what facts expire quickly on mobile, UI, or history surfaces even when some residue still exists
- what size, platform, and cleanup ceilings silently shrink the recovery lane
- when does `recoverable` decay from a practical promise into a fragile maybe

Current official Resilio docs still make that seam very real.
They are candid that Archive and History exist.
They are also candid that their horizons are not universal, not equally accessible, and not equally durable.

## What current Resilio still gets right

Current official docs still publish several truths that are operationally valuable.

- **Recovery evidence has different half-lives.** Current Archive docs still say old versions are kept in Archive for 30 days on desktops and 1 day on mobiles by default, while current desktop Main View docs still say History shows general syncing activity for the last 30 days.
- **Retention is adjustable and sometimes infinite.** Current Archive docs still say `sync_trash_ttl` can be changed and that `0` means Archive files are never deleted automatically.
- **Versioning has a size ceiling.** Those same current Archive docs still say `max_file_size_for_versioning` limits which files are versioned at all.
- **Surface reach decays by platform.** Current Archive docs still say Archive can be opened from desktop UI, reached through the filesystem on Android and WebUI, is unavailable on iOS, and does not work on Android shares located on SD cards.
- **Recovery residue can outlive the app.** Current docs about `.sync` and current uninstall docs still say Archive lives inside the hidden `.sync` folder and that uninstall does not remove archived files automatically.
- **The product does not pretend one recovery answer fits every seat.** Current docs still make operators work with a mixture of desktop history, hidden Archive, and platform-specific filesystem reach.

That is good candor.
Resilio is not pretending that `History`, `Archive`, `restore`, and `remove the app` all share one stable evidence-horizon model.

## Where current Resilio still stays too article-shaped

### 1. `Recoverable` still decays along several unrelated axes

Current official docs still leave operators to mentally combine at least five different limits:

- time horizon for Archive on this seat class
- time horizon for History on this surface
- file-size eligibility for version capture
- whether this platform can even browse the witness store
- whether uninstall or manual cleanup will strand or erase the easiest evidence lane

That is not one fact.
It is a horizon object.
Current Resilio still tends to publish it as scattered caveats.

### 2. Residue and reachability still drift apart

The bytes may still exist in a hidden `.sync/Archive` on disk, but the current surface may no longer expose them usefully.
The operator may therefore have one of these unstable states:

- bytes exist and are browsable
- bytes exist but only through filesystem access
- bytes exist but only on another seat class
- bytes would have existed but were never versioned because of size policy
- bytes once existed but the retention horizon expired
- bytes still survive app removal because hidden control folders were not cleaned

Those are materially different answers.
AnonSync should not clone a product where they remain implicit.

### 3. Retention mutation is still too configuration-shaped

Current docs still describe retention adjustment through power-user preferences and Archive toggles, but the operator-facing consequence is bigger than a config field.
Changing retention, disabling Archive, or cleaning hidden control folders changes future recovery truth.
That deserves one review surface, not a support-memory tax.

### 4. The strongest safe sentence still decays over time

At one moment the honest sentence may be:

- `Desktop seat B still holds a recoverable prior version and matching history window.`

Later, the strongest safe sentence may only be:

- `A hidden local Archive may still exist on one seat, but history context has aged out or this surface cannot reach it.`

Current docs are candid enough to imply that drift.
But current Resilio still does not own one product page that publishes the present recovery horizon and its approaching cliffs.

## What AnonSync should do instead

AnonSync should treat recovery durability as a first-class **horizon** problem, not as a buried set of Archive settings.
The product should own four page families:

1. **Recovery horizon**
   - current byte witness horizon
   - current event witness horizon
   - access reach by seat and surface
   - strongest honest sentence right now

2. **Witness expiry forecast**
   - near-term expiry cliffs
   - size-policy exclusions
   - platform/access decay
   - cleanup and uninstall residue warnings

3. **Retention mutation review**
   - changing retention or Archive posture as a reviewed mutation
   - effect on future recovery claims
   - space cost and residue consequences

4. **Recovery horizon receipt**
   - durable record of the horizon used for a decision
   - available-until estimate, exclusions, and proof floor

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that recovery evidence has real time, size, platform, and cleanup limits. But it is not worth cloning the way current operators still have to infer *how long bytes remain recoverable, what surfaces can still reach them, what policy excluded them, and what residue may survive app removal* by stitching together several help articles.

## New replacement pages added in this revision

- `542` Recovery horizon
- `543` Witness expiry forecast
- `544` Retention mutation review
- `545` Recovery horizon receipt
