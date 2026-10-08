# Release-gate process-surface audit and concurrency refactor

**Track:** Shared / Release gate / Audit
**Status:** v856 audit/refactor record
**Scope:** `artifacts/reports/release-gate-process-surface-audit-rev0856.*`, `scripts/check_release_gate_single_instance_lock.py`

## Audit result

v856 treats the one-command release gate as a mutable process surface, not just a list of Python checks. The high-risk operational facts are:

```text
release-gate child-step inventory: 139 checks plus final manifest step
mutating/generated-control steps before manifest sealing: present
single-instance mutation lock: required for mutating runs
lock file inside release root: no
release_gate.py --list lock-free: yes
nested runner while lock held: fails closed
default leftover handling: detect and fail, do not signal
local opt-in termination knob: ELECTION_STACK_RELEASE_GATE_TERMINATE_LEFTOVERS=1
```

The refactor removes a cloud-container foot-gun: release-gate diagnostics should not launch competing mutating runs against the same tree, and a child-step daemonization problem should not be “fixed” by sending signals from a tool running inside an unknown harness.

## Maintainer rule

Run only one mutating release gate against a source root at a time. Use `--list` freely. Use diagnostic slices when localizing failures, but treat a successful slice as diagnostic only; it is not a release verdict and cannot seal `MANIFEST.sha256`.

Boundary: this audit improves local release-runner safety only. It does not turn synthetic verifier fixtures into production trust governance or live-election authority.
