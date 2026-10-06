# RFC-0166: Service promise profiles (pledge/unveil ergonomics)

- Status: draft
- Author(s):
- Created: 2026-02-25
- Last updated: 2026-02-25

## Summary

Introduce **promise profiles**: small, versioned artifacts that express *least-authority intent* for build sandboxes and runtime services, compiling to FreeBSD primitives (jails + Capsicum/Casper + portals + optional MAC).

## Motivation

We want pledge/unveil’s operational superpower: *widespread adoption through low friction*. In practice:
- engineers need a concise, reviewable declaration
- the platform needs to compile it into enforcement without bespoke per-service glue
- diff/review needs to treat authority edits as first-class changes

## Goals

- A single profile artifact that can be referenced from `svcdb` entries and sandbox plans
- Profiles are diff-friendly and monotonic (tighten is easy; loosen is policy-gated)
- Compiler/linter support: detect obvious mismatches (declared network use without egress grants, portal use without allowance, etc.)

## Non-goals

- Reproducing pledge/unveil syscall semantics exactly
- A universal seccomp-like system call filter DSL

## Proposal

### 1) Add a new artifact type: `sandbox-profile`

A profile is represented as canonical JSON and stored in the Derive store.

Schema: `spec/sandbox.profile.schema.json`
Example: `spec/examples/sandbox.profile.json`

### 2) Extend svcdb to reference promise profiles

In `spec/svcdb.schema.json`, extend `services[].security` with:

- `promise_profile_digest` (optional): digest of a `sandbox-profile` artifact.

### 3) Compilation targets

A profile may compile into:
- jail mount plan + devfs ruleset (filesystem visibility)
- capsicum rights plans (fd rights tightening)
- portal allowlists (what can be brokered)
- optional MAC toggles

### 4) Linting

The svcdb compiler SHOULD:
- require explicit opt-in for network use (prefer net egress grants)
- require explicit portal surface declarations
- warn on “broad” profiles (e.g., excessive fs patterns)

## Alternatives

- Hand-authored per-service jail configs (hard to review and scale)
- Add a syscall-filter DSL (high complexity, low adoption)

## Backwards compatibility

- New fields are optional.

## Security considerations

- Profiles become high-value policy surfaces; require signatures and decision records for relaxing profiles.
- “Lock” semantics should be monotonic where possible.

## Open questions

- What is the minimal curated promise vocabulary that remains stable?
- How should profiles interoperate with `capset_digest` and portal grants?
