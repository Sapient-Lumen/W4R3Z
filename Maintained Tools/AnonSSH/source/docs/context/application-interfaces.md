# Application Interfaces

This document records the application-facing boundary around the implemented bond. The
[specification ledger](../../specs/spec_ledger.json) is authoritative for status and
exit conditions; ADR [0004](../adr/0004-ssh-compatible-remote-shell.md) chooses the SSH
remote-shell contract and ADR [0005](../adr/0005-public-local-transport-socket.md)
chooses the native local-socket contract.

## Status

| Interface | Status | What works now |
| --- | --- | --- |
| Interactive SSH | Implemented | `anonssh user@machine-id` and explicit `connect`. |
| Named local TCP forwarding | Implemented | One hardened OpenSSH local forward. |
| Public Rust bond API | Implemented | `BondDialer`, `BondListener`, `BondSession`, and `BondedStream`. |
| SSH-compatible remote commands | Implemented | Bounded options, byte-pure stdio, and exact remote status. |
| Rsync and Git remote-shell use | Implemented | Packaged push/pull/resume and push/clone/fetch proof. |
| Borg remote-shell use | Implemented | Stock Borg repository create/check/extract is mixed-bond proven. |
| scp/SFTP | Implemented | Stock clients, modern SFTP transport, and legacy scp are packaged and mixed-bond proven. |
| SSHFS | Implemented | Stock SSHFS read/write/rename and managed unmount are mixed-bond proven. |
| Peer native service dispatch | Implemented | Capability-negotiated ASP1 and static owner-private Unix services. |
| Public local Unix transport API | Implemented, mixed live-proven | ALP1 socket, authorization, CLI dial, static service dispatch, and raw transition. |
| C/Python/Go clients | Designed | They will target ALP rather than a native ABI. |

The interfaces solve different problems. Implemented SSH compatibility lets unchanged
tools reuse their existing remote execution protocol. ALP lets new software skip SSH
and select native stream semantics. It is a distinct protocol and socket, not a renamed
private broker interface.

## SSH Remote-Shell Surface

### Grammar

The compatibility parser has three phases: AnonSSH global options, SSH-compatible
options, then destination and remote command. Explicit AnonSSH subcommands remain
unambiguous and retain their existing grammar.

Accepted target forms are `[user@]machine-id` and `-l user machine-id`. A bare machine
ID requires either a configured default user or `-l`; it must never silently substitute
the local username without a documented configuration. A user in both locations is an
error unless the values are identical. The machine ID continues to select deterministic
identity, not DNS.

Options are classified before any process starts:

- AnonSSH consumes product options such as `--config`, `--transport`, and verbosity.
- Safe SSH presentation options can be forwarded, including terminal, subsystem,
  quiet/debug, stdin, X11-disable, and similarly bounded options after review.
- `-l` is consumed into the recovery target rather than forwarded as an identity
  override.
- Route, destination, port, config-file, proxy, key, agent, host-key, known-hosts,
  control-master, authentication, and canonicalization controls remain forbidden.
- Unknown options and missing option arguments fail closed before prompting.
- `--` ends local option parsing. Everything after the destination is a remote command,
  including values beginning with `-`.

The parser retains `OsString` values until OpenSSH receives them. It does not convert a
command into a shell string. OpenSSH itself defines how multiple command arguments are
represented to the remote login shell, exactly as with `/usr/bin/ssh`.

### Process contract

Tool compatibility depends at least as much on process behavior as command syntax:

- password input comes from `/dev/tty` or an equivalent controlling-terminal handle,
  never from stdin;
- setup and route progress use stderr only, with quiet mode suppressing routine output;
- stdout is exclusively remote stdout and stdin is exclusively remote stdin;
- no-command operation inherits interactive terminal behavior;
- command operation defaults to no PTY unless the caller asks for one;
- EOF and half-close are relayed rather than converted into process cancellation;
- SIGINT, SIGTERM, SIGQUIT, and terminal resize behavior remain equivalent to an
  ordinary OpenSSH child; and
- the AnonSSH process exits with the OpenSSH/remote exit status instead of turning every
  nonzero status into code 1 plus an error message.

The generated command rejects conflicting caller options and emits all
recovery-controlled OpenSSH options in the position required by OpenSSH's first-value
semantics, then appends the target, then appends the untouched remote command. A caller
cannot smuggle `RemoteCommand`, `ProxyCommand`, or an `Include` through `-o` and create a
second command or route.

### Compatibility matrix

The implemented remote-shell tranche targets tools that use a remote shell:

