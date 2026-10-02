# IoTox local terminal profile v1

> Retained compatibility format. The current encoder emits `iotox-terminal-profile-v7`; byte-
> canonical v1 through v6 records remain accepted. V1 maps to explicit
> `confinement=compatibility`, historical fields retain their exact meanings, and no old record
> invents account groups, privilege, or payload pins. See `terminal-profile-v7.md`.

Status: implemented for the rev0020 host role behind its explicit default-off Agent gate
Wire effect: feature bit 23 is advertised only after secure pre-network activation; profile fields
remain entirely local and never appear on the wire

## Purpose

A terminal profile is operator-owned local policy for one Ratox OPEN. It freezes everything
that can select or shape a process: executable and arguments, cwd, environment, terminal type,
window bounds, identity, resource limits, and shutdown timing. A proven principal may resolve at
most one enabled binding. Remote bytes never select a profile and never become argv, shell text,
paths, environment, identity, or limits.

The profile registry remains policy rather than a remote command surface. rev0020's host Agent may
resolve it only after explicit startup activation, bilateral `ratox-interactive-v1` negotiation, a
transcript-confirmed current online epoch, an authenticated stable principal, and exact current
`interactive.terminal` authority. Default configurations advertise no Ratox feature. The separate controller role now exposes
`iotox terminal` over owner-private `terminal.sock`, but it never selects host profile policy and
there is still no PTY persistence across daemon restart.

## Store layout and filesystem contract

The loader accepts exactly this normalized absolute tree:

```text
ROOT/
├── profiles/
│   └── <profile-id>.profile
└── bindings/
    └── <principal-hex>.binding
```

Constraints:

- `ROOT` must be a normalized absolute path. Each component is opened from `/` with
  `O_DIRECTORY|O_NOFOLLOW`; a symlink in any component rejects the load.
- `ROOT`, `profiles`, and `bindings` must be directories owned by the configured daemon UID, with no
  group/other permissions and no set-ID/sticky bits.
- The root contains exactly `bindings` and `profiles`; hidden or extra entries reject the load.
- A record is opened with `O_NOFOLLOW|O_NONBLOCK`, must be a regular file owned by the configured
  UID, have link count 1, have no group/other permissions or special bits, and fit its byte bound.
- There are at most 64 profiles and 256 bindings.
- Filenames and record content must agree exactly.

This is a whole-store fail-closed read. One malformed or insecure entry rejects the candidate data.
The caller may then keep the previously committed registry generation authoritative.

## Canonical text rules

Both record types are UTF-8-independent byte grammars over ASCII field names and hexadecimal
payloads. A decoder requires:

- exact header and field order;
- exactly one LF after every line, including the last;
- no CR, blank trailing line, unknown field, duplicate singleton, or trailing byte;
- lowercase hexadecimal with an even number of digits;
- canonical unsigned decimal without sign or leading zeroes except the value `0`;
- byte-for-byte equality after decode and canonical re-encode.

Arguments, cwd, and environment values are hex-encoded so spaces and arbitrary non-NUL bytes do not
create a second textual grammar.

## Profile record grammar

The exact order is:

```text
iotox-terminal-profile-v1
id=<profile-id>
enabled=<0|1>
argument-hex=<hex bytes>                 repeated 1..32 times
working-directory-hex=<hex bytes>
terminal-type=<token>
inherit-environment=<name>               repeated 0..64 times, sorted
environment-hex=<name>:<hex value>       repeated 0..64 times, sorted by name
identity=inherit
    OR
identity=exact:<uid>:<gid>:1
minimum-dimensions=<columns>:<rows>
initial-dimensions=<columns>:<rows>
maximum-dimensions=<columns>:<rows>
allow-resize=<0|1>
limit-cpu-seconds=<u64>
limit-address-space-bytes=<u64>
limit-file-size-bytes=<u64>
limit-open-files=<u64>
limit-processes=<u64>
hangup-grace-ms=<u64>
terminate-grace-ms=<u64>
kill-reap-grace-ms=<u64>
```

Example canonical record:

