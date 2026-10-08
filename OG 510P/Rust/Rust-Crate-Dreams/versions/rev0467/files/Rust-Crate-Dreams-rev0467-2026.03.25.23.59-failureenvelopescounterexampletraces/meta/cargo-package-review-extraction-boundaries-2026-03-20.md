# Cargo package-review extraction / authority boundaries — 2026-03-20

This note exists to keep future passes from collapsing several package-adjacent surfaces into one fake “reviewed tarball” story.

## The lane sharpened in this pass

**P-0470 Cargo Package Review Kit** now owns the layer above `cargo package` where one team needs to know:

> which surface was actually reviewed, which packaged paths were copied or generated, and which mutations happened only after unpacking for verification?

That means this lane may legitimately own:

- packaged-surface receipts,
- archive-authority reports,
- extraction-mutation reports,
- `Cargo.toml.orig` versus generated `Cargo.toml` lineage,
- `.cargo-ok` / mtime / verification-tree mutation review,
- and conservative hash/signoff posture tied to a specific package surface.

## Adjacent lanes that must stay separate

### 1. Post-publish receipt joins

**P-0477 Cargo Publish Receipt Join Kit** answers:

> what happened after publication, what registry/index facts are authoritative, and which public surfaces converged?

That is about **release confirmation after upload**, not pre-publish package-surface authority.

### 2. Source parity / vendoring

**P-0496 Cargo Vendor & Source Parity Kit** answers:

> how do downloaded, mirrored, or vendored sources relate to registry/source identity?

That is about **source replacement and offline parity**, not package-review truth inside one `.crate` / extraction cycle.

### 3. Provenance / attestation / signature lanes

Those lanes answer:

> who made this artifact, can that claim be verified, and how should downstream users trust it?

That is not the same as saying which bytes Cargo generated, copied, or mutated during packaging and verification.

### 4. Generic file-list or policy-warning tools

Those lanes answer:

> what files are present or what heuristics fired?

This lane is stricter: it must also say **which surface is authoritative** and **which mutations are verification-only**.

## Boundary reminders for future revisions

1. Do **not** let `cargo package --list` become shorthand for full review truth. A path list is not an authority decision.
2. Do **not** let extracted verification trees borrow the authority of raw `.crate` bytes without an explicit mutation report.
3. Do **not** let `Cargo.toml.orig` plus generated `Cargo.toml` collapse into one “manifest reviewed” claim.
4. Do **not** let `.cargo_vcs_info.json` or dirty-worktree facts pretend to identify authoritative package bytes.
5. Do **not** let post-unpack `.cargo-ok` or mtime changes masquerade as proof that the uploaded archive itself changed.
