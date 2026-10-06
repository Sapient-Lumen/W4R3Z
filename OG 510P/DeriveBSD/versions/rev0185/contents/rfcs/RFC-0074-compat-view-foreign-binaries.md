# RFC-0074: Compat view for foreign / normally-linked binaries

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary

Provide a policy-governed “compat view” so users can run prebuilt binaries without making the host mutable or breaking explainability.

## Motivation

Running foreign binaries is persistently painful in content-addressed ecosystems because binaries assume conventional loader and library paths.

On FreeBSD, the dynamic linker supports:
- dependency mapping (libmap.conf / LD_LIBMAP)
- a hints file produced by ldconfig

These can be used to construct an explainable compatibility environment.

## Goals / Non-goals

Goals:
- compat view is opt-in and policy-controlled
- compat view is derived from a closure (no ambient host libs)
- compat mapping is recorded as an evidence object

Non-goals:
- “run arbitrary blobs without constraints”

## Proposal

### Compat view types

1) **Compat jail** (default):
- create an ephemeral root (or ZFS clone)
- provide a minimal `/lib` and `/usr/lib` view that is symlinks into the store
- install a generated `/etc/libmap.conf` for mapping (when needed)
- generate a hints file with `ldconfig` inside the jail

2) **Compat microVM** (optional): same as above, but stronger boundary.

### Evidence object: compat mapping record

A structured object containing:
- binary id (digest)
- selected library digests
- any mapping rules (libmap lines)
- hints file digest
- policy decision digest

This object is emitted by `derive compat explain --json` and included in `derive explain` of workloads that use compat mode.

### CLI sketch

- `derive compat run <binary> --with <closure>`
- `derive compat explain <binary> --json`

## Alternatives considered

- require static linking for everything (unrealistic)
- patch/relocate binaries (sometimes possible but often painful)

## Backwards compatibility

Additive.

## Security considerations

- forbid falling back to host libraries by default
- record and diff compat mappings (blast-radius diffs)
- require signatures/policy for any compat closure served via cache

## Open questions

- best mechanism for building the minimal compat root (symlink farm vs unionfs overlay)
- ABI selection rules when multiple `libX.so` providers exist
