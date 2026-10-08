# Release-gate single-instance lock and detect-only leftover cleanup

**Track:** Shared / Release gate / Operator safety
**Status:** v856 release-gate mutation and process-boundary hardening
**Scope:** `scripts/release_gate.py`, `scripts/release_gate_lock.py`, `scripts/check_release_gate_single_instance_lock.py`, `scripts/release_gate_steps.py`

## Problem fixed in v856

The release gate is not a read-only command. Early steps regenerate navigation, track, tombstone, source, schema, and packet indexes before later checks and the final manifest decision. Two concurrent gate runs against the same tree can interleave generated writes and leave maintainers with diagnostics that are technically from two different source states.

A second risk sat in the post-step process cleanup path. Previous revisions attempted to terminate scoped descendants left behind by a child step. That is useful on an isolated workstation, but in a PID-namespace or supervised cloud container a diagnostic tool should not risk signalling the harness that invoked it. The safer default is detect-and-fail-closed.

## v856 change

`scripts/release_gate.py` now acquires a packet-external, non-packaged single-instance lock before running any mutating gate subset or full gate. `--list` remains available without the lock so maintainers can inspect the step inventory even when another gate is running.

Post-step daemonization handling now defaults to detection, not termination. If a child step exits but leaves a scoped process-group member behind, the gate marks that step failed and reports the leftover PID list. Maintainers can opt into automatic termination only on an isolated local machine with:

```text
ELECTION_STACK_RELEASE_GATE_TERMINATE_LEFTOVERS=1
```

## Executable guard

`scripts/check_release_gate_single_instance_lock.py` proves the lock path is outside the release root, nested acquisition fails closed, `release_gate.py --list` remains lock-free, a second mutating runner is rejected while the lock is held, the lock releases cleanly, and daemonizing child steps are detected without default automatic termination.

Boundary: this is local release-runner hygiene. It does not prove CI exclusivity, hosted-runner isolation, production signer authority, legal reliance, certification, or live-pilot readiness.
