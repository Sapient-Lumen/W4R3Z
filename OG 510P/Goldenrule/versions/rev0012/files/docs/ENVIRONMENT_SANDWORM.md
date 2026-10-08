# Sandworm Environment Notes

This repo is typically developed inside **sandworm** (see `Original-Starting-Place/sandworm`).

## What sandworm is (in this repo)

- `Original-Starting-Place/sandworm` is a wrapper that launches a containerized workspace (Podman-backed by default).
- It supports multiple “postures” (SAFE/UNSAFE/STRICT) and can expose host integrations.

See also:
- `/home/sandworm/SANDWORM_ENV.md` (inside the sandbox)
- `/home/sandworm/SANDWORM_CAPS.json` (inside the sandbox)
- `python3 tools/sandworm_py.py doctor` (quick local diagnostics)

## Network (current blocker)

We observed a case where outbound networking appeared configured (host network, DNS stub present) but **AF_INET sockets were denied** *inside the Codex tool sandbox*:

- `python3 -c 'import socket; socket.socket(socket.AF_INET, socket.SOCK_STREAM)'` → `PermissionError: [Errno 1] Operation not permitted`
- AF_UNIX sockets still worked.
- `/proc/self/status` showed:
  - `Seccomp: 2`
  - `Seccomp_filters: 1`
- `env` included `CODEX_SANDBOX_NETWORK_DISABLED=1`

This indicates the Codex sandbox seccomp profile is preventing IPv4/IPv6 sockets in *sandboxed* tool runs, regardless of `SANDWORM_NETWORK_MODE`.

### Suggested diagnosis steps (run in `sandworm shell`)

1) Confirm whether AF_INET sockets work:

```bash
python3 - <<'PY'
import socket
socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("AF_INET socket ok")
PY
```

2) Check whether a seccomp filter is active:

```bash
rg -n 'Seccomp|Seccomp_filters|NoNewPrivs' /proc/self/status
```

3) If sockets are blocked, inspect sandworm posture + networking settings:
- `Original-Starting-Place/sandworm doctor`
- `env | rg '^SANDWORM_|^SW_'`

### What we likely need (Codex)

- When web access is required, run commands **outside** the Codex tool sandbox (the sandbox disables networking by design in some configurations).
- In Codex CLI terms, this typically means running in a mode equivalent to “danger-full-access” / bypassing the sandbox for shell commands.

## Rust in constrained sandboxes (practical fallback)

When native `cargo` is missing and Sandworm nix preflight fails (`nix_preflight_runtime_constraint`), use the JuNest fallback:

1) Initialize JuNest once:

```bash
/run/sandworm/toolroot/bin/junest setup
```

2) Refresh package metadata and keyring:

```bash
SW_JUNEST_HOME=/workspace/.sandworm/toolroot/junest-home /run/sandworm/toolroot/bin/junest ns -f -- sh -lc 'pacman -Syy --noconfirm && pacman -Sy --noconfirm archlinux-keyring'
```

3) Install Rust toolchain in JuNest:

```bash
SW_JUNEST_HOME=/workspace/.sandworm/toolroot/junest-home /run/sandworm/toolroot/bin/junest ns -f -- sh -lc 'pacman -S --noconfirm rust'
```

4) Run Rust commands through the repo wrapper:

```bash
tools/rust_exec.sh cargo test -p gr_engine
tools/rust_exec.sh cargo fmt --check
```

### Offline mode fallback

- If web access isn’t available, prefer an explicit “offline mode” workflow: keep a curated local reading pack + notes under `docs/LIBRARY/` and record which claims are based on offline sources vs refreshed web sources.
