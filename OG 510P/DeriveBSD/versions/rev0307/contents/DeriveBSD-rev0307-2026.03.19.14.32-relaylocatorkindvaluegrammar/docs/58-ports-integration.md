# Ports integration: from ports tree to Derive specs

Ports are BSD’s ecosystem power.
DeriveBSD treats the ports tree as a pinned input (git commit / branch) and translates recipes into Derive specs incrementally.

## Strategy
- importer emits Spec templates + distfiles list for locking
- curated overlay for high-value ports
- optional bulk build patterns inspired by poudriere

See RFC-0035.
Last updated: 2026-02-23