```text
iotox-terminal-profile-v1
id=maintenance-shell
enabled=1
argument-hex=2f62696e2f6563686f
argument-hex=666978656420617267756d656e74
argument-hex=2d2d6e6f742d72656d6f7465
working-directory-hex=2f746d70
terminal-type=xterm-256color
inherit-environment=LANG
inherit-environment=TZ
environment-hex=ALPHA:6669727374
environment-hex=ZETA:6c617374
identity=inherit
minimum-dimensions=20:5
initial-dimensions=100:30
maximum-dimensions=240:80
allow-resize=1
limit-cpu-seconds=10
limit-address-space-bytes=134217728
limit-file-size-bytes=1048576
limit-open-files=32
limit-processes=8
hangup-grace-ms=20
terminate-grace-ms=40
kill-reap-grace-ms=60
```

### Profile ID

A profile ID is 1–64 bytes. The first byte is lowercase `a`–`z` or `0`–`9`; later bytes may also be
`.`, `_`, or `-`. The filename is exactly `<id>.profile`.

### Arguments and paths

There are 1–32 fixed arguments. Each decoded argument is nonempty, contains no NUL, and is at most
4096 bytes. `arguments[0]` is a normalized, non-root absolute path; the remaining arguments are
opaque fixed bytes. The total argument-byte accounting is bounded.

The working directory is a normalized absolute path, may be `/`, contains no NUL, and is at most
4096 bytes. Normalization rejects redundant separators, `.` and `..` components, and lexical aliases.
At native spawn, path components are opened without following symlinks and the child uses the
already-open descriptors.

V1 native targets and the IoTox helper must be regular ELF executables, owned by root or the daemon
UID, have an execute bit, have no set-ID bits, and not be group/other writable. Interpreter scripts
are intentionally unsupported.

### Environment

`TERM` is never supplied as a general entry. It is generated from `terminal-type`, whose 1–64 byte
token permits ASCII letters, digits, `-`, `_`, `.`, and `+`.

Inherited names are limited to:

```text
LANG TZ HOME USER LOGNAME SHELL PATH LC_*
```

The following are rejected for both fixed and inherited entries:

```text
TERM IFS ENV BASH_ENV SHELLOPTS PS4
GCONV_PATH LOCPATH NLSPATH GLIBC_TUNABLES
LD_* DYLD_* MALLOC_*
```

Names use the portable identifier grammar `[A-Za-z_][A-Za-z0-9_]*` and are at most 64 bytes. Values
contain no NUL and are at most 4096 bytes. Fixed and inherited names must be globally unique and may
not collide with `TERM`. Resolution scans at most 256 ambient entries, rejects duplicate/invalid
ambient names, copies only requested safe names that actually exist, adds fixed entries and `TERM`,
sorts by name, and caps the final vector at 64 entries and 32 KiB of `name=NUL-free-value` bytes.
The final `execve` environment contains no other daemon variable.

### Identity

`identity=inherit` is canonical only with zero UID/GID fields in memory and the default
clear-supplementary-groups flag. It keeps the helper's current real/effective UID and GID.

`identity=exact:<uid>:<gid>:1` requires clearing all supplementary groups before exact real,
effective, and saved GID/UID transitions, then verifies all six IDs and a zero supplementary-group
count. The trailing field must be `1`; an exact identity that retains supplementary groups is
invalid. Exact transition usually requires root or appropriate capabilities and fails closed when
unavailable.

### Dimensions

Columns and rows are unsigned 16-bit nonzero values. For both axes:

```text
minimum <= initial <= maximum
```

The requested OPEN dimensions are validated and clamped into the policy bounds. The accepted pair
is frozen into the resolved profile. Later resize is permitted only when `allow-resize=1`, and every
resize is clamped by the same policy. A disabled resize policy does not change the initial accepted
window.

### Resource limits

Each value is bounded to at most `2^60`. Zero means “leave the inherited soft limit unchanged” for
that named limit. Nonzero values set the soft limit only and may not exceed the inherited hard limit.
`limit-open-files`, when nonzero, must be at least 3. The native backend maps the fields to:

