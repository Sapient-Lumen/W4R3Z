# Installation clearance review page: uninstall, storage residue, and peer-record afterlife interface spec

This page exists so `uninstalled` stops pretending to mean `forgotten`, `deleted`, or `cleaned up everywhere`.
For a sync product, removing the program binary is only one slice of the lifecycle.

## Operator question

> after uninstall or teardown, what survives in storage, in rosters, in archives, and in remote memory of this seat?

## When this page must appear

Render whenever the product is about to:

- uninstall or purge an installation
- retire a service runtime
- claim that a seat is gone
- guide manual deletion of storage roots or service residue
- explain why a dead installation still appears offline elsewhere

## Fixed page order

1. **Clearance verdict**
2. **Program vs state split**
3. **Storage residue inventory**
4. **Roster afterlife review**
5. **Blocked stronger sentence**

## 1) Clearance verdict

Show one verdict:

- `program removed only`
- `program removed and local state retained`
- `program removed and local state purged`
- `installation retired but peer records may persist`
- `clearance claim incomplete`

The operator must be able to answer: **what was actually cleared?**

## 2) Program vs state split

Separate these classes explicitly:

- executable / package files
- settings / storage roots
- `.sync` and archive/service residue
- shell / service helper residue
- local synced folder bytes
- mobile platform device-file exceptions

The operator must be able to answer:

> what disappeared with uninstall, and what required a separate cleanup step?

## 3) Storage residue inventory

For each residue row show:

- path or object class
- still present / manually removed / unknown
- contains ordinary data, metadata, archive versions, or service state
- safe-to-delete basis or missing proof

## 4) Roster afterlife review

Show how the retired seat may still survive elsewhere:

- linked-device list still shows offline record
- peer list still has stale row until cleanup or timeout-equivalent review
- remote seats may still remember approvals or historic presence
- remote bytes and archives remain outside uninstall scope

## 5) Blocked stronger sentence

Allowed examples:

- `The application was removed, but synced folders remain in the file system.`
- `Archive residue still existed until manually cleared.`
- `Other peers may still display this seat as offline until roster cleanup.`

Blocked examples:

- `Uninstall erased all traces.`
- `No remote seat remembers this installation.`
- `All synchronized data was removed.`

## Main actions

Examples:

- `Review leftover state paths`
- `Review stale roster records`
- `Confirm manual archive clearance`
- `Export installation-clearance receipt`
