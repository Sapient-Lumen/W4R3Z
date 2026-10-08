# Resilio remedy hardening, recurrence prevention, and carry-forward fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials do expose several ingredients an operator can use when trying to reduce the chance that the same causal class returns after a case re-enters guarded ordinary life.
That candor is valuable.

The strongest ingredients from the present contract are:

- current `Running Sync in configuration mode` docs still say Sync can start with pre-configured parameters and apply the same settings on a number of different machines, while also noting that config mode can only set up Standard folders, not Advanced
- current `Sync Preferences` docs still say notifications, startup behavior, global pause, scheduler, bandwidth limits, proxy, and debug logging are ordinary settings surfaces
- current `Power user preferences` docs still say advanced knobs such as peer expiration, free-space warning threshold, config refresh interval, config save interval, disk priority, and per-job disk workers are ordinary tunables
- current `Folder Preferences` docs still say relay use, tracker use, LAN search, predefined hosts, Archive use, overwrite-on-read-only, and file download priority can all be configured on a folder-by-folder basis
- current `User Management` docs still say permissions can be changed on the fly for Advanced folders without disrupting synchronization, and that Owners control onward sharing and revocation
- current `Ignoring files in Sync (Ignore List)` docs still say IgnoreList controls what is indexed and synchronized, already ships with default ignore rules, and re-reads on change or at rescan interval
- current `Is one-way synchronization possible?` docs still say Read Only can enforce one-way flow, but Advanced folders do not allow read-only synchronization across linked devices

## Where the current contract still fragments

The problem is not that Resilio lacks hardening knobs.
The problem is that it still lacks a first-class, case-scoped **remedy-hardening** object.

Today the operator can often infer only weaker facts such as:

- some config values were changed
- a per-folder preference looks safer now
- read-only or owner permissions were adjusted
- one ignore rule was added
- one schedule or bandwidth rule was tightened
- one linked-device topology was left intact while another lane was narrowed

Those are useful operational moves.
They are not the same as an explicit answer to `has the specific cause class behind this case actually been hardened against recurrence across the required cohort and future carry-forward surface?`

## Why that matters for AnonSync

AnonSync needs to support stronger post-reentry claims than `we changed some settings` or `the dangerous path is now less likely`.
It needs to support claims such as:

- the triggering cause family is now blocked by durable defaults across the required cohort
- one lane is hardened, but linked-device carry-forward still leaves the stronger recurrence-safe sentence blocked
- the case can re-enter guarded ordinary life, but only under a named hardening debt because the permanent guardrail is not yet deployed everywhere
- a temporary manual fix exists, but the stronger claim of recurrence hardening stays blocked until the durable policy is pushed to every covered peer and role
- a harmful path was narrowed only in Standard-folder semantics, so Advanced-folder authority surfaces still keep the stronger sentence blocked

AnonSync therefore needs a first-class object for **remedy hardening** rather than merely borrowing config, preference, ignore-list, or permission language.

## Non-clone conclusion

Borrow the ingredients.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `after honest re-entry, has this case actually been hardened against recurrence of the same cause?` — only by making the operator combine several operational surfaces:

- startup and configuration-mode deployment
- global preferences and power-user tunables
- per-folder network and archive behavior
- on-the-fly permission edits and owner topology
- IgnoreList behavior and rescan-based activation timing
- read-only and linked-device limitations across folder types

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model the following as separate public truths:

- cause remediated once
- temporary local workaround only
- durable hardening drafted
- hardening partially deployed
- required-cohort hardening deployed
- future-carry-forward surface still exposed
- linked-identity spread still weakens hardening
- permission hardening incomplete
- recurrence budget narrowed but not hardened
- recurrence-hardened discharge achieved

That is why this tranche adds five more first-class pages: **Remedy-hardening contract sheet**, **Remedy-hardening review**, **Remedy-hardening proof**, **Remedy-hardening timeline**, and **Remedy-hardening lineage receipt**.
