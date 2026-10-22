# D-RUMPK v0 selection posture (rump kernels, FS-only)

Purpose: resolve **OQ-0003 (D-RUMPK selection)** by pinning a small, implementable v0 choice for what runs *inside* a Foreign Cell when the optional compat lane is enabled.

This doc does **not** change the membrane contract (that is D-FCELL / `foreign-cell-contract.md`). It only constrains the *internal runtime* choice and its initial scope.

## Decision surface
Attaches to:
- **D-RUMPK** (compat runtime choice)
- **D-FCELL** (membrane; host integration rules)
- **OQ-0003** (runtime selection inside the cell)

## v0 posture (hard, narrow)
If the compat lane is enabled (D-FCELL + D-RUMPK):

1) **Default internal runtime: NetBSD rump kernels (rump servers).**
   - “Rump domain” == ordinary user-space component hosted behind the compat membrane.
   - Treat the runtime as **untrusted**; all host effects must remain portalized (I-COMPAT-1).
   - Refs: RFC-0036; REF-RUMPKERNEL-WIKI; REF-RUMPKERNEL-ABC2015.

2) **Scope is filesystem drivers only (FS image handling is the first-class case).**
   - The v0 compat runtime may mount/parse **untrusted filesystem images** via a translator/view path (D-TRANS/D-NS), but does not become a general “POSIX app” substrate.
   - No v0 expansion to general networking stacks, storage stacks, or “legacy app” ABI facades without a new RFC + explicit evidence plan.
   - Refs: RFC-0036; RFC-0083.

3) **Explicit non-goals for v0 (keep sealed compat honest):**
   - **No LKL** as a drop-in “donor kernel” in v0.
   - **No gVisor-style userspace kernel** as the compat runtime in v0.
   - **No Drawbridge/picoprocess-style POSIX facade** in v0.

These may be reconsidered only via an explicit RFC that (a) preserves I-COMPAT-1/I-COMPAT-2, (b) is killable by policy, and (c) carries an evidence plan that measures syscall/ABI surface closure + ambient-channel resistance.

## Evidence hooks (what makes the posture real)
- **AC-071 escape suite** must pass for any enabled compat capsule (`foreign-cell-escape-suite-v0.md`).
- **PO-COMPAT-CLOSESET / PO-COMPAT-NOAMBIENT** remain binding: unknown syscalls/ioctls deterministically fail; no ambient host channels.
- Phase-1 evidence for D-RUMPK stays *FS-first*:
  - time-to-first-mount and fuzzed image containment (RFC-0036)
  - cap-graph export confirms no unintended authority edges were introduced

## Phase-1 scope decision (hard)

**Phase 1 forbids introducing a second compat runtime family.**

- v0 remains **rump-only** (`runtime.kind == rump`) and **FS-image handling only**.
- Any proposal to add a second runtime family (LKL/userspace-kernel/libOS/POSIX facade) is **out of scope for Phase 1** and MUST be treated as a *new* decision via RFC + evidence.

Rationale (keep the expensive choice contained):
- A second runtime family expands ABI/hostcall risk surfaces and reopens “donor stack” drift.
- Phase 1 already has a concrete, testable compat goal (mount/parse untrusted images) that exercises I-COMPAT-1/I-COMPAT-2 without importing a general POSIX substrate.

## Revisit trigger (Phase 2+ only)

Revisit D-RUMPK runtime diversity only if *all* of the following become true:
- A concrete, recurring Phase-1 product need cannot be met by **rump FS capsules** (not a vague “POSIX would be nice”).
- The proposal names the runtime family and its ABI/hostcall surface as a **closed set** (I-COMPAT-2), and preserves portal-only effects (I-COMPAT-1).
- The proposal adds **new negative tests beyond AC-071** that are specific to the new family’s escape vectors (syscall surface, name resolution, ambient FD/namespace exposure, etc.).

## Notes
- This posture is compatible with all four product profiles:
  - **(A) workstation**: compat can exist for opening/mounting untrusted images without inflating the privileged core.
  - **(B) cloud substrate**: remains optional; useful for niche tooling; must stay lane-killable.
  - **(C) embedded/separation**: likely disabled by default.
  - **(D) agent/automation**: compat is not an automation bypass; all effects remain portalized + receipted.

## References (link out; do not paste)
- RFC-0036, RFC-0083
- REF-RUMPKERNEL-WIKI, REF-RUMPKERNEL-ABC2015
- Comparison-only (non-v0): REF-LKL-GITHUB, REF-GVISOR-GITHUB, REF-DRAWBRIDGE-ASPL11
