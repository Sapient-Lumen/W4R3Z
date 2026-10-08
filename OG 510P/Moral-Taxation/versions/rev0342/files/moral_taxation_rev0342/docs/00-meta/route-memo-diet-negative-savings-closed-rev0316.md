# Route-memo diet and negative-savings closure — rev0316

Result: substantive compression pass. The prior waste queue is closed, not merely acknowledged.

## What changed

- Compact profile-backed capsule tails replaced repeated local accountability/failure/retrigger prose in tax-administration, wealth/property, and procurement route memos.
- Companion-route blocks in the touched families were tightened without removing links.
- `tools/audit_waste_signals.py` now fails if any `_bytes_saved` metric is negative.

## Byte outcome

| Family / section | Before bytes | After bytes | Saved bytes |
|---|---:|---:|---:|
| `tax_administration_access` | 145987 | 136935 | 9052 |
| `wealth_property_rent` | 42835 | 37825 | 5010 |
| `public_procurement_industrial_policy` | 20622 | 19663 | 959 |
| `tax_admin` capsule section metric | 16827 | 9513 | 7314 |

## Correction rule now enforced

A compactness refactor may not leave negative `*_bytes_saved` metrics behind. If a future pass wants to spend more bytes for a real reason, it must change the metric name or add a different non-compactness justification; the waste-signal gate no longer treats negative compactness as an acceptable queue state.
