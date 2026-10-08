# Resilio remedy hardening bootstrap reproducibility, rebuild safety, and world-rebirth fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials are still admirably candid that `the current world is configured the way we want` and `a fresh or rebuilt world will come back with the same safety posture` are not one flat truth.
That candor matters.

The strongest present ingredients are:

- current `Running Sync in configuration mode` docs still say Sync can apply pre-configured parameters at program start and that this is useful when applying the same settings on a number of different machines
- those same configuration-mode docs still say configuration mode can set up only Standard folders
- current `Running Sync as a service on Windows` docs still say service install has a migrate-settings path and also a clean-install path that requires re-sharing and reconnecting folders
- current `Sync Service Troubleshooting on Windows` docs still say changing the service principal to Local System creates a different storage folder and requires re-adding plus re-sharing or reconnecting all folders
- current `Guide to Linux, and Sync peculiarities` docs still say storage location determines where Sync keeps settings, identity, and applied license, and that multiple instances can be run when the operator manually configures them
- current `Sync Private Identity & Linking My Devices` docs still say mixed v2 and v3 linked devices are strongly discouraged because they may conflict on applied license and lead to lost access to Sync UI and shares configuration
- current `Installing Sync package on Linux` docs still say Business users should continue using v2, that updating a current Business installation to v3 is unsupported, and that configured-share access might be lost with reinstall required
- current `Folder Preferences` docs still say important behavior remains folder-by-folder and desktop-only, which means not all safety-relevant behavior lives in one portable startup configuration

## Where the current contract still fragments

The problem is not that Resilio lacks ways to *rebuild* a world.
The problem is that it still lacks a first-class, case-scoped **remedy-hardening-bootstrap** object.

Today the operator can often infer only weaker truths such as:

- there is a sync.conf recipe somewhere
- a current service world looks healthy
- a clean install can probably be reconnected
- linked devices will probably repopulate folders
- current settings can probably be migrated
- a Linux or service storage location can probably be pointed at the right state
- current version lanes are probably close enough
- the hardening probably survives reinstall or world rebirth

Those are useful operational clues.
They are not the same as an explicit answer to `if we rebuild, migrate, reinstall, or re-bootstrap this case onto a fresh world, will the same hardening really reproduce without silent downgrade or scope loss?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-baseline claims than `this is now the safe baseline for future arrivals in the current world`.
It needs to support claims such as:

- the current baseline is safe, but a clean bootstrap would reproduce only Standard-folder lanes and would silently drop Advanced-folder safety assumptions
- the current baseline is safe, but service-account or storage-world migration would require manual rebind and therefore blocks a stronger bootstrap-safe sentence
- the current baseline is reproducible for one named platform or version lane only
- a settings-migration path exists, but the stronger `fresh-world-safe` sentence remains blocked until the new world is re-proven
- the baseline is now not only safe for future arrivals, but reproducible through the required clean-install, rebuild, service-world, storage-world, and supported-version lanes with explicit scars preserved

AnonSync therefore needs a first-class object for **baseline bootstrap reproducibility and world-rebirth safety** rather than merely borrowing config-mode, service, storage, version, or linked-device language.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `would a fresh world reproduce the same safe hardened baseline, or are we still relying on the continuity of the current world?` — only by making the operator combine several operational surfaces:

- startup-scoped configuration mode
- service installation migrate-versus-clean-install branching
- storage-folder identity and share-state binding
- service-principal changes that fork the storage world
- Linux storage and instance-launch choices
- linked-device auto-availability
- v2 versus v3 compatibility warnings
- platform-specific installation and upgrade instructions
- per-folder desktop-only preferences

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- baseline safe in the current world only
- bootstrap recipe present but partial
- clean-world reproduction pending
- reproducible for Standard or named lanes only
- service or storage-world migration still blocks full reproduction
- version-lane compatibility still blocks full reproduction
- clean-world reproduction proven for the required cohort
- baseline bootstrap-reproducible with explicit scars preserved
- bootstrap reproducibility collapsed or stale after later drift

That is why this tranche adds five more first-class pages: **Remedy-hardening-bootstrap contract sheet**, **Remedy-hardening-bootstrap review**, **Remedy-hardening-bootstrap proof**, **Remedy-hardening-bootstrap timeline**, and **Remedy-hardening-bootstrap lineage receipt**.
