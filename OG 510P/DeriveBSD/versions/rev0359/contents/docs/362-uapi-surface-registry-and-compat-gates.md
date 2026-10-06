# UAPI surface registry + compatibility gates (treat syscalls/ioctls as contracts)

DeriveBSD treats **every crossing** as a contract surface: IPC methods, broker APIs, file-shaped control planes…
and also the **kernel UAPI**: system calls, ioctls, sysctl nodes, device nodes, and pseudo-filesystems.

The greenfield win is to make UAPI drift **mechanically hard**:
- *every* stable surface is registered
- *every* change is diffed + classified
- *every* surface has a conformance/fuzz harness story
- policy gates can reason about “new authority / new attack surface” *before* merge

## Non-goals

- Pretending we can freeze *all* UAPI forever. We can’t.
- Replacing the existing contract machinery (digests, receipts, blast-radius diffs). This extends it.

## Prior art worth stealing

- Kernel ABI = **syscalls + ioctls + vDSO** (and similar surfaces). (LWN)  
  https://lwn.net/Articles/726021/
- Linux’s explicit **ABI stability levels** + the `/Documentation/ABI/` habit.  
  https://docs.kernel.org/admin-guide/abi-stable.html  
  https://www.kernel.org/doc/html/next/admin-guide/abi-testing.html  
  https://github.com/torvalds/linux/blob/master/Documentation/ABI/README
- “Detect userspace breakage” automation for UAPI drift (UAPI compatibility checking).  
  https://www.qualcomm.com/developer/blog/2024/01/uapi-compatibility-checker-automated-tooling-detect-userspace-breakage-linux-kernel
- Capsicum: file-descriptor authority is a great base, but ioctls/sysctls are where ambient authority sneaks back in.  
  https://www.usenix.org/event/sec10/tech/full_papers/Watson.pdf

## The registry (a first-class derived artifact)

Define a canonical object:

- `uapi.surface` (source): human-maintained declarations
- `uapi.registry` (compiled): normalized, stable ordering + digests
- `uapi.diff` (derived): “what changed and why it matters”

Suggested shape:

```json
{
  "id": "uapi.syscall.openat",
  "class": "syscall|ioctl|sysctl|devnode|pseudofs|vdso",
  "stability": "stable|provisional|deprecated|internal",
  "owner": "kernel/vfs",
  "since": "2026-02-27r102",
  "contract_digest": "sha256:…",
  "authority_notes": [
    "may create new names in namespace",
    "consumes directory capability",
    "may consult global resolver unless capsicum-mode"
  ],
  "tests": {
    "conformance": "tests/uapi/openat/*",
    "fuzz": "fuzz/uapi/openat_harness"
  }
}
```

### What gets registered

At minimum:

- every syscall (including `*at` variants and “escape hatches”)
- every ioctl family (with a stable name + command set)
- sysctl nodes that matter (especially those that gate security posture)
- device nodes that represent authority (raw disks, network devices, sensors, TPM, etc.)
- pseudo-filesystems and any “magic file” control planes

## Compatibility gates (make breakage loud)

Add a required CI gate:

- compute `uapi.diff` between `main` and PR
- classify each change:
  - **compatible** (additive, new optional fields, new ioctl cmd in an *explicitly extensible* family)
  - **breaking** (signature/semantics change, removal, narrowing rights, structure layout changes for stable UAPI)
  - **suspicious** (new ambient authority, new global namespace access, new kernel-to-user parsing)
- require explicit approvals for:
  - breaking changes
  - “new authority” changes
  - “new parser” changes (prefer linking to `parser.registry` / `parser.diff`; see `docs/376-parser-surface-registry-and-fuzz-gates.md`)

Tie this into:
- `docs/348-design-review-rubric-and-feature-intake.md`
- `docs/106-blast-radius-diff.md`
- `docs/237-lint-reports-and-contract-testing.md`

## “UAPI is authority”: the policy posture

Use the registry to enforce two rules:

1) **No unregistered stable UAPI**  
   If users can depend on it, it is registered.

2) **No silent authority growth**  
   Any change that increases authority must:
   - show up in `uapi.diff`
   - update authority notes
   - include a test + fuzz harness plan

## Open questions

- How do we represent “semantic changes” that don’t change structs?
- Do we want an explicit “extensible ioctl family” pattern (versioned structs, size fields, feature flags)?
- What’s the minimal “good enough” UAPI fuzz harness story for each class?

## Related docs

- `docs/361-safe-crossing-apis-and-boundary-bugs-lessons-from-tock.md`
- `docs/49-capsicum-casper-hardening.md`
- `docs/318-kernel-tunables-and-sysctls-as-evidence.md`
- `docs/276-kernel-module-policy-and-loading-as-evidence.md`
- `docs/406-uapi-fuzz-descriptors-and-conformance.md`

## Wiring (schemas + examples)

- `uapi.registry` schema: `spec/uapi.registry.schema.json` (example: `spec/examples/uapi.registry.json`)
- `uapi.diff` schema: `spec/uapi.diff.schema.json` (example: `spec/examples/uapi.diff.json`)
