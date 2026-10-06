# UAPI fuzz descriptors and conformance (syzkaller-shaped, registry-aligned)

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability
**Patterns:** Registry→Diff→Gate  

`docs/362-uapi-surface-registry-and-compat-gates.md` establishes the posture:
UAPI is a **contract** and an **authority surface**. Every stable surface is registered, diffed,
classified, and gated.

To make that real, DeriveBSD needs a crisp “fuzz and conformance story” that is:
- registry-aligned (targets keyed by `uapi.*` ids)
- reproducible (harness identity is digest-pinned)
- operable (fits the fuzz farm + promotion gates)

syzkaller is the best prior art for kernel UAPI fuzzing because it couples:
- a declarative interface description language
- VM orchestration
- corpus/crash management

The greenfield win is to *bake the description linkage into the registry itself*.

## Goals

- Every stable UAPI surface can point at:
  - a conformance suite (structured “expected behavior” tests)
  - a fuzz descriptor/harness (untrusted structured inputs at scale)
- UAPI drift that changes shape must update these pointers (or gate fails).
- Harnesses and descriptors are content-addressed artifacts.

## A derived artifact lane: `uapi.fuzz.desc`

Introduce a conceptual object (name can vary):

- `uapi.fuzz.desc` (source/compiled)
  - describes how to generate calls/inputs for a UAPI surface class
  - binds to `uapi.registry` entries by stable ids

Recommended fields (sketch):

```json
{
  "kind": "uapi-fuzz-desc",
  "manifest_version": "0.1",
  "targets": [
    {
      "uapi_id": "uapi.syscall.openat",
      "desc_digest": "sha256:...",
      "harness_digest": "sha256:...",
      "notes": ["directory-fd capability required", "path parsing"]
    }
  ]
}
```

This plugs directly into:
- `docs/274-continuous-fuzzing-farm.md` (harness_digest becomes the `fuzz.receipt.harness_digest`)
- `docs/376-parser-surface-registry-and-fuzz-gates.md` (UAPI endpoints that parse structured inputs are parsers)

## Practical approach (v0)

Start with a *minimal* but shippable lane:

1) **Manual descriptors for the highest-value surfaces**
   - syscalls/ioctls that parse complex structs
   - device ioctls for drivers that routinely break
   - filesystem/packet interfaces that parse untrusted bytes

2) **Link each descriptor to registry ids**
   - no “free-floating” fuzz harnesses

3) **Require a fuzz plan for new registered stable UAPI**
   - if a surface is declared stable and parses inputs, it must point at a harness

This keeps the scope bounded while still forcing the habit.

## Optional acceleration: derive descriptors from headers (later)

Long term, the OS should reduce hand work:
- parse kernel headers and ioctl definitions
- generate skeleton descriptors
- require human review for semantics and constraints

Even syzkaller notes that syscall interface descriptions are largely manual today,
with partial generation assistance.

## Conformance vs fuzz (don’t confuse them)

- **Conformance**: “this contract behaves as documented” (small, deterministic)
- **Fuzzing**: “this parser boundary is robust under hostile inputs” (large, probabilistic)

A registry entry should carry both when appropriate.

## Policy gates

Gates can be simple and mechanical:

- Any `uapi.diff` entry classified as:
  - `new-surface`, `parser-broadening`, or `new-authority`

…must include at least one of:
- a conformance suite update
- a fuzz descriptor/harness update
- a high-assurance lane claim (proof artifact)

See: `docs/362-uapi-surface-registry-and-compat-gates.md`, `docs/348-design-review-rubric-and-feature-intake.md`.

## References

- syzkaller syscall descriptions (syzlang): https://github.com/google/syzkaller/blob/master/docs/syscall_descriptions.md
- syzkaller internals: https://github.com/google/syzkaller/blob/master/docs/internals.md
- SyzDescribe paper (automating syscall description generation): https://www.shitong.me/pdfs/oakland23_syzdescribe.pdf

Last updated: 2026-02-27r118
