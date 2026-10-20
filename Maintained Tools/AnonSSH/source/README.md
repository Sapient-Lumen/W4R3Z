> **W4R3Z source browser:** This directory contains the project code, documentation and bootstrap manifests. The 636 binary RouterInfo records are preserved in the portable executable and the [complete 1.28 MB project-source ZIP](https://github.com/Sapient-Lumen/W4R3Z/releases/download/anonssh-v0.2.0-9831b007cd47/anonssh-project-source-9831b007cd47-public.zip), rather than duplicated as individual Git files here. Use that ZIP for a complete build tree.

# AnonSSH

AnonSSH reconstructs a machine's anonymous-network destinations and SSH keys from an
identity password plus a stable machine ID. From a fresh Linux machine, the intended
recovery path is:

```sh
anonssh user@machine-id
```

Enter the same identity password used by the destination. No copied SSH key, host-key
record, IP address, onion address, or I2P destination is required.

## Current status

AnonSSH is a working x86-64 Linux product, not a protocol sketch. The portable artifact
is one statically linked `anonssh` executable containing static Tor, i2pd, OpenSSH
`ssh`, `scp`, and `sftp-server`, and Dropbear child programs, i2pd reseed certificates,
and the public I2P bootstrap corpus.
It runs on NixOS and conventional Linux without host copies of those programs or a Nix
installation.

The default path is an authenticated adaptive bond over Tor and I2P. Tor-only and
I2P-only bonds, direct Tor, and direct I2P remain explicit recovery modes. The resident
broker reuses router pools and destination sessions across commands, supports concurrent
clients, and gives each SSH connection its own ordered bond stream.

AnonSSH is an SSH-compatible remote-shell executable for the tested rsync, Git, Borg,
scp, SFTP, SSHFS, and generic-command subset. It preserves remote stdio and exit status
while refusing SSH options that could replace its route, identity, or trust policy.
Stock clients select AnonSSH through `-e`, `-S`, `BORG_RSH`, `GIT_SSH_COMMAND`, or
`ssh_command`; there are no AnonSSH tool-specific subcommands. A separate owner-only
Unix-socket transport API is implemented and mixed-overlay proven for statically
configured peer services. See [application
interfaces](docs/context/application-interfaces.md).

The embedded I2P bootstrap corpus contains 636 currently corroborated RouterInfos whose
stable identities were observed from two mature routers on three UTC days spanning at
least seven days. The promoted corpus passed reseed-disabled fresh-I2P login on
2026-10-19; ordinary certificate-verified I2P reseeding also remains enabled. See
[I2P bootstrap](#i2p-bootstrap).

The RustCrypto ML-KEM-768 dependency follows FIPS 203. Existing SSH streams do not
survive loss of their owning AnonSSH process; process restart restores new connections
from retained router state. Use a remote `tmux` or `zellij` session when shell work must
survive reconnect. Transparent stream survival would require durable cryptographic,
flow-control, reassembly, and backend-process state at both peers and is not a current
product promise.

## First use

### Connect from a downloaded binary

If the destination is already running as machine `home`:

```sh
chmod 755 ./anonssh
./anonssh doctor
./anonssh alice@home
```

Replace `alice` with the destination's Unix account and `home` with its exact AnonSSH
machine ID. The first client run creates persistent local Tor and I2P state. Cold I2P
startup can take several minutes. Normal output reports only meaningful provider-level
changes (`starting`, `router ready`, `connected`, `retrying`) and the route that
ultimately won.
Run `anonssh --verbose alice@home` when diagnosing a connection; verbose mode adds
per-slot attempts and the exact machine-readable `anonssh-route` report. Later commands
can reuse the resident broker, routers, and authenticated sessions.

The explicit advanced form is:

```sh
anonssh connect alice@home --transport bond-i2p
```

Available client transports are `auto`, `bond`, `bond-tor`, `bond-i2p`, `tor`, and
`i2p`. `auto` prefers authenticated bonds, gives the mixed bond a bounded head start,
and races delayed direct recovery routes under independent deadlines. One winner reaches
OpenSSH; losing attempts are cancelled.

### Start a destination

For an interactive foreground server:

```sh
anonssh server --machine-id home
```

On a bonded server, expose an owner-private local Unix service by symbolic name:

```sh
anonssh server --machine-id home --native-service sync=/run/user/1000/sync.sock
```

The path is local policy: it must already be an absolute Unix socket owned by the
AnonSSH server user with no group or other permissions. Only `sync` crosses the bond;
the path never does. `ssh` is reserved for the built-in recovery service.

For a long-lived Linux user service:

```sh
anonssh service install --machine-id home
anonssh service unlock
anonssh service status --json
```

`service install` writes and enables user-scoped broker and recovery-server systemd
units. `service unlock` stores the entered password only in an owner-only runtime file,
allowing crash restart during the current login; reboot deliberately returns the service
to a locked state. For unattended startup, install with an explicit owner-only regular
`--credential-file` and then use `service start`. AnonSSH never converts an interactive
password into a persistent credential. `service stop` removes the runtime credential,
and `service uninstall` removes both units. Starting a user service before login also
requires an administrator-selected systemd lingering policy.

The server's default bonded publication also exposes compatible direct Tor and I2P
recovery endpoints. Explicit `bond-tor` or `bond-i2p` server policy restricts the bond to
that provider; automatic clients authenticate the offered topology rather than trusting
an unauthenticated hint.

### Forward a named service

AnonSSH can expose one explicit remote TCP service through the same authenticated route:

```sh
anonssh forward alice@home \
  --listen 127.0.0.1:8080 \
  --remote 127.0.0.1:80
```

The local listener must be a nonzero loopback endpoint. Remote authorization still
comes from hardened OpenSSH local forwarding; this command is not an unauthenticated
exit proxy. Unix-socket forwarding and general SOCKS/TUN interception are not shipped.

### Existing tools and native applications

Tool integration uses ordinary SSH remote-shell composition, not one wrapper per tool.
Rsync uses AnonSSH in its normal form:

```sh
rsync -a --info=progress2 -e anonssh ./data/ alice@home:/srv/data/
```

Git uses the same interface:

```sh
GIT_SSH_COMMAND='anonssh -q' git clone alice@home:/srv/git/project.git
```

The stock OpenSSH file-transfer clients use their standard SSH-program option:

```sh
scp -S anonssh ./archive.tar alice@home:/srv/data/
sftp -S anonssh alice@home
```

Modern `scp` uses the embedded SFTP subsystem. Explicit legacy `scp -O -S anonssh`
also works through the embedded server-side `scp` helper.

Borg and SSHFS likewise use their standard SSH selection mechanisms:

```sh
BORG_RSH='anonssh -q' borg create alice@home:/srv/borg::snapshot ./data
mkdir -p ./home-mount
sshfs -o ssh_command=anonssh alice@home:/srv/data ./home-mount
fusermount3 -u ./home-mount
```

The packaged live campaign proves bidirectional rsync with resume and metadata, Git
push/clone/fetch, Borg repository creation/check/extraction, modern scp, direct SFTP,
legacy scp, SSHFS read/write/rename/unmount, exact stdout and stderr, remote exit status,
clean missing-command failure, and independent SSH streams reusing one bonded session.
Tool-specific remote executables such as `rsync`, Git, and Borg must still exist on the
destination, as with ordinary SSH; the SFTP and legacy scp server helpers are embedded.
SSHFS is a client-side dependency and requires a functioning local FUSE installation.

Software that should not use SSH can use the distinct owner-only ALP socket. Authorize
the destination through the controlling terminal, then open a classed raw stream:

```sh
anonssh authorize alice@home
printf 'payload' | anonssh dial alice@home sync --class bulk
```

External programs may speak the documented ALP1 setup protocol directly to
`$XDG_RUNTIME_DIR/anonssh/transport.sock`; after one ready result the socket contains
only raw application bytes. Each connection owns an independent encrypted
`BondedStream` while reusing warm routers and destination sessions. ALP never exposes
ABP keys, provider endpoints, remote addresses, or server paths, and it is not
Unix-socket forwarding, SOCKS, TUN, or an arbitrary network exit. Packaged live proof
hash-verifies simultaneous bulk and real-time streams over one reused mixed bond.
Dynamic registration, homogeneous-overlay proof, and planned Rust, C, Python, and Go
clients remain unfinished; see
[application interfaces](docs/context/application-interfaces.md).

## How the bond works

The normal mixed topology declares eight Tor and eight i2pd candidate slots at each
endpoint. Each slot has its own persistent state root, local endpoint, deterministic
destination, and failure-domain identity. Formation races the first policy lane from
each provider and becomes usable after either representative authenticates. A mixed
session then converges on a two-Tor plus two-I2P baseline; a homogeneous session has an
eight-candidate, four-lane baseline. Optional candidates remain dormant until measured
demand justifies their startup and resource cost.

The default `performance` profile permits at most sixteen active product lanes; sixteen
is a ceiling, not a target. The separate 16+16 topology is an explicit high-resource
test facility. The adaptive controller keeps bounded per-slot priors for useful goodput,
queue delay, startup time, CPU, and RSS; responds quickly to sustained pressure; drains
slowly; and periodically explores stale or unknown optional paths. An endpoint-wide
resource governor charges one physical router once even when multiple destination
sessions share it.

The scheduler assigns bulk chunks by predicted delivery time rather than round robin.
It adapts new bulk chunks between 16 and 64 KiB from measured bandwidth-delay product,
queueing, acknowledgement gaps, and retransmissions. Every eligible bulk lane receives
bounded periodic probe traffic so an old estimate cannot permanently starve a path.
Unequal lanes therefore contribute according to useful capacity instead of forcing the
bond to run at the weakest lane's rate.

Two low-latency lanes stay protected from bulk while another healthy bulk lane exists.
Typing-sized `Interactive` writes and explicit `Realtime` data up to 2 KiB race one copy
over each protected lane; the first authenticated copy advances the ordered stream and
the duplicate is eliminated. Bulk remains single-copy. This reduces avoidable queueing
and path-jitter tails, but AnonSSH cannot provide Mosh-style predictive local echo: below
OpenSSH encryption it cannot identify a keystroke, password, terminal control sequence,
or SSH channel. A terminal predictor would require a separate client/server terminal
protocol above encryption and is deliberately not part of the bond.

The reusable transport supplies authenticated lane joins, mandatory native payload
encryption, selective acknowledgements, peer-advertised stream credit, bounded reorder
and sender state, cross-lane retransmission, encrypted topology changes, authenticated
liveness probes, and lane repair. See the [architecture](docs/context/architecture.md),
[wire/runtime protocol](docs/context/bond-protocol.md), and
[provider API](docs/context/provider-api.md).

## Configuration

With no file, AnonSSH uses the `performance` resource profile and `auto` transport
profile. Pass `--config PATH` globally or write
`$XDG_CONFIG_HOME/anonssh/config.json` (normally
`~/.config/anonssh/config.json`):

```json
{
  "version": 2,
  "resource_profile": "balanced",
  "transport_profile": "auto",
  "external_tor_services": [
    {
      "socks": "127.0.0.1:19050",
      "control": "127.0.0.1:19150",
      "cookie_file": "/absolute/control_auth_cookie"
    }
  ],
  "resident_service": {
    "maximum_sessions": 8,
    "maximum_local_connections": 32,
    "minimum_warm_slots_per_provider": 2,
    "maximum_warm_slots_per_provider": 4,
    "cache_quota_bytes": 2147483648,
    "state_quota_bytes": 17179869184,
    "old_runtime_retention_seconds": 2592000
  }
}
```

Resource profiles are admission ceilings, not reservations:

| Profile | Active lanes | Changes/evaluation | CPU ceiling | RSS ceiling | Warm/provider |
| --- | ---: | ---: | ---: | ---: | ---: |
| `low` | 4 | 1 per 15 s | 1 core | 1 GiB | 1-2 |
| `balanced` | 8 | 2 per 10 s | 3 cores | 2 GiB | 2-4 |
| `performance` | 16 | 4 per 10 s | 8 cores | 4 GiB | 2-8 |

The profiles respectively default to 4/16, 8/32, and 16/64
destination-session/local-connection limits; 1, 2, and 4 GiB cache quotas; and 8, 16,
and 32 GiB persistent-state admission ceilings. Runtime-cache retention defaults to 30
days. Cache collection may remove only old, unselected content-addressed embedded
payloads. Persistent Tor and I2P state is never deleted automatically.

Transport profiles are `auto`, `mixed`, `tor-only`, and `i2p-only`; an explicit command
`--transport` wins. `ANONSSH_CONFIG_FILE`, `ANONSSH_RESOURCE_PROFILE`, and
`ANONSSH_TRANSPORT_PROFILE` are higher-precedence emergency/test overrides. Unknown or
duplicate keys, unsafe endpoints, malformed values, and unsupported versions fail
closed. A broker rejects a request using a different resource profile instead of
silently reusing the wrong policy.

An external Tor daemon must be declared with exact nonzero loopback SOCKS/control
endpoints and an owner-only regular 32-byte CookieAuthentication file. AnonSSH
authenticates control, verifies bootstrap, requires `IsolateSOCKSAuth`, never adopts an
undeclared occupied port, and never stops the external daemon. Repeating one control
cookie across slots is rejected because it is not an independent failure domain.
`ANONSSH_TOR_BIN`, `ANONSSH_I2PD_BIN`, `ANONSSH_I2PD_CERTS_DIR`, `ANONSSH_SSH_BIN`, and
`ANONSSH_DROPBEAR_BIN` instead select operator-provided executables or certificates.

## State and security

Managed router state lives in the platform user-data directory and survives restart.
Client and server roles use disjoint pools, so one machine can stay ready for outgoing
and incoming sessions. Ephemeral SSH identity and trust files live in the cache and are
removed after use. Existing healthy external I2P SAM routers are borrowed and never
stopped.

Passwords are exact nonempty UTF-8 strings. Password files must be owner-only, nonempty
regular files and must not be symlinks. One conventional trailing LF or CRLF is removed;
all other whitespace is identity material. Derived SSH host and client keys are pinned,
and route, identity, and host-trust overrides are rejected.

Router output is retained only as a bounded redacted in-memory diagnostic tail. Owned
Tor, i2pd, and Dropbear children receive graceful shutdown and Linux parent-death
handling. Router cache/state walks reject symlinks. Content-addressed embedded payloads
are verified on every use. A state quota blocks new admission rather than deleting
router state or breaking established sessions.

Each bond lane uses an authenticated ephemeral ML-KEM-768 exchange mixed with the
password-derived bond key and transcript through HKDF-SHA-256. ChaCha20-Poly1305 records
use independent directional keys and monotonic counters. SSH remains independently
encrypted above this layer.

## I2P bootstrap

AnonSSH keeps three different facts separate:

1. **Identity longevity** comes from observing the same public router identity from at
   least two mature local routers on three distinct UTC days spanning at least seven
   days.
2. **Current usefulness** comes from the newest corroborated signed RouterInfo for a
   qualifying identity; addresses and RouterInfo timestamps can change.
3. **Recovery** comes from i2pd's ordinary certificate-verified reseeding when embedded
   hints are absent, stale, or invalid.

There is no corpus-count ceiling. The observer retains temporarily absent identities
indefinitely and counts at most one observation day per UTC day. Private router keys,
destination keys, and peer profiles are never embedded; profiles are local selection
evidence only.

The 2026-10-19 observation produced 637 qualifying identities. Curation promoted all 636
that were also currently corroborated, using their newest signed RouterInfos; the one
temporarily absent identity remains in the ledger for future consideration. The shipped
v3 manifest records the complete longevity evidence. The dated distribution and
reseed-disabled fresh-login result are recorded in
[evidence.md](docs/context/evidence.md#longitudinal-i2p-evidence).

Normal collection and promotion are deliberately separate:

```sh
make status-i2p-bootstrap
make status-i2p-sources
# On each intended UTC observation day:
make observe-i2p-bootstrap
# Once the observation policy has qualifying identities:
make curate-i2p-bootstrap
# Review bootstrap/i2p.next and artifacts/i2p-bootstrap.diff.
make promote-i2p-bootstrap
make check-i2p-bootstrap
make live-i2p-fresh
```

The two status targets are read-only: one reports the versioned observation ledger and
the other applies the curator's current-source rules without recording an observation.
Keeping the mature routers online grows their local history but does not silently modify
the repository ledger. Observation is explicit and idempotent within a UTC day. Curation
stages every currently corroborated identity meeting the policy. Promotion requires a
human review of the complete staged corpus and diff. Validation checks schemas,
symlinks, sizes, identities, digests, observation history, and RouterInfo ages. Age is
diagnostic rather than a release-expiration rule.

## Build and release

Use Make targets for repository workflows:

```sh
make doctor
make test-quick
make gate
```

Nix supplies the pinned toolchain and package inputs. `make package` builds the wrapped
Nix package. `make package-static` writes the portable executable and its release bundle
under `artifacts/release/`; the target rejects dynamic dependencies in the outer binary
and all six embedded executable payloads, runs embedded deterministic and local SSH
proofs, and emits SHA-256, SPDX SBOM, license, source, and release manifests. Its
corresponding-source archive materializes every vendored Rust crate, embedded-program
source, selected Tor static-library source, and the Java I2P certificate source as
ordinary files; both release and publication checks reject any surviving symlink. The
supported portable target is x86-64 Linux. AArch64 is outside the current release
contract.

`make package-static-reproducible` rebuilds independently and requires the same digest.
`make package-publication` requires a clean committed tree and produces a verified ZIP
containing a Git-ready source snapshot, the complete static release bundle, selected
machine-readable evidence, and no Git history or local runtime state. See
[PUBLISHING.md](PUBLISHING.md).
`make sign-release RELEASE_SIGNING_KEY=...` accepts only an explicit publisher-owned SSH
signing key; repository-generated checksums are integrity metadata, not publisher
authentication. See [third-party obligations](THIRD_PARTY.md).

An external NixOS repository should pin this complete source tree and use its own
`nixpkgs`:

```nix
let
  anonsshSource = /* pinned source containing default.nix, Cargo.lock, and bootstrap/ */;
  anonssh = pkgs.callPackage anonsshSource { };
in {
  environment.systemPackages = [ anonssh ];
}
```

Do not publish a mutable checkout path. `make test-package-consumer` proves this
`pkgs.callPackage` boundary.

For the local Monsternix checkout, the repository also exposes a Nix-integrated product
that omits all six embedded executable payloads and uses Tor, i2pd, OpenSSH, and Dropbear
from the host's Nix package set. It is the same Rust program and adaptive transport, not
a fork, but its executable is intentionally dependent on its Nix store closure:

```nix
environment.systemPackages = with pkgs; [
  (import /path/to/AnonSSH/nix/monsternix.nix { inherit pkgs; })
];
```

That mutable path is appropriate for this personal source checkout, not for a public
reproducible package pin. `make package-monsternix` builds and tests the exact integration,
proves that no child-program payload was compiled into the Rust executable, and writes
its report to `artifacts/monsternix-package/report.json`.

The source wrapper `./anons.sh` executes an installed `anonssh` when available, otherwise
builds `default.nix`, validates the repository corpus, and runs the packaged command. It
is convenience machinery, not a second product implementation.

## Verification and evidence

`make test-quick` runs formatting, Clippy, and the complete workspace test suite.
`make test-fuzz` runs the fixed-seed parser mutation facility embedded in the shipped
binary and writes `artifacts/fuzz/report.json`. `make gate` adds that campaign, bootstrap
validation, package, static release, external-consumer, service-lifecycle, and smoke
proofs. Live public-overlay campaigns are explicit because they consume network time and
substantial resources; they write machine-readable JSON under ignored `artifacts/` and
never treat stdout as evidence.

Campaign purposes, retained conclusions, artifact schemas, and interpretation rules are
centralized in [evidence.md](docs/context/evidence.md). Exact measured values belong to
the artifact produced by a specific run, not to the product contract. The authoritative
claims and exit conditions are in [spec_ledger.json](specs/spec_ledger.json).

## Rust transport API

`anonssh-bond-tokio` exposes `BondDialer`, `BondListener`, `BondSession`, and
`BondedStream` for non-SSH Rust applications. Callers select `Control`, `Realtime`,
`Interactive`, or `Bulk` streams and provide exact policy-gated lane providers. Built-in
adapters cover loopback tests, Tor SOCKS/onion publication, and I2P SAM dialing/listening;
router process supervision and machine-wide policy stay in the product layer. The public
provider contract, including the SAM initial-payload requirement, is documented in
[provider-api.md](docs/context/provider-api.md).

## Documentation map

- [Specification ledger](specs/spec_ledger.json): authoritative claims, assumptions,
  statuses, and exit conditions.
- [Architecture decisions](docs/adr/INDEX.md): why the current product boundaries exist.
- [Architecture](docs/context/architecture.md): current product components and ownership.
- [Bond protocol](docs/context/bond-protocol.md): ABP v6 wire/runtime semantics and limits.
- [Provider API](docs/context/provider-api.md): reusable dial/listen boundary.
- [Application interfaces](docs/context/application-interfaces.md): implemented SSH
  remote-shell compatibility and public local transport protocol.
- [Evidence](docs/context/evidence.md): campaigns, artifacts, and interpretation.
- [I2P identity](docs/context/i2p-identity.md): compatibility-critical destination derivation.
- [Third-party programs](THIRD_PARTY.md): embedded versions and distribution obligations.

AnonSSH is open source under the [MIT License](LICENSE).
