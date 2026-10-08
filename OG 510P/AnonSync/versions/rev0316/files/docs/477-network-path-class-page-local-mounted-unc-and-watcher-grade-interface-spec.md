# Network path class page: local, mounted, UNC, and watcher grade interface spec

## Purpose

This page answers:

> what exact kind of storage path is this, what runtime is binding it, and what watcher/freshness grade comes with that path class before we pretend it is just another folder?

The page exists because `Folder path`, `Browse`, `Choose directory`, and `Connected` are not enough truth when the path is remote.

## Core rule

Every non-trivial remote or service-mounted path must compile to one first-class **Network path class** page before the product represents it as an ordinary sync subject.
That page owns:

- path class
- runtime identity
- watcher grade
- service/storage-root consequences
- class receipt

## Primary layout

The page always renders the same regions:

1. path verdict
2. path-class card
3. runtime / identity card
4. watcher-grade card
5. receipt and follow-on links

### 1) Path verdict

Show:

- verdict label: `local`, `mounted-network`, `unc-under-service`, `service-inherited`, `unknown`
- strongest honest one-line summary
- runtime currently binding the path
- one safest next action

### 2) Path-class card

Show:

- exact normalized path
- class (`local fs`, `smb mount`, `unc share`, `service virtualized`, `unknown remote`)
- protocol family if known
- whether the path is chooser-visible, manually typed, or config-declared
- strongest class-specific caveat

The operator must be able to answer: **what kind of path did we actually bind here?**

### 3) Runtime / identity card

Show:

- process form (`desktop`, `service`, `config mode`, `headless`)
- effective user / service identity
- storage-root consequences if identity changes
- whether mapped-drive semantics are unavailable here
- whether re-add / re-share would be required after runtime identity change

The operator must be able to answer: **who is really touching this path, and what else changes if that runtime changes?**

### 4) Watcher-grade card

Show:

- grade: `live notifications`, `partial notifications`, `rescan only`, `restart-sensitive`, `unknown`
- proof basis (`path probe`, `protocol rule`, `runtime workaround`, `operator assertion`)
- expected freshness ceiling
- strongest downgrade cause

The operator must be able to answer: **how fresh can this path honestly be?**

### 5) Receipt and follow-on links

Link to:

- Protocol discipline
- Detection grade
- Network subject admission

After any accepted action, emit a receipt that preserves:

- path class before and after
- runtime identity
- watcher grade
- strongest caveat acknowledged
- chosen next review

## Honest outputs

This page may conclude:

- `mounted SMB path · live notifications not proven · rescan-grade until demonstrated otherwise`
- `UNC path under service · mapped drive unavailable · restart/rescan freshness ceiling`
- `local filesystem path · notification-capable · ordinary admission path`
- `unknown remote semantics · do not admit without review`

It may not collapse these into one generic `folder selected` verdict.

## Rules

### Rule 1 — path class must stay visible after bind

Do not identify a remote subject only by its friendly name.
The bound class must stay public after setup.

### Rule 2 — watcher grade is part of path class, not a hidden diagnostic

A path that can sync only on rescan is a different contract from one with live notifications.
Do not hide that behind an `Advanced` panel.

### Rule 3 — service identity changes need overt receipts

If path usability depends on switching to Local System or another runtime identity, the page must keep that consequence adjacent to storage-root and re-add fallout.

### Rule 4 — unknown remote semantics block confidence

If the product cannot prove what kind of remote path this is, it must say `unknown` and widen review rather than bluffing a local-grade contract.

## Event language

Use explicit phrases such as:

- `path class changed from mapped-drive expectation to UNC-under-service`
- `live watcher support unproven on this mounted share`
- `runtime switch would relocate state root and require subject rebind`
- `remote semantics unknown; admission blocked pending review`

Avoid vague lines such as:

- `folder available`
- `path accepted`
- `connected successfully`

## Non-clone reason

Current official Resilio docs are usefully candid that SMB shares, UNC workarounds, and service identities are real path classes with different freshness and permission behavior.
But the operator still has to reconstruct that class from multiple articles.
AnonSync should instead expose one Network path class page where storage kind, runtime identity, watcher grade, and path caveat stay adjacent.
