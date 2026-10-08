# Resilio replay class, piece shift, and differential-sync edition ceiling evaluation

## Why this seam matters

Another current official Resilio pass exposes a sharper non-clone reason than a generic `incremental sync is fast` slogan.
Resilio's public Sync FAQ still says files are split into pieces from **32 KB to 2 MB**, that usually **only changed pieces** are transferred, but that if the edit shifts all pieces the **whole file is re-synced** instead. The same official FAQ still says **Sync Business** has a **diff delta sync** feature for that shifted-file case. Official Resilio documentation for Active Everywhere goes even further: administrators can still choose whether to disable differential sync entirely, retain or drop hashes, and accept whole-file replay on slower disks or when hash availability is weak. The live Sync v3 help-center line still runs through **3.1.2.1076**.

That is exactly the kind of truth AnonSync should not hide under one reassuring sentence like `incremental`, `delta`, `efficient`, or `only changed parts`.
The real operator contract already has several materially different replay classes:

1. **piecewise replay** — changed pieces only
2. **shift-sensitive fallback** — whole-file resend when piece boundaries move
3. **diff-delta replay** — stronger changed-block replay when the edition/runtime supports it
4. **full-file replay by policy** — the system intentionally prefers resend over recheck because CPU/disk cost is judged too high

Resilio is candid that these are real.
The non-clone problem is again workflow ownership.
The operator still has to reconstruct the answer to `what replay class is actually in force for this file/job/seat right now?` from a consumer FAQ, enterprise/job-profile documentation, and performance-tuning guidance.

## What current official docs still say

### 1) Public Sync FAQ already narrows the `only changed pieces` promise

The current Sync FAQ still says:

- each file is split into pieces from 32 KB to 2 MB depending on file size
- only changed pieces are usually transferred
- if an edit shifts all pieces, the **whole file** is re-synced
- Sync Business has **diff delta sync** to avoid full re-sync even in that shifted-file case

That means the ordinary public promise is already not one thing.
It is a layered replay ladder.

### 2) Official enterprise documentation makes replay class policy-bearing

Current official Resilio documentation for pre-seeded synchronization still says that after a file is judged to need sync, the system follows the **Disable differential sync** parameter:

- `Yes` means the whole file is synced across the network
- `No` means the system checks file pieces, hashes them, discovers changed pieces, and syncs only those

The same documentation still ties replay quality to hash strategy and ownership reality:

- lazy indexing can leave only the owner with usable hashes
- forcing owner hashing or retaining hashes changes replay cost and future reuse
- weak or absent hash availability can turn changed-file replay back into heavier resend behavior

So replay class is not merely an implementation detail.
It is a real policy choice with CPU, disk, and network consequences.

### 3) Best-practice guidance shows the contract is workload-shaped, not universal

Current official Resilio best-practice pages for VDI / profile-style workloads still say:

- on slower storage it may be preferable to disable differential sync and just re-transfer the file
- on faster storage it may be worth rechecking and sending only changed pieces
- rolling-checksum choices affect whether shifted blocks can still be reused
- some storage families are advised to leave differential sync off because the local recheck cost is too high

That is strong operational candor.
But it also means the user-facing product should not collapse `changed file` into one imaginary replay path.

## Why AnonSync should not clone this contract

AnonSync should absolutely borrow the Resilio instinct that replay cost is a first-class operational truth and that the product should admit when CPU/disk cost can outweigh network savings.

AnonSync should **not** clone a contract where:

- `incremental` can still mean three or four materially different replay classes
- shift-sensitive fallback to full resend appears only after the fact
- stronger diff-delta capability is edition- or runtime-dependent without one ordinary posture page
- operators have to infer from help prose whether replay is limited by edit shape, hash availability, disk speed, or product tier

The product should instead surface one ordinary answer before a heavy replay starts:

> **What replay class is active here, why, what could make it worse, and what stronger class is unavailable?**

## Product obligations this evaluation adds

AnonSync should add one explicit family around **replay class honesty**:

1. **Replay class posture** — current class, strongest available class, edit-shape ceiling, and hash basis
2. **Replay cost review** — before commit or policy change, show likely CPU/disk/network tradeoff and whole-resend risk
3. **Replay evidence** — piece map, rolling/diff lane, and why the current subject is using this class right now
4. **Replay receipt** — preserve the class actually used and the strongest sentence the product may safely say afterward

## Tightened conclusion

Borrow Resilio's candor that changed-file replay is workload-shaped and policy-bearing.
Do not clone a product contract where `only changed pieces`, `delta`, or `incremental` still hide **piece-shift full resend**, **hash-availability fallback**, and **edition-gated stronger replay**.
