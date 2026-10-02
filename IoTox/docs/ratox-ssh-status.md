# Ratox and SSH status

Status: founding-machine Ratox v1 construction complete; manual mode remains default-off, while
`--mode self` makes the Ratox host and local terminal controller default-on for self-owned machines.
Native activation and daily-driver graduation porches now exist, but production
claims remain host/route/operator bounded. Updated 2026-10-01.

## For an outsider: what Ratox is

Ratox is IoTox's remote interactive terminal. It gives an owner a terminal-shaped connection to a
device over Tox without requiring the device to expose an SSH port, possess a public address, or
depend on a vendor coordination account.

There are three separate decisions, which is the heart of the design:

1. Tox answers **how encrypted bytes reach this peer**.
2. IoTox's stable device identity and signed authority ledger answer **which principal may request a
   terminal**.
3. A profile installed by the device owner answers **which exact local program, arguments,
   environment, directory, resource limits, and confinement policy that principal may reach**.

The remote peer supplies terminal input, not a command line. If the owner binds that principal to a
shell profile, the peer gets that shell. If the owner binds it to a serial-console, diagnostic, or
single-purpose maintenance profile, the peer cannot turn it into a general shell merely by changing
the request.

The ordinary flow is:

```text
device owner installs and binds a local profile
        ↓
both IoTox peers authenticate a current Tox application session and authority proof
        ↓
operator runs: iotox terminal PEER_PUBLIC_KEY_HEX
        ↓
device starts the owner-selected program inside a PTY and requested confinement
        ↓
terminal bytes, resize, detach, replay, and explicit resume travel over Ratox v1
```

A route outage detaches the controller while the device Agent and PTY remain alive. The ordinary
`terminal --reconnect` command can wait for a higher authenticated Tox application epoch and resume
only that exact session; explicit `terminal-resume` remains available. If the IoTox device daemon
itself dies, today's PTY dies with it; route reconnection and daemon-crash persistence are
intentionally different claims.

The name comes from the older `ratox` Tox client, which made peer interaction feel like ordinary
Unix files and FIFOs. IoTox keeps that composable Unix instinct but replaces implicit friendship,
buffering, identity, and retry assumptions with typed authority, bounded replay, and explicit
failure states.

The shortest useful analogy is: **an owner-approved login shell reached through Tox, with a
detachable PTY and a separate capability ledger**. The executable at the boundary is still fixed
like forced-command SSH. Once that executable is the owner's real login shell, however, the owner
can do ordinary interactive shell work and can invoke the host's own `sudo` policy. The differences
matter more than the slogan, but it puts the idea in the right neighborhood.

Self mode is the product shape for that daily-owner case:

```sh
iotox init plan --root ~/.local/state/iotox --mode self --enable-sync
iotox init write-config --root ~/.local/state/iotox --mode self --enable-sync
```

It selects both Ratox roles by default. It still does not choose a shell, bind a principal, grant
`interactive.terminal`, or enable sudo; those remain explicit owner decisions.

For daily setup, the grouped porch is:

```sh
iotox terminal daily-plan --root ~/.local/state/iotox --peer alias:desktop
iotox terminal daily-status --root ~/.local/state/iotox --peer alias:desktop
iotox terminal service plan --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit iotox-self \
  --binary /usr/bin/iotox
iotox terminal service render --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit iotox-self \
  --binary /usr/bin/iotox \
  --raw > ~/.config/systemd/user/iotox-self.service
iotox terminal service receipt --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit iotox-self \
  --binary /usr/bin/iotox \
  --accept-operator-responsibility \
  --out ~/.local/state/iotox/terminal-service.receipt
iotox service plan --target all --root ~/.local/state/iotox \
  --manager systemd-user \
  --unit-prefix iotox-self \
  --binary /usr/bin/iotox
iotox terminal doctor
iotox terminal activation-check --root ~/.local/state/iotox --peer alias:desktop
iotox terminal graduation-check --root ~/.local/state/iotox --peer alias:desktop
iotox ship-check terminal stable
iotox terminal profile plan shell owner-shell "$USER" \
  --store ~/.local/state/iotox/ratox
iotox terminal profile check ./owner-shell.profile
```

