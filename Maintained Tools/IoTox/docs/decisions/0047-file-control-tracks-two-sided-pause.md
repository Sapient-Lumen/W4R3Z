# ADR 0047 — File control tracks two-sided pause ownership

- Status: accepted
- Revision: rev0013
- Date: 2026-08-14
- Extends ADR 0017, ADR 0018, ADR 0045, and ADR 0046

## Context

c-toxcore file transfer pause is not one boolean. The sender and receiver may each pause. If both
pause, both must resume before bytes move. A local RESUME can therefore succeed as a local action
without making the transfer active when the peer still owns a pause.

The earlier IoTox record had one state value and a cancellation-only local control operation. That
could not represent the provider contract honestly and left generic local pause/resume parsing
reserved but undispatched.

## Decision

Each live file-transfer record carries:

```text
local_paused
peer_paused
```

Effective state is active only when neither flag is true. Provider `file_recv_control` callbacks
change peer-owned pause state. Local `file-control` commands change local-owned pause state. Local
RESUME never clears peer pause.

The one binary exposes `file-control FRIEND FILE pause|resume|cancel` through the structured local
protocol and the peer-local FIFO. `file-cancel` remains a compatibility alias.

A pending incoming offer cannot be resumed through generic control. It must first pass
`file-receive`, which acquires and validates the destination before sending RESUME. Repeated local
PAUSE is idempotent; RESUME without a local pause is rejected. CANCEL always releases local
resources even if sending the control fails.

## Consequences

Runtime projections no longer claim a transfer is active merely because one side resumed. Tests can
separately exercise local and remote pause ownership.

The local protocol minor version advances from 13 to 14 and adds operation 36 for generic file
control. Operation 34 remains the cancellation compatibility form.

Pause state remains process-local and transfer-ephemeral. Disconnect or restart terminates the
provider transfer; this ADR does not invent resumable durable transfer sessions.
