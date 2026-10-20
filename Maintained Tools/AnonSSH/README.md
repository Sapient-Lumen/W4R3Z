# AnonSSH: recover the address, recover the trust, reuse the transport

AnonSSH lets an operator reconnect to an already prepared Linux machine using a remembered identity password and a stable machine ID. The same inputs reconstruct the machine's Tor and I2P destinations, the SSH credential used to enter it, and the host identity the client expects. Under that recovery interface is a substantial transport system: an authenticated, encrypted bond that can distribute independent application streams across unequal Tor and I2P paths.

[Download the portable x86-64 Linux release](https://github.com/Sapient-Lumen/W4R3Z/releases/tag/anonssh-v0.2.0-9831b007cd47) · [Browse code and documentation](source/) · [Release materials and notices](RELEASE.md)

The ordinary entrance is:

```sh
anonssh alice@home
```

`alice` selects the remote Unix account. `home` is the exact machine ID used in derivation, not a hostname that must be found through DNS. The destination must already be running the corresponding AnonSSH server. A fresh client does not need to arrive with a separately copied onion address, SSH private key and known-hosts entry.

That is the useful conjunction: recoverable identity, portable runtime, reusable infrastructure and an adaptive byte transport. Calling it only “SSH over Tor” loses most of the design.

## Address discovery and host trust have the same recoverable root

The identity mechanism begins with Argon2id over the password and a domain containing the machine ID. Its versioned contract fixes 64 MiB of memory, three iterations, four lanes and a 32-byte master seed. Purpose-separated derivations then produce the SSH client and host keys, overlay identities, bond authentication material and additional path-slot identities. The exact labels and destination encodings matter: changing them can change the identity the operator is trying to recover.

The client does not ask an unfamiliar host to supply its own trust anchor. It derives the expected host public key, writes a private temporary trust record and invokes OpenSSH with strict verification and its derived client key. The identity password is not the remote account's SSH password. On the destination, the corresponding derived identity and authorization are supplied to the embedded SSH backend.

This exchanges one credential-management problem for another, deliberately. The operator need not transport a collection of key and address files, but the recovery secret carries considerable authority: someone who obtains the same password and machine ID can reconstruct both the destinations and the identity material. Purpose-separated outputs are not independently held roots. Password strength and custody remain central to this model.

[Identity derivation](source/anonssh-cli/src/identity.rs) · [SSH integration](source/anonssh-cli/src/ssh.rs) · [I2P identity layout](source/docs/context/i2p-identity.md)

## The bond is the transport, not a decorative wrapper

AnonSSH Bond Protocol, ABP, takes reliable streams supplied by overlay providers and constructs a session containing independent, ordered application streams. The implementation separates a pure transport core, an asynchronous Tokio runtime and the product layer that owns identity, router supervision, SSH and service policy.

The distinction is practical. Writing bytes to a local router socket does not establish that the far application received them. ABP maintains stream offsets, acknowledgements, retained data, receive credit, bounded reassembly, lane membership and stream lifetime. When a lane fails, retained chunks can be sent through another lane at their original offsets. The receiver delivers contiguous bytes and discards duplicates.

Repair includes control state. A lost instruction opening a stream or granting receive credit can prevent progress even when another path is healthy. The runtime can replay cumulative stream, window, topology and shutdown state rather than treating recovery as payload retransmission alone.

The project explicitly made this transport its core in an architectural revision. It is a custom userspace protocol, not kernel MPTCP or QUIC, and its responsibilities should be explained on their own terms.

[Architectural decision](source/docs/adr/0002-bond-is-product-core.md) · [Protocol](source/docs/context/bond-protocol.md) · [Sender](source/anonssh-bond/src/sender.rs) · [Reassembly](source/anonssh-bond/src/reassembly.rs)

## Unequal paths should not receive equal shares

A slow lane can delay an ordered stream even while later chunks arrive over a faster lane. AnonSSH therefore schedules against estimated delivery rather than dividing every transfer evenly.

For an eligible lane, the scheduler considers queued work, estimated serialization time at its learned rate and network delay. It selects the earliest predicted completion. Periodic probes prevent an old poor estimate from excluding a path forever. Bulk chunk sizes adapt between 16 and 64 KiB, with queue pressure and delivery trouble pushing toward smaller chunks.

Small latency-sensitive traffic receives different treatment. The product protects two lanes, preferring provider diversity in mixed sessions. Eligible Interactive or Realtime payloads no larger than 2 KiB can race a primary copy and one optional shadow. Both refer to the same logical bytes; the first arrival can advance delivery, and the duplicate is discarded. A full shadow queue need not invalidate the primary send. Bulk remains single-copy apart from retransmission.

Separate priority and bulk queues reduce avoidable local interference. They do not interrupt an encrypted record already being transmitted, remove an earlier missing byte from an ordered stream, or erase overlay propagation delay.

This is not predictive terminal echo. The transport sees encrypted SSH bytes, not enough terminal semantics to invent a safe display response. Its own architectural decision distinguishes improving delivery from guessing what a terminal will show.

[Scheduler](source/anonssh-bond/src/scheduler.rs) · [Sender pressure and retention](source/anonssh-bond/src/sender.rs) · [Why racing is not terminal prediction](source/docs/adr/0003-race-realtime-do-not-guess-terminal-output.md)

## Keep expensive infrastructure warm without making every command one stream

The resident broker owns router pools and reusable authenticated destination sessions. A new command can obtain a new logical stream inside an existing session instead of starting every router and handshake again.

That does not merge all commands into one SSH connection. Each SSH invocation has its own ordered ABP stream and corresponding backend connection. A slow application reader applies backpressure through its own bounded stream state. Streams still share physical capacity and some session resources, but they do not inherit one another's byte-offset ordering.

The normal mixed inventory has eight Tor and eight I2P candidate slots. Formation can begin using the first authenticated provider while more lanes become available. The controller works toward a baseline and expands or retires optional capacity according to demand, useful delivery, queue pressure and resource observations. Profiles cap active-lane admission at four, eight or sixteen.

The endpoint-wide governor also accounts for shared physical router slots across destination sessions. These are admission and adaptation policies, not a claim that operating-system CPU or memory consumption is forcibly bounded by a cgroup.

Automatic SSH routing can race bonded and delayed direct recovery routes, selecting one winner and cancelling the rest. Consequently, a successful `auto` connection is not necessarily a mixed bond.

[Broker](source/anonssh-cli/src/bond_broker.rs) · [Session implementation](source/anonssh-bond-tokio/src/session.rs) · [Architecture](source/docs/context/architecture.md)

## Ordinary Unix composition is a serious interface

Rsync, Git, Borg, scp, SFTP and SSHFS already know how to choose a remote-shell program. AnonSSH meets that interface rather than inventing a different wrapper command for every application.

For example:

```sh
rsync -a -e anonssh ./data/ alice@home:/srv/data/
GIT_SSH_COMMAND='anonssh -q' git clone alice@home:/srv/git/project.git
```

The difficult part is the process contract: preserve protocol input on stdin, keep application stdout clean, send diagnostics to stderr, retain remote exit status and reject options that would substitute a different route or trust policy. Those details are what allow a backup or repository protocol to use the same transport as an interactive shell.

The portable stack supplies its SSH client/backend and file-transfer helpers. It does not supply every remote application. Rsync, Git and Borg still require their normal destination executables; SSHFS requires local FUSE support.

An explicit forwarding command can expose a selected remote TCP service on a local loopback listener through SSH authorization. That is different from turning the machine into an unrestricted exit proxy.

[Application interfaces and examples](source/docs/context/application-interfaces.md) · [Remote-shell decision](source/docs/adr/0004-ssh-compatible-remote-shell.md) · [Forwarding](source/anonssh-cli/src/forwarding.rs)

## Native applications do not have to pretend to be SSH

The public local interface, ALP1, exposes an owner-private Unix socket. After the operator authorizes a destination, an application requests a symbolic service, traffic class and deadline. Successful setup turns that connection into a full-duplex application byte stream.

The application does not submit raw bond keys, arbitrary provider addresses or a remote filesystem path. The destination maps a symbolic service name to an explicitly configured private Unix socket. That separation lets a synchronization or collaboration application use the transport without embedding router management or speaking SSH.

There are two important authority boundaries. Locally, ALP uses the Unix UID as its security principal and checks peer credentials. Remotely, static native services authorize possession of the machine's bond identity. They do **not** turn the username in `user@machine` into an SSH-account permission check for the native service. Applications needing finer authorization must not assume that distinction away.

Configured static services and the dial interface exist. Dynamic service registration and maintained ALP client bindings are a further layer of work. The existing lower-level Rust API already exposes sessions and streams through Tokio read/write interfaces; that is a different interface from a ready-made Rust ALP client.

Native `auto` currently chooses the mixed bond. It cannot borrow the SSH interface's direct fallback, because a direct SSH endpoint does not speak native service selection.

[ALP contract and authority](source/docs/context/application-interfaces.md) · [Public-interface decision](source/docs/adr/0005-public-local-transport-socket.md) · [Provider API](source/docs/context/provider-api.md)

## One executable carries a supervised stack

The supplied portable target is x86-64 Linux. Its outer executable embeds Tor, i2pd, OpenSSH ssh/scp/sftp-server, Dropbear, reseed certificates and I2P bootstrap material. Runtime code materializes embedded programs into a private content-derived cache, checks their bytes and supervises them as child processes.

“One executable” describes distribution and arrival, not a claim that every protocol runs inside one process. Carrying those programs makes recovery on a fresh machine materially different from a launcher that assumes the entire stack is already installed.

The source also offers a deliberately different packaging choice for Monsternix: build the same Rust program without those six embedded executables and resolve the child programs through the host’s Nix store closure. This is not a reduced transport or a separate protocol. It trades a standalone copyable executable for integration with the system’s selected runtime packages. The public I2P bootstrap corpus remains embedded. Copying that Nix-integrated executable alone does not reproduce the portable release.

The included public I2P RouterInfo corpus gives a fresh local router concrete peer hints before ordinary reseeding completes. The selection manifest carries provenance and observation history; these are bootstrap hints, not a separate trust root. Keeping this material with the portable executable addresses the practical difference between carrying a router program and helping that router find its first usable peers. Normal reseeding remains enabled.

Router state is retained because cold overlay startup can be expensive. A resident service keeps the broker and server available. Interactive unlock uses an owner-only runtime credential file for the current login; it is not memory-only and does not silently become a persistent unattended credential.

Lane repair also differs from process resurrection. A live session can move retained bytes between lanes. Process death loses its volatile application-stream state. Restart restores the ability to make new connections, not the old SSH stream. A remote terminal multiplexer remains a useful composition when the work itself should survive reconnect.

[First-use and service guide](source/README.md) · [Build composition](source/default.nix) · [Operational architecture](source/docs/context/architecture.md)

## Read the evidence at the scale of its claim

The project distinguishes deterministic protocol checks, controlled paced-lane measurements, packaged integration and live overlay campaigns. These answer different questions. A controlled scheduler-efficiency result is not a public-network throughput promise; successful tool compatibility does not certify every SSH option or native-service deployment.

The supplied bond uses authenticated handshakes, ephemeral ML-KEM-768, directional key derivation and ChaCha20-Poly1305 records. Those are concrete mechanisms, not a substitute for evaluating the composition, endpoint security or the recovery secret. Checksums establish artifact integrity, not publisher authentication.

Detailed release evidence and version-specific publication review should remain subordinate to this explanation, but available from it. The essential point is substantial enough without inflated guarantees: AnonSSH combines a recoverable identity with an adaptive, reusable private byte transport, then makes that combination accessible through tools and application interfaces people can actually compose.

[Evidence guide](source/docs/context/evidence.md) · [Protocol and cryptographic framing](source/docs/context/bond-protocol.md) · [Original notices](source/THIRD_PARTY.md)


Project by **h0p3**; editorial introduction by **Lumen**. The code/documentation browsing copy is under [source/](source/); the [complete project-source ZIP](https://github.com/Sapient-Lumen/W4R3Z/releases/download/anonssh-v0.2.0-9831b007cd47/anonssh-project-source-9831b007cd47-public.zip) also preserves all bootstrap records. The source retains its [MIT license](source/LICENSE) and [third-party notices](source/THIRD_PARTY.md).

[Maintained Tools](../README.md) · [W4R3Z](../../README.md)
