# Architecture

## Layers

### 1. Browser page adapter (content script)

Responsibilities:
- inspect the DOM
- read visible state
- propose candidate input/output nodes
- watch for transcript mutations
- emit adapter-specific payloads upward

Non-responsibilities:
- durable storage
- CLI semantics
- native messaging access directly

### 2. Extension coordinator (background/service worker)

Responsibilities:
- accept messages from content scripts and extension pages
- normalize into shared protocol messages
- talk to the native host via `chrome.runtime.connectNative()`
- mirror recent bridge state into `chrome.storage.local`
- provide a stable operator surface for the side panel

Non-responsibilities:
- brittle site-specific parsing rules
- long-term durable state outside extension storage

### 3. Native host / broker (local process)

Responsibilities:
- speak Chrome native-messaging framing on stdin/stdout
- store event logs and latest snapshots on disk
- expose a local UNIX-socket broker for the CLI
- forward local CLI requests back toward the extension

Non-responsibilities:
- direct browser DOM access
- site-specific selector logic

### 4. CLI surface

Responsibilities:
- present ergonomic commands to the terminal user
- read broker state
- submit browser requests in a shell-friendly form
- stay human-driven by default

## Core message flows

### A. Browser page → terminal

1. content script reads or observes browser state
2. background normalizes the message and stores recent copies in `chrome.storage.local`
3. background sends the message to the native host
4. native host stores JSONL events and latest snapshots
5. broker forwards events to interested CLI watchers

### B. Terminal → browser page

1. CLI connects to broker socket
2. broker asks the extension to forward a request to the active supported tab
3. background sends the request to the active content script
4. content script performs the read/write action
5. response returns to background, native host, broker, and optionally back to the waiting CLI

## Why the side panel exists

The side panel is the right in-browser control surface for GlassTTY because it persists beside the page, gives more room than a popup, and keeps the browser-open workflow user-driven.

## Why the broker exists

The broker gives the CLI a stable local interface without making shell tools parse native-messaging framing or scrape log files.
