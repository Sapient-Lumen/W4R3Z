# Protocol v0

## Envelope

```json
{
  "version": "0.1",
  "request_id": "uuid-or-null",
  "type": "message.type",
  "tab_id": 123,
  "timestamp": "2026-03-06T21:00:00+00:00",
  "payload": {}
}
```

## Shared message types in use

- `health.ping`
- `state.snapshot`
- `prompt.read`
- `prompt.write`
- `prompt.submit`
- `transcript.latest`
- `transcript.delta`
- `selection.read`
- `debug.dom_candidates`
- `adapter.detected`
- `bridge.status`
- `bridge.forward_to_active_tab`
- `error.report`

## Local broker line protocol

The local UNIX socket uses newline-delimited JSON messages.

Requests from CLI to broker include:
- `{"op": "ping"}`
- `{"op": "status"}`
- `{"op": "watch"}`
- `{"op": "submit_browser_request", "message": <envelope>}`

Responses/events are also newline-delimited JSON objects.

## Stability guidance

- prefer additive changes
- keep site-specific data inside `payload`
- keep core names generic
