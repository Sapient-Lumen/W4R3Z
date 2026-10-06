# Current removable-media post-detach export-bundle deletion

The current post-detach export path has a terminal deletion/revocation step. A redacted export bundle can become visible only through the r528 export access receipt, and that managed export is not complete until r529 emits `removable.media.local.post_detach.export.bundle.deletion.receipt`.

The deletion receipt proves the exact export access receipt by computed digest, bounded retention expiry or explicit revocation, terminal deletion or quarantine of local managed copies, revocation or deletion of controlled remote objects, absence of live/raw locators, support-safe digest-only projection, and CAS-rooted deletion ledger advancement after the export ledger.

offline-copy erasure is not claimed. The receipt denies future managed authority and records controlled cleanup, but it does not pretend to erase unmanaged recipient copies that already left the host.

The red corpus rejects missing or stale export-access bindings, deletion before expiry without revocation, remote/local copies left live, raw locator visibility, unbounded retention, non-advancing deletion ledgers, and non-terminal outcomes.

Last updated: 2026-05-30r529