`terminal daily-plan` collects the service/run-check/status/session/reconnect/profile commands an
operator normally needs. `terminal daily-status` is the non-failing daily
dashboard/runbook form: it prints the same core commands, points at the strict
`terminal activation-check` gate, and reports that production activation still
requires that fail-closed check. `terminal service plan|render|receipt`
generates reviewed service-manager artifacts and a content-free legacy
`service-supervision=terminal.service.*` receipt without claiming systemd is
active, cgroups are delegated, or routes are qualified. `terminal profile check` decodes a profile record and hashes the live pinned
executable, plus the rescue `toybox` payload when present, so stale shell paths or byte mismatches are
visible before install/bind/use.
Use the top-level
`iotox service plan|render|receipt|status-plan|status-receipt` command when
you want the full resident shape: Agent/sync/Ratox plus the person messenger
background worker, with systemd-user, NixOS-user, NixOS-system, or
MonsterNix-adapter output. The render receipt is the broader
operator-reviewed service shape. The status receipt is the preferred
`terminal.service-supervision` stable evidence after the service is active,
enabled/static/managed, logs are reviewed, health passes, and the upgrade
check passes. It still does not prove routes, cgroups, sync health, or person
read state.

`terminal activation-check` is the fail-closed daily-driver gate. With no evidence labels it exits
blocked and prints the exact doctor, daily-control, delegated cgroup, service, reconnect, and
profile-freshness commands to run. A fully labeled invocation can record operator custody:

```sh
iotox terminal activation-check --root ~/.local/state/iotox --peer alias:desktop \
  --evidence daily-control=local.gate \
  --evidence profile-freshness=profile.check \
  --evidence service-supervision=terminal.service.systemd-user \
  --evidence reconnect-continuity=cli.reconnect \
  --evidence cgroup-delegation=nixos.cgroup \
  --evidence route-loss=tox.loss
```

That output says `production-activation=operator-attested` and
`repo-certified=0`. The labels are content-free operator evidence, not
cryptographic proof that another host, sudo policy, network route, or future
kernel will behave the same way.

`terminal graduation-check` is the stricter daily-driver gate. It reprints the
daily-plan, activation-check, service, session, reconnect, profile-freshness,
sudo-profile-freshness, cgroup, long-soak, direct route-loss, impairment, Tor,
and I2P proof commands, then fails closed until these labels are present:

```sh
iotox terminal graduation-check --root ~/.local/state/iotox --peer alias:desktop \
  --evidence daily-control=local.gate \
  --evidence profile-freshness=profile.check \
  --evidence service-supervision=terminal.service.systemd-user \
  --evidence reconnect-continuity=cli.reconnect \
  --evidence cgroup-delegation=nixos.cgroup \
  --evidence route-loss=tox.loss \
  --evidence long-soak=soak.24h \
  --evidence tor-route-loss=tor.operator \
  --evidence i2p-route-loss=i2p.fronts \
  --evidence sudo-policy=host.sudo \
  --evidence security-review=review \
  --evidence activation-decision=owner
```

`terminal soak-plan` is the native entrance for the long-soak part of that
label. It prints the daily-status, session, reconnect, runner, manual receipt,
and verifier commands for a real elapsed run. The ordinary path is the elapsed
runner:

```sh
iotox terminal soak-plan --root ~/.local/state/iotox --peer alias:desktop
iotox terminal soak-run --root ~/.local/state/iotox --peer alias:desktop \
  --route native \
  --seconds 86400 \
  --sample-every 300 \
  --out terminal-24h.receipt
iotox terminal soak-verify terminal-24h.receipt
```

Manual receipts remain available when importing externally supervised elapsed
evidence. A stable-terminal receipt is content-free and hashes root/peer labels
instead of recording paths or terminal data:

```sh
iotox terminal soak-receipt --root ~/.local/state/iotox --peer alias:desktop \
  --route native \
  --required-seconds 86400 \
  --observed-seconds OBSERVED_SECONDS \
  --samples SAMPLES \
  --max-sample-gap-seconds MAX_GAP_SECONDS \
  --reconnect-attempts RECONNECT_ATTEMPTS \
  --session-generations SESSION_GENERATIONS \
  --failures 0 \
  --result accepted \
  --label terminal.24h > terminal-24h.receipt
iotox terminal soak-verify terminal-24h.receipt
```

