# Resilio hydration-engine, shell lane, and history-ceiling evaluation

## Why this pass exists

The archive already had strong doctrine for placeholders, shell affordances, archive replay, subject-kind overrides, and substrate admission.
What it still lacked was one direct evaluation for a sharper modern seam:

> when a product says `Selective Sync`, is it naming one stable contract, or hiding several materially different hydration engines, action lanes, history guarantees, and conflict ceilings behind one friendly label?

Current official Resilio docs make that seam much sharper than a basic `placeholders exist` story.
Across current Sync and Resilio official Windows cloud-file documentation they still say all of the following:

- Selective Sync can mean classic `.rsl` placeholders on Sync, with new files arriving as placeholders and existing full files left as they are.
- Removing a Selective Sync share in Sync still removes placeholders from that device.
- File-browser context actions for Selective Sync still depend on OS/file-system integration: on macOS Finder extensions may need reset or can conflict with Dropbox/Google Drive, and on Windows context items appear only on NTFS because the feature depends on alternate data streams.
- Resilio Sync's live v3 line still recently included a fix for missing context-menu items in Selective Sync shares on macOS.
- Resilio's Windows Transparent Selective Sync docs still distinguish a newer cloud-file style engine from legacy Selective Sync.
- Those same current docs still say the newer engine is default, requires specific Windows versions and `cldapi.dll`, works on local NTFS but not FAT32/exFAT, and cannot create the new Selective Sync root on a network share.
- Current TSS docs still say Archive behavior changes materially on v3.x and older: file versions are not stored for TSS folders, only remote deletions are archived.
- Those same docs still say file-edit collision detection does not work on TSS shares on Windows for v3.x and older because of Archive limitations.
- They also still say two Agents with Selective Sync on one computer are unsupported, OneDrive on-demand files are incompatible, some VMware disk modes can cause unexpected I/O errors with cloud stubs, and inherited Cloud API flags can cause unexpected auto-sync behavior.

That is strong candor.
It is also a very good reason not to clone the label contract.

## What Resilio gets right

### 1) It admits that hydration is real, not cosmetic

Current docs still plainly distinguish:

- placeholders versus hydrated files
- `Always available`, `Available on this device`, and `Available when online`-style states in the newer Windows engine
- local materialization versus local space reclaim
- automatic future hydration beneath some hydrated subtrees

That is worth borrowing.

### 2) It admits that the action lane depends on local integration health

Current docs are candid that hydration affordances are not only daemon policy.
Finder extension health, shell registration, file-system capability, and local OS integration still matter.
That is useful honesty.

### 3) It admits that the engine changes more than icons

The Windows cloud-file docs are especially useful here.
They still say history and collision behavior differ materially from ordinary expectations on older lines.
That means `Selective Sync` is not just a storage-saving toggle.
It can change what rollback and conflict sentences are still honest.

### 4) It admits that some local worlds are simply bad fits

Current docs still call out local NTFS requirements, network-share-root limits, OneDrive conflict, VMware caveats, and multi-agent unsupported cases.
That is the right instinct.

## Why this is still a strong reason not to clone them

The ordinary operator answer is still overloaded.
Current official docs still force too much reconstruction before the product fully owns these questions:

- is this subject using a basic placeholder engine or a deeper OS hydration engine?
- which actions are available because of daemon policy, and which only because shell/provider integration is healthy?
- does this hydration mode still have normal archive/version history, only delete history, or a narrower rollback ceiling?
- does collision detection still work here, or has the active engine silently lowered that guarantee?
- is the target path merely inconvenient, or actually ineligible for the requested hydration engine?
- is a second runtime / other provider merely coexisting, or actively invalidating the contract?

That should not require stitching together Selective Sync help, shell-extension troubleshooting, a changelog, and a separate Windows cloud-file article.

## The tighter AnonSync conclusion

AnonSync should borrow the following from current Resilio more boldly:

- explicit candor that hydration is a real contract, not a cosmetic file-list trick
- explicit candor that action lanes depend on local integration health and substrate prerequisites
- explicit candor that some hydration engines change rollback and conflict guarantees
- explicit candor that some path / provider / co-tenant combinations are not safely eligible

But AnonSync should refuse the exact label contract whenever one ordinary answer still depends on several articles.
The product should not let `Selective`, `Placeholder`, `Online-only`, `Keep on device`, or similar language stand without one owned surface that states:

- active hydration engine
- active action lane
- local prerequisite basis
- history / archive guarantee
- collision guarantee
- co-tenant or parallel-runtime ceiling
- strongest safe sentence and stronger forbidden sentence

## Replacement pages added for this seam

This pass therefore adds four more page-shaped obligations:

1. **Hydration-engine posture** — what engine is active, what local lanes it depends on, and what guarantees are still honest.
2. **Hydration-mode change review** — what changes in prerequisites, action lanes, history, and collision behavior before commit.
3. **Hydration evidence** — what proves engine kind, OS/provider readiness, shell health, path eligibility, and guarantee ceilings.
4. **Hydration receipt** — what later proves the effective engine, action lane, and remaining history/conflict ceiling.

## Bottom line

The tighter no-clone reason is now this:

> Resilio is current evidence that placeholder and hydration modes are useful and operator-worthy; it is also current evidence that one friendly label can still hide several different engines, shell dependencies, archive ceilings, and collision guarantees. AnonSync should copy the candor and refuse the overloaded label contract.
