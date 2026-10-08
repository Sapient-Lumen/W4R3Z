# GlassTTY

GlassTTY is a user-driven bridge between a live browser tab and a local terminal workflow.

The project is intentionally **browser-app agnostic**. Claude.ai is the first real adapter we care about, but the architecture treats it as one adapter among many.

## What this archive now includes

- a Chromium-first Manifest V3 extension in TypeScript
- a Python native host with a local UNIX-socket broker
- a side-panel operator surface inside Chromium
- Nix development shell setup
- scripts for launching isolated Chromium profiles, listing them, and packaging releases
- docs, decisions, and session-memory files designed to survive multi-session LLM collaboration

## Working principles

- **User-driven first.** The browser stays open and visible.
- **No credential scraping.**
- **No network reverse engineering.**
- **Native messaging bridge.** Browser extension ↔ local daemon.
- **Generic core, site-specific adapters.**
- **CLI-friendly local state.** JSONL plus a local broker socket.
- **Nix-friendly dev environment.**
- **Rust-friendly protocol boundaries.** Hotspots can move later without changing the whole design.

## What is newly real in this rev

- native host now exposes a local broker socket under `GLASSTTY_HOME/run/daemon.sock`
- CLI can submit browser requests through the broker and optionally wait for replies
- extension background persists recent bridge state in `chrome.storage.local`
- side panel exposes live bridge status and quick actions
- generic adapter registry is present; Claude is the first concrete adapter
- a profile-management script exists for multiple isolated Chromium profiles
- Python tests cover protocol framing, state persistence, and broker routing

## Repository map

```text
.
├── AGENTS.md
├── CHANGELOG.md
├── DECISIONS.md
├── MEMORY.md
├── ROADMAP.md
├── STATUS.md
├── TASKS.md
├── docs/
├── adapters/
├── daemon/
├── extension/
├── native-host/
├── scripts/
├── tests/
└── flake.nix
```

## Quick start

### 1) Enter the dev shell

```bash
nix develop
```

### 2) Build the extension

```bash
cd extension
npm run build
```

### 2.5) Make the Python CLI importable

Inside `nix develop`, `PYTHONPATH` is already set for `daemon/src`. Outside Nix, either export `PYTHONPATH="$PWD/daemon/src"` or install the daemon in editable mode.

### 3) Launch an isolated Chromium profile for GlassTTY

```bash
./scripts/glasstty-profile.sh open main chrome://extensions/
```

This creates and reuses a dedicated Chromium user-data directory under `~/.local/share/glasstty/profiles/main` unless `GLASSTTY_HOME` is set.

### 4) Load the unpacked extension

Open Chromium to `chrome://extensions`, enable Developer mode, and load the `extension/` directory.

### 5) Install the native-host manifest

Once the extension has an ID, install the native-host manifest:

```bash
./scripts/install-native-host.sh   --target chromium   --extension-id YOUR_EXTENSION_ID   --host-exe "$PWD/daemon/.venv/bin/python -m glassttyd.native_host"
```

### 6) Use the broker-backed CLI

```bash
python -m glassttyd.cli socket-status
python -m glassttyd.cli read-prompt --wait
python -m glassttyd.cli read-latest --wait
python -m glassttyd.cli debug-candidates --wait
```

## First things to verify on a live machine

1. `health.ping` round-trip: extension ↔ native host
2. broker socket creation at `GLASSTTY_HOME/run/daemon.sock`
3. side-panel status view reflects active tab and last adapter
4. `prompt.read` from Claude.ai
5. `transcript.latest` from Claude.ai
6. `prompt.write` into the Claude input

## LLM hygiene

If an LLM is driving changes in this repo, it should read these files first:

1. `README.md`
2. `STATUS.md`
3. `MEMORY.md`
4. `DECISIONS.md`
5. `AGENTS.md`
6. `TASKS.md`

Then update `STATUS.md`, `MEMORY.md`, `TASKS.md`, and `CHANGELOG.md` at the end of a work session.
