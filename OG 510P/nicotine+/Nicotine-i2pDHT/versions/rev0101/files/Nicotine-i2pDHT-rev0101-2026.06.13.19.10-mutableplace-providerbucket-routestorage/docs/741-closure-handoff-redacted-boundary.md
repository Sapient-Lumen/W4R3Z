# Closure handoff redacted boundary

`closurehandoff.py` prepares redacted handoff packets for local operator, garden witness, or public summary audiences.  It joins export receipt and retention-GC reports at the same exact boundary before handoff is locally accepted.

Handoff rejects raw boundary/payload exposure, component-digest drift, boundary drift, replay, sequence forks, previous-link mismatch, low diversity, dropped contradiction memory, and hard-negative pressure.

The design rule: a closed repair trace may be shared only as scoped redacted evidence, never as raw boundary material by accident.

Needle: closure handoff.