For stable/no-concern, the verifier requires an accepted
`iotox.terminal-long-soak-receipt.v1` receipt covering at least 86,400 observed
seconds, at least two samples, maximum sample gaps no larger than 900 seconds,
and zero failures. Short smoke receipts are useful construction tests, but they
do not satisfy `terminal.long-soak`.

Once that real long-soak receipt exists, the native manifest porch is:

```sh
iotox evidence collect terminal \
  --root ~/.local/state/iotox \
  --peer alias:desktop \
  --out /proof/stable \
  --service-reality /proof/terminal-service-supervision.receipt \
  --long-soak terminal-24h.receipt \
  --evidence daily-control=local.gate \
  --evidence profile-freshness=profile.check \
  --evidence reconnect-continuity=cli.reconnect \
  --evidence cgroup-delegation=nixos.cgroup \
  --evidence route-loss=tox.loss \
  --evidence tor-route-loss=tor.operator \
  --evidence i2p-route-loss=i2p.fronts \
  --evidence sudo-policy=host.sudo \
  --evidence security-review=owner.review \
  --evidence activation-decision=owner.decree
```

The command writes native content-free receipts for the 11 operator-attested
terminal gates and copies the long-soak receipt only after the stable 24-hour
semantic check passes. If `/proof/stable` already contains sync receipts, the
manifest becomes an `all stable` manifest; otherwise it is a terminal-stable
manifest.

With every gate labeled it can say
`daily-driver-graduation=operator-attested` and
`production-activation=operator-attested`, while still keeping
`repo-certified=0`. This graduates the operator runbook for one host and route
set; it does not turn Ratox into OpenSSH, certify every kernel, or prove future
Tor/I2P conditions.

`iotox ship-check terminal stable` answers the release question and remains
blocked for no-concern shipping. The founder-preview channel is explicit:
`iotox ship-check terminal founder-preview` means profile-bound self-machine
daily-driver candidate, sudo off by default, no fleet certification, and no
claim that Ratox is a universal OpenSSH replacement.

## What exists now

Ratox is a real interactive remote PTY service carried by Tox; it is no longer a diagnostic echo or
a framing proposal. The current binary implements:

- bilateral feature negotiation and exact authority-ledger v2 `interactive.terminal` proof;
- owner-selected canonical profile v7 and principal binding; remote bytes never select executable,
  argv, environment, working directory, profile, or path;
- frozen lossless custom-packet `0xA2` framing, at-most-once committed input, cumulative output ACK,
  bounded replay with explicit gap, resize, detach, explicit resume, close, and stale-attachment
  fencing;
- a real Linux PTY/process adapter and a separate owner-only `SOCK_SEQPACKET` local controller;
- the current user commands `iotox terminal PEER_PUBLIC_KEY_HEX [--reconnect]` and
  `iotox terminal-resume SESSION_ID_HEX [PEER_PUBLIC_KEY_HEX]`, including raw-mode restoration and
  detach/close escapes, plus `--batch` attachment with clean stdout and remote exit-status return;
- canonical profile template/lint/install/show/list/remove/bind/unbind commands, a content-free
  `terminal-sessions` view of the one retained local controller session, and authenticated
  `terminal-close` (including explicit resume-then-close for a detached session);
- `host-capabilities`, which live-probes pidfd, seccomp, MDWE, Landlock, the privilege-escalation
  prerequisites, and a usable privileged `sudo` helper, and reports the caller's exact cgroup-v2
  delegation, controller, PSI, and resource interfaces;
- deterministic login-shell/account discovery and disabled canonical shell-profile generation.
  Ordinary profiles retain the sealed baseline; `--allow-sudo` emits a visibly distinct
  compatibility profile that starts as the frozen non-root account and delegates elevation to the
  machine's existing sudoers/PAM policy;
