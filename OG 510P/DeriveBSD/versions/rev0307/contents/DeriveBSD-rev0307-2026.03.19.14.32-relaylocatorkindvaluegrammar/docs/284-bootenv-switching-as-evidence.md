# Boot environment switching as evidence (ZFS BE + try-counters + health gates)

DeriveBSD already treats host deployments as **generation-like artifacts** realized from the Derive pipeline.
What tends to remain “folklore” in other ecosystems is the *moment of switching boots*:

- which generation is *next*?
- what is the automatic fallback?
- what does the bootloader consider a “successful boot”?
- what proof do we keep when we change any of the above?

This file makes **boot environment selection** an explicit, typed, receipted operation.

(see also: `docs/69-host-generations-bectl.md`, `docs/231-ab-updates-and-recovery-semantics.md`,
`docs/241-boot-try-counters-and-boot-assessment.md`, `docs/112-health-gated-updates.md`,
`docs/277-loader-verification-and-boot-config-constraints.md`)

## Lessons to steal

- FreeBSD’s ZFS boot environments (`bectl(8)`/`libbe(3)`) make OS updates naturally rollbackable, but
  the *policy* around switching and fallback can still become informal if not captured as data.
- Try-counters (systemd-boot/BLS-style) are a tiny primitive that prevents “soft bricks” by allowing
  automatic fallback after repeated failures.
- Health-gated updates make “booted” insufficient; we need “booted and assessed”.

## DeriveBSD stance

### 1) A boot switch is a Plan + Receipt, not an rc script

When we decide to boot a new deployment, we emit a **bootenv switch plan** and store it next to the
deployment metadata. Applying that plan emits a receipt.

- Plan: `spec/bootenv.switch.plan.schema.json`
- Receipt: `spec/bootenv.switch.receipt.schema.json`

This keeps boot selection inside the same explainability surface as everything else.

### 2) Explicit fallback and explicit assessment hooks

A switch plan always specifies:

- `target` deployment (what we want)
- `fallback` deployment (what we revert to automatically)
- a try-counter policy: max attempts and what counts as success

DeriveBSD already carries boot health reporting (`spec/boot.health.report.schema.json`).
A “successful boot” for try-counters should be tied to **boot assessment**:
a minimal service or agent that can mark the generation as “good” once the health gate passes.

### 3) Constrained mutable boot config (no policy bypass)

The switch plan is not allowed to smuggle in arbitrary loader overrides.
If overrides exist, they must fit inside the **boot config constraint surface**
described in `docs/277-loader-verification-and-boot-config-constraints.md` and `docs/482-boot-code-admission-and-constrained-overrides.md`, and produce evidence.

## Minimal data model (v0)

- **Boot environment identity**:
  - ZFS dataset / BE name (human-facing)
  - `deployment.ref` (content/evidence facing)
- **Switch intent**:
  - `target` and `fallback`
  - `max_tries` and `assessment_deadline`
- **Evidence pointers**:
  - references to the target deployment’s `closure.proof`/`attestation.receipt`
  - subsequent `boot.health.report` objects for that boot attempt

## Operational flow (one reasonable baseline)

1) Realize new host deployment artifact (store roots + closure proof).
2) Create ZFS BE for the target deployment (BE name may include short deployment id prefix).
3) Emit `bootenv-switch-plan` that:
   - sets boot-next to target
   - arms fallback
   - sets `max_tries` (bootloader-visible try-counter)
4) Apply plan:
   - update bootloader entry for target (subject to loader verification constraints)
   - write try-counter and fallback metadata
   - emit `bootenv-switch-receipt`
5) On boot:
   - bootloader decrements try-counter on failure
   - system emits `boot.health.report`
   - on success, the assessment agent marks the generation “good” (disarms fallback)

## Open edges worth deciding later

- Do we standardize a single “health gate contract” (service name + condition), or allow multiple gates?
- How do we expose try-counters across different bootloaders in a uniform way?
- What is the BE layout contract (single root dataset vs split datasets), and what is the minimal required set?

See also: `docs/266-open-questions-and-risk-register.md`.

