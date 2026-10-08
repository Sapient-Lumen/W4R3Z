# Python surface — rev0031

New modules:

```text
src/i2p_dht_lab/leaseprobe.py
src/i2p_dht_lab/repairdebt.py
src/i2p_dht_lab/auditmesh.py
```

New tests:

```text
tests/test_rev0031_leaseprobe_repairdebt_auditmesh.py
```

Important decisions:

- `LeaseProbeAttempt` joins a lease, live-probe report, egress events, and optional key-crisis gate.
- `assess_lease_probe_window` adds probe-family diversity and replay pressure.
- `RepairDebtItem` records typed debt without turning repair triggers into work automatically.
- `build_repair_debt_plan` schedules hard-negative/tombstone work before convenience repair and defers by budget.
- `audit_audit_mesh` pins current revision visibility while checking the rev0030 predecessor fold.
