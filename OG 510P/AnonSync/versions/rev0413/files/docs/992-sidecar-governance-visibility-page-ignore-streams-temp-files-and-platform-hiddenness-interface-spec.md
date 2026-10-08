# Sidecar governance visibility page — ignore rules, streams policy, temporary transfer files, and platform hiddenness

## Purpose

Give one inspectable place for policy-bearing and residue-bearing sidecars that would otherwise be dismissed as `just hidden files`.

## Page families covered

This page must distinguish at minimum:

- **Ignore rules**
- **Metadata whitelist / stream policy**
- **Transfer-temporary artifacts**
- **Metadata stub residue**

## Required table

Columns:

- family
- example on-disk representation
- authority class
- intended editor
- activation class
- retroactivity class
- visibility default
- danger if bulk-cleaned

### Example row guidance

#### Ignore rules

Must say:

- operator-editable policy sidecar
- affects indexing and future publication scope
- not fully retroactive to already-shared structure
- case/path semantics matter

#### Streams / metadata whitelist

Must say:

- operator-editable advanced policy sidecar
- governs which xattrs/streams propagate
- can create cross-platform surprises
- removal changes future metadata posture

#### Temporary transfer files

Must say:

- transient transfer residue
- not stable user file naming
- safe interpretation depends on transfer state

#### Metadata stub residue

Must say:

- compatibility bridge residue
- may represent metadata that cannot be stored natively on this substrate
- deleting it can weaken onward propagation guarantees

## Interaction rules

- bulk cleanup tools must preview which hidden entries are policy vs residue vs capsule-critical.
- `show hidden files` is presentation only; it must not change authority class.
- any edit to policy sidecars must link to activation timing and retroactivity notes.

## Strongest safe sentences

Examples:

- `These hidden entries are editable policy, not cache.`
- `These hidden entries are temporary transfer artifacts and not final files.`
- `These hidden entries bridge metadata across incompatible peers.`

## Blocked stronger sentences

Examples:

- `All dotfiles here are expendable.`
- `Changing this sidecar only affects the local view.`
- `This temp-looking file is always safe to delete.`
