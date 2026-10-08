# Resilio event evidence retention, notification ephemerality, and audit-ceiling evaluation

## Decision for AnonSync

Borrow Resilio's candor that different evidence surfaces have different durability.
Do **not** clone the present Resilio contract for `History`, notifications, transfer logs, archive evidence, or quick status columns.

## Why this pass matters

Current official Resilio materials still make one ordinary operator question — `what durable proof remains of what happened, who did it, and for how long?` — depend on several pages instead of one owned interface family.

The useful truths are real:

- the desktop main view still says **History** shows general syncing activity for the last **30 days**
- archive docs still say **Archive** does not itself tell you which peer made a change and points the operator to **History** for actor attribution
- the same archive docs still say archive retention defaults differ by platform: **30 days on desktops** and **1 day on mobiles**
- Sync preferences still expose **Show notifications**, which makes notifications a configurable surface rather than a durable audit ledger
- iOS single-file sharing docs still say file-download transfer history can remain visible even after the downloaded file is removed from the device
- older-but-still-relevant changelog lineage still shows observational aids such as **Date synced**, **Last transferred**, and synchronized notifications, which are helpful but weaker than a durable evidence contract

## The non-clone problem

Those truths are useful.
The page shape is not.

Present-day Resilio still externalizes too much meaning into documentation archaeology:

- `History` is a bounded activity lane rather than a plainly-scoped evidence contract
- `Archive` can preserve prior bytes without preserving actor attribution in the same place
- notifications can be shown, hidden, or synchronized without becoming a durable proof object
- transfer-history views can survive file deletion in some flows, which is useful, but the product still leaves the durability meaning implicit
- convenience columns such as `Last transferred` can look evidentiary even when they only support a weaker sentence than `proven actor-authored mutation`

So one ordinary operator answer still requires reconstructing:

1. the **evidence source family** being consulted
2. the **retention horizon** for that family
3. the **actor-attribution ceiling** of that family
4. the **join requirements** between byte evidence, event evidence, and notification evidence
5. the **strongest safe sentence** the product may still say afterward

## AnonSync product stance

AnonSync should instead own evidence durability as one page family:

- an **Evidence retention contract sheet** that states source family, durability class, retention horizon, and proof ceiling
- an **Evidence-source join review** that previews which sources are being joined and which facts remain absent
- an **Attribution gap page** that says plainly when byte recovery exists without actor proof, or actor proof exists without durable byte witness
- a **Retention horizon watch** that makes upcoming expiry and export/escalation needs visible before the proof disappears
- an **Evidence lineage receipt** that preserves which source families were joined, what they proved, what they did not prove, and what stronger sentence remained blocked

## Hard decisions now locked

1. Notifications are **signals**, not audit by implication.
2. Activity history is always **retention-bounded**.
3. Byte witness and actor witness are separate evidence families.
4. Convenience timestamps may aid explanation but may not silently impersonate durable proof.
5. Evidence expiry must be visible before it destroys the strongest safe sentence.
6. Durable receipts must preserve both the surviving proof and the blocked stronger reading.
