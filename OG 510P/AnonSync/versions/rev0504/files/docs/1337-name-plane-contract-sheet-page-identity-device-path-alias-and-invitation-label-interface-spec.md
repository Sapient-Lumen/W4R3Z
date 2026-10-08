## Name-plane contract sheet

### Purpose
Make the product say **which naming plane is being changed or read** before it says `rename`, `label`, `identity`, `share name`, `device name`, or `folder name`.

### The contract object
Each serious naming sentence renders these fields together:

- **Plane family**: identity handle, device handle, filesystem subject name, local UI alias, invitation label, derived default folder name, or unknown.
- **Authority consequence**: presentation only, peer-recognition relevant, certificate lineage affecting, or unknown.
- **Propagation scope**: local current surface only, local runtime only, delivered through a generated invite only, remote peers directly, linked-family wide, or unknown.
- **Persistence class**: survives disconnect locally, survives restart, survives relink, survives filesystem move, or unknown.
- **Reset path**: reset to disk name, unlink and regenerate, edit in place, regenerate invite, or unknown.
- **Visible companions**: fingerprint, path, peer row, backup role, or none.
- **Blocked stronger sentence**: the next stronger naming claim the product refuses to make.

### Default language rules
- `renamed in UI` is intentionally weaker than `renamed on disk`.
- `renamed on disk` is intentionally weaker than `renamed on every peer`.
- `changed device label` is intentionally weaker than `changed identity / certificate lineage`.
- `new invite label generated` is intentionally weaker than `share alias changed`.
- `same displayed name` is intentionally weaker than `same authority unit`.

### Required persistent receipts
Any serious naming, relabeling, sharing, unlink, or backup-default event stores one durable receipt preserving plane family, authority consequence, propagation scope, persistence class, reset path, and the blocked stronger sentence.
