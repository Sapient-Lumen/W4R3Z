# Monsternix

## A computer that carries the reasons for its own changes

Monsternix makes a NixOS machine into a continuing, inspectable project that a succession of human and AI collaborators can work on. Its single [configuration.nix](../Maintained%20Tools/configuration.nix) carries system declarations, an executable operator interface, a collaboration protocol, and the machinery for connecting a proposed change to the exact system that was built, tried and accepted. The aim is not merely to reproduce a package selection. It is to keep the computer understandable and governable as its configuration, circumstances and collaborators change.

A useful example is a service change proposed during one model session and reconsidered in another. The successor should receive more than a plausible patch and “the tests passed.” It needs the complete candidate, the reason for the change, the system on which it was tried, the failures that mattered, and the decision still owed by the operator. Monsternix organizes that handoff around the machine itself rather than relying on an uninterrupted chat or a particular model's memory.

The supplied object is the **portable Foundation module**, not a universal ready-to-boot configuration. Hardware, storage, console access, hostname and clock policy belong to an explicit machine adapter. Its [Foundation boundary](../Maintained%20Tools/configuration.nix#L601-L615) also distinguishes this reusable module from the particular production systems that informed it. A mechanism learned on one machine can travel without exporting that machine's private or hardware-specific decisions as everybody else's defaults.

## One file, several precise readings

The file is deliberately more than its suffix suggests. Nix reads it as a system module. Its first line gives it a Bash entrance. Humans can read its constitution and incident memory. Stable source markers let a collaborator locate definitions, ownership boundaries and unresolved questions. Installed generations carry the complete source that identifies them.

These are not competing versions of the project. They are different readings of one carried object. Generated helpers may use other languages, provided their source, rendered bytes and installed projections remain inspectable. The goal is one accountable source and transaction protocol, not a demand that all programming be done in Bash. The [polyglot design](../Maintained%20Tools/configuration.nix#L243-L305) makes the imperative work behind a declarative system visible: building, activating, observing, choosing a boot default and recovering from failure are operations, not consequences that a declaration can prove by itself.

That arrangement gives the full-file handoff practical force. A recipient receives the surrounding constraints and navigation as well as the requested edit. Derived maps and working fragments can help construction, but they must converge back into the complete candidate rather than quietly becoming another source of authority.

## Changing the machine without changing what “passed” means

The central distinction is between a candidate and an accepted system. Monsternix separates temporary trial from permanent selection, and separates the predecessor's judgment from the candidate's account of itself.

Its [test transaction](../Maintained%20Tools/configuration.nix#L13707-L13988) does the following:

1. Checks candidate lineage and source structure, takes the transaction lock, and freezes the exact candidate into a private, single-file input. It does not scoop up the surrounding directory, untracked work or credentials.
2. Records both the currently running system and the boot default. These can be different: a successful temporary trial need not yet be the system selected for the next boot.
3. Uses the machine's activation hook or the NixOS test path to realize and temporarily activate the candidate. It checks the resulting closure identity, unchanged boot default and correspondence between the candidate and the complete source carried by the running generation.
4. Applies the accepted predecessor's audit as a floor, then the candidate's format-aware audit as an additional ceiling. Machine-specific postflight and behavior checks have their own dispositions.
5. Retains a receipt for this exact trial. A passing temporary system can remain running for review before promotion.

The two judges answer a genuine evolution problem. Letting a candidate supply its only judge would allow it to redefine success to suit itself. Letting an old judge permanently define every future format would prevent the protocol from growing. The predecessor floor and candidate ceiling keep continuity and extensibility in tension instead of choosing one and forgetting the other.

[Promotion](../Maintained%20Tools/configuration.nix#L14350-L14535) then checks the receipt, exact source identity, current running closure and health before setting the system profile to the already-tested closure. It does not rebuild whatever text happens to be in the editor now. Temporary instrumentation must be removed before permanent promotion; removing it changes the candidate and therefore requires a new trial. This is an operational meaning of “accept that change,” not merely a label attached to a conversation.

The [source-recorded history](../Maintained%20Tools/configuration.nix#L462-L469) explains why exact source attachment is more than bookkeeping: an early observer found a guest closure carrying unrelated machine source selected by generic NixOS copying. A build can succeed while its account of what built it is wrong. The source/closure check makes that discrepancy a transaction failure rather than leaving it for the next collaborator to discover.

The boundary is important and specific: **temporary activation runs reviewed candidate code as root**. The protocol guards judgment and promotion; it is not a sandbox for hostile candidates. Recovery also distinguishes reselecting a prior closure, reapplying activation and establishing restoration. Its [recovery witness](../Maintained%20Tools/configuration.nix#L13067-L13100) explicitly does not promise rollback of arbitrary mutable application state or qualified durable crash recovery. A service's database migration does not become reversible just because its old executable remains available.

## Evidence that another collaborator can actually use

Monsternix treats observability as part of the computer, not an accessory dashboard. The [observation contract](../Maintained%20Tools/configuration.nix#L390-L498) and [collector implementation](../Maintained%20Tools/configuration.nix#L9609-L10019) relate source and closure identities to running services, failed-unit results, listeners, timers, bounded journals, coredumps, resource pressure and transaction state. It can retain private evidence bundles and produce compact summaries without raw logs, with bounded, control-safe diagnostic excerpts when needed. Raw evidence remains private; the credential filter is fallible, so even a diagnostic excerpt needs review before sharing. Machine-specific observers extend that account through declared interfaces.

Several distinctions make these measurements more useful than a single reassuring status:

- The observer's health and the observed system's health are separate. A collector can fail while its subject is healthy, or work correctly while reporting a damaged system.
- Missing, inapplicable, deferred and failed observations are not interchangeable. An old successful observation is history, not a fresh answer.
- A selected measurement baseline is a comparison point, not acceptance of a candidate or permission to expose a service.
- Seeing a listener does not authorize it. A record of what exists and a decision about what ought to exist have different jobs.

The [sensory-organ contract](../Maintained%20Tools/configuration.nix#L5858-L5946) gives that separation a concrete interface: readings carry bounded codes, while their explanatory text and action meanings come from the source-owned registry. A critical reading does not acquire permission to notify, remediate or promote a system.

The compact `mnx brief` interface combines source checks and current bounded observations into a handoff. Its [next-action selection](../Maintained%20Tools/configuration.nix#L10572-L10587) prioritizes matters such as an active transaction, source/closure mismatch, failed units and missing observations before suggesting review of a temporary system. The operator supplies the actual purpose; the report does not invent one.

This is also a way to make collaboration work with limited attention. The source distinguishes present requests, inherited intent, measured facts, inferences, proposals and unknowns. Keeping those categories legible prevents a successor from promoting an old suggestion into present permission or a confident explanation into a measurement. Brief summaries point back to bounded evidence rather than requiring the next reader to trust the previous reader's fluency.

## A foundation that can be adapted, reduced or left

Monsternix does not make preservation of all its machinery a condition of continuity. Source ownership supports [ejection profiles](../Maintained%20Tools/configuration.nix#L12224-L12280), including plain-NixOS and Foundation-oriented outputs. The directions differ: `plain-equivalent` strips the framework while retaining explicitly owned ordinary machine declarations; `foundation` keeps portable mechanisms and experimental definitions while removing machine policy and optional flavor; `foundation-core` removes the experimental definitions too. The [ownership contract](../Maintained%20Tools/configuration.nix#L6443-L6626) makes those dispositions explicit. These are source transformations, not activation commands or proof that the resulting machine behaves equivalently. The point is that adopting the project's discipline should not make the operator dependent on keeping its entire framework forever.

Optional mechanisms are similarly distinguished from universal requirements. The source calls this **semipermanent flavor**: carried machinery with a named gate, absent-capability behavior, evidence surface and ejection disposition. It can remain useful across many revisions without becoming mandatory or immortal. Experimental vault and encrypted keystroke-journal facilities belong in this category. Their presence is not enrollment or consent to capture input; their explicit activation and privacy boundaries matter to their use.

The longer horizon is independence from the current substrate. Nix and NixOS presently supply immutable artifacts, dependency closures and system selection. Monsternix's [reconstruction curriculum](../Maintained%20Tools/configuration.nix#L532-L560) asks what a successor would have to preserve or replace if that substrate changed: meanings, source witnesses, adapter roles and acceptance conditions. It is a carried reconstruction plan, not an implemented generator for arbitrary operating systems. Preserving the ability to reason about the machine is a different achievement from claiming today's file runs everywhere.

## Reading and using the object

Start with the [opening office protocol](../Maintained%20Tools/configuration.nix#L28-L161), then the Foundation boundary, then the transaction implementation. The marked regions are `00.00` for constitution and office, `10.00` for the Foundation system, and `90.00` for the control plane. Read the observation contract alongside the transaction, because a successful build and a well-behaved computer are different findings.

The [portability ladder](../Maintained%20Tools/configuration.nix#L307-L360) distinguishes readable source, executable entry, source inspection, runtime observation and actual transactions. The direct entrance requires Linux, a trusted Bash 4-or-newer interpreter, compatible `sed` and the described launcher support. Bootstrap remains plan-only. A machine adapter and an appropriate NixOS environment are needed for system trials; the Foundation is not a configuration to switch blindly onto an existing host.

Where [qomrade](qomrade.md) sustains turns of work, and [Sandcodex](Sandcodex.md) or [Sandpi](Sandpi.md) provide distinct working environments, Monsternix makes the system under development carry an inspectable account of change and acceptance. These are related concerns, not one mandatory stack. Its particular contribution is to join configuration, empirical observation, succession and exit in the same portable object.

[Supplied-source identity and review scope](review/Monsternix-2026-10-20.md). Original source notices and component terms remain applicable.

[Maintained Tools](../Maintained%20Tools/README.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
