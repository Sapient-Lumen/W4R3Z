# Maintained Tools

Choose where the work should happen: a Linux project environment, a persistent virtual machine, a continuing ChatGPT conversation, connected devices, recoverable remote access, or a NixOS system under revision. Each tool provides a different way to organize that work.

- **Build a local edition of shared forum conversation:** [0opschan](#0opschan).
- **Carry a project, its source and a native continuation interface:** [Datacube](#datacube).
- **Code with Codex on Linux:** [Sandcodex](#sandcodex).
- **Run the Pi coding agent in its own persistent VM:** [Sandpi](#sandpi).
- **Keep ChatGPT working on a project over successive rounds:** [qomrade](#qomrade).
- **Recover remote access and share adaptive Tor/I2P transport:** [AnonSSH](#anonssh).
- **Connect your devices for commands and folder sync:** [IoTox](#iotox).
- **Operate a CityB network:** [CityB](#cityb).
- **Develop a NixOS system with carried reasons, measurements and exact acceptance:** [Monsternix](#monsternix).

These are different tools, not parts you must install together. The single-file launchers and userscript are linked below; IoTox is distributed as a single executable carrying its source and other materials. Nothing on this page is an installation instruction.

“Maintained” names a continuing responsibility to address breakage in usable software. It is not a ranking of visual polish, a claim that every operating environment is supported, or a guarantee that a supplied revision is free of defects. The individual guide and source define the tool's actual requirements. [Foundry](../Foundry/README.md) offers developing works with materials for continuation; a coherent argument or useful prototype does not need to cross into this shelf to justify its place in the collection.

## Three different ways to sustain agent work

**qomrade keeps the conversation moving.** It supplies repeated opportunities for ChatGPT to continue an established project. The instruction can remain stable while the sources, argument, code and next useful action change. Its browser controller governs sending and recovery; it does not supply the project's execution environment. The [full explanation](../guides/qomrade.md) also opens its own source-carrying development workshop.

**Sandcodex supplies a capable project environment.** Codex can build, use a browser and operate native applications inside a selected Linux project boundary. Sequential loops continue one session lineage; campaigns stage separate Git work for explicit collection and review. The [Sandcodex guide](../guides/Sandcodex.md) explains why project authority, frontend credentials, human desktop input and worker adoption must remain distinct.

**Sandpi supplies a persistent machine for Pi.** A named NixOS VM retains packages and agent state, while Pi owns its conversation tree and the host project remains a live writable share. These are three different kinds of persistence: restoring the guest disk does not roll back the shared project. The [Sandpi guide](../guides/Sandpi.md) follows that distinction through project identity, package reuse, terminal/RPC entry and native settlement loops.

Choose by the work and the boundary it needs, not by treating “autonomy” as one interchangeable feature. More turns, a useful development room and a persistent machine can each matter, but they solve different problems. A portable launcher is also different from a backup of its live state.

## 0opschan

Make a local-first forum edition from signed sources and curators while keeping trust, synchronization, custody and local selection separate. The supplied Linux x86-64 Datacube carries the forum core, its source and the wider project. It is checksum-identified, not publisher-authenticated; the [guide](../guides/0opschan.md) explains the distinction and how to inspect the carrier.

- [Read the 0opschan introduction](../guides/0opschan.md)
- [Download the single 0opschan foundation executable](0opschan)

## Datacube

Carry a documentary project and its native C++ source together in a compact Linux executable, with a readable bootstrap entrance beside it. The carried contract separates inspecting the current object, recovering its materials, reviewing exact changes and constructing a descendant. A continuation can develop the work rather than merely replay its predecessor. Historical checkpoint routes remain distinct from the current native interface and can require a separately acquired archive.

- [Read the Datacube guide](../guides/Datacube.md)
- [Read BOOTSTRAPROSE.md](Datacube/BOOTSTRAPROSE.md)
- [Supplied Linux x86-64 executable](Datacube/datacube)

Keep exactly `BOOTSTRAPROSE.md` and lowercase `datacube` together in their own directory. The supplied linked-pair contract expects both files to be regular, non-symlink files with mode `0555`; Git tracks executable status but does not preserve those exact read-only permissions. After downloading or checking out the pair, set those two files to `0555` before using the linked interface. Do not rename the executable to match the capitalized shelf title. The supplied bytes are unchanged; the interface account above comes from the carried contract, not a new execution test.

## AnonSSH

Recover a prepared machine’s overlay addresses and SSH trust from an identity password and exact machine ID, then carry independent application streams over an adaptive Tor/I2P bond. A resident broker reuses expensive router infrastructure; ordinary SSH tools and a native local socket interface give different applications access to the transport. The portable Linux executable carries its router and SSH stack, while the separate Monsternix package uses the system’s Nix closure.

- [Read the AnonSSH introduction](AnonSSH/README.md)
- [Portable executable and source downloads](AnonSSH/RELEASE.md)
- [Project source](AnonSSH/source/) · [Release materials](AnonSSH/RELEASE.md)

## IoTox

IoTox connects devices through a single-file Linux Datacube carrying its source and other project materials. The maintained download is the supplied v0.52.0 executable; the earlier repository remains recoverable in Git history.

- [Download IoTox v0.52.0](IoTox/iotox-v0.52.0-x86_64-linux-17cca7b22e64)
- [IoTox SHA-256 checksums](IoTox/IoTox-v0.52.0-SHA256SUMS)
- [IoTox entry](IoTox/README.md)

## CityB

CityB's operator kit brings together an operator workbench, field node and development tool with their source, documentation and fixtures. The supplied Linux x86-64 kit is unsigned; its checksums establish byte integrity, not publisher authentication. This maintained product is distinct from the vaulted CityB of ChatGPT artwork.

- [CityB entry](CityB/README.md)
- [Download the operator kit](CityB/CityB-operator-kit-0.1.0-x86_64-linux-unsigned-revised.zip)

## Monsternix

Make the system itself a continuing, inspectable project for human and AI collaborators. One carried configuration joins source, reasons, bounded observations and a transaction that promotes the exact tested system rather than rebuilding changed editor text. The accepted predecessor supplies an audit floor; the candidate adds checks for its newer format. The portable Foundation requires a machine adapter, and temporary activation runs reviewed code as root. The guide explains its recovery boundaries, source-level exits and separately gated experimental facilities.

- [Read the Monsternix introduction](../guides/Monsternix.md)
- [Portable Foundation configuration.nix](configuration.nix)
- [Machine-specific m16-configuration.nix](m16-configuration.nix) · [Read the m16 account](../guides/Monsternix-m16.md)
- [23 October m16 publication receipt](../updates/2026-10-23-m16.json)
- [23 October 2026 source-update receipt](../updates/2026-10-23-monsternix.json)

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

It means the current supplied copy in W4R3Z, not automatic tracking of every upstream release. Exact supplied-file identities and update notes are retained in the [3 October](../updates/2026-10-03.json), [20 October](../updates/2026-10-20.json) and [23 October Monsternix](../updates/2026-10-23-monsternix.json) receipts and Git history. IoTox and CityB release entries record their supplied artifacts. The individual introductions lead to source, operating requirements, notices and subordinate review records.

Projects maintained by **h0p3**; editorial introductions by **Lumen**. Original attribution and notices remain with each source.

[Whole catalog](../CATALOG.md) · [The prose library](../OG%20510P/README.md) · [W4R3Z](../README.md)
