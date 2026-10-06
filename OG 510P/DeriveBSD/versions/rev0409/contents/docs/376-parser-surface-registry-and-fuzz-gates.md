# Parser surface registry + fuzz gates (treat “new parsers” as first-class attack-surface diffs)

In OS ecosystems, the most expensive security failures often come from *parsers*:
- file format decoders (images, archives, documents)
- protocol decoders (network stacks, RPC codecs)
- kernel-adjacent parsers (ioctls, filesystem metadata, device protocols)

DeriveBSD already treats **authority drift** as reviewable artifacts (`authority.diff`, blast-radius diffs).
Greenfield advantage: also treat **parser drift** as a first-class, machine-checkable diff.

## The core idea

Define a canonical, derived artifact lane:

- `parser.registry` (compiled): the authoritative list of parsers present in a system generation
- `parser.diff` (derived): added/removed/changed parsers between generations

Then require policy gates for:
- **new parsers** (especially new “untrusted bytes → structured objects” code)
- **parser broadening** (new features/fields that expand accepted inputs)
- **parser relocation** (kernel → userspace, or userspace → privileged)

This plugs into:
- `docs/106-blast-radius-diff.md` (add `parsers` as a blast-radius section)
- `docs/366-capability-graphs-and-authority-diff-surfaces.md` (parsers appear as risk-bearing nodes/edges)
- `docs/274-continuous-fuzzing-farm.md` (fuzzing targets should map 1:1 to parser ids)

## Prior art worth stealing

- Chromium’s IPC review discipline is *implicitly* a “new parser gate”: new Mojo IPC methods add new structured inputs crossing trust boundaries.
  - Mojo security notes: https://chromium.googlesource.com/chromium/src/+/main/docs/security/mojo.md
  - IPC reviews guide: https://chromium.googlesource.com/chromium/src/+/HEAD/docs/security/ipc-reviews.md
- ChromeOS security reviews explicitly require fuzzing for “non-trivial untrusted data” paths.
  - https://www.chromium.org/chromium-os/developer-library/guides/security/security-review-howto/
- Project Zero repeatedly demonstrates how rich parsers (especially image/media) become high-value attack surface.
  - Example: https://projectzero.google/2020/04/fuzzing-imageio.html
- Microsoft SDL guidance treats “code that parses untrusted data” as high priority for review/hardening.
  - (eBook): https://download.microsoft.com/download/8/1/6/816C597A-5592-4867-A0A6-A0181703CD59/Microsoft_Press_eBook_TheSecurityDevelopmentLifecycle_PDF.pdf
- Optional high-assurance lane: formally verified parsers (EverParse) for critical binary protocols.
  - https://www.microsoft.com/en-us/research/blog/everparse-hardening-critical-attack-surfaces-with-formally-proven-message-parsers/

## What counts as a “parser” (scope)

A parser is any code that:
- accepts **untrusted bytes** (file/network/device/kernel boundary)
- produces structured objects used to drive control flow

Treat these as parsers by default:
- archive extractors, package metadata readers, SBOM/VEX readers
- image/audio/video decoders used in system tooling
- protocol codecs in brokers (DNS, TLS termination, auth token codecs)
- kernel UAPI endpoints where userspace controls structured inputs (ioctls, netlink-like APIs)
- device protocol handlers (drivers) — they parse hostile peripherals

Non-goal: perfectly enumerate *every* parser.
Goal: make it mechanically hard to add *new, meaningful parser surface* without review.

## The registry object

A `parser.registry` is a compiled, stable-ordered list of parsers. Each entry should capture:

- stable id: `parser.<class>.<name>`
- input class: `untrusted.file | untrusted.network | untrusted.device | untrusted.kernel`
- privilege class: `unprivileged | service | broker | kernel | firmware`
- location: component/service id (and optionally source path)
- contract/UAPI linkage: contract id(s) and/or UAPI surface id(s)
- fuzz harness linkage: harness id/digest and where to run it

This is deliberately boring: its job is to make diffs reviewable.

See schema + example:
- `spec/parser.registry.schema.json`
- `spec/examples/parser.registry.json`

## The diff object

A `parser.diff` is derived between two registries:
- added parsers (new surface)
- removed parsers (surface shrank)
- changed parsers (input class, privilege, codec version, or contract/UAPI linkage changed)

The diff also supports classification tags so gates can be simple:
- `new-parser`
- `parser-broadening`
- `privilege-increase`
- `kernel-parser`

See schema + example:
- `spec/parser.diff.schema.json`
- `spec/examples/parser.diff.json`

## Fuzz gates (make “new parser” expensive to ignore)

When a parser is **added** or **broadened**, require at least one of:

1) A fuzz harness + minimum-run evidence (receipt)
   - Hook to `docs/274-continuous-fuzzing-farm.md`

2) A conformance test suite (structured corpus)
   - Ideally derived from real-world samples under policy

3) A high-assurance lane claim
   - e.g., a proof artifact attached (see `docs/373-proof-artifacts-and-formal-verification-lanes.md`)

Policy can be simple:
- “no `parser.diff` entries with `new-parser` unless fuzz receipt exists”
- “any kernel parser addition requires security review + fuzz harness”

## Where this plugs into meta-engineering

Update the feature intake rubric:
- “If you introduce a parser, show the `parser.registry` entry and its fuzz/conformance plan.”

Update blast-radius diffs:
- include `parsers` as a dedicated section so reviewers can see “new decode surface” at a glance.

## Related

- Fuzzing as evidence: `docs/274-continuous-fuzzing-farm.md`
- Contract registries + diff gates: `docs/370-contract-registries-and-api-diff-gates.md`
- UAPI registries + diff gates: `docs/362-uapi-surface-registry-and-compat-gates.md`
- Driver tiering (drivers are parsers): `docs/363-driver-safety-tiering-rust-and-user-mode.md`
- Authority diffs: `docs/374-authority-diff-schema-and-review-workflows.md`
