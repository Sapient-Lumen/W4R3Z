# Resilio identity-graph adoption, certificate takeover, and containment-reset fragmentation evaluation

## Why this pass exists

The archive already has strong work on manual sharing, offer issuance, self-edge derivation, and host/runtime continuity.
What it still lacked was one tighter current Resilio pass about another ordinary operator question:

> if I link this device into that identity now, what graph do I actually join, which certificate survives, what default rights and arrivals come with the union, and what is the real containment move if one seat becomes untrusted?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `Sync Private Identity & Linking My Devices` still says each installation has its own certificate and fingerprint, linking is directional, the receiving side can take over the identity/fingerprint/shares of the source side, linked devices automatically see all folders, and linking two already-running independent instances can make the acquiring device lose its certificate and remove its Advanced folders from the app.
- the same article still says v2↔v3 linking is inadvisable because license/UI/share configuration can conflict, unlinking is local-only, and hiding an offline linked device is not the same as unlinking it.
- `Synchronization Modes` still says linked-device arrivals come in one of three default modes, while the source side still appears effectively full-owner / synced from the outset.
- `How to manually set the location of the folders synced across linked devices?` still says `Disconnected` is the escape hatch when the operator needs manual path choice instead of automatic default-folder materialization.
- `How to create a Read Only folder while syncing across linked devices?` still says linked-device arrival defaults to Owner, so a true RO exception requires leaving the identity-graph default lane and using a Standard-folder Read Only key manually.
- `Can I change the name of my Sync identity?` still says a name change is not a harmless rename; it requires unlinking, creates a new certificate, removes Advanced folders from that instance, and may require relinking other devices.
- `If your device is stolen` still says containment for a compromised linked seat can require unlinking devices from the current identity, removing synced data from storage, reinstalling, regenerating identity, relinking, and resharing.
- `How to apply license key and share license seats` still says a Business license belongs to one identity, linked devices inherit Pro automatically, and directly applying the same business license to another identity steals ownership.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that identity linking is not the same thing as per-folder sharing

Current docs still distinguish:

- graph-wide identity adoption
- per-folder manual sharing by key/link/QR
- default arrival modes for all future folders
- certificate/fingerprint continuity
- linked-device implicit full-rights posture
- exceptions that must leave the linked-device lane entirely

That honesty is valuable.

### 2) It admits that direction matters

`take the M-key from device1 and use it on device2` is not neutral.
The docs still make it clear that the receiver may adopt the source identity and shares.
That asymmetry is worth preserving.

### 3) It admits that containment may require identity regeneration rather than a small cleanup

Stolen-device guidance still escalates to unlink, storage cleanup, reinstall, new identity, relink, and reshare.
That is not mere support noise — it is contract-shaping truth about blast radius.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many pages

To answer `what exactly happens if I link this populated device into that identity right now?` the operator may still need to combine:

- identity/linking docs
- synchronization-mode docs
- manual-path docs
- RO-on-linked-devices workaround docs
- rename/unlink identity docs
- stolen-device containment docs
- license-owner docs

That is too much archaeology for one ordinary decision.

### 2) `linked device` still compresses too many different meanings

The same label can mean:

- same-certificate graph member
- future folder auto-arrival participant
- owner-default recipient
- disconnect/selective/synced arrival policy target
- hidden offline member still logically linked
- seat that can force broader containment/reset if compromised
- business-license beneficiary of identity ownership

AnonSync should not inherit that compression.

### 3) takeover and containment truths still ride on hidden directionality

`Link device` is not enough.
The operator also needs to know:

- which certificate survives
- which side's shares become the visible graph baseline
- whether Advanced folders on the receiving side will disappear from the app
- whether a read-only exception is even possible in the linked lane
- whether the honest compromise response is a graph reset, not a local unlink

Current Resilio docs leave too much of that truth scattered.

## Hard decisions now locked for AnonSync

1. **Identity linking is a first-class graph-adoption contract object.** `manual share`, `graph adoption`, `graph replacement`, `local hide only`, `local unlink`, and `identity reset` are separate verdicts.
2. **Certificate survival and display-name change stay separate.** Changing a name is certificate-affecting and graph-affecting, not a cosmetic rename.
3. **Direction is part of the contract.** `A adopts B` and `B adopts A` are different operations with different survivor maps.
4. **Linked-device default posture is explicit.** Automatic future arrival, default mode, and owner-level lane must be visible before commit.
5. **Containment reset is stronger than unlink.** Hide, unlink, regenerate identity, relicense, relink, and reshare are separate recovery classes.
6. **Receipts preserve the strongest safe sentence and the blocked stronger sentence.**

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Identity-graph adoption contract sheet**
- **Certificate takeover review**
- **Linked-graph default arrival and rights page**
- **Identity containment reset proof**
- **Identity lineage receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right to admit that identity linking is a real graph-level act with certificate direction, automatic folder visibility, owner-default arrival posture, containment blast radius, and license-owner coupling. But it still makes one ordinary operator answer — `if I link this device into that identity now, what survives, what gets replaced, and what is the honest containment move if things go wrong?` — depend on linking docs, mode docs, RO workaround docs, identity rename docs, stolen-device guidance, and licensing docs instead of one stable page family. AnonSync should keep the candor and refuse the archaeology.
