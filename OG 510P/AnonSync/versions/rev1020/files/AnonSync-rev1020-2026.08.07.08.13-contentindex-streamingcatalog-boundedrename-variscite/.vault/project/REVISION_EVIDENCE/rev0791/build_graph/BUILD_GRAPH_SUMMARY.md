# rev0791 build-graph proof

The pure sender-replay semantic owner is a genuine focused boundary. A fresh
Ninja graph for `anonsync_ingress_sender_replay_record_test` contains
**4 actions**, **2 first-party translation units**,
**417 lines**, and **19,479 bytes**. It does not compile or link
SQLite or `anonsync_core_lib`.

The integrated restart/restore proof still requires **47 actions**,
**36 first-party translation units**, and **53,242 first-party lines**, plus the
SQLite amalgamation. `anonsync_core` similarly exposes **53,632 first-party lines** in
**47 actions**.

The full-core-to-focused ratios are **128.61× by first-party lines** and
**11.75× by actions**. The integrated proof exposes
**127.68×** as many first-party lines as the pure proof. This is why
field/time/binding semantics belong in the extracted owner even though durable
row acquisition necessarily remains integrated with the ledger.

Configure-time CMake guards reject source reabsorption into the core and a
reverse dependency from the focused library or test onto `anonsync_core_lib`.
