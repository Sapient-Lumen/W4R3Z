## Byte-cost proof page

A strong movement claim must publish the strongest honest proof it has.

### Proof ladder
- **P0 — no byte-cost proof**  
  Only a general feature description exists.

- **P1 — rule-derived expectation**  
  The current lane is known to prefer changed-piece transfer or Archive rename reuse, but no case-specific witness is shown.

- **P2 — case-shaped witness**  
  The current case has a known trigger like piece shift, Archive hash hit, or queue preemption.

- **P3 — observed movement proof**  
  Runtime evidence shows delta movement, full resend, or priority-only suspension in this concrete transfer.

### Stronger-sentence barriers
Do not say:
- `only changed data moved` without at least P2
- `rename avoided retransmission` without Archive-hit basis
- `priority reduced transfer cost` unless byte-cost evidence exists independently of order evidence
- `strict priority applied` when the lane is not proven splittable
