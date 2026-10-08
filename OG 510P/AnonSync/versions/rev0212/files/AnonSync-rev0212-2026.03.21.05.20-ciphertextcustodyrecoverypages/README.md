# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0212`
- Timestamp: `2026.03.21.05.20` (America/New_York)
- Codename: `ciphertextcustodyrecoverypages`

## What changed in this revision

This revision continues directly from `rev0211` and does seven concrete things:

1. Re-checks another cluster of current official Resilio Sync docs so the archive's non-clone stance now also covers ciphertext-only custody on untrusted nodes, encrypted-target admission, decrypt prerequisites, and encrypted-Archive replay ceilings.
2. Adds one new **Resilio evaluation** document focused on how current Resilio still makes ordinary opaque-node answers depend on encrypted-folder caveats, read-only behavior, ordinary pre-populated connect guidance, and CLI-style recovery instructions.
3. Sharpens the main non-clone argument with a tighter claim: borrow Resilio's candor that ciphertext-only custody is useful, but refuse any contract where operators still have to reconstruct `is this target safe`, `what can this node never do`, `what must survive for later recovery`, and `why can't encrypted Archive restore the file from here` across several articles.
4. Adds four new **interface page specs** for the strongest seams in this pass: encrypted target admission, ciphertext custody, decrypt recovery, and encrypted Archive limit.
5. Extends the interface/workbench doctrine so opaque landing hygiene, ciphertext capability ceilings, recovery prerequisites, and history replay limits all point back to one stable product-owned page family instead of dissolving into support-style caveat memory.
6. Refreshes scorecard, clone-veto tests, product direction, interface doctrine, workbench notes, pattern language, architecture decisions, roadmap notes, and source notes so the new tranche is integrated into the archive rather than bolted on.
7. Packages the result as another continuation archive with the new tranche called out explicitly in the reading order and archive map.

## Current conclusion, tightened again

Another current Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's page contracts**

This time the evidence is especially clear around **ciphertext-only custody, encrypted-target admission, decrypt prerequisites, and encrypted-Archive replay ceilings**.

Current official docs still openly distinguish real encrypted-node truths such as:

- encrypted folders still existing specifically to keep a peer on an untrusted device without revealing plaintext
- encrypted destinations still needing a freshly created directory rather than a casual non-empty target
- same-F-key residue still being re-synced and moved to Archive with extra-space cost
- encrypted nodes still being read-only, forced-overwrite, and without Selective Sync
- onward sharing from the opaque node still being limited to encrypted format
- later recovery still depending on saved RW/RO keys and database continuity, or on an explicit CLI/offline decrypt lane
- encrypted Archive still not being able to replay a deleted file back into the live share from that node

That candor is good.
The non-clone problem is the page shape.
Ordinary operators still have to reconstruct one encrypted-custody answer from several articles to know:

- whether the chosen target is safe for opaque landing
- whether this node can ever produce plaintext in ordinary flow
- which exact materials must be preserved now to make later recovery real
- whether retained encrypted history here is evidence, fetchability, or actual live replay authority

That means AnonSync should become **more explicit than Resilio about opaque custody and recovery prerequisites, not less candid than Resilio about the hard ceilings of encrypted nodes.**

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
4. `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
5. `docs/486-resilio-ciphertext-custody-recovery-prerequisites-and-encrypted-archive-ceiling-evaluation.md`
6. `docs/487-encrypted-target-admission-page-empty-root-fkey-reuse-and-archive-side-effects-interface-spec.md`
7. `docs/488-ciphertext-custody-page-plaintext-ceiling-onward-share-and-default-ro-guardrails-interface-spec.md`
8. `docs/489-decrypt-recovery-page-saved-key-database-continuity-and-cli-witness-interface-spec.md`
9. `docs/490-encrypted-archive-limit-page-delete-state-following-and-recovery-source-ladder-interface-spec.md`
10. `docs/38-operator-workbench-interface-spec.md`
11. `docs/30-interface-spec.md`
12. `docs/20-product-direction.md`
13. `docs/40-architecture-decisions.md`
14. `docs/50-roadmap.md`
15. `docs/sources.md`

## Archive map for this revision

- `docs/486-resilio-ciphertext-custody-recovery-prerequisites-and-encrypted-archive-ceiling-evaluation.md`
- `docs/487-encrypted-target-admission-page-empty-root-fkey-reuse-and-archive-side-effects-interface-spec.md`
- `docs/488-ciphertext-custody-page-plaintext-ceiling-onward-share-and-default-ro-guardrails-interface-spec.md`
- `docs/489-decrypt-recovery-page-saved-key-database-continuity-and-cli-witness-interface-spec.md`
- `docs/490-encrypted-archive-limit-page-delete-state-following-and-recovery-source-ladder-interface-spec.md`

The rest of the archive remains in place and is updated in-place where the new tranche changes doctrine.
