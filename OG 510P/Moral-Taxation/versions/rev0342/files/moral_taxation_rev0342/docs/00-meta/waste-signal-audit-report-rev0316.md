# Waste-signal audit report — rev0316

Result: pass; queue closed.

No negative bytes-saved metrics remain.

## Closure details

- `tax_admin_section_bytes_saved`: 7314
- `wealth_property_route_memo_bytes_saved`: 5010
- `procurement_route_memo_bytes_saved`: 959

`tools/audit_waste_signals.py` now fails the release if any live `*_bytes_saved` metric is negative.
