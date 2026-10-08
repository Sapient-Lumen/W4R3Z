## Participant-unit contract sheet

### Purpose
Make the product say **what kind of participant** it is talking about before it says anything about approval, permissions, counts, or disconnect scope.

### The contract object
Each participant reference renders these fields together:

- **Participant unit class**: human-facing identity, certificate-bearing identity, linked-device family, individual device seat, grouped user row, device row, or historical roster record.
- **Stable authority basis**: certificate fingerprint, linked-family witness, per-device handle, or unknown / row-only basis.
- **Display planes**: identity name, device name, row label, and any collapsed group label.
- **Count basis**: row count, device-seat count, grouped-user count, authority-capable count, or unknown mixed count.
- **Permission attachment scope**: identity-wide, family-derived, per-device only, row-only approximation, or not provable here.
- **Approval-memory scope**: none, row-local only, certificate memory, linked-family memory, or unknown.
- **Change sensitivity**: device rename, regrouping, relink, identity regeneration, folder-family switch, or surface-specific rendering.
- **Blocked stronger sentence**: the next stronger statement the product refuses to make.

### Default language rules
- `participant` is intentionally weaker than `identity`.
- `identity` is intentionally weaker than `same certificate continuity`.
- `peer row` is intentionally weaker than `device seat`.
- `device seat` is intentionally weaker than `authority unit`.
- `X participants` is forbidden unless the count basis is explicit.

### Required persistent receipts
Any serious share, approval, disconnect, count, or permission action stores one durable receipt preserving participant-unit class, count basis, authority basis, approval-memory scope, regroup risks, and the blocked stronger sentence.
