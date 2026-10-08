# Materialization contract sheet page: placeholder, hydrated, pinned, and byte witness

This page exists so `I can see the file` stops pretending to mean `I have the bytes`, `it will stay local`, or `someone still has a fetchable source`.
A subject with placeholders needs one page that tells the operator what kind of local presence actually exists.

## Operator question

> For this file, folder, or share, what is visible, what bytes are actually local, what future-locality promise exists, and what source witness still supports later fetches?

## When this page must appear

Render this page whenever the product detects or the operator opens:

- a placeholder-backed subject
- a fetch / hydrate action
- a `keep on this device` / pin action
- a `remove from this device` / revert-to-placeholder action
- a `remove everywhere` / propagating delete action
- a ghost-file or missing-source warning
- a mode switch that changes placeholder behavior

## Fixed page order

1. **Target object and scope**
2. **Materialization class**
3. **Local-byte witness**
4. **Future-arrival commitment**
5. **Source-byte witness**
6. **Mutation consequences**
7. **Receipt promise**

## 1) Target object and scope

Show:

- object kind: `single-file`, `subtree`, `share`, `device-default`, `unknown`
- object id and current path
- current permissions relevant to deletion or hydration
- current mode: `disconnected`, `placeholder-capable`, `sync-all`, `unknown`

The operator must be able to answer: **what exact object is this contract about?**

## 2) Materialization class

Show one primary class:

- `name-only-placeholder`
- `hydrated-file`
- `hydrated-subtree`
- `pinned-file`
- `pinned-subtree`
- `fully-synced-share`
- `unknown-materialization`

Also show the strongest safe sentence currently allowed and the stronger blocked sentence.

The operator must be able to answer: **what kind of local presence do I really have?**

## 3) Local-byte witness

Show:

- whether bytes are currently local: `none`, `partial`, `full`, `unknown`
- whether the local object is only metadata / placeholder
- whether opening relies on network fetch right now
- whether local deletion would remove bytes or merely remove a placeholder entry

The operator must be able to answer: **do I actually have the bytes on this device now?**

## 4) Future-arrival commitment

Show:

- whether future arrivals beneath this object will auto-download locally
- whether this is only a one-time hydration or an ongoing residency promise
- whether the commitment is `file-only`, `subtree-only`, `share-wide`, or `none`

The operator must be able to answer: **if new files appear later, will this object pull them down automatically?**

## 5) Source-byte witness

Show:

- whether at least one known source peer currently claims real bytes
- freshness of that witness
- whether all known peers appear to hold placeholders only
- whether demand is ghost-risky because the product no longer has a live byte witness

The operator must be able to answer: **can I honestly expect a future fetch to succeed?**

## 6) Mutation consequences

Show consequences for:

- `Hydrate now`
- `Pin locally`
- `Revert to placeholder`
- `Delete everywhere`
- `Turn Sync All on`
- `Disconnect or remove share`

Each action must publish survivor map, propagation scope, and whether the action risks removing the last known full copy.

The operator must be able to answer: **what exactly changes if I act from here?**

## 7) Receipt promise

Show:

- the receipt id that will be written
- what the receipt will preserve about class, local bytes, future-arrival commitment, source witness, and blocked stronger sentence
- which later observation should reopen this contract automatically

## What this page must never imply

It must never imply that these are the same:

- visible file name and local bytes
- one-time hydration and ongoing local pin
- pinned subtree and whole-share sync-all
- no current byte witness and safe offline promise
- local revert to placeholder and delete everywhere

## CLI projection expectation

A headless projection such as `anonsync materialization show --view contract` must render the same sections and verdicts without requiring GUI-only nuance.
