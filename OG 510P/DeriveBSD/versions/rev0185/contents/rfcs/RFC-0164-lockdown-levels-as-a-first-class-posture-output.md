# RFC-0164: Lockdown levels as a first-class posture output (securelevel integration)

Status: Draft  
Last updated: 2026-02-25

## Problem

DeriveBSD has a strong story for:
- derived artifacts (spec/lock/plan → outputs)
- atomic activation + rollback
- platform posture evidence (`docs/226-platform-posture-and-attestation-results-as-evidence.md`)

But we lack a *simple, enforceable* “steady-state lockdown” primitive that:
- reduces what even `root` can do post-boot
- is monotonic (hard to silently undo)
- is governed and receipted (not “someone ran sysctl”)

BSD securelevel provides a useful kernel mechanism (and a cautionary tale): it is powerful, but historically gets applied ad-hoc and breaks workflows if you don’t design for it.

## Goals

- Make “lockdown level” a **policy output** with explicit prerequisites.
- Integrate lockdown changes into the evidence spine:
  - emit a `platform.lockdown.receipt`
  - log `platform.lockdown.event` milestones (optional, via the structured journal)
- Ensure DeriveBSD’s apply/activation pipeline can always reach the intended lockdown level without surprises.
- Keep escape hatches explicit (specialisations / maintenance windows), not accidental.

## Non-goals

- Replacing all MAC frameworks with securelevel.
- Providing a universal cross-OS lockdown API.
- “Perfect” post-compromise security (this is a defense-in-depth rail, not a silver bullet).

## Proposal

### 1) Extend platform posture profile with lockdown intent

Extend the posture profile (or add a sibling policy object) with:

- `lockdown.target_level`: enum
  - `bootstrap` (default during activation)
  - `operational` (normal steady state)
  - `high` (draconian / last line)

- `lockdown.prerequisites`: list of checks that must be satisfied before raising
  - required kernel modules loaded
  - firewall/routing posture applied
  - optional: attestation receipt present
  - optional: time sync within bounds
  - optional: storage health ok
  - optional: “no blocking faults” snapshot

- `lockdown.actions`: mapping from target levels to concrete actions
  - `kern.securelevel := N`
  - disable DDB consoles (where available)
  - enforce immutable flags on specified paths
  - lock certain sysctls behind capabilities (DeriveBSD-specific)

### 2) New evidence object: `platform.lockdown.receipt`

Add `spec/platform.lockdown.receipt.schema.json`:

- `requested_level`, `effective_level`
- `policy_digest` (posture profile / lockdown policy digest)
- `at` (timestamp; include `observed_at` in journal exports)
- `preconditions` + their evidence digests (attestation/time/storage/fault/etc.)
- `actions_applied` (normalized list)
- optional: `signature` (if we require signed receipts)

### 3) Activation lifecycle

- Activation (and initial boot) runs at `bootstrap`.
- After health gates succeed:
  - raise lockdown to the target level
  - emit a receipt and journal event
- If the system cannot reach the intended lockdown level, treat it as a gate failure and roll back (policy-dependent).

### 4) Escape hatches are explicit

- A “maintenance” specialisation may target `bootstrap` or a reduced lockdown level, but:
  - must be configured by policy
  - must emit receipts (and ideally require console presence + explicit operator confirmation)

## Tradeoffs / risks

- Lockdown is inherently disruptive if you load modules late or mutate the host at runtime.
  DeriveBSD must keep mutation and late-binding as explicit, planned steps.
- Some restrictions differ across BSDs (FreeBSD vs OpenBSD).
  Our policy should describe **intent** and map to the platform-specific knobs.

## Alternatives considered

- “Just use MAC” (strong, but doesn’t provide monotonic global lockdown by itself; still valuable).
- “Only do measured boot + remote attestation” (orthogonal; posture ≠ lockdown).
- “No lockdown; rely on least privilege everywhere” (idealistic; still benefits from a last-line rail).

## References

- FreeBSD Handbook: Secure Levels (definitions + semantics): https://docs.freebsd.org/en/books/handbook/security/
- OpenBSD `securelevel(7)`: https://man.openbsd.org/securelevel

## Related work in this archive

- `docs/230-lockdown-levels-and-securelevel.md`
- `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- `docs/219-change-sets-and-apply-engine.md`
- `docs/174-specialisations-and-variants.md`
