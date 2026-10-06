# Current removable-media post-detach terminal closure

The current post-detach removable-media lane now has a terminal closure capsule. After r528 export access and r529 export-bundle deletion, r530 emits `removable.media.local.post_detach.terminal.closure.capsule` to bind deletion, denial selection, denial reason registry, support projection, transition witness, and scenario replay into one end-state artifact.

Terminal closure means future access is denied unless new authority is issued. Query projection, export, rehydration, and reader observation cannot use the old handle, expired root, or deleted managed export after closure. A new export also requires new approval.

offline-copy erasure is not claimed. The capsule records terminal managed-authority posture and denies future managed access, but it does not pretend to erase unmanaged recipient copies that already left the controlled host.

The r530 cut also completes the denial receipt schema split: `spec/removable.media.local.post_detach.denial.receipt.schema.json` is runtime-shaped, while `spec/removable.media.local.post_detach.denial.receipt.fixture.schema.json` preserves the exact r510 fixture.

Last updated: 2026-05-30r530
