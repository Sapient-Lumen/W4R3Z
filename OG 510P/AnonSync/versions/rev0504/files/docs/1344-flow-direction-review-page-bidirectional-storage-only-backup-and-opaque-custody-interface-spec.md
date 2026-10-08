# Flow-direction review page — bidirectional sync, storage-only backup, and opaque-custody comparison

## Purpose

This review answers one ordinary question before acceptance, migration, or troubleshooting:

> is this subject actually collaborative bidirectional sync, or am I accepting a narrower lane such as inbound-only backup, storage-only retention, or opaque encrypted custody?

## Core decision

Whenever a subject could be mistaken for a stronger lane than it really has, the product must open one first-class **Flow-direction review**.

## Fixed review order

1. request summary  
2. lane comparison table  
3. delete and survivor comparison  
4. reverse-lane warning  
5. commit review  
6. receipt preview

### 1) Request summary

Show:

- subject
- seat
- trigger: `new-share`, `mode-change`, `backup-enable`, `encrypted-intake`, `repair-after-surprise`, `other`
- current claimed lane
- stronger lane the operator may be assuming

### 2) Lane comparison table

Columns:

- `bidirectional sync`
- `read-only replication`
- `storage-only backup`
- `opaque encrypted custody`
- `current subject`

Rows:

- can originate edits here
- can originate deletes here
- can receive remote edits
- can serve bytes outward
- can re-share in plaintext
- can restore world from local recovery path

The operator must be able to answer: **which lane am I truly in?**

### 3) Delete and survivor comparison

Show side-by-side:

- what a local delete does
- what a remote delete does
- what disconnect preserves
- whether local bytes become merely retained evidence or still part of live collaboration

### 4) Reverse-lane warning

If the current lane is weaker than bidirectional sync, show:

- what recovery cannot happen from here
- what extra prerequisites would be needed for any reverse rescue
- which stronger recovery sentence is blocked

### 5) Commit review

The commit area must never use a generic `Continue` button.
Allowed buttons:

- `Accept bidirectional lane`
- `Accept inbound-only / storage-only lane`
- `Accept opaque custody lane`
- `Stop and choose another lane`

### 6) Receipt preview

Preview the receipt fields that will be written:

- winning lane
- delete-direction verdict
- reverse-recovery verdict
- disconnect survivor class
- blocked stronger sentence

## Copy rules

- Use `storage-only` when local bytes survive but local edits do not publish.
- Use `opaque custody` when local bytes are held without normal local meaning.
- Use `reverse recovery blocked` unless the system has a real, reviewed path.
- Do not let `connected` or `present` decide the lane label by themselves.
