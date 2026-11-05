# Sandpi: selected source passages

Read the embedded documentation alongside the [Sandpi introduction](../Sandpi.md). These passages come from the supplied 0.86.0 / rev0086, Orbit artifact. GitHub does not display the complete launcher because of its size; this page makes the cited material available without running it.

**Original source and documentation: sandpi contributors; supplied by h0p3. Selection and navigation: Lumen.** The extracts retain their exact source bytes and render as the Markdown carried inside the launcher. The original MIT license and its exclusions are reproduced at the end.

**Reading scope:** commands, authority statements and verification claims below belong to the supplied documentation. They are not present authorization, fresh execution results or evidence about a running machine. No launcher, materializer, VM, provider or source test was run to produce this page. Paths mentioned inside an extract are paths in the carried project, not new files in this reading page.

## Source identity

- Repository path: `Maintained Tools/sandpi`.
- Source commit: `26d2a9f3d360ca31dbc65e4d44fc6263221313be`.
- Git blob: `188c7fdab8ee3679318f445c22fa188c1db7fe74`.
- Original size: 4,828,827 bytes.
- Original SHA-256: `e006b77079bf87b1a2eb5b70def74eba4e55dedbce3bc03a4cf1d8546e9b5ea0`.
- [Pinned complete original](https://github.com/Sapient-Lumen/W4R3Z/blob/26d2a9f3d360ca31dbc65e4d44fc6263221313be/Maintained%20Tools/sandpi) · [Raw original for download](https://raw.githubusercontent.com/Sapient-Lumen/W4R3Z/26d2a9f3d360ca31dbc65e4d44fc6263221313be/Maintained%20Tools/sandpi).
- [Machine-readable source and excerpt identities](Sandpi-excerpts.json). Checksums cover exact excerpt bytes, including original line endings.

## Find a passage

- [Start here](#source-start-here)
- [Native packages and programmatic use](#source-packages-and-programmatic-use)
- [Session and workspace continuity](#source-session-and-workspace)
- [Host requirements](#source-host-requirements)
- [Resource profile](#source-resource-profile)
- [Files and caching](#source-files-and-caching)
- [Credentials](#source-credentials)
- [Cold checkpoints](#source-cold-checkpoints)
- [Network and explicit host-root mode](#source-network-and-host-root)
- [Project identity and live attachment](#source-project-identity)
- [Native Pi work loops](#source-loop-contract)
- [Original license and attribution](#source-license)

<a id="source-start-here"></a>

**Source excerpt: Start here.** Embedded `README.md`, original launcher lines 4714–4791. SHA-256: `c9c21349fddff97ea4090d4b9bf5e958faf3caf315e00ba628227fa4a934d13f`.

<!-- source-excerpt sandpi-L4714-L4791 -->

## Start here

From the directory you want the agent to work on, run the executable as your
normal Nix user. Do not prefix VM mode with `sudo`.

```bash
chmod +x /path/to/sandpi
/path/to/sandpi creds
/path/to/sandpi plan
/path/to/sandpi machine
/path/to/sandpi upgrade
/path/to/sandpi
```

`run` is the default command. The first actual launch builds missing pinned
dependencies, creates the room's persistent sparse disk and starts its NixOS guest.
Later launches reuse the Nix closures and the same room disk. A room is identified by the host-only stable project anchor and a validated name.
Without an explicit `--name`, Sandpi uses the project selector (initially the
implicit `default`). The first anchor preserves the legacy canonical-path room ID;
a later rename or move follows that same room. If an ignored-file cleanup removes
the anchor, a unique exact-object binding is recovered on the next real launch.
A copied or replacement identity is refused until you choose `project --new
--yes`, `project --recover [SHA256_PREFIX] --yes`, or an intentional `project
--rebind --yes` as appropriate.

Use plain `sandpi` unless you already know which initial state you want. It boots a
stopped room or re-enters a running one. Once Pi is open, prefer its native
`/resume`, `/new`, `/name`, `/tree`, `/fork`, `/clone`, `/model`, `/thinking`,
`/compact`, `/mcp`, and `/reload` commands. Use `sandpi up` only when you
specifically want the machine alive before opening Pi.

```bash
sandpi                                  # boot or re-enter; Pi owns initial selection
sandpi rooms                            # list this project's named machines
sandpi use experiment                    # make an existing room the plain-entry room
sandpi use --reset                       # return to the implicit default room
sandpi rename feature                    # rename the selected stopped room
sandpi rename new --name old             # rename an explicit stopped room
sandpi upgrade                           # inspect retained cold runtime rollback
sandpi backup create ~/backups/app-room --store full
sandpi backup inspect ~/backups/app-room --verify
sandpi backup import ~/backups/app-room restored --activate
sandpi --name default                    # one-command room override
sandpi up                               # detached selected room only; no Pi process yet
sandpi entries                          # active owner/secondary host entries
sandpi down                             # safe stop; refuses active entries
sandpi down --wait 30                   # drain active entries before stopping
sandpi down --force                     # explicit stop despite active entries
sandpi --RESUME                         # native latest session shortcut
sandpi --resume                         # native picker shortcut
sandpi gpt                              # initial GPT scope
sandpi gemini                           # initial Gemini scope
sandpi openrouter                       # bounded qualified free-coder selection
sandpi --paid --preset kimi             # exact paid coding model, no ladder
sandpi --RESUME --paid                  # resume with explicit paid permission
sandpi gpt --model YOUR_GPT_MODEL_ID
sandpi gemini --model YOUR_GEMINI_MODEL_ID
sandpi openrouter --model VENDOR/MODEL_ID
sandpi openrouter --model VENDOR/MODEL_ID --thinking high
sandpi openrouter --tool-profile classic
sandpi openrouter --full-pi             # Pi owns the active tool selection
sandpi --models 'openai-codex/*,google/*,openrouter/*'
sandpi --RESUME --resume-fallback best
sandpi gpt --BARE-METAL                 # explicitly root on your host
sandpi -- --session EXACT_PI_SESSION_ID
```

GPT/Gemini model IDs use Pi's native catalog. OpenRouter discovery includes exact
zero-price text models, including those without a `:free` suffix; prices are not
guessed from names. Explicit `--paid` also discovers validated priced text models. `sandpi models --refresh` refreshes that public catalog. `sandpi models --snapshots` and `--diff previous current` inspect the one retained local predecessor/current pair; add `--paid` for the full catalog. GPT uses shared Codex subscription credentials when present; native
OpenAI API-key mode is selectable as `sandpi openai`. Provider-only selection uses
Pi's model scope, because Pi does not accept `--provider` without `--model`.
Flags following `--` are Pi arguments. Sandpi's guest extension applies the
model-aware active-tool profile after Pi has selected or restored the physical
model. It treats Pi's current direct/MCP tool set as authoritative and manages only
Codemode presence versus classic presentation; text-only catalog entries receive a
temporary empty active-tool set. Raw Pi tool flags, native wildcard patterns,
`--no-mcp`, and `--full-pi` remain Pi-owned process policy.

<!-- /source-excerpt sandpi-L4714-L4791 -->

<a id="source-packages-and-programmatic-use"></a>

**Source excerpt: Native packages and programmatic use.** Embedded `README.md`, original launcher lines 4852–4903. SHA-256: `b3d291f54071f86486e0791d0f00c0a09b45b54cdaf0b04907327ee474e54121`.

<!-- source-excerpt sandpi-L4852-L4903 -->

## Pi packages and addons live in the room

Install and operate normal Pi packages from the guest:

```bash
pi install npm:@example/pi-tools@1.2.3
pi install git:github.com/example/pi-tools@COMMIT
pi list
pi config
pi update --extensions
pi update --models
```

Those packages, their helper processes, MCP servers and dependencies execute in
the VM and persist on that room's disk. Every room keeps its own writable Pi agent
state; concurrent VMs do not mutate one shared `~/.pi/agent`. Nix/store reuse and
ordinary package caches avoid needless downloads without conflating room state.

`@sandpi/core` is different only in provenance: it is supplied by the pinned
Sandpi Nix closure and reconciled before every wrapped Pi invocation. It contains
the credential-bank provider wrappers, free-model policy, profile/session
continuity hooks and Sandpi slash commands. A small room-global base record is
projected into a unique fixed-schema invocation record before each Pi process; the
host never becomes a second Pi session engine and invocation records never contain
prompt or transcript content.

`pi update`, `pi update --self`, `pi update self`, `pi update pi`, and
`pi update --all` are refused because they would replace the tested Pi executable
inside one room. Upgrade Sandpi to change Pi. Updating packages or the model
catalog remains native Pi behavior.

## Headless and programmatic Pi

Print, JSON and RPC automatically use a non-PTY path and never drop into a
guest shell or put a shell banner in stdout. When they boot a stopped owner room,
Pi completion stops that room; when they re-enter an already-running room, only
the new Pi process exits and the machine remains live. Boot probes do not read
your stdin. For one-shot print/JSON calls launched from a terminal, unused
terminal input is closed so Pi does not wait for an extra Ctrl-D; actual piped
input and RPC streams are preserved. Diagnostics stay on stderr.

```bash
git diff | sandpi gpt -- --print 'Review this change'
sandpi gemini -- --mode json 'Inspect the project' > events.jsonl
sandpi openrouter --model VENDOR/MODEL_ID -- --mode rpc --no-session
```

RPC callers must keep reading stdout, correlate responses by ID, and close stdin
to request orderly shutdown. An accepted prompt or `agent_end` is not completion;
wait for `agent_settled`. Split JSON records on LF, not Unicode line separators.
The included no-inference RPC acceptance test exercises these transport details.
The usual Pi-to-shell handoff remains the default when attached to a terminal.

<!-- /source-excerpt sandpi-L4852-L4903 -->

<a id="source-session-and-workspace"></a>

**Source excerpt: Session and workspace continuity.** Embedded `README.md`, original launcher lines 4905–4955. SHA-256: `255ff8df9f4e1cca47aa0fbc23aa370591f80004208ff829469969c7bcbccef7`.

<!-- source-excerpt sandpi-L4905-L4955 -->

## Pi owns sessions; Sandpi supplies narrow continuity policy

The normal interactive surface is Pi itself:

```text
/resume          choose another native session
/new             start a new native session
/name            name the current thread
/copy            copy the last assistant reply through the terminal clipboard
/tree            move within the conversation tree
/fork /clone     create a separate session from native history
/model           switch GPT, Gemini or a free OpenRouter model
/thinking        choose an available reasoning level
/compact         compact native context
/mcp /reload     manage Pi integrations
/sandpi          explain the room/Pi boundary
```

Uppercase `sandpi --RESUME` is an ergonomic alias for Pi's native `--continue`;
lowercase `sandpi --resume` opens Pi's picker. The shortcut does not create a
Sandpi transcript or parallel conversation database. Pi remains the only parser
and owner of its append-only session tree.

Sandpi defaults Pi to regular TUI mode. The caller's terminal therefore owns
scrollback and highlighted-text copying across the SSH/vsock boundary. An existing
personal `tuiMode` setting is preserved, and `--tui-mode fullscreen` overrides the
default for one invocation. In either mode, native `/copy` copies the last
assistant response via the available clipboard transport. `Ctrl+C` is Pi's
clear/exit action, not the terminal copy shortcut.

Sandpi performs one deliberately narrow preflight for deterministic `--continue`:
it asks the pinned Pi `SessionManager` which branch Pi will select for the exact
active cwd and
copies only the selected session identity, physical model, thinking level,
branch-local profile, transport and Gemini affinity into the runtime policy. This
lets the guest package refuse a silent startup substitution, preserve a signed
Gemini conversation's key affinity, or record an explicit OpenRouter handoff.
Picker, `/resume`, `/tree`, `/fork`, `/clone`, `/model` and ordinary session work
remain native Pi operations.

Inside Pi, `/sandresume` reports the preflight and final outcome;
`/sandprofile` reports or changes the branch-local presentation;
`/sandroute`, `/sandmodels`, and `/keys` expose model/key evidence without becoming
conversation authority. The host `sandpi sessions` command is a transcript-free
observation index for diagnostics only. It stores no prompts, answers, tool calls,
usage or cost.

A Pi conversation branch is not a filesystem snapshot. `/tree` can move to an
older conversational branch while `/workspace` still contains current files. Use
Git, a separate room/clone, or a stopped-room disk checkpoint when filesystem
rollback matters.

<!-- /source-excerpt sandpi-L4905-L4955 -->

<a id="source-host-requirements"></a>

**Source excerpt: Host requirements.** Embedded `README.md`, original launcher lines 4957–4985. SHA-256: `3b388c2137f8e7345cea56f94dbcc5c1f78cb09f8b6c5e08bb55737749315e12`.

<!-- source-excerpt sandpi-L4957-L4985 -->

## Host requirements and dependency installation

The host is Linux with an existing Nix installation, KVM, cgroup v2, a systemd user
session, systemd-run 254+ and unprivileged user/mount namespaces. Targets are `x86_64-linux` and
`aarch64-linux`. This is not macOS virtualization or a software-emulation fallback.

```bash
sandpi doctor
sandpi setup              # prebuild the guest and missing host tools
sandpi doctor --fix       # build tools and repair current-user KVM access
```

If Python 3.11+, coreutils or `flock` is absent, the shell first obtains them
through the pinned Nix input. The build then supplies Pi, Cloud Hypervisor,
virtiofsd, passt, SSH, filesystem tools and the NixOS guest. It does not install
anything with apt, npm's mutable latest tag, or an unpinned curl-to-shell installer.

Missing KVM permissions may trigger `sudo` for a targeted module load and a
current-user `/dev/kvm` ACL. This is not host-root execution of Pi. Disable that
repair with `--no-host-fix`. Persistent NixOS host settings are illustrated in
`examples/host.nix`; kernel capabilities and a login session are not ordinary
packages that a user-space launcher can manufacture.

Pinned inputs: Pi 1.1.0 at a fixed commit; the supplied Sandcodex nixpkgs revision
and NAR hash; Cloud Hypervisor 53.0 and the other tools provided by that nixpkgs.
`pins.json` records the identities. Each build retains its generated `flake.lock`
and a build receipt. The managed OpenRouter catalog has a six-hour freshness window and a bounded
stale-cache fallback. Native GPT/Gemini catalogs and user extensions retain Pi's
normal behavior; binary pinning is not a claim to freeze remote model offerings.

<!-- /source-excerpt sandpi-L4957-L4985 -->

<a id="source-resource-profile"></a>

**Source excerpt: Resource profile.** Embedded `README.md`, original launcher lines 4987–5037. SHA-256: `60b39286c7accac3de15adc29a857b334f58d44ab6a2f442cf791d0bcf9e5736`.

<!-- source-excerpt sandpi-L4987-L5037 -->

## Resource defaults and Cloud Hypervisor recommendation

### Persistent machine profile

CPU, total room memory, disk capacity, Nix cache mode, and TCP/UDP forwards are
machine settings. They are calculated for a new room, then saved after launch and
reused by plain `sandpi`. They do not follow a Pi session and they do not select a
provider. Inspect or forget them with `sandpi machine`; forgetting them preserves
the disk and every in-guest Pi artifact.

When an explicit machine option is supplied for a stopped room, it replaces that
saved field. Repeating `--publish` builds the complete replacement TCP set for that
launch; use `--no-publish` or `--no-publish-udp` to clear a saved protocol set.
Changing a live room is refused because Cloud Hypervisor and its host cgroup are
already constructed. Stop it, then relaunch with the new value.

| Item | Default / behavior |
|---|---|
| Guest processors | Half effective host logical CPUs, rounded down; minimum one |
| Total room RAM budget | Half effective host RAM, including host-side VMM/backends |
| Guest RAM | Budget minus at least 512 MiB and normally at least 1/16 overhead |
| Aggregate active rooms | One per-user half-host CPU/RAM slice; memory reservations prevent oversubscription |
| Guest disk | 100 GiB sparse ext4, persistent, created only when absent |
| Boot | Direct pinned Linux kernel and initramfs; no firmware or RAM snapshots |
| Lifecycle | systemd user service, whole-cgroup stop, graceful power-button request first |

Memory means the whole room, not just the emulated RAM. For example, a 16 GiB
room budget normally gives the guest 15 GiB and retains 1 GiB for host processes.
Large initial host-store leases increase the reserved backend share within the
same total budget (a 768 MiB floor plus 8 KiB per leased path, rounded to 128
MiB); a too-small room fails before VM launch with an instruction to increase
`--memory`.
CPU limits count VMM and backend CPU too. The half-host slice remains an aggregate
cap when several rooms run. Specify smaller individual budgets for concurrent
rooms; two default-size rooms will not both reserve the same half of host memory.
On a one-logical-CPU host the minimum one vCPU necessarily exceeds literal half.

```bash
sandpi machine                         # saved profile or current-host preview
sandpi --cpus 4 --memory 8G           # persists for this project/name room
sandpi --name worker-a --cpus 2 --memory 4G
sandpi --name worker-b --cpus 2 --memory 4G
sandpi disk-grow 150G                 # stop first; saved disk capacity follows
sandpi machine --reset --yes          # preserve disk/Pi state, forget defaults
```

`--memory` accepts binary sizes or percentages of effective host memory. Limits
above the half-host pool are rejected. The default 100G is logical capacity, not
100G eagerly written. Host logs, Nix builds and retained host store paths are
outside that disk's capacity; it is not a total host disk quota. No existing disk
is reformatted, no automatic shrink is attempted, and a failed boot preserves it.

<!-- /source-excerpt sandpi-L4987-L5037 -->

<a id="source-files-and-caching"></a>

**Source excerpt: Files and caching.** Embedded `README.md`, original launcher lines 5039–5105. SHA-256: `d3970f2c33b5a0b7ea96713c867bb1ae6b943860b14464120089fa6fb5180793`.

<!-- source-excerpt sandpi-L5039-L5105 -->

## Files and caching

The selected project root is a **live writable virtiofs share** at `/workspace`.
Pi and the first guest shell start in the validated relative caller directory below
that root, while the share itself remains the whole anchored project. Changes and
deletions affect that directory immediately; this is not a throwaway copy. Files created by guest root or guest Nix build users are owned by the
launching host user. Other host directories are not donated just because a
symlink in the project points to an absolute host path.

The project's `.sandpi` is replaced inside the VM by an empty read-only mount.
When the project encloses global sandpi or Sandcodex control state, the top-level
component containing that state is masked too. A project directly inside sandpi
state or Sandcodex's credential directories is rejected. Ordinary Sandcodex
project clones elsewhere under its global tree may be used. Symlinked exclusion
directories are rejected rather than followed.

The host `/nix/store` is exposed through one read-only virtiofs view. An
OverlayFS upper/work pair on the guest's persistent root gives the guest a
writable `/nix/store`. A Nix registration stream—not a live SQLite copy—registers
the exact leased paths in the guest database, and matching store content is reused
without copying it into every disk. The broader host-store listing is visible to
guest root; it is not a secret or exact-subset boundary.

```bash
# In the guest:
nix shell nixpkgs#hello
nix profile install nixpkgs#ripgrep
nix build nixpkgs#jq
nix-collect-garbage
```

The default `--store-cache host` registers an initial snapshot of realized host
store objects and their references. Later starts preserve that lease and add the
current pinned Sandpi runtime closure; unrelated host builds do not churn the
room's registration identity. It does not realize unrelated `.drv` files
just to cache them; that would unexpectedly build their outputs. GC roots are kept on **both host and guest** so subsequent garbage
collection does not remove dependencies needed by persistent rooms. One small
aggregate Nix object records the full reference graph on each side; Sandpi does
not create one GC-root symlink per host object. This is intentionally
retention-heavy. The legacy `--store-cache base` spelling is accepted,
but is promoted visibly to `host`: a smaller registration set is unsafe when the
guest can see the full read-only host store, because guest GC would treat visible,
unregistered objects as disposable.
`sandpi cache-info` shows the retained path count.

A first boot on a host with a very large Nix database can spend several minutes
importing registration metadata before SSH is declared ready. The default
`--boot-timeout 600` covers that bounded preparation. Later launches verify the
retained lease and registration segment hashes without reevaluating its complete
Nix reference graph; the guest loads only segments it has not already marked as
imported. A shorter explicit deadline still fails closed and preserves room logs
for diagnosis.

Guest-installed packages persist in that room. They are not automatically copied
back to the host or deduplicated across other rooms. The host and guest GC roots
protect every path in the room's launch-time lease. Host-store objects created
after launch can become visible before the guest database knows about them; do not
run guest GC concurrently with host Nix mutation. They are outside the durable
lease unless a Sandpi runtime update itself requires them.
See `docs/ARCHITECTURE.md` before manually pruning global cache roots.

The immutable read-only store, workspace, and seed shares use virtiofs
`cache=auto`. This avoids replaying large immutable closure metadata during every
switch-root while the room service's explicit descriptor and memory limits remain
in force. Real VM gates execute Pi and Nix programs through the cached lower view.
Host and guest should not concurrently edit the same workspace file expecting
transactions.

<!-- /source-excerpt sandpi-L5039-L5105 -->

<a id="source-credentials"></a>

**Source excerpt: Credentials.** Embedded `README.md`, original launcher lines 5150–5187. SHA-256: `3d97088a23b6cdb9b793e4adad9f0381feabe37ef890f347cbea1445eb547bc6`.

<!-- source-excerpt sandpi-L5150-L5187 -->

## Shared Sandcodex credentials

The canonical root is `$SANDCODEX_GLOBAL_ROOT`, otherwise
`~/.sandstuff/sandcodex`. Override with `--credentials-root PATH`.

| Provider | Existing canonical file |
|---|---|
| GPT / Codex subscription or OpenAI API key | `auth-home/auth.json` |
| Gemini bank | `remote/gemini-keys.txt` |
| Gemini single-key fallback | `remote/google-ai-studio-api-key.txt` |
| OpenRouter bank | `remote/openrouter-keys.txt` |

Sandcodex's `auth-home/auto-import-disabled` logout marker wins over any stale
auth copy. Broken/expired GPT subscription state does not silently switch to
OpenAI API billing; choose `openai` explicitly when that is intended.

No independent credential bank is created. No login is performed by this revision.
Use Sandcodex's existing login/key-bank setup, then launch sandpi. Metadata-only
inspection is `sandpi creds --json`; select a bank label with `--gemini-key LABEL`
or `--openrouter-key LABEL`. Unpinned banks now balance through shared request
leases with classified cooldowns; Gemini continuations retain key affinity.
There is no silent physical-model fallback, room-wide spend firewall or quota-
evasion system. `sandpi keys` shows usage and cooldown metadata.

A host broker reads these files on demand. Native Pi provider resolvers obtain
API keys or access tokens through vsock; model HTTP requests originate normally
from the guest. **Access tokens and API keys used by Pi are available to guest
root.** Codex refresh tokens remain in the canonical host file and are refreshed
there with locking, ownership preservation and compare-and-swap checks.

**Existing Sandcodex 0.88.0 has a refresh/reconciliation race:** its frontend can
later promote a stale auth copy without honoring sandpi's lock. Sandpi protects
its own writes but cannot stop the unchanged old launcher from overwriting a
newer file. Prefer non-overlapping Codex OAuth refresh windows until the small
Sandcodex-side CAS change described in `docs/CREDENTIALS.md` is adopted. API-key
bank sharing does not have that rotating-token race. Do not solve it by creating
an unrelated Pi login: that would violate the shared-credentials requirement.


<!-- /source-excerpt sandpi-L5150-L5187 -->

<a id="source-cold-checkpoints"></a>

**Source excerpt: Cold checkpoints.** Embedded `README.md`, original launcher lines 5188–5206. SHA-256: `6989ff2b201c34751370238b56e0e8a05b92d05644ae804f6cf80b1d403fc76f`.

<!-- source-excerpt sandpi-L5188-L5206 -->

## Cold checkpoints and restore

```bash
sandpi checkpoint before-experiment       # selected room must be stopped
sandpi checkpoint                         # list checkpoints
sandpi restore before-experiment --yes    # stopped room; saves current disk first
```

These are **guest-disk-only, host-local checkpoints**. They include the guest's
Pi sessions and installed packages, not VM RAM, your canonical host credentials,
or the live host project. Restoring a guest never undoes project edits. Use Git
or your normal project backup procedure for those files.

A checkpoint uses a filesystem reflink when supported, otherwise a sparse copy.
Restore builds a replacement before touching the current disk and retains an
automatic `before-restore-*` checkpoint. A fully allocated disk can require
substantial free host space; a sparse 100G capacity is not a storage reservation.
Checkpoints still depend on the retained host Nix-store lease and are not portable
machine backups. Details and recovery recipes are in `docs/OPERATIONS.md`.

<!-- /source-excerpt sandpi-L5188-L5206 -->

<a id="source-network-and-host-root"></a>

**Source excerpt: Network and explicit host-root mode.** Embedded `README.md`, original launcher lines 5207–5249. SHA-256: `8d05184b0147fec1822ab9834a4b07d79032c4974d822da9ac836d0d842c5ba9`.

<!-- source-excerpt sandpi-L5207-L5249 -->


## Network

**No sandpi network policy.** Guest firewall is disabled; no egress allowlist,
private-LAN/metadata blocking, provider-only routing or host firewall rules are
installed. Passt provides ordinary outbound TCP/UDP connectivity and ICMP echo.
It is a userspace IP connection backend, not a raw Ethernet bridge.

```bash
sandpi --publish 8080:8080 --publish 3000:3000   # replace saved TCP set
sandpi --publish-udp 5353:5353                         # replace saved UDP set
sandpi --no-publish                                    # clear saved TCP set
sandpi --no-publish-udp                                # clear saved UDP set
```

Inbound publication is explicit to avoid automatic host port collisions, then it
persists as part of the room's machine profile. Omit the flags on later launches
to keep the saved set. Change or clear it only while the room is stopped. Terminal
access and credential resolution use vsock, independent of guest DNS. Inspect
`sandpi logs --file network` for passt problems. Whatever the existing host
network or upstream service permits still applies.

## Explicit host root: --BARE-METAL

```bash
sandpi --BARE-METAL
sandpi --BARE-METAL gemini --model YOUR_MODEL_ID
```

This deliberately runs Pi and its subprocesses with **actual UID 0 on the host**
and then opens a host-root shell. It is not a renamed sandbox. No VM, guest disk,
workspace masking, half-host resource limit or host-file protection is applied.
The normal-user parent keeps the credential broker alive and updates canonical
auth as that user; `sudo -H` starts the explicitly privileged frontend.

The exact uppercase flag is required. A VM failure never switches to bare metal.
VM-only `--cpus`, `--memory`, `--disk-size`, `--store-cache`, and publish/clear
flags are rejected rather than ignored, and malformed VM room metadata does not
block an explicitly selected host-root process. The flag itself is the explicit
request; there is no extra interactive consent wizard beyond sudo's normal
authentication. Exit Pi, then exit that root shell, to return to the original
unprivileged shell. Bare Pi state is separate from the VM's native sessions and
lives under global `bare/<room-id>/agent`.

<!-- /source-excerpt sandpi-L5207-L5249 -->

<a id="source-project-identity"></a>

**Source excerpt: Project identity and live attachment.** Embedded `docs/ARCHITECTURE.md`, original launcher lines 5372–5480. SHA-256: `d8dbd13b884e96b411cf511c458ea32f48629edda2a2840ba9bb13ff1dd73001`.

<!-- source-excerpt sandpi-L5372-L5480 -->

## Stable project identity, recovery and live workspace attachment

The host project has a tiny fixed-schema anchor at `.sandpi/project.json`. The
first value is the canonical path used by older revisions, preserving every
existing room ID. Room identity is `hash(anchor namespace, room name)`; moving the
path therefore does not rename the room directory or guest disk.

A second, optional fixed-schema file at `.sandpi/room-selection.json` records the
name that an omitted `--name` means for this project. Its absence means the
implicit `default`. It is a host convenience pointer, not machine authority and
not conversation state. The file is namespace-digest bound, owner/private/single-
link validated, atomically replaced, and hidden with the rest of `.sandpi` from
the guest. The selected room must already exist; stale pointers fail closed.

The anchor is not trusted alone. A central binding under `SANDPI_HOME/projects/`
records the namespace, current canonical path, `st_dev`, and `st_ino`. The tuple
identifies an inode only within its filesystem, which is exactly what is needed to
distinguish an atomic same-filesystem rename from a copied or replacement
directory. `bound` requires both path equality and filesystem-object equality.
An unchanged pathname with a different object is `replaced-at-same-path`, not a
valid binding.

### Project root and Pi working directory

Sandpi now resolves two related paths for every host entry:

```text
persistent project root  -> room ID, machine profile, live virtiofs share
entry working directory  -> Pi cwd, project resources, native session group
```

When `--project` is absent, the closest ancestor that already contains a
`.sandpi` directory is the project root. If no such ancestor exists, the exact
current directory is retained as the first-use root. Sandpi does not infer a Git
root: repository topology and machine ownership are different concepts, and a
nested repository may intentionally have its own room. `--project` explicitly
selects a root; the caller cwd is retained only when it resolves inside that root.

For VM entry, a relative host cwd is mapped beneath `/workspace`; for bare metal it
remains the canonical host path. The guest launch seed carries both `workspace`
and `workdir`. Before Pi or Bash runs, the guest resolves both and requires the
workdir to be a real directory inside the workspace. A path that disappeared
between host planning and guest entry therefore fails instead of silently falling
back to the root. Secondary attach and exec derive a fresh cwd from the invoking
host process rather than inheriting the owner entry's cwd.

This preserves Pi's native semantics. Pi uses cwd for project settings, context
files, package/resource discovery, and session grouping. Root and nested
conversations can share one machine and filesystem while remaining separate native
Pi session groups. The host index stores mode and cwd only as transcript-free
advisory metadata. Exact mode/cwd rows are preferred; a legacy row with neither
field is a bounded migration fallback; a known row from another cwd is never used.

The selector rejects broad system roots, the whole home directory, either control
root containing the project or being contained by it, and `.sandpi` as the Pi cwd.
The host-only `.sandpi` directory remains an empty read-only mask in the VM.

### Missing-anchor resolution

Anchor deletion is recoverable from host evidence without making the central
binding a second mutable room selector. Read-only resolution follows this order:

1. A valid project anchor is authoritative.
2. With no anchor, scan at most 4,096 strict central bindings. One namespace whose
   device/inode equals the current project is a strong automatic candidate. Path
   equality distinguishes `exact-object` from `same-object-moved` only for
   diagnostics.
3. Strict `room.json` records that name the current path can supply weaker
   `room-path` evidence when the binding was lost. A same-path binding with a
   different inode supplies `path-replaced` evidence.
4. Weak or ambiguous evidence never changes normal room lookup. The operator must
   explicitly select recovery or create a new lineage.

The binding root and each candidate file are checked for owner, type, link count,
size, schema, namespace digest and filename. Room receipts must match their room
ID derivation. Discovery never parses Pi's session directory, transcript JSONL,
prompt/model/tool content, guest filesystem, or workspace files.

`plan` remains side-effect free. It may present a unique strong candidate as a
`binding-recovery-preview`, preserving the effective namespace and room ID in
memory. The first state-changing launch reacquires the project lock, recomputes
evidence, and writes the anchor only if the candidate still matches.

Anchor recreation and binding publication form one transaction. The project lock
remains held while stopped-room path metadata and transcript-free host session
observations are migrated and the central binding is published. If anything
raises, only the exact anchor created by that transaction is removed and staged
host metadata rolls back before locks are released. A manually or concurrently
replaced anchor is never unlinked.

Unqualified explicit recovery requires one namespace. Ambiguous recovery can be
selected only by an 8–64 character prefix of the namespace SHA-256 printed by
`sandpi project`; the prefix must identify exactly one namespace.

### Move and live attachment

Rebinding is a stopped-room transaction. The namespace lock and all matching room
preparation/lifetime locks remain held while room/status metadata and the
transcript-free session observation index are staged and the central binding is
published. A publication exception restores those staged documents before locks
are released. No native Pi session, conversation entry, tool result, or compaction
record is parsed or rewritten.

The live workspace is still a virtiofs mount of one host directory object. Linux
same-filesystem rename preserves that object, so a live room remains coherent after
an inode-preserving rename. A cross-filesystem move is a copy plus deletion, and an
archive/checkout replacement at the same path also creates a new object. The live
guest still has the old object mounted. Sandpi refuses entry in that state and
requires stop/relaunch plus an explicit recover/rebind/new decision.

<!-- /source-excerpt sandpi-L5372-L5480 -->

<a id="source-loop-contract"></a>

**Source excerpt: Native Pi work loops.** Embedded `docs/PI-WORK-LOOP.md`, original launcher lines 16135–16225. SHA-256: `b990c8e8765d8248fa8e5ff7edcc3b510c2b7c048458c45e24f59037b7fb6b9b`.

<!-- source-excerpt sandpi-L16135-L16225 -->

# Native Pi work loops

Sandpi rev0086 adds a small, bounded continuation primitive inside the pinned Pi
runtime. It is for work that benefits from several autonomous review-and-improve
passes without replacing Pi's conversation engine.

```text
/loop "make the parser robust and test it"
/loop 12 "finish this refactor, verify it, then red-team it"
/loop status
/loop stop
/loop help
```

`/loop "objective"` defaults to five passes. An explicit leading integer chooses
from 1 through 100 passes. Quotes are optional for a multiword objective; they
mainly make the boundary easy for a human to see.

## What a pass means

A pass is one **complete Pi agent settlement**. It is not one provider request.
A pass can contain the model's normal tool calls, native automatic retries and
native compaction, so request and cost counts can exceed the pass count. The next
pass is inserted only at Pi's final actionable `agent_before_settle` boundary.

Every continuation remains part of the same native Pi conversation. Sandpi does
not change the selected model, thinking level, active tool loadout, paid-access
permission, provider policy, credential route, project authority or compaction
settings. The ordinary provider layer still owns key leasing and its existing
no-replay-after-visible-output behavior.

Each visible continuation repeats the user's objective and asks the model to
reconcile earlier claims with durable state, avoid repeated work, verify changes,
and use already-satisfied passes for review or red-teaming. This is instruction
scaffolding at the user's existing authority, not a judge or proof that progress
was made.

## Stop and failure behavior

- `/loop stop` records a stop request. The current pass may finish, but Sandpi
  does not schedule the next loop pass.
- Escape aborts current work and closes the loop.
- A provider/agent error closes the loop without a loop replay.
- The incoming boundary preview describes context before the loop's draft. The
  visible continuation makes the final context runnable; Pi validates that final
  context after every handler. If it still rejects continuation, final settlement
  records a durable failed loop rather than replaying work.
- Session switching, forking, tree navigation, reload/shutdown and process exit
  retire the process-local loop authority. A surviving `running` marker is shown
  as `interrupted`; it never causes automatic inference on a later process.
- Continuations requested independently by another Pi extension remain that
  extension's responsibility. `/loop` neither cancels nor claims them.

The loop is deliberately finite. Re-arm it after inspecting the result rather
than creating an unattended, unpriced forever loop.

## Durable state and privacy

The actual objective lives in ordinary visible Pi conversation messages. Loop
status entries are excluded from model context and retain only:

- a random loop ID;
- running/stopping/completed/aborted/failed/stopped state;
- current, completed and requested pass counts; and
- the SHA-256 digest of the objective.

`/loop status`, `/loop stop` without an active run and `/loop help` make no model
request. Malformed newest loop metadata fails closed instead of rolling back to
an older apparently valid entry.

## Non-goals

The command is not a Sandcodex campaign, recursive worker tree, background host
daemon, success detector, hidden evaluator, model fallback, billing grant,
credential scheduler or permission boundary. Pi and the selected model still do
the work; normal human review and project verification remain necessary.

## Verification

`tests/node/loop.test.mjs` covers parsing, completion, five-pass sequencing,
content-minimized state, stop, Escape/error behavior, pre-draft boundary context,
busy-state rejection, session retirement, stale-process behavior and malformed
state. `tests/node/extension.test.mjs` loads the complete TypeScript extension and
ensures the command composes with the existing Pi lifecycle handlers.

`python3 tools/acceptance.py --stage loop --output FRESH_DIRECTORY` drives two
passes through the actual pinned Pi RPC runtime and local synthetic OpenRouter
adapter. It verifies native tool continuation, one pre-content key failover, two
settlement boundaries, visible loop context, final durable state, unchanged
session/model/thinking and inference-free `/loop status`. It uses no real key or
provider and does not establish model usefulness or TUI rendering.

<!-- /source-excerpt sandpi-L16135-L16225 -->

<a id="source-license"></a>

**Source excerpt: Original license and attribution.** Embedded `LICENSE`, original launcher lines 4040–4067. SHA-256: `ef4651ca604cfe94b1ba4fca1d13885c84816f0942548f0a3c7cfb278afef9dd`.

<!-- source-excerpt sandpi-L4040-L4067 -->

MIT License

Copyright (c) 2026 sandpi contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This license covers the original sandpi integration sources, not independently
licensed upstream packages fetched by Nix. Pi, NixOS, Cloud Hypervisor, virtiofsd,
passt, Linux and other dependencies retain their respective upstream licenses.

The Sandcodex reference excerpts under tests/fixtures and the exact coding-course
payload in src/benchmark_course.py are user-supplied reference material; this license does not relicense that original source.

<!-- /source-excerpt sandpi-L4040-L4067 -->

[Sandpi introduction](../Sandpi.md) · [Maintained Tools](../../Maintained%20Tools/README.md) · [Preservation and rights](../../PRESERVATION.md) · [Catalog](../../CATALOG.md)
