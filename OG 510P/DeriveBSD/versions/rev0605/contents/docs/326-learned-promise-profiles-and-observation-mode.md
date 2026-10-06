# Learned promise profiles (observation mode) and least-authority tightening

DeriveBSD wants **pledge/unveil ergonomics** without requiring pledge/unveil in the kernel.
Promise profiles (`spec/sandbox.profile.schema.json`) are the review surface that compiles into:
- jail + mount views
- Capsicum rights reductions
- brokered portals (net egress, listen, clipboard, docs, etc.)

The adoption trap is familiar: *people will not hand-author perfect least-authority profiles first try*.
Greenfield advantage: bake in a **learning loop** as a first-class workflow, so tightening authority is cheap.

## Prior art: “complain mode” and log-driven policy generation

Other ecosystems solved this with an explicit learn→review→enforce loop:

- **AppArmor**: `aa-genprof` / `aa-logprof` parse audit logs and propose rules, with an interactive review step.
  - https://documentation.suse.com/sles/15-SP7/html/SLES-all/cha-apparmor-commandline.html
  - https://documentation.ubuntu.com/server/how-to/security/apparmor/
- **SELinux**: `audit2allow` generates candidate rules from denial logs (dangerous if used blindly; still useful for iteration).
  - https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/6/html/security-enhanced_linux/sect-security-enhanced_linux-fixing_problems-allowing_access_audit2allow
- **Seccomp** (containers): trace syscalls → generate a whitelist profile.
  - OCI hook example: https://github.com/containers/oci-seccomp-bpf-hook

The key pattern:
1) run in **observe/complain** mode
2) collect **structured denials + accesses**
3) generate a **candidate policy patch**
4) require human review before enforcement

## DeriveBSD proposal: a policy-safe learning loop

Introduce a UX lane that makes profiles easy to converge:

### `derive learn <unit>`

- Launches the unit with:
  - a **baseline** promise profile (usually too restrictive)
  - **observation hooks** enabled (DTrace/ktrace + audit, plus broker receipts)
  - an explicit **session id** (so logs are not “grep folklore”)

- Produces:
  - a `trace.session` and/or `trace.receipt` evidence bundle (bounded window)
  - a `policy.suggestion` object (target kind: `sandbox.profile`): *an additive patch* to the profile
  - a diff-style report suitable for review in PRs

Schema: `spec/policy.suggestion.schema.json`.

### What gets learned

Learn the “high leverage” authority surfaces first:

1) **Filesystem allowlist**
   - observed `open(2)`/`execve(2)` paths
   - map into `sandbox-profile.fs.rules[]` (unveil-like)

2) **Network intent**
   - observed connects/listens
   - map into **classes** (`net.egress.policy`, `net.listen.policy`) rather than hardcoding IPs
   - optionally learn DNS receipts to propose hostname bindings (see `docs/305-dns-mediation-and-hostname-binding.md`)

3) **Portal needs**
   - requests to clipboard/docs/notification/etc.
   - map to `sandbox-profile.portals[]`

4) **Capability family deltas**
   - map common syscall families into pledge-like promises (`docs/271-promise-profile-vocabulary-and-lint.md`)

### What must NOT be learned automatically

A learning loop can accidentally “teach” you to permit bad behavior.
DeriveBSD should default to conservative rules:

- **Never auto-approve** broad classes (e.g., “network:any”, “fs:rw:/**”).
- Prefer *narrow* path rules and named egress/listen classes.
- Treat the first run as *incomplete* by default: learning is iterative.

## Evidence model

Treat learning as evidence (not as magic):

- the suggestion references the underlying traces and broker receipts
- the suggestion has a bounded window (time + max events)
- the suggestion is reproducible: rerunning the same workload should yield similar deltas

This keeps the Derive “why did this permission appear?” story intact.

## UX hooks

- `derive learn --interactive`:
  - presents each new permission as a yes/no prompt (uBlock-style), but writes durable policy objects
- `derive learn --ci`:
  - runs a fixed test suite, generates a patch, and fails CI if new authority is required without review

## Relationship to lint and drift alarms

- Learning produces candidate policy.
- Lint (`docs/237-lint-reports-and-contract-testing.md`) checks for footguns.
- Drift alarms (`docs/298-authority-budgets-and-permission-drift-alarms.md`) detect unexpected widening over time.

## Open questions

- Best tracing substrate: DTrace vs ktrace vs audit-first.
- How to normalize paths in the presence of mounts/overlays.
- How to represent “optional features” (feature flags) without over-permitting.

Last updated: 2026-02-26r89
