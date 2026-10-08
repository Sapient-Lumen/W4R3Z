# Resilio volume capability, metadata fidelity, and fallback evaluation

## Why this pass exists

The archive already had hidden-sidecar work, shell-affordance work, provider-grant work, and the fresh network-path tranche.
Those were necessary, but another current Resilio pass still exposes a more ordinary operator seam.
The problem is no longer only `can this path connect` or `does the extension seem healthy`.
It is now:

- what exact **volume/filesystem class** is carrying this subject?
- what exact **native primitives** does that volume really support?
- is metadata carriage **native, limited, or stub-backed**?
- are missing actions a **client problem** or a **volume ceiling**?
- should the operator **accept degraded semantics**, **migrate the subject**, or **reformat the target**?

That is where current official Resilio docs stay candid yet still become too article-shaped.

## What current Resilio still gets right

Current official material is still admirably candid about volume capability reality.

Examples the docs still openly describe include:

- **The current v3 line is still active**: the current official v3 change log still lists Sync through `3.1.2.1076`, and the same page still records `3.0.3.1065` fixing missing context-menu items in Selective Sync shares on macOS. That means filesystem/surface capability is still current product work, not dead history.
- **xattrs / alternate streams are still treated as a real contract**: the current `Alt Streams and Xattrs in Sync` article still says xattrs are synchronized according to a whitelist kept in hidden `.sync/StreamsList`.
- **Cross-platform capability ceilings are still named directly**: the same article still says Windows alt streams are not supported on FAT32, Linux xattrs must fit naming/size rules, and macOS xattrs are size-limited.
- **Fallback carriage is still explicit**: when Sync cannot store xattrs natively, the same article still says it creates stub files in `.sync/Streams` and stores the xattr data there so it can propagate onward.
- **IgnoreList is still not the metadata truth surface**: the same doc still says xattrs cannot be ignored through IgnoreList and must instead be removed from StreamsList.
- **Shell/materialization affordances are still volume-sensitive**: the current `No Sync icons...` article still says Windows context-menu items appear only for files on NTFS because that filesystem supports alternate data streams.
- **Hidden service state still carries part of the capability story**: the current `.sync folder` article still says StreamsList whitelists alternate streams, xattrs, and resource forks, and that `.!sync` files represent in-flight transfer artifacts.
- **Official fix history still remembers real filesystem edge cases**: the official historical change log still records FAT32 log flooding, exFAT attribute issues, CIFS/SMB strange files when alternate streams are unavailable, and xattr-delivery problems on Linux.

That candor matters.
Resilio is not pretending every target volume is semantically equal.

## Where the current page shape still fails

The ordinary operator answer is still reconstructed across too many articles and too many capability classes.

### 1. Volume class truth still leaks across sidecar and shell docs

Current docs are candid that StreamsList matters, FAT32 lacks alt streams, NTFS gates shell actions, and xattr storage can fall back to stubs.
But the operator still has to combine:

- the xattr article
- the shell-affordance troubleshooting page
- the `.sync` sidecar article
- old fix history

just to answer one ordinary question:

- what exact capability class does this target volume belong to?

That is too much reconstruction for one ordinary target verdict.

### 2. Native versus fallback metadata carriage is still too archaeological

Current docs still openly explain the `.sync/Streams` fallback.
That is excellent candor.
But the ordinary answers to:

- are metadata operations native here?
- are they silently degraded to stub fallback?
- what bundle or portability risk follows?

still require reading architecture prose and hidden-directory notes instead of one reviewed page.

### 3. Missing actions still blur product-health and volume-health

Current docs still say Windows context-menu items require NTFS and shell-extension registration.
That is a real distinction.
But the operator still lacks one ordinary page that separates:

- shell extension unhealthy
- volume not eligible
- subject not in the right sync posture
- action equivalent still available elsewhere

Without that separation, absent affordances still feel like superstition.

### 4. Repair truth still hides in workaround folklore

Current docs still teach the operator how to re-enable menus, edit StreamsList, or tolerate fallback stubs.
What they do not provide as one stable public contract is:

- should this target be kept as-is?
- should the subject be moved?
- should the operator reformat or choose a different volume?
- what proof shows the repaired target now supports the intended semantics?

That is still too much folklore for an ordinary storage decision.

## What AnonSync should do instead

AnonSync should keep the candor and reject the article sprawl.
The product should split this seam into four page families:

1. **Volume capability**
   - filesystem / volume class
   - native primitive support (`alt streams`, `xattrs`, `resource forks`, `placeholder affordances`)
   - strongest honest ceiling
   - one-line verdict

2. **Metadata fidelity**
   - native carriage versus stub fallback
   - StreamsList / whitelist effect
   - bundle or portability risk
   - strongest omitted or downgraded behavior

3. **Affordance ceiling**
   - which placeholder/materialization actions are valid on this seat and this volume
   - whether missing actions reflect sync posture, extension health, or volume class
   - equivalent in-app action if any
   - strongest blocked promise

4. **Volume repair**
   - keep degraded, migrate subject, or reformat target
   - costs, non-effects, and rebuild scope
   - postcondition proof
   - explicit receipt

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that filesystem and volume class materially change xattr fidelity, fallback carriage, shell/materialization affordances, and even hidden service-state behavior. But it is not worth cloning the way ordinary answers to `what can this target honestly carry`, `is metadata native or stub-backed`, `why is this action missing`, and `should I migrate or reformat` still sprawl across xattr docs, shell-affordance troubleshooting, hidden-sidecar notes, and old fix history instead of one stable page family.

## New replacement pages added in this revision

- `482` Volume capability
- `483` Metadata fidelity
- `484` Affordance ceiling
- `485` Volume repair
