# Current removable-media post-detach terminal-closure access gate

The current post-detach removable-media lane now has a per-attempt terminal-closure access gate. After r530 terminal closure, r531 emits `removable.media.local.post_detach.terminal.closure.access.receipt` whenever old managed authority is presented for query, export, rehydrate, observe, managed-copy, or support-debug use.

The receipt applies `terminal-closure-managed-authority-closed`: old managed authority is denied, no successor is issued from the old handle, new authority is required for any successor path, and new export or managed-copy release requires new approval.

The gate binds the r530 terminal closure capsule, r529 export deletion receipt, r525 denial-selection receipt, r524 denial reason registry, r526 rate-limit debit receipt, and r521 support projection by computed digest. It also advances a CAS-rooted access ledger and keeps support visibility digest-only.

The r531 cut also completes the fresh-authority schema split: `spec/removable.media.local.post_detach.fresh.authority.receipt.schema.json` is runtime-shaped, while `spec/removable.media.local.post_detach.fresh.authority.receipt.fixture.schema.json` preserves the exact r511 fixture. This fresh-authority schema split keeps historical examples exact without making production broker output fixture-literal.

Last updated: 2026-05-30r531
