# Resilio remedy hardening attestation regime-shift robustness, migration continuity, and world-transition fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that `the intended state stays true across ordinary steady-state churn`, `that state survives upgrades or install-style changes`, and `the same governing world still exists after service-user, storage-path, or configuration transitions` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Updating installation to Resilio Sync v3` docs still say update process depends on installation style, and non-default CLI launches must restart using the same command and same parameters so Sync points to the same storage folder and preserves configuration
- the same current `Updating installation to Resilio Sync v3` docs still say Resilio Sync Business cannot be updated to v3 and may lose shares configuration even while files remain on the device
- current `FAQ Resilio Sync 3.0.0` docs still say v2 and v3 preserve synchronization compatibility, while linked devices under one identity should all be updated to v3 to avoid license conflicts
- current `Running Sync as a service on Windows` docs still say a service install can migrate settings or do a clean installation, and the clean installation path requires re-sharing folders and connecting them to already existing peers
- current `Sync Service Troubleshooting on Windows` docs still say changing the service account to Local System creates a different storage world where old added folders are absent and new storage paths apply
- current `Sync Storage folder` docs still say storage locations vary materially by current user, Local Service, Local System, Linux launch directory, config-defined storage path, package install style, and NAS platform
- current `Running Sync in configuration mode` docs still say config mode can define a non-default storage path, can set up only Standard folders, and that shared folders in config disable WebUI while overriding folders previously added from WebUI
- current `Guide to Linux, and Sync peculiarities` docs still say Linux can run multiple instances if the operator manually assigns ports and storage, and that default storage is created in the current directory if not explicitly set
- current `Cloning Sync` docs still say cloning a Sync instance by copy or disk-clone means is unsupported and may produce multiple instances that do not transfer data to one another and show other strange behavior
- current `Resilio Sync 3.0 change log` still records upgrade-era UI and warning fixes, reinforcing that visible continuity and durable transition-safe continuity are not the same claim

## Where the current contract still fragments

The problem is not that Resilio lacks transition-relevant clues.
The problem is that it still does not produce one first-class, case-scoped **regime-shift robustness** object.

Today an operator can often infer only weaker truths such as:

- the state survived ordinary churn, but the next upgrade still depends on keeping the same binary launch shape, parameters, user, and storage path
- the service works, but changing service account can silently fork the governing world into a different storage root with no prior shares visible
- config mode is present, but switching into it can change folder class availability and disable or override prior WebUI-managed state
- the bytes remain on disk, but the shares configuration and identity continuity across product-family or install-style transitions are still conditional
- Linux can run multiple instances, but survival across that transition depends on manual port and storage discipline rather than one typed continuity verdict
- copying the instance may look like a shortcut, but the vendor explicitly says cloning is unsupported and may yield non-transferring twins or other strange behavior

Those are useful clues.
They are not the same as an explicit answer to `will this durable target state survive the named world transition class, with governing identity, storage, topology, and control surfaces still continuous enough to support the same sentence afterward?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the target state is durable in the current steady state`.
It needs to support claims such as:

- the target state is durable in the current world, but regime-shift robustness is unreviewed
- the target state survives named update paths only if the same user, storage path, and launch parameters are preserved
- the target state survives migration for a named transition class only, while service-account or config-mode forks remain blocked
- the target state is regime-robust for the governed slice across a named transition set, while broader all-transition permanence remains blocked

So AnonSync should not clone Resilio's present contract at this seam.
It should borrow the candor about update branching, storage-path dependence, service-account forks, config-mode overrides, Linux multi-instance discipline, mixed-version cautions, and unsupported cloning, while replacing the fragmented operator story with one first-class family for **regime-shift robustness, migration continuity, and world-transition survival truth**.
