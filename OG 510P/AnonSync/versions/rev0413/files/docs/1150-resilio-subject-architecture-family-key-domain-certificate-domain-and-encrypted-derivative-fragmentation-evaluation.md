# Resilio subject-architecture family, key-domain governance, certificate-domain governance, and encrypted-derivative fragmentation evaluation

## Why this pass exists

The archive already had strong doctrine around identity graphs, entitlement topology, non-authority healing, and archive/materialization truth.
What it still lacked was one tighter current Resilio pass about another ordinary operator question:

> when I choose `Standard`, `Advanced`, or `Encrypted`, what governance system am I actually choosing, who can re-share or re-authorize later, how does linked-device membership change the answer, and where does architecture migration stop being a tweak and become remove-and-readd surgery?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `What's the difference between Standard and Advanced folders?` still says Standard folders use randomly generated keys while Advanced folders are based on PKI / digital certificates; only Advanced support Owner and on-the-fly permission changes; Standard peer lists do not understand one person across several linked devices; all Standard folders can be re-shared onward while only Owners can share Advanced folders; and Standard cannot be converted in place to Advanced.
- `Key structure and flow` still says only Standard folders use keys, and that the key family itself already carries architecture-bearing distinctions such as RW, RO, encrypted-capable, encrypted-readback, encrypted-only, and identity-linking keys.
- `Sync Share Dialog (Desktop)` and `User Management` still say only Owners can share Advanced folders, all linked devices under one identity act as Owners, Standard sharing has no Owner level, and Standard peers can re-share the folder onward with whatever key class they possess.
- `How to create a Read Only folder while syncing across linked devices?` and `Is one-way synchronization possible?` still say linked-device arrival defaults into the owner lane, so a true RO linked-device outcome requires leaving that lane and using a Standard-folder RO key manually.
- `Encrypted folders` still says encrypted copies are an untrusted-backup derivative subject: they are created and attached by encrypted key, linked-device use requires `Disconnected` plus manual key entry, encrypted nodes are permanently RO, overwrite-heal is always on, Selective Sync is unavailable, and the encrypted node cannot decrypt its own bytes.
- `Running Sync in configuration mode` still says config mode can set up Standard folders only, not Advanced.

That is a good reason to keep studying Resilio.
It is also another good reason not to clone the exact interface contract.

## What current Resilio still gets right

### 1) It admits that folder architecture is not just a badge

Current docs still preserve real semantic differences among:

- key-domain Standard subjects
- certificate-domain Advanced subjects
- encrypted-derivative backup subjects
- linked-device owner-lane arrivals
- manual-key exceptions that leave the linked lane entirely

That honesty is valuable.

### 2) It admits that re-share power and write power are not the same thing

Current docs still show that:

- Standard has no Owner concept, yet peers can still pass keys onward
- Advanced introduces Owner as a separate delegation class
- linked devices collapse into an owner-default lane
- encrypted nodes can seed but cannot decrypt or meaningfully author shared truth

That distinction is worth preserving.

### 3) It admits that architecture migration has hard ceilings

Resilio still says Standard cannot simply be converted to Advanced, and config mode still only authors Standard subjects.
That is contract-shaping truth, not an implementation detail.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many pages

To answer `what architecture should I use for this subject, and what will that lock in later?` the operator may still need to combine:

- the Standard-vs-Advanced comparison page
- key-structure notes
- share-dialog language
- user-management language
- linked-device identity docs
- linked-device RO workaround docs
- encrypted-folder docs
- config-mode docs

That is too much archaeology for one ordinary decision.

### 2) `folder type` still compresses too many separate truths

The one label can hide:

- governance domain
- delegation model
- identity visibility model
- linked-device default lane
- manual-exception availability
- encrypted-derivative limitations
- config authorship support
- migration ceiling

AnonSync should not inherit that compression.

### 3) upgrade and exception paths still feel bolted on

Current Resilio docs still make the operator discover late that:

- real RO across linked devices is not simply a toggle on Advanced
- encrypted is not just `Advanced but private`
- Standard→Advanced is remove-and-readd rather than in-place upgrade
- config-authored subjects stay trapped in the Standard family

AnonSync should surface those truths at architecture-pick time, not as later surprises.

## Hard decisions for AnonSync

This pass freezes five decisions.

### Decision 1 — subject architecture is first-class governance

AnonSync should model at least these distinct architecture families:

- **key-domain subject**
- **certificate-domain subject**
- **encrypted-derivative subject**

### Decision 2 — write authority and delegation authority stay separate

`can write`, `can re-share`, `can invite`, `can change permissions`, and `can only seed encrypted bytes` must never collapse into one capability label.

### Decision 3 — linked-graph default lane stays visibly separate from manual-key exceptions

If a desired outcome requires leaving linked auto-arrival and using a manual Standard RO key, the product must say so plainly.

### Decision 4 — architecture migration is reviewed, not implied

Any move between subject families must publish whether it is:

- in-place
- remove-and-readd
- app-roster replacement only
- unsupported in config / automation lane
- impossible to claim safely

### Decision 5 — every architecture-affecting action emits one receipt

The receipt must preserve governance domain, delegation lane, migration ceiling, linked-lane exceptions, and the blocked stronger sentence.

## Resulting page family

This tranche therefore adds five more first-class pages:

- **Subject architecture contract sheet**
- **Governance-domain review**
- **Authority and re-share review**
- **Architecture migration watch**
- **Subject architecture lineage receipt**

## The non-clone line

Borrow Resilio's candor that key-based Standard subjects, certificate-based Advanced subjects, linked-device owner lanes, and encrypted derivative subjects are materially different governance systems — but refuse any product contract where `what architecture am I actually choosing here, what power does it give up or confer later, and can I migrate without tearing it down?` still makes the operator merge comparison charts, key docs, sharing docs, linked-device caveats, encrypted-folder caveats, and config-mode notes just to understand one ordinary design choice.
