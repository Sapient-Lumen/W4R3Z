# HTTP control server (webhook bridge)

VHK can run a tiny local HTTP server that **emits bus events**. This is a
practical integration point for:

- Node-RED / home automation
- Stream Deck controllers (e.g. Companion “Generic HTTP Requests”)
- simple shell scripts (`curl`) and dashboards

This is intentionally **not** “browser automation.” It’s a webhook bridge into
VHK’s existing trigger surface (the bus).

## Run

```bash
vhk httpd /path/to/project
```

Default bind: `127.0.0.1:39999` (localhost only).

### Authentication

If you bind to a non-local interface (e.g. `--host 0.0.0.0`), use a token:

```bash
vhk httpd /path/to/project --host 0.0.0.0 --token "…"
```

Clients can authenticate using either:

- `Authorization: Bearer <token>`
- `X-VHK-Token: <token>`

## Endpoints

### `GET /health`

Returns `{"ok": true}`.

### `POST /emit`

Body JSON:

```json
{"event":"name","data":{...}}
```

Emits the bus event `name` with payload `data`.

### `POST /bus/<event>`

- If the body is JSON, it is emitted as the bus payload.
- Otherwise, the request body is treated as plain text and emitted as the bus
  payload.

### `POST /dispatch/<macro>`

Convenience endpoint for **dispatch=true** bus watchers.

Example:

```bash
curl -sS -X POST \
  -H 'Content-Type: application/json' \
  -d '{"vars": {"n": 1}, "binding": "deck.1"}' \
  http://127.0.0.1:39999/dispatch/screenshot_region
```

This emits the project’s dispatch event (default `hotkey`) with payload:

```json
{"macro":"screenshot_region","vars":{"n":1},"binding":"deck.1"}
```

## Recommended pattern

- Run `vhk busd` as the “brain” (long-lived)
- Export hotkeys (sxhkd/i3/Hyprland) **via the bus**
- Use `vhk httpd` as an optional external control surface

See also:

- `docs/BUS_EVENTS.md`
- `docs/BUS_DAEMON.md`
