# OSC control (UDP)

VHK can expose a small **OSC (Open Sound Control)** UDP listener that forwards
messages to the VHK **bus**.

OSC is a common control protocol for "button box" and automation ecosystems.
For example:

- Bitfocus Companion's generic OSC connection lets you specify an OSC path and a value.
- Node-RED has OSC nodes (e.g. `node-red-contrib-osc`) that can receive/send OSC and
  bridge OSC <-> HTTP/MQTT/etc.

OSC messages consist of an **address pattern** (usually starting with `/`) and
arguments.

## Run the server

```bash
vhk busd /path/to/project
vhk oscd /path/to/project --host 127.0.0.1 --port 40001
```

By default, VHK binds to localhost only.

## Address mapping

VHK treats a handful of `/vhk/...` addresses as control surfaces:

- `/vhk/emit <event> <json?>`
- `/vhk/emit/<event_path> [<json?>]`
- `/vhk/bus/<event_path> [<json?>]`
- `/vhk/dispatch <macro> <vars_json?>`
- `/vhk/dispatch/<macro> [<vars_json?>]`

Where:

- `<event_path>` is converted to an event name by replacing `/` with `.`
  (e.g. `/vhk/bus/foo/bar` -> event `foo.bar`).
- `<json?>` and `<vars_json?>` are optional; if present and parseable as JSON,
  they are decoded into dict/list/etc.

All other OSC messages emit the `--default-event` name (default `osc`) with
payload:

```json
{"address": "/something", "args": [1, "x", true]}
```

## Dispatch integration

If you use a `dispatch: true` bus watcher (recommended), `/vhk/dispatch/...`
messages directly drive that surface.

Example `project.yaml`:

```yaml
bus_watchers:
  - name: controls
    event: hotkey
    dispatch: true
    dispatch_allowed_macros: ["sig", "screenshot_region"]
```

Then your controller can send:

- OSC address: `/vhk/dispatch/sig`
- OSC args: `"{\"x\": 1}"` (a JSON string)

VHK will emit a `hotkey` bus event with `{"macro":"sig","vars":{"x":1},...}`.

## Token gating

To avoid accidental LAN triggers when you bind beyond localhost, VHK supports a
simple shared-secret mechanism:

- Run with `--token sekret` (or env `VHK_OSC_TOKEN=sekret`)
- Your controller must pass `sekret` as the **first OSC argument**

If the token does not match, the packet is ignored.
