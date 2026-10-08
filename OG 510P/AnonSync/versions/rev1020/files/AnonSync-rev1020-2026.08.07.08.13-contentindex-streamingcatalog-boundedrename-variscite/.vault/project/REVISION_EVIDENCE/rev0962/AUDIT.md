# Audit — rev0962

Rev0962 closes the bounded operator lifecycle for diagnostic corrupt-payload evidence. Exact release is admitted only after the active integrity alarm clears, holds the exact reader-fenced exclusive identity lease, validates the complete bounded quarantine namespace, re-proves the selected private inode, unlinks only that inode, synchronizes the directory, proves absence, and re-proves retained authority. It deliberately does not claim the diagnostic bytes are authentic merely because an owner selected their exact expected/observed pair.

The adjacent refactor removes a whole-store reread. Preserving one corrupt payload no longer revokes unrelated exact current-byte proofs; only durable namespace checkpoint and relevant scrub scheduling state are refreshed. Releasing diagnostic evidence changes no authoritative payload namespace and retains all verification reuse.

Mechanical evidence: 186/186 structural checks; 562 payload-store checks; 92 local-control checks; real-process same-PID preserve, authenticated re-admission, recheck, exact release, unchanged authoritative inode/bytes, and clean drain; complete GCC and bounded sanitizer product matrices.

Nonclaims remain explicit: no automatic retention, archive browser, restore, reachability graph, quota eviction, age policy, or garbage collector; no defense against hostile same-UID code; no universal network-filesystem or power-loss guarantee.
