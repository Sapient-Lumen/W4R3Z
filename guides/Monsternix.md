# Monsternix

## A computer that carries the reasons for its own changes

Monsternix makes a NixOS machine into a continuing, inspectable project that a succession of human and AI collaborators can work on. Its single [configuration.nix](../Maintained%20Tools/configuration.nix) carries system declarations, an executable operator interface, a collaboration protocol, and the machinery for connecting a proposed change to the exact system that was built, tried and accepted. The aim is not merely to reproduce a package selection. It is to keep the computer understandable and governable as its configuration, circumstances and collaborators change.

A useful example is a service change proposed during one model session and reconsidered in another. The successor should receive more than a plausible patch and “the tests passed.” It needs the complete candidate, the reason for the change, the system on which it was tried, the failures that mattered, and the decision still owed by the operator. Monsternix organizes that handoff around the machine itself rather than relying on an uninterrupted chat or a particular model's memory.

The supplied object is the **portable Foundation module**, not a universal ready-to-boot configuration. Hardware, storage, console access, hostname and clock policy belong to an explicit machine adapter. Its [portable-seed declaration](../Maintained%20Tools/configuration.nix#L85-L97) distinguishes this reusable module from an inhabited machine whose local facts and purposes are known. A mechanism learned on one machine can travel without exporting that machine's private or hardware-specific decisions as everybody else's defaults.

The separately supplied [m16 edition](Monsternix-m16.md) shows Monsternix around a particular machine and its ongoing obligations. It is retained as [m16-configuration.nix](../Maintained%20Tools/m16-configuration.nix); it does not replace the portable Foundation linked above.

## An inhabited source, not an imitation of memory

The [opening](../Maintained%20Tools/configuration.nix#L23-L156) treats a home computer as a place where work, habits, experiments and unfinished intentions accumulate. Its collaboration protocol is meant to preserve that specificity without requiring the next worker to imitate the previous one's voice. A successor can question the design, change an explanation or propose a simpler mechanism. Continuity means carrying enough to make those decisions intelligible, not making a predecessor's language untouchable.

The supplied file deliberately begins as a **portable seed**. Its bounded “Inhabited Source” card names the difference: the adopter's machine facts, purposes, treasured data and present request are still unknown. A welcoming introduction does not fill those gaps. This gives a recipient somewhere to begin without supplying a fictitious biography or pretending the reference module is already their functioning computer.

The [passage model](../Maintained%20Tools/configuration.nix#L158-L211) then distinguishes a durable source from one encounter with it:

- **Current request:** what the person is asking now, separate from inherited plans.
- **Warm attention:** the selected source and evidence needed for this particular piece of work.
- **Cold estate:** the larger recoverable body of source and evidence, precisely addressable without all of it occupying the present conversation.
- **Worker return:** changes, reasoning, observations, disagreements and unknowns attributed to their author.
- **Disposition:** a recommendation, hold, rejection or question, not automatic acceptance or activation.

This is a practical answer to limited context. Consider a successor investigating a troublesome service change. It should not need to reread every past session merely to begin; it does need the present request, exact source identity, relevant evidence, last disposition and unresolved question. The rest can remain available for a deeper inquiry. A smaller active reading should not require throwing the history away, and possessing the history should not be mistaken for having read it.

The same distinction matters when work is interrupted. A queued instruction is not necessarily received, an available response is not necessarily reviewed, and an uncertain external effect should not simply be repeated. The protocol makes room for an unfinished encounter to remain honestly unfinished.

## Where the neighboring projects meet

Monsternix belongs in **Maintained Tools**: h0p3 describes it as usable software with a responsibility to fix breakage for its users. Its experimental breadth and connections to the Foundry do not change that maintenance commitment.

The source describes several ways to carry an encounter: the complete raw file, a Cloudtainer with an exact repository and selected reading material, and a Sandwurm/GlassTTY environment with continuing browser/provider custody. Those are different carriers of work, not interchangeable definitions of the collaboration itself. A stronger carrier does not become the author or gain authority to accept its own result.

There are also explicit [optional integration inputs](../Maintained%20Tools/configuration.nix#L830-L844) for Sandwurm, AnonSSH and IoTox. This makes Monsternix a potential meeting place for independently useful projects: communication, remote access, portable construction and the evolving machine can participate in one continuing practice. It does not mean every Foundry object is already integrated, every named capability is enabled, or the projects must be adopted together. Further convergence is a direction for development, not a completed universal stack.

What makes that direction interesting is the combination of hospitality and exit. The source invites a machine to acquire its own voice and habits with its people, while preserving ways to remove or reduce the framework. Its phrase “Adoption is not captivity” expresses the ambition well: the work should remain understandable and usable even when its collaborators or supporting machinery change.

## One file, several precise readings

The file is deliberately more than its suffix suggests. Nix reads it as a system module. Its first line gives it a Bash entrance. Humans can read its constitution and incident memory. Stable source markers let a collaborator locate definitions, ownership boundaries and unresolved questions. Installed generations carry the complete source that identifies them.

These are not competing versions of the project. They are different readings of one carried object. Generated helpers may use other languages, provided their source, rendered bytes and installed projections remain inspectable. The goal is one accountable source and transaction protocol, not a demand that all programming be done in Bash. The [polyglot design](../Maintained%20Tools/configuration.nix#L436-L498) makes the imperative work behind a declarative system visible: building, activating, observing, choosing a boot default and recovering from failure are operations, not consequences that a declaration can prove by itself.

That arrangement gives the full-file handoff practical force. A recipient receives the surrounding constraints and navigation as well as the requested edit. Derived maps and working fragments can help construction, but they must converge back into the complete candidate rather than quietly becoming another source of authority.

## Changing the machine without changing what “passed” means

The central distinction is between a candidate and an accepted system. Monsternix separates temporary trial from permanent selection, and separates the predecessor's judgment from the candidate's account of itself.

Its [test transaction](../Maintained%20Tools/configuration.nix#L15565-L15846) does the following:

1. Checks candidate lineage and source structure, takes the transaction lock, and freezes the exact candidate into a private, single-file input. It does not scoop up the surrounding directory, untracked work or credentials.
2. Records both the currently running system and the boot default. These can be different: a successful temporary trial need not yet be the system selected for the next boot.
3. Uses the machine's activation hook or the NixOS test path to realize and temporarily activate the candidate. It checks the resulting closure identity, unchanged boot default and correspondence between the candidate and the complete source carried by the running generation.
4. Applies the accepted predecessor's audit as a floor, then the candidate's format-aware audit as an additional ceiling. Machine-specific postflight and behavior checks have their own dispositions.
5. Retains a receipt for this exact trial. A passing temporary system can remain running for review before promotion.

The two judges answer a genuine evolution problem. Letting a candidate supply its only judge would allow it to redefine success to suit itself. Letting an old judge permanently define every future format would prevent the protocol from growing. The predecessor floor and candidate ceiling keep continuity and extensibility in tension instead of choosing one and forgetting the other.

[Promotion](../Maintained%20Tools/configuration.nix#L16208-L16393) then checks the receipt, exact source identity, current running closure and health before setting the system profile to the already-tested closure. It does not rebuild whatever text happens to be in the editor now. Temporary instrumentation must be removed before permanent promotion; removing it changes the candidate and therefore requires a new trial. This is an operational meaning of “accept that change,” not merely a label attached to a conversation.

The [source-recorded history](../Maintained%20Tools/configuration.nix#L662-L669) explains why exact source attachment is more than bookkeeping: an early observer found a guest closure carrying unrelated machine source selected by generic NixOS copying. A build can succeed while its account of what built it is wrong. The source/closure check makes that discrepancy a transaction failure rather than leaving it for the next collaborator to discover.

The boundary is important and specific: **temporary activation runs reviewed candidate code as root**. The protocol guards judgment and promotion; it is not a sandbox for hostile candidates. Recovery also distinguishes reselecting a prior closure, reapplying activation and establishing restoration. Its [recovery witness](../Maintained%20Tools/configuration.nix#L14925-L14958) explicitly does not promise rollback of arbitrary mutable application state or qualified durable crash recovery. A service's database migration does not become reversible just because its old executable remains available.

## Evidence that another collaborator can actually use

Monsternix treats observability as part of the computer, not an accessory dashboard. The [observation contract](../Maintained%20Tools/configuration.nix#L590-L698) and [collector implementation](../Maintained%20Tools/configuration.nix#L11228-L11638) relate source and closure identities to running services, failed-unit results, listeners, timers, bounded journals, coredumps, resource pressure and transaction state. It can retain private evidence bundles and produce compact summaries without raw logs, with bounded, control-safe diagnostic excerpts when needed. Raw evidence remains private; the credential filter is fallible, so even a diagnostic excerpt needs review before sharing. Machine-specific observers extend that account through declared interfaces.

Several distinctions make these measurements more useful than a single reassuring status:

- The observer's health and the observed system's health are separate. A collector can fail while its subject is healthy, or work correctly while reporting a damaged system.
- Missing, inapplicable, deferred and failed observations are not interchangeable. An old successful observation is history, not a fresh answer.
- A selected measurement baseline is a comparison point, not acceptance of a candidate or permission to expose a service.
- Seeing a listener does not authorize it. A record of what exists and a decision about what ought to exist have different jobs.

The [sensory-organ contract](../Maintained%20Tools/configuration.nix#L6428-L6516) gives that separation a concrete interface: readings carry bounded codes, while their explanatory text and action meanings come from the source-owned registry. A critical reading does not acquire permission to notify, remediate or promote a system.

The compact `mnx brief` interface combines source checks and current bounded observations into a handoff. Its [next-action selection](../Maintained%20Tools/configuration.nix#L12191-L12206) prioritizes matters such as an active transaction, source/closure mismatch, failed units and missing observations before suggesting review of a temporary system. The operator supplies the actual purpose; the report does not invent one.

This is also a way to make collaboration work with limited attention. The source distinguishes present requests, inherited intent, measured facts, inferences, proposals and unknowns. Keeping those categories legible prevents a successor from promoting an old suggestion into present permission or a confident explanation into a measurement. Brief summaries point back to bounded evidence rather than requiring the next reader to trust the previous reader's fluency.

## A foundation that can be adapted, reduced or left

Monsternix does not make preservation of all its machinery a condition of continuity. Source ownership supports [ejection profiles](../Maintained%20Tools/configuration.nix#L14054-L14110), including plain-NixOS and Foundation-oriented outputs. The directions differ: `plain-equivalent` strips the framework while retaining explicitly owned ordinary machine declarations; `foundation` keeps portable mechanisms and experimental definitions while removing machine policy and optional flavor; `foundation-core` removes the experimental definitions too. The [ownership contract](../Maintained%20Tools/configuration.nix#L7013-L7196) makes those dispositions explicit. These are source transformations, not activation commands or proof that the resulting machine behaves equivalently. The point is that adopting the project's discipline should not make the operator dependent on keeping its entire framework forever.

Optional mechanisms are similarly distinguished from universal requirements. The source calls this **semipermanent flavor**: carried machinery with a named gate, absent-capability behavior, evidence surface and ejection disposition. It can remain useful across many revisions without becoming mandatory or immortal. Experimental vault and encrypted keystroke-journal facilities belong in this category. Their presence is not enrollment or consent to capture input; their explicit activation and privacy boundaries matter to their use.

The longer horizon is independence from the current substrate. Nix and NixOS presently supply immutable artifacts, dependency closures and system selection. Monsternix's [reconstruction curriculum](../Maintained%20Tools/configuration.nix#L738-L766) asks what a successor would have to preserve or replace if that substrate changed: meanings, source witnesses, adapter roles and acceptance conditions. It is a carried reconstruction plan, not an implemented generator for arbitrary operating systems. Preserving the ability to reason about the machine is a different achievement from claiming today's file runs everywhere.

## Reading and using the object

Start with the [opening office protocol](../Maintained%20Tools/configuration.nix#L23-L343), then the Foundation boundary, then the transaction implementation. The marked regions are `00.00` for constitution and office, `10.00` for the Foundation system, and `90.00` for the control plane. Read the observation contract alongside the transaction, because a successful build and a well-behaved computer are different findings.

The [portability ladder](../Maintained%20Tools/configuration.nix#L507-L560) distinguishes readable source, executable entry, source inspection, runtime observation and actual transactions. The direct entrance requires Linux, a trusted Bash 4-or-newer interpreter, compatible `sed` and the described launcher support. Bootstrap remains plan-only. A machine adapter and an appropriate NixOS environment are needed for system trials; the Foundation is not a configuration to switch blindly onto an existing host.

Where [qomrade](qomrade.md) sustains turns of work, and [Sandcodex](Sandcodex.md) or [Sandpi](Sandpi.md) provide distinct working environments, Monsternix makes the system under development carry an inspectable account of change and acceptance. These are related concerns, not one mandatory stack. Its particular contribution is to join configuration, empirical observation, succession and exit in the same portable object.

[23 October supplied-source identity and publication scope](../updates/2026-10-23-monsternix.json) · [Earlier source-reading record](review/Monsternix-2026-10-20.md). Original source notices and component terms remain applicable.

[Maintained Tools](../Maintained%20Tools/README.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
