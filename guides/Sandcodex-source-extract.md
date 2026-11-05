# Sandcodex: selected source passages

A reading convenience for the supplied Sandcodex 0.88.0 file at [commit e41e378](https://github.com/Sapient-Lumen/W4R3Z/blob/e41e378c83a9b2bd318fa71438c104d9f6b6ee6c/Maintained%20Tools/sandcodex). GitHub does not render this 7.5 MB file inline; use View raw to download the complete original. The passages below are exact line extracts, not a replacement for the complete handbook, current source, original notices or operating contract. Reading does not require execution.

Source SHA-256: `720e9b40001c58f5e30a369c3e47c35ff4349809aa16b00970835ee766a6f785`; Git blob: `0db74bdaf0eedd99bd66807cfb9287f88d05ec66`. Line numbers are one-based and apply only to that exact source.

## Opening handbook

Source lines 18–54; excerpt SHA-256 `ae2333eefdddeb863482c782c85c069643e7c4dc3d78df8bf48dd2cbc38bda62`.

```text
#                                     FIELD HANDBOOK
#
# This comment is the publication manual for the file that contains it. It is deliberately part of the artifact: copy
# `sandcodex` to another Linux/NixOS machine and the implementation, pinned dependency graph, operator handbook,
# recovery notes, agent contract, desktop controller, browser broker, inner jail, campaign broker, and deep diagnostic
# fixtures travel together. Run `sandcodex manual` to print this exact handbook without creating state, invoking Nix,
# contacting a provider, or selecting a project. This handbook explains policy; executable validation remains
# authoritative.
#
# The executable version and every dependency pin are declared immediately below this block. `sandcodex version --json`
# is the machine-readable release identity; its artifact_sha256 identifies the exact copied file. Do not infer identity
# from a filename, a Git branch, or this prose.
#
# ── 01 · PURPOSE ──────────────────────────────────────────────────────────────────────────────────────────────────────
#
# Sandcodex is a neoshell for sustained human–agent work. It gives Codex a capable Linux project room while keeping the
# authority decision legible to the human who launched it. The default room is not a toy sandbox: the agent can rewrite,
# delete, execute, commit, and configure ordinary content in the selected project. It can use a real browser, a native
# Linux desktop, pinned build tools, controlled ingress, staged companion agents, and a smaller disposable jail. What it
# cannot do by default is mistake that one project for the whole machine, inherit arbitrary host secrets, or leave
# descendants running outside the launcher's supervision.
#
# The governing ideas are:
#
#   • Capability must be useful. A boundary that prevents ordinary engineering is theatre, not a command room.
#   • Authority must be explicit. The selected project is mutable; the rest of the host is not silently donated.
#     `--BARE-METAL` is an unmistakable promotion, never an automatic fallback.
#   • Continuity belongs outside the mutable project. Credentials, sessions, policy, locks, and lifecycle records remain
#     in trusted per-user state.
#   • The agent and human are collaborators, not mutually exclusive pilots. Human desktop input does not pause model
#     mutation; the interface exposes control state and fences so both participants can reason about change.
#   • Claims must be narrower than evidence. A listening TCP socket is not proof of LAN reachability; a screenshot is
#     not proof of semantic success; a sandbox is not a VM. Diagnostics report those distinctions.
#   • Failure closes the room. Required relays, publishers, desktop controllers, and the complete Codex process tree
#     share a supervised lifetime.
#   • One file is a design constraint. The long embedded sources below are not generated debris: they remove dependency
#     on an unpublished repository.
```

## Authority postures

Source lines 290–330; excerpt SHA-256 `b3a5ca1ce3e6655cd5aba6541d376a41fe84bbb2fd0eca99d6a84b385c480c53`.

```text
# ── 04 · AUTHORITY POSTURES ───────────────────────────────────────────────────────────────────────────────────────────
#
# DEFAULT SAFE ROOM
#   Filesystem               selected project read/write; system and Nix store read-only; other host trees absent;
#                            trusted frontend state hidden from ordinary model tool commands
#   Process                  complete frontend tree in private user/PID/IPC/UTS/mount/net namespaces; parent-death
#                            coupling; required-service watchdog
#   Kernel                   host kernel shared; capabilities dropped; keyring syscalls denied; nested command sandbox
#                            remains active
#   Network                  direct routes absent; explicit loopback proxy bridge; default unrestricted HTTP/HTTPS/SOCKS
#                            including LAN, or provider-only when `--restricted-network` is selected
#   Resources                transient user systemd cgroup unit; 50% host memory, no swap, 2048 tasks. A scope is
#                            preferred; a service with a private one-use environment handoff covers callers in sibling
#                            session cgroups. Safe failure remains mandatory unless `--no-resource-scope` is explicit;
#                            that degradation also disables the cgroup-backed inner jail for the launch.
#   Project trust            `.codex`, hooks, MCP declarations, IDE files, and shell startup files are mutable project
#                            content but are not loaded as frontend policy unless `--trust-project-config` is chosen
#
# BARE METAL
#   `--BARE-METAL` removes Sandcodex's outer containment, preserves the invoking environment/PATH, and, by default,
#   runs `sudo -v`. Sandcodex never reads the password; sudo reads the terminal and Sandcodex refreshes only that ticket
#   while Codex lives. Before provider launch it proves `sudo -n -- id -u` returns 0, and Codex is instructed to use
#   `sudo -n` for root work so no model-controlled command can stall on a password prompt. Add `--no-sudo-ticket` when
#   the host-uncontained room should not touch sudo at launch; root commands may still work later if the host already
#   has an ambient reusable ticket. This is intentional host administration authority. The inner jail remains available
#   as a voluntary delegation tool, not a parent boundary.
#
# INNER JAIL
#   `sandcodex-jail` lets the primary agent hand a smaller, fresh boundary to a less-trusted action. The action controls
#   argv only. The delegator controls tool closure, workspace/cache, network, time, CPU, memory, swap, PIDs,
#   file/tmp/home ceilings, sealed inputs, and declared result evidence. Grants recurse only by narrowing. The jail is
#   for suspect commands and reproducible evidence; it is not where the primary agent must perform ordinary work.
#
# OPERATOR SERVICE
#   `--operator-service FILE` freezes one reviewed declaration at launch and runs that application in a credentialless
#   sibling boundary. An authenticated host-loopback ingress and one-time bootstrap support a durable cockpit. It is the
#   preferred durable-service mechanism when argv and authority are known before launch. Socket-aware applications may
#   consume the inherited listener and readiness descriptors directly. Ordinary servers may instead declare a
#   `tcp-loopback` adapter: Sandcodex waits for their exact private target port, emits readiness on their behalf, and
#   bridges the stable listener without granting frontend credentials or a network route. Runtime controls use
#   generation numbers to prevent stale stop/restart requests.
```

## Process and data map

Source lines 332–371; excerpt SHA-256 `9ef60c871c33565dc84fe8d2b1b12b33988f1e3b35af56df8a8aa64af1cccbd2`.

```text
# ── 05 · PROCESS AND DATA MAP ─────────────────────────────────────────────────────────────────────────────────────────
#
#   host user session
#   └─ sandcodex launcher + project lock + resource scope
#      ├─ trusted auth/session/control state                                 outside project
#      ├─ egress proxy + TCP publishers                                      birth-pinned
#      ├─ browser owner / desktop / operator                                 explicit, supervised
#      ├─ campaign and inner-jail brokers                                    capability-checked
#      └─ outer bubblewrap command room
#         ├─ Codex frontend                                                  credentials projected
#         ├─ Codex model-command sandbox                                     credentials hidden
#         ├─ agent-loopback publish relays                                   declared ports only
#         └─ project and disposable worker state                             ordinary authority
#
# Persistent layout (conceptual; query exact paths with `sandcodex-env --json`):
#
#   PROJECT/
#   ├─ ordinary source and Git metadata                                      agent mutable
#   └─ .sandcodex/                                                           disposable worker state
#      ├─ work/{home,cache,scratch,state,downloads}
#      ├─ work/{browser-home,browser-output,desktop-home,
#      │        desktop-output}
#      ├─ work/agent + work/agent-bin                                        launcher-protected
#      └─ launcher/                                                          protected copy/helpers
#
#   ~/.sandstuff/sandcodex/                                                  trusted global root
#   ├─ auth-home/                                                            shared auth source
#   ├─ projects/PROJECT-HASH/                                                sessions/frontend state
#   ├─ logs/                                                                 metadata-only launcher logs
#   ├─ runtime/                                                              invocation-private, ephemeral
#   └─ locks, supervisors, campaigns, transactions validated control records
#
# The project-local tree is disposable by design, but not casually trusted. Every launch and maintenance path checks
# ownership, type, hardlink count, marker identity, inherited ACL absence, symlink components, and nested mounts before
# mutation. Owned, non-mounted legacy `.sandcodex` debris and stale managed-Git stores are moved into trusted quarantine
# instead of blocking first contact with the agent; unsafe roots still fail closed. Launcher logs contain lifecycle
# metadata, diagnostic classifications, and resource facts; they do not capture prompts, provider output, application
# output, credentials, or inherited secrets. Operator application output goes only to its private per-run application
# log. Sandcodex drains it continuously, retains at most 64 MiB, and discards excess so a noisy service cannot consume
# storage without bound or deadlock on a full pipe.
```

## Visual work

Source lines 373–398; excerpt SHA-256 `fec84773121a5684c56c26ef19d8ccd4650d75edd849a78d8e9808d2483971f4`.

```text
# ── 06 · BROWSER, DESKTOP, AND HUMAN PRESENCE ─────────────────────────────────────────────────────────────────────────
#
# There are two different visual systems:
#
#   Browser          Persistent Chromium plus complete Playwright MCP. It is suited to web automation, authenticated
#                    sites, downloads, DevTools, and local web applications. Its continuous human viewer is a private
#                    nested Xephyr projection and is hidden until `sandcodex-browser show`. The browser never has to
#                    open merely because it exists.
#
#   Desktop          A separate credentialless Linux workstation controlled by the native desktop MCP. Wayland and
#                    X11/Xvfb/Xephyr are both first-class lanes with different jobs: Wayland is the high-assurance
#                    native/headless path with per-application fences, while X11/Xvfb/Xephyr is the practical
#                    shared-workstation path for headful collaboration and applications that expect an ordinary X
#                    desktop. The headless viewer is a smooth continuous read-only mirror; headful Xephyr accepts
#                    direct human keyboard and pointer input.
#
# Human and agent input may overlap. Sandcodex does not freeze the agent while the human pilots. Desktop observations
# therefore carry frame, pointer, keyboard, launch-scene, tick, outcome, accessibility, and mutation fences. The agent
# should observe again after unexpected motion or focus changes and should say what it is about to do when a human is
# visibly active. The human should expect the agent to continue shell, browser, and desktop work unless they explicitly
# ask it to stop.
#
# Files cross the desktop boundary only through reviewed FileDropSeal and FileCopySeal transactions. Screenshots and
# completed exports are published into read-only agent-visible artifact roots; staging remains controller-only.
# Accessibility is preferred for semantics; guarded pixels remain available when applications expose no usable
# accessibility tree.
```

## Ingress

Source lines 400–432; excerpt SHA-256 `875724571dd5cf22bec6079d19a71d574c110577aaea126742a312b0defb89f7`.

```text
# ── 07 · PUBLISH: INGRESS WITHOUT FICTION ─────────────────────────────────────────────────────────────────────────────
#
# `--publish` is supervised raw TCP ingress from a host listener to one exact agent-loopback target. It adds no HTTP,
# TLS, origin policy, authentication, authorization, rate limiting, or firewall rule. Repeat it for at most sixteen
# listeners. Forms are:
#
#   --publish 3000                                    127.0.0.1:3000 → 127.0.0.1:3000
#   --publish 8080:3000                               127.0.0.1:8080 → 127.0.0.1:3000
#   --publish 0.0.0.0:8080:3000                       all host IPv4 interfaces → agent port 3000
#   --publish 192.168.1.25:8080:3000
#                                                     one host IPv4 address → agent port 3000
#
# A non-loopback bind is a deliberate LAN exposure if the address exists and the host firewall permits it. Prefer
# loopback plus SSH forwarding for private remote use:
#
#   ssh -N -L 8080:127.0.0.1:8080 user@machine-running-sandcodex
#
# Inside the room, read `$SANDCODEX_PUBLISH_CONFIG` and bind the application to the declared `127.0.0.1` target, not
# `0.0.0.0`. Keep an ad-hoc server attached to a live tool call unless using a reviewed operator service; Codex may
# revoke descendants when a tool call ends. Publication dies if its required outer or inner relay dies.
#
# From another terminal on the machine running Sandcodex:
#
#   sandcodex publish status --project /path/to/project
#   sandcodex publish doctor --project /path/to/project
#
# `status` is read-only and reports declaration, launcher identity, publisher process identity, known relay facts, and
# candidate host IPv4 interfaces for wildcard binds. `doctor` additionally opens each listener from the same host and
# reports the exact `host_probe_address`; wildcard listeners are probed through `127.0.0.1` because the check proves the
# local listener and relay, not the physical interface path. Neither command claims a physical client traversed the LAN,
# firewall, Wi-Fi isolation, VPN, or router. Test that last hop from the actual client. For HTTP, use `curl -v`; for raw
# TCP, use `nc -vz` or the protocol's real client. A host socket accepting a connection does not prove application
# readiness unless a protocol request succeeds.
```

## Continuation and delegation

Source lines 434–469; excerpt SHA-256 `46437134b4efe536d3d4186d1f2713658406b7a210ea95679e0ac3d0d109f864`.

```text
# ── 08 · CONTINUATION AND DELEGATION ──────────────────────────────────────────────────────────────────────────────────
#
# `loop` is sequential continuity: one project, one session lineage, one turn at a time. A detached safe loop may
# survive the terminal under the user systemd manager, retry classified transient provider failures, and stop at
# explicit disk-growth thresholds. `--turns 0` means continue until stopped or a turn fails. The active agent can
# request future turns through the protected `$SANDCODEX_LOOPER` protocol but cannot widen the outer launch authority.
#
# `campaign` is parallel staged work: the broker snapshots one exact clean Git commit into an independent clone, starts
# a browserless worker, and collects only committed work as an explicit Git bundle plus digest receipt. It never merges
# or adopts work automatically. Workers run until completion or an explicit stop by default; a positive `--turns`
# value sets a launch-time ceiling. Campaign count and storage remain bounded launch authority. `campaign remove`
# remains host-only.
#
# Managed-local, remote, and Gemini interactive rooms authorize up to four concurrent campaigns by default. The
# foreground TUI remains fully interactive while its agent starts, observes, steers, stops, restarts, and collects each
# worker through `$SANDCODEX_CAMPAIGN` / `sandcodex-worker`. Foreman and workers are concurrent Codex processes in
# different checkouts.
# A local worker shares the exact birth-pinned Ollama service owned by the foreground room; its one-generation policy
# queues inference requests instead of loading a second model or multiplying KV-cache memory. A fixed remote worker
# inherits the foreground room's exact endpoint snapshot, qualification receipt, and copied credential in trusted state.
# A remote-auto worker instead uses a copied, digest-checked key/model bank and its own conversation-bound Responses
# relay. Each provider request can fail over within that sealed bank before downstream commit. Its outer provider retry
# envelope remains intentionally short, so route exhaustion reaches a terminal loop boundary quickly and the broker can
# replay the worker with another eligible preflight selection. A Gemini worker starts and owns a fresh adapter from
# launch-sealed authority containing the free-tier-model-only ladder, five-account key-rotation bank, and signed-state
# contract. Before output becomes visible it keeps the strongest model while rotating account keys on quota, rate,
# authentication, or permission pressure, then falls through models when every account route is cooling. Hosted
# concurrency, limits, pricing, and behavior remain provider-defined. Local and fixed-remote companions depend on
# the foreground provider authority remaining alive; Gemini companions do not after their start succeeds. A
# worker exists only after its start request returns success. Status and events are the sole evidence for lifecycle and
# turn progress; a timeout never proves launch, progress, or completion. Use `sandcodex-worker status --name NAME` and
# `events` rather than leaving the TUI. Use `sandcodex-worker grant status` when the human asks whether new companions
# are currently allowed.
#
# Native Codex subagents inherit the primary sandbox and approval posture. Agent depth and thread count bound fan-out,
# not semantic responsibility. The primary remains accountable for review, integration, and tests.
```

## Authentication and configuration

Source lines 471–491; excerpt SHA-256 `603d327565493605e9237c8b2f2762a0bf593fcdc8c0cb0832fbf9cb3c88bc33`.

```text
# ── 09 · AUTHENTICATION, TRUST, AND CONFIGURATION ─────────────────────────────────────────────────────────────────────
#
# Authentication is host-side lifecycle state. Use `sandcodex auth status`, `verify`, `login`, `logout`, or `reauth`;
# `auth path` reports the trusted source. A frontend logout is reconciled back to trusted state. Sandcodex never asks
# for a sudo password in safe mode. If sudo appears, the invocation explicitly selected `--BARE-METAL` without
# `--no-sudo-ticket` (or a host program independently requested it).
#
# Explicit imports accept only user-owned, single-link, non-empty JSON objects no larger than 1 MiB. If Codex rejects an
# import, Sandcodex restores the prior working credential. Account-cache invalidation and destructive credential cleanup
# preflight every selected global and per-project file, directory, symlink, hardlink, and mount target before mutation.
#
# Project instructions are data under agent authority. By default Sandcodex writes a generated frontend configuration
# outside the project and does not let project `.codex` settings, hooks, or MCP servers execute with frontend credential
# authority. `--trust-project-config` knowingly changes that trust decision. It is not required for AGENTS.md
# instructions: Codex can read and follow ordinary project guidance without loading executable project policy. Plainly:
# AGENTS.md is text the agent can obey; `.codex` config, hooks, and MCP declarations are executable/frontend policy that
# can affect credentials and tools, so they stay inert unless explicitly trusted.
#
# The generated `sandcodex-env --capabilities` card is the authoritative map inside a running room. An agent should
# inspect it before guessing at paths or authority. The card gives exact versions, mounts, helpers, network posture,
# browser/desktop state, ingress declarations, jail recipes, and known limits.
```

## Recovery

Source lines 493–520; excerpt SHA-256 `bc5bcdd3fcf09bd54445cc2d3834c48de879b26ad6c47d85a0a8803c37e720db`.

```text
# ── 10 · RECOVERY, CLEANUP, AND DIAGNOSTICS ───────────────────────────────────────────────────────────────────────────
#
#   sandcodex doctor                                  pins, state, auth, boundary prerequisites
#   sandcodex doctor --deep                           includes real safe-boundary self-tests
#   sandcodex doctor --desktop-only                   focused native-workstation verification
#   sandcodex logs tail                               launcher lifecycle metadata only
#   sandcodex version --json                          exact artifact and supply-chain identity
#
# Plain `clean` removes disposable caches while preserving sessions, downloads, persistent browser login/profile,
# desktop home, and launcher logs. Add narrow flags to remove those scopes. `clean --everything` removes every Sandcodex
# scope owned by the selected project—including local worker state, sessions, project auth copy, campaigns, supervisors,
# browser/desktop state, and logs—but preserves the shared authentication source. Every destructive path validates the
# same ownership/marker/hardlink/ACL/mount invariants as launch and requires `DELETE` unless `-y` is explicit.
#
# State import/export is transactional and schema-checked. Use `state migrate --dry-run` before a migration and retain
# the printed transaction identifier for rollback. Never copy a live `.sandcodex` tree as a backup.
#
# A failed required publisher, relay, browser owner, desktop controller, or display is not silently ignored. Sandcodex
# terminates the provider tree and reports which dependency was lost. Stale active-run records are observations, not
# invitations to kill a PID; identity is always PID plus process start time.
#
# The foreground room follows its terminal: closing it or losing the enclosing SSH connection interrupts and reaps the
# complete room rather than orphaning helpers. This is not an idle timeout. The native conversation remains in trusted
# per-project state; reconnect in that project and run `sandcodex --RESUME`. Signal shutdown is logged as an
# interruption, not as a provider failure. When SSH detachment must not interrupt the room, opt into the retained tmux
# layer with `sandcodex terminal NAME [LAUNCH-OPTIONS]`. It changes presentation and reconnect behavior only: the
# ordinary launcher remains in the tmux pane and the existing user-systemd scope still contains its complete process
# tree. Use `terminal attach NAME`; taking another viewer over requires the explicit `--takeover` switch.
```

## Implementation atlas

Source lines 579–603; excerpt SHA-256 `9af66cf11ff9f2099667ce053d27beecc96364e776390437311a5691240f5988`.

```text
# ── 12 · IMPLEMENTATION ATLAS ─────────────────────────────────────────────────────────────────────────────────────────
#
# The source is intentionally ordered from policy to mechanism:
#
#   constants and state                      release identity, schemas, launch selections
#   diagnostics and safety                   logging, ownership, filesystem/process validation
#   grammar and validation                   help, command parsers, normalized authority
#   trusted state                            auth, sessions, locks, migration, campaign records
#   generated agent surface                  environment card, helpers, frontend configuration
#   runtime assembly                         proxy transit; browser, desktop, operator setup
#   embedded components                      protocol clients, brokers, portals, patched Sway
#   boundaries                               outer/inner bubblewrap, seccomp, Landlock, cgroups
#   execution and cleanup                    supervised launch, doctor, cleanup, main dispatch
#
# Search for a named `sc_*` function before editing an embedded heredoc with a similar term. Heredoc sources execute in
# different trust domains and often use independent schemas deliberately. Sequential appends are intentional for
# generated helper scripts; ShellCheck SC2129 is disabled for that reason.
# Practical navigation: `rg -n '^sc_NAME\\(\\)' sandcodex` finds one shell function; `rg -n '^SANDCODEX_.*_(PY|JS|SH)$'`
# finds embedded component boundaries; `sandcodex help topics` maps public commands to focused human help.
#
# Large embedded C, Python, JavaScript, shell, portal, compositor, and patch bodies are necessary until the same
# behavior can be obtained from a pinned, stable upstream component without weakening the one-file contract. Historical
# aliases and inert compatibility switches are not necessary and do not belong in the public grammar. Narrow state
# reconciliation may remain when removing it would strand a safely detectable prior layout; such code must still fail
# closed and must not silently adopt ambiguous state.
```

## Outer boundary implementation

Source lines 121579–121762; excerpt SHA-256 `c5a43db1a0971dd54f22442d681980c709a03536db2e9486d7c8c4e3780eb7ae`.

```text
sc_bwrap() {
  local proxy_url="http://127.0.0.1:3128" cert user codex_daemon_stub codex_daemon_visible
  cert="${SSL_CERT_FILE:-/etc/ssl/certs/ca-bundle.crt}"; user="$(id -un)"
  # Codex 0.160 prepares this fixed host-local path even with --no-daemon so
  # every child sandbox can mask possible app-server sockets. Sandcodex keeps
  # /tmp read-only; provide an exact, empty, launch-private, read-only 0700
  # directory instead. It satisfies upstream's owner/mode precondition while
  # making a shared daemon socket impossible inside this command room.
  codex_daemon_stub="$SC_RUN_ROOT/codex-daemon-placeholder"
  codex_daemon_visible="/tmp/codex-daemon-$(id -u)"
  sc_ensure_dir "$codex_daemon_stub" "Codex daemon-mask placeholder"
  local path command_path
  command_path="$SC_AGENT_BIN"
  [[ -z "$SC_DEV_VENV" ]] || command_path+=":$SC_DEV_VENV/bin"
  (( ! SC_NIX_DAEMON_SAFE )) || command_path+=":$SC_WORK/state/nix/profile/bin"
  command_path+=":$SC_LOCAL/launcher:$SC_PATH"
  local -a mounts=(--tmpfs / --ro-bind /nix/store /nix/store)
  for path in /etc /usr /bin /lib /lib64 /sys; do
    [[ ! -e "$path" ]] || mounts+=(--ro-bind "$path" "$path")
  done
  [[ ! -d /etc/nix ]] || mounts+=(--tmpfs /etc/nix --remount-ro /etc/nix)
  mounts+=(
    --proc /proc --dev /dev
    --tmpfs /run --tmpfs /tmp
    --dir "$codex_daemon_visible"
    --ro-bind "$codex_daemon_stub" "$codex_daemon_visible"
    --dir /run/sandcodex
    --bind "$SC_AGENT_TMP" "$SC_AGENT_TMP_VISIBLE"
    --ro-bind-try /run/current-system/sw /run/current-system/sw
    --bind "$SC_PROJECT" "$SC_PROJECT"
    --bind "$SC_CONTROL" "$SC_SANDBOX_CONTROL"
    --bind "$SC_GLASSTTY_HOME" "$SC_GLASSTTY_RUNTIME_HOME"
    --ro-bind "$SC_PROXY_TMP" /run/sandcodex/proxy-host
    --dir "$SC_PROXY_TMP"
    --dir "${SC_JAIL_BROKER_SOCKET%/*}"
    --dir "$SC_JAIL_RELAY_ROOT"
    --dir /run/sandcodex/agent-bridge
    --ro-bind "${SC_JAIL_BROKER_SOCKET%/*}" "${SC_JAIL_BROKER_SOCKET%/*}"
  )
  if (( SC_DESKTOP )); then
    # The desktop controller owns FileDropSeal snapshots. The ordinary Codex
    # namespace may reach the MCP socket but receives an opaque empty overlay
    # at the snapshot path, preventing same-UID replacement or inspection
    # through the otherwise read-only proxy-transit projection.
    mounts+=(
      --tmpfs /run/sandcodex/proxy-host/desktop-control/file-drop
      --remount-ro /run/sandcodex/proxy-host/desktop-control/file-drop
    )
  fi
  if (( SC_NIX_DAEMON_SAFE )) && [[ -S /nix/var/nix/daemon-socket/socket ]]; then
    mounts+=(
      --dir /nix/var --dir /nix/var/nix --dir /nix/var/nix/daemon-socket
      --ro-bind /nix/var/nix/daemon-socket/socket /nix/var/nix/daemon-socket/socket
    )
  fi
  if [[ "$SC_JAIL_STORAGE_BUDGET_MIB" != null ]]; then
    mounts+=(
      --bind "$SC_JAIL_WORKSPACES" "$SC_JAIL_WORKSPACES"
      --bind "$SC_JAIL_CACHES" "$SC_JAIL_CACHES"
    )
  fi
  if [[ -n "$SC_BROWSER_BUNDLE_ROOT" ]]; then
    mounts+=(--ro-bind "$SC_BROWSER_BUNDLE_ROOT" /run/sandcodex/bundle)
  fi
  if (( SC_BROWSER )) && [[ "$SC_BROWSER_ACTIVE_OUTPUT" != "$SC_BROWSER_VISIBLE_OUTPUT" ]]; then
    mounts+=(
      --bind "$SC_BROWSER_ACTIVE_OUTPUT" "$SC_BROWSER_VISIBLE_OUTPUT"
      --bind "$SC_BROWSER_ACTIVE_DOWNLOADS" "$SC_BROWSER_VISIBLE_DOWNLOADS"
    )
  fi
  if (( SC_OPERATOR_ENABLED )); then
    mounts+=(
      --bind "$SC_PROXY_TMP/operator-agent" /run/sandcodex/operator-control
      --ro-bind "$SC_OPERATOR_SERVICE_SOCKET" "/run/sandcodex/operator-control/$SC_OPERATOR_NAME.service.sock"
      --ro-bind "$SC_OPERATOR_LISTENER_ROOT/$SC_OPERATOR_LISTEN" "$SC_OPERATOR_SOCKET"
    )
  fi
  sc_protected_mounts mounts
  mounts+=(--remount-ro / --remount-ro /run --remount-ro /tmp --remount-ro /sys)
  mounts+=(
    # Codex 0.160 also prepares a per-uid synthetic-mount registry below the
    # profile-selected TMPDIR before its inner Bubblewrap begins. Re-project
    # only the already launch-private short temp root after /run is sealed;
    # every sibling path under /run remains read-only.
    --bind "$SC_AGENT_TMP" "$SC_AGENT_TMP_VISIBLE"
    --bind "$SC_PROXY_TMP/agent" /run/sandcodex/agent-bridge
    --bind "$SC_JAIL_RELAY_ROOT" "$SC_JAIL_RELAY_ROOT"
  )
  local -a args=(
    --unshare-user --unshare-pid --unshare-net --unshare-ipc --unshare-uts
    --hostname sandcodex --new-session --die-with-parent --cap-drop ALL
    "${mounts[@]}"
    --clearenv
    --setenv HOME "$SC_SANDBOX_CONTROL/frontend-home"
    --setenv CODEX_HOME "$SC_SANDBOX_CONTROL/codex-home"
    --setenv TMPDIR "$SC_SANDBOX_CONTROL/tmp"
    --setenv XDG_CACHE_HOME "$SC_SANDBOX_CONTROL/xdg-cache"
    --setenv XDG_CONFIG_HOME "$SC_SANDBOX_CONTROL/xdg-config"
    --setenv XDG_DATA_HOME "$SC_SANDBOX_CONTROL/xdg-data"
    --setenv XDG_STATE_HOME "$SC_SANDBOX_CONTROL/xdg-state"
    --setenv PATH "$command_path"
    --setenv SHELL "$(command -v bash)"
    --setenv USER "$user" --setenv LOGNAME "$user"
    --setenv TERM "${TERM:-xterm-256color}" --setenv LANG "${LANG:-C.UTF-8}"
    --setenv SSL_CERT_FILE "$cert" --setenv NIX_SSL_CERT_FILE "${NIX_SSL_CERT_FILE:-$cert}"
    --setenv NODE_USE_ENV_PROXY 1
    --setenv HTTP_PROXY "$proxy_url" --setenv HTTPS_PROXY "$proxy_url"
    --setenv WS_PROXY "$proxy_url" --setenv WSS_PROXY "$proxy_url"
    --setenv http_proxy "$proxy_url" --setenv https_proxy "$proxy_url"
    --setenv ws_proxy "$proxy_url" --setenv wss_proxy "$proxy_url"
    --setenv NO_PROXY '127.0.0.1,localhost' --setenv no_proxy '127.0.0.1,localhost'
    --setenv SANDCODEX_ACTIVE 1 --setenv SANDCODEX_OUTER_PROJECT "$SC_PROJECT"
    --setenv SANDCODEX_RUN_ID "$SC_RUN_ID"
    --setenv SANDCODEX_TEMP "$SC_AGENT_TMP_VISIBLE"
    --setenv SANDCODEX_JAIL_RUNTIME /run/sandcodex/agent-bridge
    --setenv SANDCODEX_LOOPER "$SC_LOCAL/launcher/sandcodex"
    --setenv GLASSTTY_HOME "$SC_GLASSTTY_RUNTIME_HOME"
    --chdir "$SC_PROJECT"
  )
  if (( SC_DEV_NET )); then
    args+=(--setenv ALL_PROXY "socks5h://127.0.0.1:3128" --setenv all_proxy "socks5h://127.0.0.1:3128")
  fi
  local provider_bridge_kind="" provider_bridge_port="" provider_bridge_endpoint="" provider_bridge_needs_node=0
  if sc_local_provider_enabled; then
    provider_bridge_kind="$SC_LOCAL_PROVIDER"
    provider_bridge_port="$SC_LOCAL_PROVIDER_PORT"
    provider_bridge_endpoint="$SC_LOCAL_PROVIDER_ENDPOINT"
    provider_bridge_needs_node=1
  elif [[ -n "$SC_GEMINI_ADAPTER_HOST_PORT" ]]; then
    provider_bridge_kind="responses-router"
    provider_bridge_port="$SC_GEMINI_ADAPTER_NAMESPACE_PORT"
    provider_bridge_endpoint="http://127.0.0.1:$SC_GEMINI_ADAPTER_HOST_PORT"
    provider_bridge_needs_node=1
  elif [[ -n "$SC_REMOTE_ROUTER_HOST_PORT" ]]; then
    provider_bridge_kind="responses-router"
    provider_bridge_port="$SC_REMOTE_ROUTER_NAMESPACE_PORT"
    provider_bridge_endpoint="http://127.0.0.1:$SC_REMOTE_ROUTER_HOST_PORT"
    provider_bridge_needs_node=1
  fi
  if (( SC_CAMPAIGN_AVAILABLE )); then
    args+=(--setenv SANDCODEX_CAMPAIGN "$SC_LOCAL/launcher/sandcodex-campaign")
    args+=(--setenv SANDCODEX_WORKER "$SC_AGENT_BIN/sandcodex-worker")
  fi
  if (( SC_CAMPAIGN_AVAILABLE )) || [[ -n "$SC_TEAM_MEMBER_NAME" ]]; then
    args+=(--setenv SANDCODEX_TEAM "$SC_AGENT_BIN/sandcodex-team")
  fi
  if (( SC_OPERATOR_ENABLED )); then
    args+=(
      --setenv SANDCODEX_OPERATOR_SOCKET "$SC_OPERATOR_SOCKET"
      --setenv SANDCODEX_OPERATOR_SERVICE "$SC_OPERATOR_HELPER"
    )
  fi
  local -a launch=("$SC_BWRAP")
  [[ -z "${SC_BWRAP_TIMEOUT:-}" ]] || launch=(timeout "$SC_BWRAP_TIMEOUT" "$SC_BWRAP")
  sc_seccomp_filter
  local seccomp_fd rc=0
  exec {seccomp_fd}<"$SC_RUN_ROOT/seccomp.bpf"
  if [[ "${SC_BWRAP_EXEC:-0}" == 1 ]]; then
    sc_close_inherited_fds "$seccomp_fd"
    exec "${launch[@]}" "${args[@]}" --seccomp "$seccomp_fd" -- \
      bash -c "$(sc_bwrap_body)" sandcodex \
      "$SC_SOCAT" /run/sandcodex/proxy-host/proxy.sock \
      "$([[ $SC_BROWSER == 1 || $provider_bridge_needs_node == 1 ]] && command -v node || true)" \
      "$([[ $SC_BROWSER == 1 ]] && printf /run/sandcodex/proxy-host/agent-loopback-relay.js || true)" \
      "$([[ $SC_BROWSER == 1 ]] && printf /run/sandcodex/agent-bridge/loopback.sock || true)" \
      "$([[ $SC_BROWSER == 1 ]] && printf %s "$SC_BROWSER_COMMAND_SOCKET" || true)" \
      "$([[ $SC_BROWSER == 1 ]] && printf /run/sandcodex/proxy-host/browser-mcp.sock || true)" \
      /run/sandcodex/proxy-host/publish.map "$provider_bridge_kind" "$provider_bridge_port" "$provider_bridge_endpoint" "$@"
  fi
  (
    sc_close_inherited_fds "$seccomp_fd"
    exec "${launch[@]}" "${args[@]}" --seccomp "$seccomp_fd" -- \
      bash -c "$(sc_bwrap_body)" sandcodex \
      "$SC_SOCAT" /run/sandcodex/proxy-host/proxy.sock \
      "$([[ $SC_BROWSER == 1 || $provider_bridge_needs_node == 1 ]] && command -v node || true)" \
      "$([[ $SC_BROWSER == 1 ]] && printf /run/sandcodex/proxy-host/agent-loopback-relay.js || true)" \
      "$([[ $SC_BROWSER == 1 ]] && printf /run/sandcodex/agent-bridge/loopback.sock || true)" \
      "$([[ $SC_BROWSER == 1 ]] && printf %s "$SC_BROWSER_COMMAND_SOCKET" || true)" \
      "$([[ $SC_BROWSER == 1 ]] && printf /run/sandcodex/proxy-host/browser-mcp.sock || true)" \
      /run/sandcodex/proxy-host/publish.map "$provider_bridge_kind" "$provider_bridge_port" "$provider_bridge_endpoint" "$@"
  ) || rc=$?
  exec {seccomp_fd}<&-
  return "$rc"
}
```

## Authentication reconciliation

Source lines 24612–24640; excerpt SHA-256 `4efb93f23d6b62ef218bece1b02e6aeafabe8b6713cf79667fcb18dedf3f0a70`.

```text
sc_reconcile_frontend_auth() {
  sc_frontend_requires_openai_auth || return 0
  local source target marker source_hash target_hash
  target="$SC_CONTROL/codex-home/auth.json"
  marker="$SC_CONTROL/auth-source.sha256"
  [[ -f "$marker" && ! -L "$marker" ]] || return 0
  sc_owned_single_file "$marker" 600 "project authentication marker"
  if [[ ! -e "$target" && ! -L "$target" ]]; then
    sc_clear_auth_state
    SC_FRONTEND_LOGOUT=1
    sc_log_event info frontend_logout "propagated Codex frontend logout to trusted authentication state"
    sc_ok "Codex logout propagated to Sandcodex"
    return 0
  fi
  if ! sc_valid_auth "$target"; then
    sc_warn "Codex left an invalid project credential copy; trusted authentication was not replaced"
    sc_log_event warn frontend_auth_invalid "project credential copy was not eligible for promotion"
    return 0
  fi
  source="$(sc_auth_path)"
  target_hash="$(sha256sum -- "$target" | awk '{print $1}')"
  source_hash=""
  sc_valid_auth "$source" && source_hash="$(sha256sum -- "$source" | awk '{print $1}')"
  if [[ "$target_hash" != "$source_hash" ]]; then
    sc_atomic "$source" 600 <"$target"
    printf '%s\n' "$target_hash" | sc_atomic "$marker" 600
    sc_log_event info auth_refresh "promoted refreshed frontend authentication to trusted state"
  fi
}
```
