# Risk register — rev0018

## New tested risks

- A clean adaptive lookup can still spend too much metadata once provider probes are added.
- Useful refusals can be misread as failure and trigger floods; rev0018 treats them as backoff pressure.
- Fast-window capture should quarantine even when the metadata budget has room.
- Raw content-key probes must be bounded separately from query count.
- A live tombstone plus cached alive evidence is resurrection pressure.
- A key-compromise tombstone must affect later mutable-head acceptance.
- Same-sequence tombstone forks are quarantine evidence.
- Provider surface migration should classify adapter debt before deleting old names.

## Still open

- No live SAM transport measurements.
- No private provider confirmation protocol.
- No tombstone consensus or appeal process.
- No production compatibility wrapper.
- No adversarial scale simulation beyond deterministic toy surfaces.
