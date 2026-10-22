# Foreign Cell contract (sealed compatibility membrane)

This document pins the **compatibility membrane** for any legacy/POSIX runtime we may host.
The runtime *inside* the cell may vary (D-RUMPK), but the **host integration rules do not**.

Goal: enable bootstrap/interop **without accepting ambient authority** as a design constraint.

## Definitions

- **Foreign Cell**: an isolated domain hosting a legacy ABI surface (POSIX/Linux/BSD, library OS, rump/LKL, etc.).
- **Membrane**: the fail-closed contract that governs *all* interactions between a foreign cell and the host.
- **Portal**: a host-mediated capability interface that grants bounded effects with receipts/transcripts.

## Non-negotiable properties

1) **No ambient channels** (I-COMPAT-1; PO-COMPAT-NOAMBIENT)
   - No ambient host filesystem / global paths.
   - No ambient network stack access.
   - No ambient time/entropy sources.
   - No ambient device nodes.

2) **Interop is portalized and observable**
   - All host effects occur via explicit portal capabilities and are recorded via transcripts/receipts (including per-adapter CH-FADAPT receipts (v0 or v1) when adapters are used).

3) **Closed ABI surface** (I-COMPAT-2; PO-COMPAT-CLOSESET)
   - The emulated ABI is a closed set. Unknown syscalls/ioctls/protocol ops deterministically fail.

4) **Policy-killable**
   - The platform must be able to disable the entire foreign-cell lane by policy (boot-time and runtime), producing deterministic failures.
   - When the lane is disabled, IF-ACP SHOULD emit a CH-DENY record with `deny_code = lane-disabled` bound to the relevant `cfg.params.*` key, and bind it from CH-LOG via `deny_digest`.
   - Individual interop adapters must also be policy-killable (granular compat): each `adapter_kind` has a dedicated kill switch `cfg.params.lane.fcell.adapter.<adapter_kind>` (normalize `.` → `_`) that MUST be checked in addition to the bound `cfg.params.lane.portal.<family>` portal lane gate; missing/unknown toggles are treated as disabled (fail closed).

5) **Non-authoritative configuration**
   - Declarative configuration artifacts (e.g., CH-FCELL) do not grant authority; they can only reference already-issued handles and must validate fail-closed (I-FCELL-1).

## Membrane model (what the host may expose)

All host exposure to a foreign cell occurs through **explicit handles**, typically derived from portals:

- **Documents/FS**: only via document handles (e.g., CH-DOCREF) and view attachments. No raw host path traversal.
- **Network**: only via network leases (CH-NETLEASE) from the network portal. No ambient sockets.
- **Time/entropy**: only via Clock/Entropy handles (CH-CLOCK/CH-ENTROPY) if D-NONDET is enabled; otherwise deterministic absence.
  - Handles are normally issued by `portal.clock.*` / `portal.entropy.*` (or a host shim in micro-VM profiles); there are no ambient time/RNG syscalls for the cell.
  - v0: time/entropy remain **explicit resource handles** (`CH-FCELL.resources.clocks` / `resources.entropy`), not adapter-mediated portal workflows.
- **Devices**: only via explicit device leasing (CH-IOLEASE) and only if DMA posture (D-DMA) is satisfied.
- **Clipboard/transfer**: only via transfer/capture descriptors (CH-XFER/CH-CAPTURE), never raw bytes in the manifest.

The host may provide **adapters** that translate legacy expectations into portal calls (e.g., mapping `open()` to a document portal flow), but adapters must:

- use a closed, reviewable `adapter_kind` set (see `fcell-adapter-kind-registry.md`),

- be fail-closed on unsupported calls,
- be transcript-visible,
- emit a CH-FADAPT receipt (v0 or v1) for each portalized host effect (allow/deny), binding `portal_token` + issued descriptor digests (no bearer caps); v1 may additionally carry `reqctx_digest = digest(CH-REQCTX v1)` for correlation/veto-only policy,
- emit CH-DENY for non-effectful rejects (e.g., lane-disabled, unknown ABI op) when applicable, and bind it from CH-LOG via `deny_digest`,
- be policy-killable, and
- never silently widen authority.

## Bootstrapping posture

Foreign cells are allowed as a **bootstrap tool** (building toolchains, importing legacy formats) as long as:

- their authority is tightly bounded,
- outputs are promoted through explicit lanes (build artifacts, attestations, receipts), and
- the privileged core remains unchanged.

## Evidence targets (seed)

Minimum evidence for “sealed compat is real”:

- Negative tests: attempt ambient filesystem/network/time acquisition from inside a foreign cell must deterministically fail (AC-071).
- Capability diff: enabling a foreign cell cannot increase the host’s authority set; only explicit, receipt-visible grants may occur.
- Replay sanity: given the same CH-FCELL manifest and policy bundle, the launch outcome (allow/deny and receipts) is deterministic.

See also:

- Decision: D-FCELL (membrane contract) and D-RUMPK (runtime choice)
- Abuse case: AC-071 (compat capsule escape)
- REF-DRAWBRIDGE-POSIXPICO, REF-CLOUDABI, REF-RUMPKERNEL-ABC2015, REF-LKL-GITHUB
