# Namespace-role review page — hidden files, service artifacts, Streams sidecars, and temp residue

## Purpose

Review any odd pathname before the interface lets the operator treat it as ordinary user content.
This page exists because hidden dotfiles, `.sync` service state, xattr sidecars, and `.!sync` temporary residues do not share one lifecycle or one deletion contract.

## This review must distinguish

- ordinary hidden user file;
- hidden-but-critical `.sync` service state;
- `IgnoreList` / `StreamsList` policy artifacts inside service state;
- xattr stub or Streams-sidecar artifact created because a filesystem could not store metadata directly;
- partially transferred or currently transferring `.!sync` residue;
- invalid-name-blocked pathname that is not safe to treat as normal content.

## Inputs the page must collect

### Namespace facts

- exact pathname
- current parent directory
- whether the pathname lives under `.sync`
- whether the name is dot-prefixed or otherwise hidden by platform/UI convention
- whether the suffix or location signals temporary transfer state
- whether the name matches a known unsupported pattern

### Role facts

- whether the object is policy text, service identifier, archive state, stream stub, temp transfer file, or user file
- whether deletion would suspend syncing, merely remove local residue, or remove only a policy artifact
- whether the object is meant for operator editing, observation only, or no direct manipulation
- whether the object is recoverable or auto-regenerated if removed

### Safety facts

- whether sync is actively using the object now
- whether the object represents incomplete download state
- whether the object is the only remaining record of a metadata lane
- whether removal would require folder re-add or other repair workflow

## Decision ladder

### Branch 1 — ordinary hidden user subject

Use this branch when the pathname is hidden only by naming/UI policy.
The page should show:

- that the file is still ordinary user content
- whether UI invisibility is the only reason it was missed
- that delete safety follows ordinary user-content rules, not service rules

### Branch 2 — service-critical artifact

Use this branch for `.sync` and other service-owned state whose removal breaks identity or tracking.
The page should show:

- why the object is service-owned
- what breaks if it is damaged or removed
- whether repair would require re-adding the share or rebuilding state

### Branch 3 — metadata-sidecar artifact

Use this branch for `StreamsList`-governed xattr fallback artifacts.
The page should show:

- that metadata is traveling in a separate lane
- why `IgnoreList` does not govern this object
- whether the underlying filesystem limitation is the cause
- what ordinary delete or ignore assumptions are blocked

### Branch 4 — temp transfer residue

Use this branch for `.!sync` objects.
The page should show:

- whether transfer is still live or merely stuck residue
- whether restart/retry is expected before deletion
- that this artifact is not the healthy completed file yet

### Branch 5 — invalid-name-blocked subject

Use this branch when the pathname itself is unsupported.
The page should show:

- exact unsupported-name basis
- whether sync treated the subject as system-like or invalid
- that the failure is namespace validity, not ordinary transport failure
- safe remediation path before re-admission

## Required warnings

- `Hidden` is weaker than `out of scope`.
- `.sync` is weaker than `ordinary folder`; it is service-critical state.
- `Odd file under .sync` is weaker than `safe to delete`.
- `Streams sidecar` is weaker than `ignored metadata`; it may be the only portable copy.
- `.!sync` is weaker than `downloaded file`.
- `Bad name` is weaker than `temporary sync hiccup`.

## Review outputs

- namespace-role class
- manipulation-safety class
- lane owner (`user`, `service`, `metadata`, `transfer-temp`, `invalid-name-review`)
- repair cost if removed or altered
- strongest safe handling sentence

