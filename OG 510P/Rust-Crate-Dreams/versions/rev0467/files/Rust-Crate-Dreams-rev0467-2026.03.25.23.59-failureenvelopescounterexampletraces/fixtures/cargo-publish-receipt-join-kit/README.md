# Cargo Publish Receipt Join Kit fixtures

This fixture family is for `P-0477 Cargo Publish Receipt Join Kit`.

The goal is to freeze the **post-publish** artifact surface:

- local package facts,
- registry/index confirmation,
- publish identity,
- and release-history diffs.

These fixtures should help keep post-publish receipts distinct from:

- trusted-publishing rehearsal,
- registry-auth diagnosis,
- and provenance attestations.

This fixture family now also freezes three additional post-publish truths:

- **capture basis** — what local or imported artifact the receipt actually came from;
- **receipt authority** — which observation is authoritative for bytes, publish time, identity, and public visibility;
- **publication visibility** — whether the index is visible, docs are pending, or the public story is still partial.


This fixture family now also freezes three more registry-facing truths:

- **registry capability** — what the selected registry lane actually exposes and what remains crates.io-specific or unknown;
- **protection scope** — which mitigations, audits, advisory/watch channels, and client-version windows were really in scope;
- **bundle honesty** — one portable inventory keeping bytes, identity, registry capability, protection scope, and visibility distinct.