- native daily-driver porches: `terminal daily-plan` names the operator commands for service setup,
  sessions, and reconnect continuity; `terminal activation-check` fails closed until the operator
  labels daily-control, profile-freshness, service-supervision, reconnect-continuity, cgroup
  delegation, and route-loss evidence; `terminal graduation-check` adds long-soak, Tor/I2P
  route-loss, sudo-policy, security-review, and activation-decision labels before recording
  daily-driver graduation; `terminal-profile-check` / `terminal profile check` verifies local
  profile payload freshness before relying on it;
- an optional separately packaged static rescue entrance: oksh 7.9 supplies the interactive shell
  and Toybox 0.8.14 supplies 238 applets. The disabled rescue profile starts baseline/non-root,
  prefixes a qualified immutable toolbox PATH, and deliberately excludes Toybox's pending shell;
- default baseline seccomp, capability/securebits/descriptor/core-dump sealing, and optional strict
  MDWE, Landlock ABI 10, delegated cgroup-v2 process/memory/swap/CPU/I/O limits, aggregate admission,
  teardown accounting, PSI admission, and live PSI triggers;
- retained two-guest direct-UDP/forced-TCP latency, 1/8/16/32/64 interference, impairment, complete
  loss, explicit higher-epoch resume, daemon replacement, and guest-restart evidence. ADR 0300 adds
  a production-CLI cell in which one unchanged `terminal --reconnect` process crosses genuine
  total loss and resumes the same retained PTY over direct UDP and forced TCP. ADR 0316 repeats that
  loss twice in one process and one shell, with exact progress between generations 1, 2, and 3.

Transport route loss detaches the local controller but retains the live PTY for an authenticated
explicit resume. IoTox daemon death intentionally does not preserve that PTY: the restarted daemon
uses a higher durable host incarnation and returns `not_found` for the old session. Preserving a PTY
across daemon/process death would require a separately supervised child, a durable session journal,
and a crash-safe input-commit protocol; it is not implied by today's reconnect support.

ADR 0306 optionally binds that host incarnation to the authenticated remote rollback-witness service
with `--witness-ratox-incarnation`. Every host start commits one exact next signed namespace before
runtime creation; restoring an older valid record therefore refuses instead of reusing session IDs.
This protects namespace freshness, not the profile/binding store: restoring an old sudo-enabled or
weakly confined profile remains an explicit workstream-8 gate.

In manual mode, the host and local terminal entrance are both default off. A configured construction
run must enable them separately, load a secure profile/binding store, pass every requested
confinement preflight, and negotiate the feature bilaterally. In self mode, `--mode self` selects
both roles by default for owned machines, but the same profile/binding, current authority, and
preflight gates remain. No ordinary upgrade silently turns manual-mode Agents into Ratox hosts.

The 2026-09-01 Ratox operator-surface recheck passed the 723-check owned registry and completed the
54-entry CTest suite without a failure. ADR 0326's separate NixOS KVM check now crosses the
production PTY through both a deterministic noninteractive sudo child and a real Bash login-shell
PAM password prompt. The password branch observes UID 1000 before and after sudo, UID 0 only in the
child, no password echo, and a clean exit. ADR 0349 hardens that test against shell/termios handoff
timing after sudo returns and gives future timeout failures bounded PTY phase/output diagnostics.
This is one NixOS sudo/PAM policy, not every host or PAM module. ADR 0327's separate
`ratox-cgroup-vm` check now boots NixOS Linux 6.6.94 and runs all five
delegated-cgroup process oracles under transient systemd `Delegate=yes` services: lifecycle,
memory/pids, CPU, I/O, and pressure admission. This is one named Linux/systemd controller branch, not
fleet, container, physical-device, long-soak, route-traversal, or production-activation proof.
ADR 0343 adds a current-host delegated user-service helper for fast repeat checks without a VM:
`./tools/ratox-cgroup-delegated-service-check.sh` passed lifecycle recovery, memory/pids controls,
CPU controls, and PSI pressure admission on 2026-09-09, while the I/O oracle skipped because this
qualification filesystem did not expose cgroup-attributed block I/O.

