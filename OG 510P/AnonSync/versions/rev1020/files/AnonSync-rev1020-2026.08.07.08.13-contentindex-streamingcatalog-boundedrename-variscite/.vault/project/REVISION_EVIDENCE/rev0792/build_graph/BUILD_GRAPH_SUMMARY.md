# rev0792 build-graph proof

The exact schema contract is a genuine focused boundary. A fresh Ninja graph
for `anonsync_sqlite_replay_ledger_schema_contract_test` contains **4 actions**,
**2 first-party translation units**, **448 lines**, and **23,413 bytes**. It does
not compile or link SQLite or `anonsync_core_lib`.

The integrated hostile-file/startup/restore proof requires **49 actions**,
**37 first-party translation units**, and **53,458 first-party lines**, plus the
SQLite amalgamation. `anonsync_core` exposes **53,767 first-party lines** in
**49 actions**.

The full-core-to-focused ratios are **120.02× by first-party lines** and
**12.25× by actions**. The integrated proof exposes **119.33×** as many
first-party lines as the pure proof.

Configure-time CMake guards reject source reabsorption into the core and a
reverse dependency from the focused schema library or test onto
`anonsync_core_lib`.