```text
RLIMIT_CPU RLIMIT_AS RLIMIT_FSIZE RLIMIT_NOFILE RLIMIT_NPROC
```

`RLIMIT_CORE` is always set to soft and hard zero independently of the record. These limits are
process/user kernel mechanisms, not a complete sandbox or a per-session descendant quota.

### Shutdown graces

Each grace is 0–60,000 ms. Once close begins the controller observes exit before signaling, then
uses fresh monotonic deadlines:

```text
SIGHUP / hangup-grace-ms
SIGTERM / terminate-grace-ms
SIGKILL / kill-reap-grace-ms
```

Input and resize are closed immediately when shutdown begins. Output remains drainable until the PTY
reports closure. Expiry after SIGKILL without a reap becomes an explicit controller timeout.

## Binding record grammar

The exact record is:

```text
iotox-terminal-binding-v1
principal=<64 lowercase hex characters>
profile=<profile-id>
enabled=<0|1>
```

Example:

```text
iotox-terminal-binding-v1
principal=0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20
profile=maintenance-shell
enabled=1
```

The principal is the nonzero 32-byte stable IoTox principal, not a transient Tox friend number. The
filename is exactly `<principal>.binding`. One principal may occur at most once in a registry
candidate. A binding may refer only to an existing profile.

## Registry replacement and OPEN resolution

`ProfileRegistry::replace` validates every profile and binding, rejects duplicate profile IDs,
ambiguous principal bindings, and references to missing profiles, and checks generation exhaustion
before mutating live state. A successful replacement atomically swaps vectors and increments the
64-bit generation. Invalid input leaves all prior records and the prior generation unchanged. The
committed vectors and generation share one reader/writer lock, so concurrent replacement, resolve,
and snapshot calls observe one complete generation rather than a mixed profile/binding view.

Resolution requires a loaded nonzero generation, an exact principal binding, and both binding and
profile enabled. It clamps requested dimensions and resolves the exact environment, then returns a
value copy containing profile, environment, dimensions, and policy generation. Mutation of the
caller's source objects after replacement cannot alter the committed registry. The resolved value is
immutable policy for one OPEN attempt; the R4 coordinator does not silently re-resolve midway through spawn.

## Native process boundary

The Linux backend allocates a PTY, uses the installed IoTox binary's hidden child entrance, transfers
a canonical bounded binary manifest over a private socket, and passes target/cwd by open descriptor.
The manifest and status sockets must be distinct stream sockets and must report one agreeing
kernel-authenticated parent PID/UID/GID through `SO_PEERCRED`; fd 0/1/2 must name the same PTY. The
reviewed child must emit a fixed readiness record immediately before final `fexecve`; only the
following close-on-exec EOF proves startup. Setup failure returns a stage and errno. A wrong ELF
helper that merely exits is rejected before readiness.

The target starts as a session and process-group leader with the PTY slave on fd 0/1/2, that PTY as
its controlling terminal, itself as the foreground group, the accepted initial window, core dumps
disabled, every catchable signal reset to its default disposition, requested limits applied,
`PR_SET_NO_NEW_PRIVS=1` set and verified, the complete ambient capability set cleared and verified,
requested identity applied and verified, parent-death `SIGKILL` armed and re-armed after credential
changes, `umask(077)`, and all original handoff descriptors closed.

## Explicit limitations

Profile v1 is local policy and process hygiene, not confinement. It does not provide namespaces,
seccomp filters, cgroups, mount isolation, capability dropping beyond any UID transition, an LSM,
container, VM, or full descendant ownership. A target may create a new session/process group and
escape later group signals unless deployment confinement prevents it. Same-UID replacement of
trusted executable content is outside this loader's guarantee. rev0020 retains default-off host
activation through the exact Agent gate and adds a separately gated same-user controller stream, but
still provides no PTY survival across daemon restart, complete reconnect qualification, or
production-support claim.

Ambient capabilities are the one explicit capability-inheritance exception: rev0020 clears them so
an ambient daemon capability cannot silently become final-target privilege. This is not a complete
policy for permitted, effective, inheritable, or bounding capability sets.
