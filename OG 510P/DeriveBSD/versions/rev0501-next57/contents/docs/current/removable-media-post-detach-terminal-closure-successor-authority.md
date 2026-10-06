# Current removable-media post-detach terminal-closure successor authority

r532 defines the terminal-closure successor authority path. r530 closes managed authority, r531 denies each later old-authority attempt, and r532 is the positive recovery artifact: a new successor may be issued only from fresh authority while the terminal closure remains terminal.

The current contract is `removable.media.local.post_detach.terminal.closure.successor.authority.receipt`.

Required posture:

- old managed authority remains denied before successor issuance;
- the r531 terminal-closure access receipt is bound by computed digest;
- the fresh-authority receipt, approval, policy, and new lease are bound exactly;
- the successor outcome is `successor-authority-issued-from-new-authority-only`;
- expired roots are not resurrected and terminal closure is not reopened;
- export requires new approval;
- reader use requires `removable.media.local.post_detach.reader.admission.receipt`;
- support remains digest-only and does not claim offline erasure.

Red fixtures live under `spec/examples/invalid/removable-media/post-detach-terminal-closure-successor-authority-receipt/`.

Last updated: 2026-05-30r532
