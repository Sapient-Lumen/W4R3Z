# Control substrate contract sheet page — user bytes vs service capsule and authority boundary

## Purpose

Show the operator, in one durable place, whether a subject contains:

- user-visible bytes
- service-critical capsule state
- editable policy sidecars
- temporary transfer residue
- metadata propagation residue

The page exists to answer **`what kind of namespace is this really?`** before the operator edits, copies, scans, backs up, rehomes, or double-attaches it.

## Required sections

### 1. Subject header

Must show:

- subject name
- canonical subject identifier
- local path / binding
- seat or runtime currently claiming capsule authority
- substrate class

### 2. Namespace composition

Render five rows:

- **User content**
- **Service capsule**
- **Policy sidecars**
- **Transfer residue**
- **Metadata residue**

Each row must publish:

- presence state: `absent`, `present`, `present-hidden`, `present-mixed`, `unknown`
- editability class
- breakage risk if moved / deleted / duplicated
- whether contents are intended for operator editing

### 3. Capsule authority block

Must say:

- current capsule owner / owning runtime
- whether ownership is singular, migrated, disputed, or unknown
- whether another runtime has ever been observed against the same local tree
- whether export/copy/rebind would preserve or fork capsule lineage

### 4. Sidecar policy block

Must distinguish sidecars that are:

- operator-editable policy
- advanced/operator-editable with review
- generated residue only
- implementation-private and non-editable

Each sidecar row must include:

- sidecar family name
- effect class
- reread / activation class
- retroactivity class
- path/audience scope

### 5. Strongest safe sentence

Examples:

- `This folder contains user bytes plus a service-critical capsule; deleting or relocating the capsule suspends sync.`
- `Ignore rules are editable policy sidecars; changes alter future indexing/publication but do not unsync previously shared structure.`
- `Metadata propagation residue exists because one or more peers cannot store native xattrs.`

### 6. Blocked stronger sentence

Examples:

- `This is just a normal folder.`
- `All hidden files here are safe to ignore.`
- `Copying this tree necessarily preserves a single lineage.`

## Interaction rules

- `Reveal hidden entries` may never be the only path to understanding capsule risk.
- destructive actions touching capsule rows must route through review.
- copying/exporting the subject must preview whether the capsule is copied, omitted, regenerated, or intentionally replaced.
- backup/export surfaces must say whether control substrate is included.

## Receipt obligations

Any receipt derived from this page must preserve:

- namespace composition verdict
- capsule owner / authority class
- sidecar roster with editability class
- strongest safe sentence
- blocked stronger sentence
