# Sandpi

## Give a coding agent a machine it can return to

Sandpi puts the Pi coding agent inside an agent-owned, persistent NixOS virtual machine. The agent can install packages, keep its working environment, run tools and return to native Pi sessions without treating every invocation as a fresh disposable shell. The selected host project remains available as a live working directory.

The important unit is the **room**: a named machine associated with a project, with its own disk, Pi state, installed packages and saved resource profile. Sandpi supplies that machine and its host-side lifecycle; Pi supplies the conversation, model selection, tools, session tree and interactive experience. “Pi” names the coding agent, not Raspberry Pi hardware.

[Read the supplied Sandpi 0.86.0 / rev0086, Orbit](../Maintained%20Tools/sandpi). Its single distributed file contains readable source, documentation and tests; the embedded README's [Start here section](../Maintained%20Tools/sandpi#L4714-L4791) provides the operator entrance.

## Three kinds of continuity, not one

A project can outlast a terminal session in several different senses. Sandpi keeps those senses separate.

**The machine persists.** The first launch builds missing pinned dependencies, creates the room's sparse root disk and starts the guest. Later launches reuse the disk and Nix closures. A room can be stopped and entered again with its installed software and Pi state intact. Several named rooms can hold different machine environments for the same project.

**Pi owns the conversation.** Native commands such as `/resume`, `/tree`, `/fork`, `/model` and `/compact` operate on Pi's own session history. Sandpi does not translate the conversation into another agent protocol or maintain a competing transcript database. Its host observation index is deliberately transcript-free. A narrow preflight for deterministic continuation asks Pi which session branch it will actually select, so startup policy can preserve the relevant model and settings instead of silently substituting another.

**The project stays live.** `/workspace` is a writable virtiofs share of the selected host project, not a disposable copy. Edits and deletions reach the host directory immediately. Different rooms for that project therefore have different private disks but can still touch the same project files.

This matters when experimenting. Moving backward through Pi's conversation tree does not move the filesystem backward. Restoring a stopped-room checkpoint restores the guest disk, including its sessions and packages, but does not undo changes to the shared project. Use the appropriate project versioning or backup for that separate state. The [session and workspace account](../Maintained%20Tools/sandpi#L4905-L4955) makes this distinction explicit.

## A room is attached to a project, not just its current pathname

Sandpi gives the host project a small identity anchor and combines that namespace with the room name. Renaming a directory need not abandon its machine. Host-side bindings also track the directory's filesystem identity, distinguishing an ordinary same-filesystem move from a copied checkout or a replacement placed at the old path.

That distinction has a practical consequence: a live virtiofs share still refers to the original directory object. A new directory at the same pathname is not necessarily what the guest has mounted. Sandpi requires an explicit recovery, rebind or new-project decision when identity becomes ambiguous rather than quietly attaching the old machine to an unrelated replacement.

