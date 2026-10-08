# Known / already-mentioned or overlapping findings — rev0100

Rev0100 does **not** claim a new broad user-visible freeze, memory leak, transfer stall, or connectivity symptom. Public issues already cover broad RAM/`MemoryError`, freezes, connection-closed behavior, stuck transfers, search lag, and browse lag.

Rev0100 should therefore not be presented as “Nicotine+ freezes” or “transfers get stuck.” It is a narrow bridge-hardening mechanism: once the cube adds a bounded lifecycle retry shelf, priority cleanup/rollback events must be able to displace ordinary preserved retry payloads when the shelf is full.

Known-overlap families that remain separate:

- Broad RAM / `MemoryError` / protocol receive reports.
- Broad “freezes for minutes” and UI lag reports.
- Broad connectivity / connection-closed / queued-transfer reports.
- Broad browse/search response lag reports.

The rev0100 value is the exact priority-admission invariant inside the accepted-work lifecycle bridge.
