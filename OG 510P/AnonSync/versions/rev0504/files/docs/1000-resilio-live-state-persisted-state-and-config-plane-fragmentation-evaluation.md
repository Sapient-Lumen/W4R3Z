# Resilio live state, persisted state, and config-plane fragmentation evaluation

## Why this seam matters

Another current official Resilio pass sharpens the no-clone line around **whether a change is merely true now, durably saved, or truly authoritative at next boot**.

The useful distinctions are real:

- a setting can be active in the running runtime
- persisted settings live in a storage directory
- saving to that storage is on a cadence rather than instant by definition
- config-mode values can outrank interactive state entirely
- service/principal changes can move the storage world that actually owns settings and identity

That is good candor.
It is also a strong reason not to clone the present contract.

## What current official docs still say

Current official Resilio materials still openly say all of the following:

- `Power user preferences` still says `config_save_interval` defaults to **600 seconds** and `controls how often settings are saved to storage`.
- `Sync prevents HDD from sleeping on NAS...` still recommends substantially widening `folder_rescan_interval`, `config_refresh_interval`, and **`config_save_interval`** — for example to **18000 seconds** — to preserve NAS sleep behavior.
- `Running Sync in configuration mode` still says that if shared folders are set in the config file, **WebUI will be disabled**, and config-defined shared directories **override** folders previously added from WebUI.
- `Configuring WebUI` still says that when Sync runs in configuration mode, listening IP/port are changed in the **config file**, while on non-config-mode Linux workstations they can instead be changed in settings.
- `Guide to Linux, and Sync peculiarities` still says the **storage** directory is where Sync keeps its **settings, identity, and applied license**.
- `Sync Service Troubleshooting on Windows` still says changing the service account to `Local System` creates a **different storage folder**, after which the old folders are gone from view and must be re-added/re-shared.
- that same Linux guide still says if Sync is forced to listen on a specific interface and that interface is unavailable, Sync will **shut down immediately**.

Those are all real and useful distinctions.
They are also exactly why AnonSync should not clone the current page contract.

## Why this still fails the clone test

To answer one ordinary operator question — **`I changed this; what exactly is true now, what will survive restart/crash, and what source of truth will win at next boot?`** — current Resilio still makes the operator combine:

- power-user save cadence
- NAS sleep advice
- config-mode override behavior
- storage-folder location docs
- service-user troubleshooting
- listener-binding startup caveats

That is too much archaeology for a core reliability boundary.
A product can absolutely have live runtime state, persisted storage, config-file authority, and service-account-specific state homes.
It should not make the operator infer which of those is currently governing a risky action.

## Hard decisions now locked in for AnonSync

This tranche locks in five harder decisions:

1. **live-applied and durable-persisted are different truths**  
   The interface must never imply that a successful click already survived crash or restart unless persistence proof exists.

2. **boot-authoritative plane must be visible**  
   If the next boot will replay config-file truth rather than interactive truth, that fact must be adjacent to any edit and any receipt.

3. **risky actions may depend on persistence class**  
   Destructive, exposure-widening, or policy-significant actions should not quietly rely on state that is only live and not yet durably persisted.

4. **storage-home changes are lineage events**  
   Service-account changes, storage-root changes, and config-mode adoption are not cosmetic; they can move the world that owns settings, identity, and remembered objects.

5. **receipts must preserve persistence ceiling and blocked overstatement**  
   Any receipt must say whether the mutation is only live, durably persisted, boot-authoritative, shadowed by stronger config, or pending a restart/rebind world.

## Resulting interface family

That is why this tranche adds:

- a **Mutation durability contract sheet**
- a **Persist-before-risk review**
- a **Persisted-state proof** page
- a **Boot-authority replay review**
- a **Mutation durability receipt**

The point is not to glorify config files.
The point is to stop the ordinary operator from having to infer whether `changed in UI`, `saved to storage`, `survives crash`, `wins on next boot`, and `still belongs to this same storage world` all mean the same thing when making a consequential decision.
