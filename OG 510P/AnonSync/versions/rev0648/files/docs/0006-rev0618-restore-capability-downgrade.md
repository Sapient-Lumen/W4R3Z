# Rev0618 restore capability-downgrade hardening

Rev0618 closes a slim-cube restore seam: SQLite/WAL snapshot restore no longer accepts missing or downgraded backend capability metadata.

The C++ runner now requires capability format `anonsync-ledger-backend-capabilities-v15` before a SQLite/WAL restore can proceed. Under v15, restore requires the signed snapshot manifest, restore-root trust profile, and operator-provided trust-profile SHA-256 digest pin. The unsigned restore path is disabled for the active slim runtime.

Negative checks in the validator cover three local failure modes:

- missing backend capability manifest;
- downgraded v14 capability manifest;
- unsigned restore fallback with no manifest/trust material.

This is still local single-node SQLite evidence. It prevents local restore-policy downgrade in this cube, but it does not prove distributed replay prevention, production PKI, tamper-proof storage, custody, delivery, or legal finality.
