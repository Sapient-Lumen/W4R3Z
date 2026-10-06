# Configuration transactions + receipts (commit-confirmed / UCI lessons)

Most OSes treat “configuration” as mutable text under `/etc`, plus restart scripts.
That makes rollouts brittle (especially for networking) and makes “what changed?” hard to answer.

DeriveBSD already has a strong pattern:

**Plan → apply → emit evidence → health gate → commit**

We should apply the same pattern to **system configuration**.

## Lessons to steal (and why)

- **Junos commit-confirmed**: apply config changes, but automatically roll back unless the operator confirms within a timeout. This prevents locking yourself out over SSH.  
  References: https://www.juniper.net/documentation/us/en/software/junos/cli/topics/topic-map/junos-configuration-commit.html , https://www.juniper.net/documentation/us/en/software/junos/cli-reference/topics/ref/command/rollback.html
- **OpenWrt UCI**: staged changes are accumulated and then written/committed atomically (“commit writes at once”). This reduces partial writes and scripting hazards.  
  References: https://openwrt.org/docs/guide-user/base-system/uci , https://forum.archive.openwrt.org/viewtopic.php?id=30428

## DeriveBSD direction

Treat config as *typed state* with explicit transitions and receipts.

### Evidence artifacts (new)

- `config-snapshot`: current effective config (what is live now), plus digests.
- `config-plan`: an explicit transition plan (candidate → active), including validation and optional confirm window.
- `config-receipt`: emitted by the apply engine (success/failure, deltas, rollback pointers).

These should be **small** and **composable**:
- include only structured metadata + digests
- payloads (full text, generated files) are referenced by store paths or bundle payloads
- redactable by deterministic transforms (see `docs/195-deterministic-redaction-transforms.md`)

### Workflow (candidate → active)

1) **Derive** a `config-plan` from the generation’s Plan and policy modules.
2) Apply into a **candidate config root** (not `/etc` directly).
3) Run **validators** (schema checks, `pfctl -n`, network reachability probe, etc).
4) **Activate** by swapping a small set of “live roots” (symlink/rename), and emitting `config-receipt`.
5) Optionally require **confirmation** (commit-confirmed) for riskful scopes (network, auth, remote access).
6) Health gate promotes the generation only if:
   - config apply receipts are successful, and
   - confirm window (if required) is satisfied.

### Commit-confirmed (DeriveBSD flavor)

`config-plan.confirm` can request a time-bounded confirmation.
If not confirmed, the system auto-applies the rollback plan (or swaps back to the prior config root) and emits a rollback receipt.

This pattern is treated as a general DeriveBSD primitive for *any* multi-step transition:
see `docs/242-confirmable-change-sets-and-auto-revert.md` (RFC-0174) and its boot-assessment integration (`docs/241-boot-try-counters-and-boot-assessment.md`).

Design goals:
- confirmation is **capability gated** (only holders of a “confirm authority” can finalize)
- confirmation can be automated by a watcher that verifies reachability / canary checks
- confirmation events go into the structured journal (`docs/215-structured-event-log-as-evidence.md`)

## Integration points (tight wiring)

- **Change sets**: config plans are typically executed as part of a broader `change-set` (state migrations + restarts + health gate) (`docs/219-change-sets-and-apply-engine.md`).
- **Service supervision**: config receipts can declare which services must be restarted or reloaded (`docs/214-service-supervision-health-as-evidence.md`).
- **Health-gated updates**: treat config apply/confirm as part of “healthy enough to commit” (`docs/112-health-gated-updates.md`).
- **Incident bundles**: include current config snapshot + last N receipts by default (`docs/216-incident-snapshots-and-support-bundles.md`).
- **State migrations**: config schema versions can be represented as state datasets when persistence is required (`docs/217-state-datasets-and-migrations-as-evidence.md`).

## Open questions

- Which scopes are “commit-confirmed required” by default? (network, auth, remote access are obvious)
- How do we represent “partial apply allowed” (e.g., network is confirmed, but noncritical tunables can proceed)?
- What is the minimal validator set that should ship in base?


See also:
- Breakglass + recovery mode: `docs/236-breakglass-and-recovery-mode.md`
