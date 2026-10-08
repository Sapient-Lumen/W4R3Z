# ROOM-SERVER-STATE-01 / U-111 + U-92 — rev0026

Status: **verified audited-backlog packet; not strict-promoted**.

## Scope

This packet combines two closely related server-room count-mismatch findings:

- **U-111** — `JoinRoom` aggregate user-list parallel-array count mismatch.
- **U-92** — `RoomList` room/user-count mismatch reaching room-list formatting/state.

The packet is intentionally narrow. It does not reopen every room-state issue, every server-message parser issue, or every GTK crash report.

## Current-behavior proof

Maintainer artifact:

```text
maintainer_artifacts/room-server-state-01/test_room_server_state_reproducer.py
```

Run summary:

```text
github-tag-3.3.10:   7 passed
github-branch-3.3.x: 7 passed
github-branch-master: 7 passed
```

## What was proven

```text
RoomList / U-92:
  too many user-count entries -> direct parser raises IndexError;
  same high-count message over framed server path -> logged/dropped, connection not closed in witness;
  too few public-room counts -> parses as [["alpha", 7], ["beta", None]];
  too few private-room counts -> preserves None count;
  humanize(None) raises TypeError in the same count-formatting helper used by the room-list UI.

JoinRoom / U-111:
  status count greater than user count -> IndexError;
  stats count greater than user count -> IndexError;
  too few parallel status/stats/slots/country rows -> second user remains in room user list with None fields.
```

## Important correction to old wording

The old `U-92` wording said “can crash/quit through GTK room-list formatting.” Rev0026 narrows that:

- High-count mismatch is parser-fatal in direct parsing, but the observed network-frame path catches/logs the exception and drops the malformed message.
- Low-count mismatch survives parsing and can feed `None` counts into UI formatting.

The retained audited-backlog claim is therefore count-normalization and room-list state hardening, not a proven automatic client crash for every malformed packet.

## Coherent fix shape

A coherent fix should validate aggregate counts at parse/admission time:

```text
- reject RoomList sections where count-array length differs from room-array length;
- reject JoinRoom user-list parallel arrays where status/stats/slots/country count differs from user count;
- do not create partial UserData objects with None status/stat/country fields from malformed full-list messages;
- do not pass None room counts into room-list state or UI formatting;
- preserve normal empty-list behavior and legitimate empty private-room sections.
```

Avoid inconsistent fixes such as catching only `IndexError` in UI code. That would leave partial room/user state in the core and would not address the `JoinRoom` parser side.

## Public-overlap classification

Classification: **candidate no direct public match found / public-adjacent parser and room-list UI hardening**.

Captured exact searches did not surface a direct public issue for the specific `RoomList` `None` count / `humanize(None)` path or `JoinRoom` aggregate parallel-count mismatch. Public-adjacent room/list crash material exists, so this should not be described as proven novel or isolated.

## Files

```text
maintainer_artifacts/room-server-state-01/test_room_server_state_reproducer.py
maintainer_artifacts/room-server-state-01/README.md
evidence/rev0026-room-server-state-pytest-run.txt
evidence/rev0026-room-server-state-source-trace.md
evidence/rev0026-room-server-state-probe.jsonl
evidence/rev0026-web-public-overlap-room-server-state.md
data/rev0026_room_server_state_probe_summary.csv
data/rev0026_public_overlap_room_server_state.csv
data/rev0026_room_server_state_coherence_refactor.csv
```