The project root and the entry working directory are separate, too. A developer entering from a subdirectory can use the same room and whole-project share while Pi starts in that particular subdirectory. This preserves Pi's own context discovery and session grouping. The [architecture's project-identity section](../Maintained%20Tools/sandpi#L5365-L5480) explains the binding and recovery rules.

## Make a capable machine without duplicating everything

The VM boots a pinned Linux kernel and NixOS environment through Cloud Hypervisor. The host supervises the VM and its file-sharing and networking backends as one systemd user-service group. Resource accounting includes those host-side processes, not merely the RAM visible inside the guest.

The default room reserves approximately half the effective host CPU and memory capacity; an aggregate per-user pool prevents multiple rooms from each assuming the same memory is free. The guest receives the budget minus backend overhead. Machine settings are saved with the room, so returning to a project does not silently choose a new machine profile. The default disk is a sparse 100 GiB capacity, not an immediate allocation of 100 GiB of written data. See the [resource profile](../Maintained%20Tools/sandpi#L4987-L5037).

Nix reuse addresses a different kind of duplication. A read-only view of the host store forms the lower layer; a persistent guest overlay supplies writable store state. Exact leased paths are registered in the guest's Nix database, with retention roots on both sides. Later launches can verify retained registration segments instead of reconstructing the entire dependency graph each time. Packages installed in the guest remain room-local; sharing the host store does not merge every room's mutable package state.

This is a substantial design choice: reuse immutable dependencies while keeping the agent's evolving machine separate. The [files and caching account](../Maintained%20Tools/sandpi#L5039-L5105) also explains the resulting storage-retention obligations.

## Let Pi remain Pi

Inside the room, ordinary Pi packages, extensions, MCP helpers and their dependencies run in the guest and persist with it. Sandpi's supplied core extension adds the credential-provider integration, model and profile policies, and a few commands without taking ownership of the whole conversation engine. Updating ordinary extensions remains native Pi behavior; replacing the pinned Pi executable is handled by upgrading Sandpi.

The terminal remains a first-class interface. Regular TUI mode lets the caller's terminal own scrollback and highlighted-text copying across the VM transport. Print, JSON and RPC use a separate non-PTY path, keep diagnostics on stderr and preserve actual piped input. In headless work, entering an already-running room and booting a stopped room have different lifecycle consequences: completion exits only the new Pi process in the former case, while the latter stops the room it started.

Those differences make Sandpi useful both for an ongoing interactive project and for a bounded call from an existing command-line workflow. The [native packages and programmatic interface](../Maintained%20Tools/sandpi#L4852-L4903) describe these paths.

## Orbit: several useful passes inside one native conversation

The supplied revision adds `/loop`: five complete Pi agent settlements by default, or an explicit count from one to one hundred. A settlement can contain multiple provider requests, tool operations, retries and compaction. Counting settlements therefore counts continuation opportunities, not individual requests or spending.

The continuation is inserted at Pi's `agent_before_settle` boundary. It repeats the objective, asks the agent to reconcile earlier claims with durable state, and directs already-satisfied work toward review, testing or simplification rather than unnecessary changes. The model, thinking level, tool policy, payment permission and provider behavior remain those of the current conversation.

Stopping the loop prevents its next pass while allowing the current one to settle; Escape or an agent error closes it. Session movement and process exit retire its process-local authority. A surviving running marker is reported as interrupted on a later process, not used to restart inference automatically. These mechanics make the loop a bounded continuation primitive, not a second agent engine or a judge that the objective succeeded. [Read the loop contract](../Maintained%20Tools/sandpi#L16135-L16225).

## Choose the boundary deliberately

Sandpi and [Sandcodex](Sandcodex.md) offer different working environments. Sandpi normally gives Pi its own guest kernel and persistent machine. Sandcodex uses Codex in an environment sharing the host kernel. Neither name should replace reading what is actually shared and authorized.

In ordinary Sandpi VM mode, Pi runs as guest root. It can change its guest environment, write the shared project and use the available provider credentials. The credential broker retains canonical refresh state on the host, but access tokens and API keys supplied to Pi are available to guest root. Sandpi does not impose a guest network filter or a room-wide spending firewall. Inbound port publication is explicit and saved as a machine setting.

When sharing Codex OAuth credentials with the supplied Sandcodex, avoid overlapping refresh windows. Sandpi documents a reconciliation race, and the current [Sandcodex reconciliation path](../Maintained%20Tools/sandcodex#L23899-L23928) can promote a frontend copy without checking that its original canonical generation is still current. This matters for the combined setup, not every use of either tool; the [inspection record](review/Sandpi-2026-10-20.md) retains the source-level finding.

The separate uppercase `--BARE-METAL` mode means actual host-root execution, not a stronger name for the VM. It is an explicit mode, never a fallback after VM failure.

The documented host is Linux on x86-64 or ARM64, with existing Nix, KVM, cgroup v2, a systemd user session, systemd-run 254+ and unprivileged user/mount namespaces. The launcher provisions pinned dependencies through Nix; it cannot manufacture missing kernel capabilities. KVM access repair can request sudo. Read the [host requirements](../Maintained%20Tools/sandpi#L4957-L4985) and [credentials, checkpoints and networking](../Maintained%20Tools/sandpi#L5150-L5249) before choosing a configuration.

## A portable launcher, with its construction materials

The distributed Bash file carries the integration's Python, TypeScript, Nix, documentation and tests as literal data. Its bootstrap verifies the extracted manifest; its build tooling regenerates the complete file from those sources. That makes the launcher inspectable and maintainable as a delivered object.

The carried source is not the whole running machine: Nix supplies dependencies, while project data, room disks and credentials remain separate. This distinction lets the launcher travel without confusing program distribution with machine backup or credential transfer.

The original integration carries an MIT license and credits **sandpi contributors**; upstream dependencies and supplied reference material retain their own notices. [Source receipt](../updates/2026-10-20.json) · [Supplied-source inspection record](review/Sandpi-2026-10-20.md).

[Maintained Tools](../Maintained%20Tools/README.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