The current tree was also rerun through the repeated production-CLI reconnect Sandwurm gate on
2026-09-09. Compact proof `pair.h25zpony` passed direct UDP and compact proof `pair.sduwsbg8`
passed forced TCP; both used IoTox binary SHA-256
`b447f6fd0445f16b3bb9acca76bc413faf12b9b779ba7d20f5c8d95a128ed6b7`, observed two total-loss
interruptions, retained a detached host PTY snapshot, and reverified from the compact export. This
is current-tree mechanism evidence, not a long-soak, Tor/I2P, daemon-death, or production-activation
claim. The exact evidence is recorded in
`evidence/2026-09-09-sandwurm-ratox-cli-reconnect-repeated-current-tree.md`.

## Relationship to SSH

Ratox is SSH-shaped at the operator experience level, not an OpenSSH protocol implementation. It
already provides the core interactive behavior that matters to IoTox: a shell-like byte stream,
PTY resize, detach/resume across route loss, explicit close, identity continuity, and measured
latency. Its security model is intentionally closer to forced-command SSH than to unrestricted
`ssh host command`: the owner pre-authorizes one fixed profile and the remote peer cannot choose a
command line at Ratox admission. When that profile is an approved login shell, terminal input can
naturally contain arbitrary shell commands, including `sudo`; authority then comes from the local
account and sudoers/PAM exactly as it would at the machine's physical terminal.

| Question | OpenSSH | IoTox Ratox |
|---|---|---|
| Reachability | Normally an IP address and listening SSH service, often with VPN/jump infrastructure | Tox peer routing; no inbound SSH port or vendor account |
| Remote identity | SSH user keys/certificates and host keys | Tox transport identity plus a stable IoTox principal and signed authority proof |
| What the client requests | Shell, arbitrary command, subsystem, or forwarding | One owner-bound profile; terminal bytes cannot select executable or initial argv, but an approved shell interprets typed commands |
| Privilege | Login account plus host sudo/doas policy, or direct root login if enabled | Always starts as one frozen non-root account; only an explicit admin profile may invoke the host's existing sudo policy |
| Session loss | TCP loss usually ends the connection unless another layer preserves it | Route loss detaches; bounded output replay and explicit higher-epoch resume retain a live PTY |
| File movement | SCP/SFTP/rsync over SSH | Separate signed IoTox synchronization protocols |
| Maturity | Widely deployed, reviewed, interoperable | New, IoTox-specific; manual mode is default-off, self mode is default-on but profile/authority gated |

SSH remains the more mature tool for general server administration, noninteractive remote-exec
requests, port forwarding, SFTP, standard automation, and interoperability. Ratox now covers the
owner's primary interactive workstation case: reach a fixed login shell over Tox, work normally,
and use explicit host-authorized sudo when needed. It is still aimed at sovereign devices and
appliances where each principal receives only an owner-selected entrance.

The following SSH features do not exist and are not implicit roadmap promises:

- remotely selected executable/argv, an SSH exec-request equivalent, or remote profile selection;
- TCP/Unix port forwarding, agent forwarding, X11 forwarding, ProxyJump, or an SSH daemon/client
  compatibility layer;
- SCP or SFTP path semantics (IoTox sync is the verified directory/file replication plane instead);
- PTY survival across IoTox daemon restart;
- automatic resume merely because heartbeat warning fired.

General forwarding would create arbitrary egress authority and agent forwarding would create
ambient credential authority, both contrary to IoTox's explicit capability model. If fixed
forwarding is ever justified, it should be a separate owner-selected profile/capability with a
frozen narrow target, not SSH's general forwarding surface.

## Relationship to Eternal Terminal and Mosh

Eternal Terminal's central product idea is that the remote session survives a broken connection.
Mosh adds a roaming, latency-tolerant terminal model whose local prediction and state synchronization
are deliberately different from a reliable byte stream. Ratox v1 already owns the first prerequisite:
the PTY is a device-side object, controller attachment is replaceable, accepted input is committed at
most once, retained output is replayable with an explicit gap, and route recovery requires a fresh
authenticated epoch.