| Tool class | Expected invocation | Additional destination requirement |
| --- | --- | --- |
| rsync | `rsync -e anonssh ... user@machine:path` | Compatible `rsync` executable. |
| Git | `GIT_SSH_COMMAND=anonssh git fetch/push ...` | Git receive/upload helpers. |
| Borg | `BORG_RSH=anonssh borg ...` | Destination `borg` executable. |
| Generic command | `anonssh user@machine command ...` | Requested executable and shell. |
| Modern scp | `scp -S anonssh ... user@machine:path` | Embedded `sftp-server`. |
| SFTP | `sftp -S anonssh user@machine` | Embedded `sftp-server`. |
| Legacy scp | `scp -O -S anonssh ... user@machine:path` | Embedded server-side `scp`. |
| SSHFS | `sshfs -o ssh_command=anonssh user@machine:/path mountpoint` | Local FUSE and `sshfs`. |

The packaged proof covers rsync paths containing spaces and Unicode, a symbolic link,
file mode, a half-file resume, bidirectional transfer, Git push/clone/fetch, default
SFTP-based scp upload/download, SFTP batch upload/download, legacy scp upload/download,
Borg repository create/check/extract, SSHFS read/write/rename/unmount, exact remote
stdout/stderr, nonzero status, missing executables, and independent SSH streams on one
reused bond session. Interrupted transfer recovery and signal forwarding remain outside
the live claim. “SSH compatible” always means the tested subset; AnonSSH does not accept
an option merely to imitate OpenSSH help output.

AnonSSH deliberately does not add `anonssh scp`, `anonssh sftp`, or tool-specific
protocol adapters. Upstream clients remain responsible for their protocols and select
AnonSSH through the same remote-shell hook they use to select OpenSSH.

### Restart boundary

The resident broker can restore new connections after a crash or upgrade from retained
router state, but an already-open SSH stream terminates with its owning broker or server
process. Transparent survival is a major protocol boundary: both peers would need
crash-safe ABP keys and nonces, acknowledgement/window/reassembly state, stream epochs,
resume authentication, and a backend that retains or reconstructs the OpenSSH/Dropbear
connection. For personal shell continuity, a remote terminal multiplexer plus reconnect
is the supported composition; resumable applications retain their own recovery policy.

## ALP Local Transport Surface

### Runtime endpoints and authority

The client-facing ALP listener is separate from the private broker socket and lease.
Its path is `$XDG_RUNTIME_DIR/anonssh/transport.sock`. A future dynamic service
registrar will use a separate endpoint; no `services.sock` listener exists yet. Fallback
runtime directories retain the same owner-only and no-symlink checks as the existing
broker. The private broker protocol continues to carry implementation details and is
never a published API.

ALP treats the Unix UID as the local security principal. Socket mode 0600 and a mode
0700 parent are necessary but not sufficient: every accepted connection checks
Linux `SO_PEERCRED` and rejects a UID other than the broker owner. Root is outside the local
adversary model because it can already inspect the process and memory.

An application names an authorized target, not a key. `anonssh authorize user@machine`
is the explicit operation when the resident service is not already unlocked.
It prompts on the controlling terminal, derives and validates the same identity as SSH,
and installs an in-memory target record. The record is bound to exact user, machine ID,
bond identity, resource profile, and broker generation. It is removed on broker exit or
after 12 hours without use. ALP returns `authorization-required` instead of prompting through
an application's data stream.

### ALP1 setup protocol

Each record is `ALP1`, a big-endian unsigned 32-bit payload length, and one UTF-8 JSON
object no larger than 64 KiB. JSON is acceptable here because it is bounded setup
metadata, not a data-plane format; named fields make independent language clients and
minor extension review practical. Unknown required versions, duplicate keys, invalid
UTF-8, trailing data, unknown enum values, and noncanonical target/service names fail
closed.

The initial `dial` object contains:

- a caller-generated request ID;
- authorized target name;
- symbolic service name;
- `control`, `realtime`, `interactive`, or `bulk` traffic class;
- `auto`, `mixed`, `tor-only`, or `i2p-only` bond constraint; and
- setup deadline from 1 second through 15 minutes.

Current `auto` selects the mixed bond; it does not silently fall back to direct SSH,
because direct endpoints have no native-service protocol. Tor-only and I2P-only select
only their authorized provider pools.

The daemon currently returns exactly one `ready` or `error` result; the grammar reserves
bounded progress records for a later compatible extension. After `ready`, framing ends permanently and both directions are raw
application bytes. There is no sentinel in the byte stream. Local EOF half-closes the
BondedStream send direction; peer EOF does the reverse. Setup cancellation cancels its
network work, while closing a ready socket resets or half-closes according to observed
state.

