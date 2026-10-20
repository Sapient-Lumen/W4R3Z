# Maintained Tools

Choose where the work should happen: a Linux project environment, a persistent virtual machine, a continuing ChatGPT conversation, connected devices, recoverable remote access, or a NixOS system under revision. Each tool provides a different way to organize that work.

- **Code with Codex on Linux:** Sandcodex.
- **Run the Pi coding agent in its own persistent VM:** Sandpi.
- **Keep ChatGPT working on a project over successive rounds:** qomrade.
- **Recover remote access and share adaptive Tor/I2P transport:** AnonSSH.
- **Connect your devices for commands and folder sync:** IoTox.
- **Develop a NixOS system with carried reasons, measurements and exact acceptance:** Monsternix.

These are different tools, not parts you must install together. The single-file launchers and userscript are linked below; IoTox is a source tree. Nothing on this page is an installation instruction.

## Three different ways to sustain agent work

**qomrade keeps the conversation moving.** It supplies repeated opportunities for ChatGPT to continue an established project. The instruction can remain stable while the sources, argument, code and next useful action change. Its browser controller governs sending and recovery; it does not supply the project's execution environment. The [full explanation](../guides/qomrade.md) also opens its own source-carrying development workshop.

**Sandcodex supplies a capable project environment.** Codex can build, use a browser and operate native applications inside a selected Linux project boundary. Sequential loops continue one session lineage; campaigns stage separate Git work for explicit collection and review. The [Sandcodex guide](../guides/Sandcodex.md) explains why project authority, frontend credentials, human desktop input and worker adoption must remain distinct.

**Sandpi supplies a persistent machine for Pi.** A named NixOS VM retains packages and agent state, while Pi owns its conversation tree and the host project remains a live writable share. These are three different kinds of persistence: restoring the guest disk does not roll back the shared project. The [Sandpi guide](../guides/Sandpi.md) follows that distinction through project identity, package reuse, terminal/RPC entry and native settlement loops.

Choose by the work and the boundary it needs, not by treating “autonomy” as one interchangeable feature. More turns, a useful development room and a persistent machine can each matter, but they solve different problems. A portable launcher is also different from a backup of its live state.

## AnonSSH

Recover a prepared machine’s overlay addresses and SSH trust from an identity password and exact machine ID, then carry independent application streams over an adaptive Tor/I2P bond. A resident broker reuses expensive router infrastructure; ordinary SSH tools and a native local socket interface give different applications access to the transport. The portable Linux executable carries its router and SSH stack, while the separate Monsternix package uses the system’s Nix closure.

- [Read the AnonSSH introduction](AnonSSH/README.md)
- [Portable executable and source downloads](https://github.com/Sapient-Lumen/W4R3Z/releases/tag/anonssh-v0.2.0-9831b007cd47)
- [Project source](AnonSSH/source/) · [Release materials](AnonSSH/RELEASE.md)

## IoTox

Operate self-owned devices over Tox through durable typed commands, working-folder synchronization and host-selected terminals. Stable identity and signed authority sit above peer reachability; local policy controls the effect. Its sync records local edits against the history actually installed in the working directory, not unseen remote branches already downloaded by the daemon. The supplied security policy excludes protection of production devices or secrets; the fuller explanation keeps that boundary alongside the implemented design.

- [Introduction and provenance](IoTox/W4R3Z.md)
- [Project files and documentation](IoTox/)

## Monsternix

Make the system itself a continuing, inspectable project for human and AI collaborators. One carried configuration joins source, reasons, bounded observations and a transaction that promotes the exact tested system rather than rebuilding changed editor text. The accepted predecessor supplies an audit floor; the candidate adds checks for its newer format. The portable Foundation requires a machine adapter, and temporary activation runs reviewed code as root. The guide explains its recovery boundaries, source-level exits and separately gated experimental facilities.

- [Read the Monsternix introduction](../guides/Monsternix.md)
- [Current supplied configuration.nix](configuration.nix)
- [3 October 2026 source-update receipt](../updates/2026-10-03.json)

## Sandcodex

Give Codex a selected Linux project directory, build tools, and browser/desktop access for hands-on coding. For Linux users working on repositories with an agent. It shares the host kernel; it is not a VM.

- [Read the Sandcodex introduction](../guides/Sandcodex.md)
- [Current supplied sandcodex file](sandcodex)
- [20 October 2026 source-update receipt](../updates/2026-10-20.json)

## Sandpi

Run the Pi coding agent in a NixOS virtual machine whose disk persists between sessions. For Linux users with Nix and KVM who want an agent in its own OS environment. Pi means the coding agent, not Raspberry Pi; shared project files remain writable.

- [Read the Sandpi introduction](../guides/Sandpi.md)
- [Current supplied sandpi file](sandpi)
- [20 October 2026 source-update receipt](../updates/2026-10-20.json)

## qomrade

Requires a userscript manager. Each tab remains independently controlled; background work, recovery and generated-file collection follow the operator settings and the supplied runtime contract.

- [Read the qomrade introduction](../guides/qomrade.md)
- [Current supplied qomrade.user.js](qomrade.user.js)
- [20 October 2026 source-update receipt](../updates/2026-10-20.json)

## What “current” means here

It means the current supplied copy in W4R3Z, not automatic tracking of every upstream release. Exact supplied-file identities and update notes are retained in the [3 October](../updates/2026-10-03.json) and [20 October](../updates/2026-10-20.json) receipts and Git history. IoTox retains its own provenance record. The individual introductions lead to source, operating requirements, notices and subordinate review records.

Projects maintained by **h0p3**; editorial introductions by **Lumen**. Original attribution and notices remain with each source.

[Whole catalog](../CATALOG.md) · [The prose library](../OG%20510P/README.md) · [W4R3Z](../README.md)


