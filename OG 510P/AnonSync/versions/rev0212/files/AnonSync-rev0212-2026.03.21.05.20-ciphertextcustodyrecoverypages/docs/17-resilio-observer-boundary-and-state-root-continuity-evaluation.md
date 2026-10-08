# Resilio observer-boundary and state-root continuity evaluation

## Purpose

The archive already has stronger answers for trust, intake, rates, lineage, custody, restore, shell parity, and filesystem shape.
What still remained under-specified was a quieter but still important class of non-clone reason:

> current Resilio docs are reasonably honest about what outside infrastructure can learn and about where local identity/runtime state lives, but those truths still live across several separate security, config, and troubleshooting pages rather than one stable product-owned interface contract.

This document tightens that line.
It does not argue that Resilio hides everything.
It argues that the current honesty still arrives as article reconstruction more often than one ordinary page.

## Bottom line

Resilio still deserves credit here.
Current official docs still show all of the following are real and useful:

- the relay is explicitly described as an encrypted pass-through rather than plaintext storage
- tracker, landing-page, update-check, and statistics services are described with meaningful specificity
- link landing pages intentionally keep link-specific data after `#` so the server does not see the unique folder-identification payload
- storage-folder paths and config-mode `storage_path` are documented rather than treated as mystical internals
- service/user-context changes are candidly described as changing the effective storage root
- unsupported cloning is stated plainly instead of being quietly tolerated

Those are good instincts.
But the same docs also show why AnonSync should not clone the page contracts.

## The four load-bearing non-clone seams in this pass

### 1) Infrastructure visibility truth is real, but still scattered

Current official docs still say:

- tracker service learns IP addresses, listening ports, and share IDs
- relay can carry encrypted transfer traffic when direct connection is impossible
- the link landing page counts clicks but does not see the anchor-fragment payload
- update check and telemetry are separate points of contact with Resilio infrastructure
- all of those can be narrowed or disabled through preferences/config

That is useful honesty.
It is still not one stable page answering the ordinary operator question:

> who outside this mesh can learn what exact facts about me or this subject right now?

### 2) Service roles are described, but their authority ceilings are not one ordinary review page

Current official docs still say:

- Resilio team cannot see file content
- Resilio neither hosts nor caches content in ordinary Sync operation
- relay cannot examine the encrypted data it passes
- link distribution is manual and link-specific payload after `#` is not sent to the server
- peers can still find one another through decentralized mechanisms beyond one vendor choke point

That is good architecture communication.
It is still not one ordinary service-role page proving:

- what each external service can observe
- what it can never observe
- what it can influence operationally
- what disabling it would change
- what reliance or residue would remain after disablement

### 3) The local state root is a real operator object, but still support-shaped

Current official docs still say:

- the storage folder contains current configuration, auxiliary settings, shares' database, logs, and identity details
- default storage paths vary across desktop, service, Linux package, NAS, and mobile environments
- config mode can create a `.sync` storage folder near the binary/current directory if no explicit `storage_path` is provided
- service configuration files must live in the service storage location, not just anywhere the operator happens to point a shortcut

That is useful documentation.
It is still not one ordinary page answering:

> which exact local world is this process attached to, where does it live, and why would another runtime profile show a different inventory?

### 4) Clone safety versus attach/import continuity is still too blunt

Current official docs still say:

- cloning a Sync instance by copying disks or app state is unsupported
- changing Windows service user/context can create a new storage folder and an apparently empty inventory
- switching into that new state then requires re-add / re-share / reconnect work
- a non-default storage path creates a new settings world there

Those are important truths.
But the practical operator answer still arrives as blunt prohibitions and troubleshooting prose instead of one attach/import review page that classifies:

- same world reattached
- successor import
- stale backup restore
- clean empty branch
- clone-risk concurrent world

## Borrow / adapt / reject line for this pass

### Borrow directly

AnonSync should borrow these ideas without embarrassment:

- explicit disclosure of what vendor-run services can and cannot see
- explicit statement that relay traffic can be encrypted pass-through rather than plaintext custody
- explicit state-root / storage-root vocabulary
- explicit refusal to bless opaque disk cloning as the normal continuity path

### Adapt instead of clone

AnonSync should adapt these families into stronger public pages:

- infrastructure visibility as one observer/fact matrix
- service role and disablement as one capability-ceiling page
- active state root as one ordinary system page
- attach/import of existing state as one reviewed continuity boundary

### Refuse the clone line

AnonSync should not clone:

- security/privacy truth that still requires hopping among tracker, relay, landing-page, and stats articles
- vague `cloudless` comfort language without one exact observer matrix
- storage-root behavior that only becomes obvious after a service-user switch produces an empty world
- unsupported-cloning prose as the main answer to state reuse, successor import, or stale-backup restore

## Replacement pages AnonSync now owes

This pass therefore claims four more ordinary pages:

1. **Infrastructure visibility** — one page listing observer classes, fact classes, and plaintext ceilings
2. **Service role** — one page showing what each outside service can do, cannot do, and what disablement changes
3. **State root** — one page showing the active local world, identity custody, runtime principal, and clone risk
4. **Attach state** — one page reviewing whether an existing root is same-world attach, successor import, stale backup, clean branch, or clone-risk

## Result

The archive now has a sharper sixth-wave answer to `why aren't we cloning Resilio here either?`

The answer is no longer just `too many hidden files` or `too much shell ritual`.
It is also:

> because current Resilio still leaves too much ordinary operator meaning spread across several separate security/config/troubleshooting pages whenever the user asks who outside can learn what, and which local state root actually defines this node.

That is a solid reason to borrow the architectural honesty while replacing the page contracts.

