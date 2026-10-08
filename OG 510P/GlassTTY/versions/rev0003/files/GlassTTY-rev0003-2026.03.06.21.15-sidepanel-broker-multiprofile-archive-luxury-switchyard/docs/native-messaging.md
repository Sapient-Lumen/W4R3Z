# Native messaging notes

GlassTTY uses a Chrome native-messaging host named `com.glasstty.bridge`.

## Current model

- background service worker opens a long-lived native port
- native host speaks Chrome's length-prefixed JSON protocol on stdin/stdout
- native host also exposes a local UNIX socket for CLI access

## Host manifest

Template: `native-host/com.glasstty.bridge.template.json`

Fields to fill:
- `path`
- `allowed_origins`

## Linux user-level install defaults

- Chromium: `~/.config/chromium/NativeMessagingHosts/`
- Google Chrome: `~/.config/google-chrome/NativeMessagingHosts/`
- Chrome for Testing: `~/.config/google-chrome-for-testing/NativeMessagingHosts/`

## Practical notes

- the extension ID must be the real unpacked ID or packaged ID that Chromium assigns
- the host executable path must be executable by Chromium
- the broker socket lives under `GLASSTTY_HOME/run/daemon.sock`

## Why long-lived native port

Using a long-lived native port helps keep the service worker alive while the host is connected and gives a stable path for broker-driven round trips.
