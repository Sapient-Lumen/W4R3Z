# IoTox

**IoTox 0.51.0 / rev0051:** [Download the supplied Linux binary](https://github.com/Sapient-Lumen/W4R3Z/releases/download/iotox-v0.51.0-6123947650d1/iotox) · [Binary, matching source inputs and notices](https://github.com/Sapient-Lumen/W4R3Z/releases/download/iotox-v0.51.0-6123947650d1/IoTox-0.51.0-6123947650d1-standalone.zip) · [Release and checksums](https://github.com/Sapient-Lumen/W4R3Z/releases/tag/iotox-v0.51.0-6123947650d1)

This exact x86-64 build is source-linked but not fully static: it retains a Nix glibc 2.40 interpreter path and needs a compatible runtime. The release records its build details; original executable bytes are unchanged.

## Keep useful control of your devices without making an account service their owner

IoTox connects machines over Tox and gives their owner a common way to operate them: exchange text and files, submit durable typed commands, synchronize working directories, and reach an explicitly approved interactive terminal. It is a C++20 device agent designed around ordinary Unix interfaces rather than a vendor-controlled device account. Its deeper project is to make ownership, permission and the record of what happened survive changes of route, disconnected peers and interrupted work.

The practical distinction is simple: **being able to reach a machine is not the same as being allowed to change it**. Tox supplies the peer connection. IoTox places stable device identities, signed authority and operation-specific checks above that connection. Local policy then determines what an authorized request may actually do. This lets a device be reachable without treating every friend, transferred file or plausible request as an administrator.

The supplied [security policy](SECURITY.md) calls IoTox pre-release security-sensitive software and says it is not yet suitable for protecting production devices or secrets. That material usage constraint remains in force alongside its substantial implemented machinery and scope-bound readiness evidence.

## Recover ownership, not a vendor password

IoTox separates the owner's identity from a device's application identity and from its replaceable Tox route keys. The [RecallRoot design](docs/recovery-and-ownership.md) reconstructs owner root material from a strongly generated phrase under a fixed public derivation contract. A local client can use that material to sign an exact authority record or session proof without sending the phrase or owner secret to the daemon or remote peer. Narrower delegated credentials are intended for ordinary use.

This changes what recovery means. The important object is not a password that persuades a service to reset somebody's account. It is owner-controlled signing authority that the device can evaluate locally. The project's design excludes an IoTox-controlled master key that can reassign ownership. It also separates software-update signing from ownership transition: distributing a new program is not permission to become the device's owner.

The fixed derivation contract makes phrase strength load-bearing. It expects independently generated words, not a memorable sentence invented by the user. Nor does recovering a key magically locate every machine: the recovery document explicitly retains a gap around discovering current route bindings from memory alone. Recovering authority, finding a route and restoring lost data are different achievements.

The signed authority ledger makes delegation and revision explicit. For example, its format migrations preserve existing grants instead of silently widening them when terminal or synchronization capabilities become available. The [sync authorization implementation](src/sync_authorization.cpp) joins a proof against the exact current ledger head with the operation's capability, namespace membership and activation policy. “This is one of my peers” is not a substitute for those checks.

## Ordinary Unix interfaces, explicit internal state

The ratox inheritance is a productive design choice: a peer can be represented through directories, status files, event journals and bounded request FIFOs that shell tools can compose. IoTox preserves that accessible outside while refusing to treat bytes written into a FIFO as evidence of a completed remote effect.

The [command protocol](docs/protocol-command-v1.md) distinguishes several events that a superficial interface might collapse into “sent”: a request committed locally, acceptance into the transport queue, a receiver's durable receipt, authorization, execution start, a terminal result and delivery of that result. A command can be complete on the receiver while its result is still waiting to travel back.

That distinction matters during an outage. Retrying a request reuses its exact canonical bytes and durable identity rather than minting a fresh command merely because the connection was busy. The receiver can replay committed evidence for an exact duplicate. Cancellation is correspondingly narrow: the [store](src/command_store.cpp#L1436-L1478) permits outgoing cancellation only before the first committed attempt. After that boundary, lack of a result is not proof that nothing happened remotely.

The typed command surface is also not arbitrary shell execution. The [executor](src/command_engine.cpp) handles named operations such as device description, system summary, setting a bounded presence status and staging an exact update. Restart behavior belongs to each operation. Setting a desired status can reapply the same frozen value and read it back; staging can recognize an already-staged exact artifact. Neither licenses replay of an arbitrary physical action. Remote update staging leaves an inert inactive slot; applying, restarting and confirming an update remain separate authority crossings.

This is useful even before adding more operations. A machine that says “the effect is uncertain” retains a problem that can be resolved. A machine that turns an interrupted transport into an invented success or cancellation destroys that knowledge.

## Synchronization as an authorized working-copy relationship

IoTox's folder synchronization joins three things that are often hidden behind one “share” button: who may publish, which namespace they may affect, and where each recipient chooses to materialize the result. The remote side does not choose an arbitrary destination path on the receiving machine.

The project supports a sole-writer path and a bounded read-write tree path. In the sole-writer model, immutable content and its manifest are established before the signed publication head commits the revision. Receiving and accepting a revision are distinct from activating it into the local working directory. An unattended follow policy can automate permitted stages without making all received data immediately live.

The read-write path gives concurrent changes a representation rather than simply pretending one writer was last. Signed branches, causal history, preserved conflicting alternatives and later resolving edits let offline work rejoin the shared tree without silently erasing disagreement. Deletion and writer retirement also need durable semantics: a surviving device's operator can [pin a retired writer to an exact admitted record](src/sync_multiwriter_maintenance.cpp#L1205-L1359) instead of accepting its later work. The [sync guide](docs/replace-resilio-sync.md) leads to ordinary editing, conflict explanation, repair, freeze and recoverable-delete operations rather than making the user operate raw protocol records every day.

An especially important [implementation choice](src/sync_multiwriter_reconcile.cpp#L188-L414) distinguishes the revision installed in the working directory from newer remote branches that the daemon merely knows about. It scans local edits against the signed workspace's visible history and publishes those edits from that history before merging the newer stored branches. If another machine's edit has arrived but was not yet shown in this working copy, the local edit must not falsely claim to have seen and superseded it. Preserving concurrency requires remembering what was made visible, not just what packets arrived.

[Sparse custody](docs/sync-sparse-custody.md) further separates knowing about a namespace from holding every byte of it. A recipient can select local path-prefix coverage and later widen that selection or fetch content on demand. Selection belongs to the recipient; exclusion is not permission to destroy unrelated local files. A sparse node still verifies the required signed history, but a completed pull can mean complete work for its selected coverage, not possession of the whole tree.

The filesystem scope is deliberately concrete: private Linux regular files and directories, with a specific path and owner-mode model. Symlinks, ACLs, extended attributes, special files and case-folding portability are not interchangeable details that a synchronizer can silently discard. The source doctor exposes or refuses unsupported semantics before the operator mistakes a successful transfer for a faithful copy.

The result is a synchronized working-copy system, not a backup. Delete propagation, retained history and conflict preservation do not by themselves provide independent recovery custody. IoTox's restore comparison and rehearsal tools help test parts of recovery practice, but a matching restored tree does not prove that the backup was independent or that every future failure can be survived. That separation gives the sync layer an intelligible responsibility instead of promising ownership of the whole storage stack.

## A terminal selected by the host, not invented by the caller

[IoTox Ratox](docs/ratox-ssh-status.md) is its interactive terminal facility. A host-installed profile fixes the account, executable, arguments, working directory, environment, limits and confinement posture. The remote peer supplies terminal input, not a surprise executable or arbitrary startup command line. Binding a principal to a diagnostic program does not grant a shell; binding it to a real login shell permits the ordinary work that shell can perform.

The terminal has its own continuity model. A route loss can detach the controller while the Agent and remote PTY remain alive. Reconnection or explicit resume must identify that session under a newly authenticated application epoch, preserving the relevant replay positions rather than silently opening another shell. Daemon death is different: the current PTY does not survive merely because the route can reconnect.

Self mode selects the host and controller roles for owner machines, but does not create a shell profile, bind a principal, grant terminal capability or enable sudo. A sudo-capable profile is an explicit host-policy choice and still relies on the host's sudo/PAM rules. This is SSH-shaped control through Tox, not a promise of every SSH feature or a general port-forwarding service.

## One person can have several devices without copying one route identity everywhere

The [person layer](docs/person-multidevice.md) extends the same separation above transport. A private self-device roster, a public signed delivery card, a signed group descriptor and local message stores have different purposes. A person's delivery card can identify active device routes while daily messages use delegated device signatures. Retiring one device need not mean treating all the person's devices as one copied Tox key.

The normal-Tox compatibility bridge preserves another useful distinction. Its signed record says that a delegated device observed an ordinary Tox message; it does not pretend that the outside sender signed an IoTox person envelope. Keeping bridge observations separate from person/group transcripts retains what the available evidence actually supports while allowing ordinary Tox clients to participate at the edge.

## The project also carries its own handoff

The [repository Datacube formats](docs/conversation-datacubes.md) package an exact committed source state and cloneable Git bundle, with available same-commit distribution and selected evidence. Public seed, full-history and richer conversation profiles serve different recipients. The source and Git history remain the development authority; the package is a bounded handoff, not a second hidden master copy.

That is a concrete relation to the collection's wider continuity work. Device state, authority ledgers and project-development context are different things, but all can be damaged by pretending a recipient possesses context that never actually arrived. IoTox's handoff describes which materials travel and which do not. The public W4R3Z folder contains the preserved source snapshot. The linked release adds the matching supplied executable and standalone distribution; it does not add every founding cube.

## Where to continue

- **Understand the product:** [original overview](README.md), [product page](docs/product-page.md), then the [architecture](docs/architecture.md). Some long documents preserve revision history; read their dates and current implementation together.
- **Investigate a use:** [quickstart](docs/quickstart.md), [folder-sync guide](docs/replace-resilio-sync.md), [terminal account](docs/ratox-ssh-status.md), [person messaging](docs/person-multidevice.md).
- **Understand the claim boundaries:** [security policy](SECURITY.md), [ship readiness](docs/ship-readiness.md), [threat model](docs/threat-model-draft.md), and [source/review record](../../guides/review/IoTox-2026-10-20.md).
- **Build or study a mechanism:** [documentation map](docs/README.md), [build instructions](BUILDING.md), [testing guide](docs/testing.md), [license](LICENSE.md) and [third-party notices](THIRD_PARTY.md).

The 1 October ship-readiness account records a locally accepted, scope-bound stable dossier and requires an explicit evidence manifest. That is not a repeal of the security policy or general production qualification. The record must identify the relevant binary, host, route, dataset and owner decision; the label alone does not carry them.

h0p3 maintains IoTox. The [source record](W4R3Z-SOURCE.json) and [checksums](W4R3Z-SHA256SUMS) preserve the imported snapshot's identity; original project notices remain with it. Editorial explanation by Lumen; it does not replace the source's contracts.

[Maintained Tools](../README.md) · [Catalog](../../CATALOG.md) · [W4R3Z](../../README.md)
