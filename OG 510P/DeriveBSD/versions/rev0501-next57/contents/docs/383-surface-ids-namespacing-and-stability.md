# Surface ids: namespacing, stability, and reviewer-facing keys

DeriveBSD relies on registry/diff artifacts (`contract.diff`, `uapi.diff`, `parser.diff`, `authority.diff`, …).
These artifacts only work if identifiers are:
- stable across time
- unambiguous
- easy to grep

This note defines **id conventions** for any “surface registry” class.

## Principles

1) **Ids are reviewer-facing**
They appear in diffs, policies, receipts, and bug reports.
Treat them like API names.

2) **Ids are namespaced**
Use a top-level prefix that matches the surface class.

3) **Ids are stable**
Changing an id is effectively a breaking change to review workflows.
If you need a new id, add it and deprecate the old one.

4) **Ids are not digests**
Digests are for bytes.
Ids are for concepts.

## Recommended shapes

### Contracts
- `contract.<domain>.<surface>`
  - e.g. `contract.portal.sanitize.open`, `contract.rpc.net.egress`

### Kernel UAPI
- `uapi.<kind>.<name>`
  - e.g. `uapi.syscall.openat`, `uapi.ioctl.hid`, `uapi.sysctl.net.inet.ip.forwarding`

### Parsers
- `parser.<class>.<name>`
  - e.g. `parser.file.zip`, `parser.protocol.dns`, `parser.uapi.ioctl.usb_hid`

### Trust boundaries
- `tb.<kind>.<from>__<to>.<name>`
  - e.g. `tb.untrusted-input.appvm__portal.sanitize.file-import`
  - delimiter `__` avoids ambiguity when node ids contain dots

### Authority edges (review keys)
- `edge.<from>__<to>.<cap_kind>`
  - edge keys should be stable even if rights/scope change

## Character set

- Use `[a-z0-9._-]` plus `__` as the “node separator” when needed.
- Avoid spaces, uppercase, and `/`.

## Stability notes

- Node ids (components) should also be stable.
  Prefer `svc.<name>` / `vm.<name>` / `jail.<name>`.
- When renaming, keep an alias mapping so old receipts can still be explained.

## Related

- Surface registry meta-pattern: `docs/379-surface-registry-pattern.md`
- Contract registries: `docs/370-contract-registries-and-api-diff-gates.md`
- UAPI registries: `docs/362-uapi-surface-registry-and-compat-gates.md`
- Parser registries: `docs/376-parser-surface-registry-and-fuzz-gates.md`
- Authority diffs: `docs/374-authority-diff-schema-and-review-workflows.md`