Structured errors include unsupported-version, malformed-request, unauthorized-peer,
authorization-required, unknown-target, unknown-service, class-denied, capacity,
timeout, peer-incompatible, route-unavailable, service-unavailable, and internal. They
carry bounded human context but no key, provider endpoint, or remote path.

### Peer service dispatch

Native dispatch is negotiated as an authenticated ABP capability. For a supporting
session, the client opens a BondedStream with the requested class, writes an encrypted
bounded service preface, and waits for an encrypted accept/reject response before ALP
reports ready. The preface contains only protocol version and symbolic service. ABP
already authenticates the session, stream ID, class, and bytes.

Service names are lowercase ASCII labels with dots, underscores, and hyphens, at most
63 bytes. The remote `ASP1` preface and response are bounded binary application records
inside the already encrypted BondedStream; their exact version is included in the
authenticated service-multiplexing capability. The remote server maps a name to one of:

- the reserved built-in `ssh` adapter;
- an operator-configured owner-only Unix socket; or
- in the planned dynamic extension, a same-UID registration whose control lease is
  still alive.

Static services are authorized by possession of the machine's bond identity; they do
not distinguish the SSH username carried by a separate SSH login. Registration supplies
a local path only to the local server; that path never crosses ABP. Unregistered names
and direct address/path requests are rejected.

Static registration is implemented with repeatable
`--native-service NAME=/ABSOLUTE/SOCKET` server options. The server validates the path
at startup and before every connection, rejects symlinks and non-sockets, requires its
own effective UID and mode 0600-equivalent permissions, verifies the connected peer's
UID after connect, and caps each service at 16 concurrent streams. Any ABP traffic class
is accepted for a configured native service; the reserved `ssh` service remains
interactive-only. Dynamic registration and configurable class policy are not yet
implemented.

The planned dynamic registration will use framed ALP1 records on `services.sock`. A
same-UID process registers a symbolic name, one owner-controlled local Unix-socket path,
allowed traffic classes, and a bounded concurrency limit. The registration connection
remains open as the lease and never carries application bytes. For each accepted remote
stream, the server revalidates the path and connects once; the application accepts an ordinary new
local socket. Closing the lease prevents new streams and drains or resets existing
streams according to policy. Static configuration uses the same registry model without
a live lease.

SSH-only peers remain compatible because service multiplexing is a negotiated
capability. New native requests do not fall back to legacy SSH bytes, and an old client
cannot accidentally enter the service-preface parser. Native service fallback over the
direct SSH endpoints is a possible later adapter, not part of ALP1.

### Client APIs

The implemented `anonssh dial TARGET SERVICE` client bridges stdin/stdout to ALP and is
useful for shell composition and proof. Programs can already implement the small
documented ALP1 codec and use the public socket directly. Planned Rust, C, Python, and
Go clients will return each language's ordinary connected-stream type and expose:

- authorize or detect authorization requirement;
- dial target/service/class with context or deadline;
- receive optional setup progress;
- read, write, half-close, and close; and
- inspect stable error codes.

The bindings do not expose lane selection, Tor/I2P addresses, bond keys, or raw broker
operations. Advanced Rust software that needs provider ownership continues to use the
existing `BondDialer` and `BondListener` API directly.

`make live-bond-native` proves the packaged ALP path through real Tor and I2P routers.
It opens bulk and real-time echo streams concurrently, hash-verifies both payloads,
requires two independent stream IDs on one reused session, checks the runtime directory
and public socket modes, and succeeds only after broker, server, endpoint, socket, and
test-state cleanup. This is one mixed-overlay integration proof, not a latency SLA or
evidence for the still-unrun Tor-only and I2P-only ALP variants.

## Implementation Order

1. Completed: typed pre-destination options, post-destination command values, and child
   exit status.
2. Completed: parser/command-vector tests and packaged rsync/Git proof.
3. Completed: embedded SFTP and legacy scp helpers plus stock-client mixed-bond proof.
4. Completed: negotiated native-service capability and encrypted stream preface with a
   reserved SSH service, without changing legacy session behavior.
5. Completed core: owner-only ALP listener, target authorization registry, static Unix
   service registry, CLI client, and raw-stream transition.
6. Add dynamic service registration and connected-stream Rust client, then black-box C, Python, and Go
   clients against the same fixtures.
7. Completed tranche: hash-verified simultaneous bulk and real-time native traffic over
   one reused mixed bond with socket and process cleanup.
8. Extend packaged coverage to simultaneous SSH plus native traffic, Tor-only and
   I2P-only bonds, denial, churn, and restart cases.

The order deliberately proves ordinary tool composition before adding a second public
protocol, then proves the remote authorization boundary before publishing bindings.