ADR 0289 now adds the first Eternal-shaped owner experience: `terminal --reconnect` keeps one local
invocation alive, retries only the exact retained session, and accepts only a higher attachment
generation after the Agent's existing higher-authenticated-epoch gate succeeds. ADR 0300 proves that
exact operator path, rather than the private controller protocol, across two real NixOS guests and
seeded total loss on native UDP and relay-only TCP. ADR 0316 proves the join is reusable rather than
one-shot by crossing two sequential losses in the same production process and remote shell. Ratox
is still not Mosh. There is no terminal-
screen state protocol, local echo prediction, roaming UDP protocol, or PTY supervisor outside the
IoTox daemon. The owner-local profile, session-list/close, batch, and
capability-doctor surfaces are now complete without changing the frozen Ratox v1 wire. Screen-state
synchronization or daemon-independent supervision should be separate later protocols only if
measurements show that they buy enough usability to justify new state.

## Operator commands now available

For a self-owned machine, start with the self-mode config porch:

```bash
iotox init plan --root ~/.local/state/iotox --mode self --enable-sync
iotox init write-config --root ~/.local/state/iotox --mode self --enable-sync
iotox config-lint ~/.local/state/iotox/agent.conf
```

Then put the machines in the owner-signed self roster before granting terminal
authority. The roster is reviewable membership; the grant still goes through
the signed authority ledger:

```bash
cat RECALLROOT.txt | \
  iotox self-swarm create-recall-stdin ~/.local/state/iotox/self.swarm \
    desktop DESKTOP_PRINCIPAL_HEX DESKTOP_TOX_KEY_HEX \
    operator interactive.terminal

cat RECALLROOT.txt | \
  iotox self-swarm join-recall-stdin ~/.local/state/iotox/self.swarm \
    laptop LAPTOP_PRINCIPAL_HEX LAPTOP_TOX_KEY_HEX \
    operator interactive.terminal

iotox self-swarm verify ~/.local/state/iotox/self.swarm \
  --min-generation 2 \
  --expect-member laptop LAPTOP_PRINCIPAL_HEX \
  --expect-route laptop LAPTOP_TOX_KEY_HEX

iotox self-swarm grant-plan ~/.local/state/iotox/self.swarm --from desktop

cat RECALLROOT.txt | \
  iotox self-swarm grant-recall-stdin ~/.local/state/iotox/self.swarm laptop \
    --min-generation 2 \
    --expect-member laptop LAPTOP_PRINCIPAL_HEX \
    --expect-route laptop LAPTOP_TOX_KEY_HEX
```

For a real owner login, first inspect what IoTox can safely resolve. The generated profiles are
deliberately disabled and must be reviewed before installation:

```bash
iotox terminal-shell-discover "$USER"

# Normal shell: no privilege may be gained across exec.
iotox terminal-profile-shell-template owner-shell "$USER" > owner-shell.profile

# Separate administrative shell: starts as the same non-root account and may call sudo.
iotox --allow-sudo terminal-profile-shell-template owner-admin "$USER" \
  > owner-admin.profile

# Optional independent static shell/tools fallback; baseline and non-root by default.
nix build .#iotox-rescue-toolbox
iotox --shell "$PWD/result/bin/oksh" --toolbox-dir "$PWD/result/bin" \
  terminal-profile-toolbox-template owner-rescue "$USER" \
  > owner-rescue.profile
```

`--shell PATH` is an exact override when automatic discovery is inappropriate. An invalid explicit
path fails rather than silently choosing another shell. Discovery canonicalizes the selected ELF,
freezes the account's UID, primary GID, and complete supplementary group set, and builds a bounded
deterministic PATH. It does not edit or validate sudoers and it never generates a root-starting
profile. A Nix-store shell path is intentionally exact and may require profile regeneration after an
upgrade or garbage collection.

The rescue profile is not automatic fallback. It must be reviewed, enabled, installed, bound, and
retained before an outage. It removes the target dynamic-loader/library dependency for its shell and
tools, but cannot repair an absent Agent, kernel/architecture mismatch, broken PTY/filesystem, lost
authority, or collected payload. Full details are in `ratox-rescue-toolbox.md` and ADR 0287.

The generic single-purpose template remains useful for maintenance programs:

```bash
install -d -m 0700 /var/lib/iotox/ratox \
  /var/lib/iotox/ratox/profiles /var/lib/iotox/ratox/bindings
iotox terminal-profile-template maintenance > maintenance.profile
iotox terminal-profile-lint maintenance.profile
iotox --ratox-profile-store /var/lib/iotox/ratox \
  terminal-profile-install maintenance.profile
iotox --ratox-profile-store /var/lib/iotox/ratox \
  terminal-profile-bind PRINCIPAL_PUBLIC_KEY_HEX maintenance
```

The host must be restarted to load a changed store. A session already running under a frozen policy
generation cannot be retargeted by later file changes. Inspect the current host before choosing a
strict/cgroup policy, then operate the controller session:

```bash
iotox host-capabilities
iotox --runtime /run/user/$UID/iotox terminal-sessions
iotox --runtime /run/user/$UID/iotox terminal-close SESSION_ID_HEX
iotox --runtime /run/user/$UID/iotox terminal PEER_PUBLIC_KEY_HEX --reconnect
producer | iotox --runtime /run/user/$UID/iotox terminal PEER_PUBLIC_KEY_HEX --batch
```

ADR 0292 permits the shared `PEER` grammar in every terminal peer position, so the same operations
may use `workstation` or `alias:workstation`. The alias resolves to one exact Tox key before terminal
attachment; it neither selects a profile nor grants terminal authority.

Batch EOF injects one PTY EOT and waits for the fixed profile to exit. It is not an SSH exec request:
the remote still supplies no initial executable or arguments, and a profile that ignores EOT needs
an operator deadline or explicit close. A shell profile may of course interpret commands delivered
as terminal input; that power is exactly why its binding and privilege flag deserve deliberate
review.

## Remaining product work

The protocol and main lifecycle are frozen and the founding-machine roadmap is complete. Optional
Ratox product work is mostly operational R8, not a new wire design:

1. Extend ADR 0316's now-qualified two-interruption direct-UDP/forced-TCP production-client loop to
   a longer soak and overlay-route Tor/I2P cells. This remains client lifecycle work above frozen
   Ratox v1 frames, not transparent network migration or daemon-restart survival.
2. Qualify cgroup lifecycle, controller accounting, aggregate admission, and positive PSI
   trigger/outcome behavior on named deployment kernels and service managers. ADR 0343 makes the
   local delegated-user-service repeat cheap; it still leaves filesystem-specific I/O accounting,
   trigger-latency measurement, and fleet coverage open.
   `./tools/ratox-daily-control-gate.sh --build` now bundles the local Ratox process/probe/analyzer
   checks with that delegated-cgroup helper; on 2026-09-09 it passed 6/6 focused CTest entries and
   reported `passes=4 skips=1 failures=0` for delegated cgroups. The current 2026-09-17 rerun passed
   the same 6/6 focused set and again reported `passes=4 skips=1 failures=0`; see
   `evidence/2026-09-17-ratox-daily-control-rerun.md`.
3. If production support is pursued, complete independent security/operational review, longer leak/
   reconnect/PTY soaks, and an activation ADR. This is outside repository completion; keep upgrades
   from silently changing manual-mode Agents, and keep self-mode claims scoped to profile/
   authority-gated owner control.
4. Use the implemented ADR 0290 `run-check` and canonical file-backed Agent configuration in each
   deployment. `host-capabilities` covers the read-only kernel/runtime and sudo-prerequisite half of
   this operator problem. Opt production hosts into ADR 0306 Ratox-incarnation and ADR 0308 terminal-
   policy witnessing only after their remote service has been separately enrolled and operationally
   isolated; the latter already refuses restoration of an old sudo-capable profile/binding tree.
5. Treat durable child supervision as a separate future milestone only if daemon-restart session
   survival proves worth its new persistence boundary.

The deliberate near-term sweet spot is therefore: keep Ratox v1 framing unchanged, keep custom
lossless as the reliable byte/control carrier, retain explicit higher-epoch resume, cap ordinary
single-Agent bulk at the qualified 32-transfer ceiling, and use protected multi-route/QoS policy for
larger concurrent sync rather than weakening terminal correctness.
