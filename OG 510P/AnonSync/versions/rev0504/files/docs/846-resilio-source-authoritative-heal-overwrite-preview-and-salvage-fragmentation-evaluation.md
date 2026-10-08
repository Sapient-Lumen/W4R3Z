# Revision addendum — destructive heal preview, source-authority surrender, and salvage truth after rev0283

Current official Resilio docs are still admirably candid about what source-authoritative healing actually does.
The live v3 line still runs through `3.1.2.1076`.
Current `Is one-way synchronization possible?` docs still say that on Read Only shares overwrite healing can re-download the old name after a rename, restore a deleted file, revert edited contents to the most recent version from a RW peer, and keep newly added files local rather than syncing them.
Current `Folder Preferences` docs still say `Overwrite any changed files` is potentially destructive, while Archive stores remotely caused changed or deleted files in `.sync/Archive` for 30 days by default and disabling Archive removes that safety copy and changes remote rename/copy behavior into re-download.
Current `Using Archive for file versioning and restoring deleted files` docs still say a device's Archive receives an old version only if the file was modified by another peer, while locally deleted files are usually recovered from local trash or recycle bin instead.
Current `Encrypted folders` docs still say encrypted backup nodes are Read Only, always have overwrite activated, and may move same-key preexisting encrypted material into Archive with extra space cost.
Current `Power user preferences` docs still publish `overwrite_changes false` and `sync_trash_ttl 30 (day)` as standing defaults.
Current Android and iOS interface docs still expose separate Archive and overwrite toggles.
Current `Running Sync in configuration mode` docs still say `"overwrite changes": "true"` restores modified files to original version for read-only configuration-mode setups.

That is real candor.
It still does **not** earn direct interface cloning.

The reason is the next clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary destructive-heal answer across one-way-sync FAQ, folder preferences, archive docs, encrypted-backup docs, power-user settings, mobile interfaces, and configuration-mode prose.
So the product idea stays useful while the page contract still fails.

The missing operator-owned question is simple:

> before I let source-authoritative healing proceed, what exact local work will be surrendered, what salvage still exists on this device or elsewhere, and what loss am I knowingly waiving?

Current official docs still expose ingredients of that answer without one stable product object.
They still show that:

- renamed, deleted, edited, and newly added local work do not all fail the same way under overwrite healing
- archive-bearing depends on where the older version lived and which peer performed the modifying action
- turning Archive off narrows the rescue ladder materially
- encrypted or backup-like custody can hardwire overwrite or weaken normal restore comfort
- defaults and advanced settings can quietly widen or narrow the loss envelope before the operator ever notices

That is why this revision adds four narrower replacement pages:

- `847` Maintenance overwrite plan page
- `848` Maintenance overwrite review page
- `849` Maintenance overwrite ledger page
- `850` Maintenance overwrite receipt page

These pages keep the Resilio candor and reject the need to improvise a loss-preview contract from several unrelated feature articles.

## Why this matters for AnonSync

A serious sync product should not let destructive healing hide behind a checkbox and a hope that Archive was configured helpfully.
The product should own at least these distinctions explicitly:

- **surrender scope** — which exact local change classes will be reverted, restored over, or left stranded
- **salvage lane** — whether rescue is available through local archive, local trash, remote archive, evidence export, or successor branch
- **bearing locality** — which device actually holds the older version, if any
- **waiver boundary** — what loss becomes knowingly accepted if healing proceeds now
- **claim ceiling** — what strongest sentence remains safe afterward, and what stronger `nothing was lost` sentence is still forbidden

Resilio's current docs still make those classes legible only if the operator already knows how to translate between Read Only overwrite semantics, Archive/device-locality rules, power-user defaults, encrypted custody, and mobile toggles.
AnonSync should not clone that burden.

## Concrete product stance

Borrow from Resilio:

- candid admission that overwrite healing is destructive to some local work classes
- candid admission that rescue depends on archive-bearing conditions and retention policy
- candid admission that encrypted and backup-like seats can have special surrender constraints
- candid admission that defaults and advanced posture shape the risk envelope

Do not clone from Resilio:

- leaving surrender scope split across one-way-sync FAQ, folder preferences, archive docs, power-user defaults, mobile toggles, and configuration-mode prose
- forcing operators to infer whether rescue exists locally, elsewhere, or nowhere convenient
- leaving no first-class reviewed object that says what loss is previewed and what waiver would actually mean
- leaving no durable receipt of what was overwritten, what was salvaged, and what sentence remains safe afterward

## Evaluation summary

Resilio still deserves credit for publishing the ingredients of destructive healing honestly.
But the current product/docs path still leaves a missing object:

> there is no first-class reviewed answer to `before source-authoritative healing proceeds, what exact local work will be surrendered, what salvage still exists, and what loss am I actually waiving?`

AnonSync should therefore make **destructive-heal preview and salvage review** first-class product objects.
Every serious read-only heal, backup-seat reset, encrypted custody surrender, source-authoritative repair, and destructive rejoin attempt should publish candidate loss classes, archive-bearing status, salvage ladder, waiver boundary, strongest safe sentence, and reopen conditions before the product treats `overwrite changed files` as routine.
