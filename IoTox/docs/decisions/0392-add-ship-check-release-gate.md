# 0392 — Add ship-check release gate

Date: 2026-09-20

Status: accepted; sync custody terminology superseded by ADR 0405

## Context

After adding sync and Ratox graduation checks, the repo had good operator
porches but still lacked one blunt command for the release question:

```text
Are sync and Ratox complete and ready to ship without concern?
```

The honest answer is no. Sync is useful as a working-copy system, but
precious-data readiness now depends on versioned recovery custody, restore
drills, and operator runbooks. Ratox is useful as a
profile-bound self-machine control surface, but no-concern release claims still
depend on host-specific sudo/PAM policy, long soak, route-loss evidence,
service-manager/cgroup coverage, and security review.

## Decision

Add a native release gate:

```sh
iotox ship-check [sync|terminal|all] [stable|founder-preview] [--json]
```

The default channel is `stable`. Stable means “ship without concern.” It fails
closed today and prints:

- `stable-without-concern=blocked`;
- sync stable blockers for precious-data readiness and recovery custody; and
- Ratox stable blockers for host/route-specific daily-driver evidence, sudo
  policy, security review, and fleet certification.

The `founder-preview` channel can pass, but only with explicit nonclaims:

- sync is `working-copy-with-versioned-recovery-custody`;
- Ratox is `self-owned-profile-bound-daily-driver-candidate`;
- root remains default-off;
- fleet certification remains blocked; and
- the command still states that stable/no-concern is blocked.

The command is content-free, non-mutating, available in JSON form, and included
in support-bundle planning. `iotox explain ship-readiness` gives the human
explanation and points at `docs/ship-readiness.md`.

## Consequences

The repo no longer relies on a human reading every ADR to avoid overclaiming a
release. Packaging, support, and future datacube reviews can run one command and
see whether the stable product claim is allowed.

This deliberately does not make the missing science disappear. It makes the
absence executable.

## Validation

The human CLI regression now verifies:

- `iotox ship-check` exits nonzero and reports stable/no-concern blocked;
- `iotox ship-check all founder-preview` exits successfully while preserving
  explicit nonclaims;
- `iotox ship-check terminal stable --json` remains machine-readable even when
  blocked; and
- `iotox explain ship-readiness` points at the release gate.
