# Boot assessment in practice (greenboot/systemd) + health-gated rollback

DeriveBSD already targets **atomic generation switching** (ZFS boot environments, `docs/69-host-generations-bectl.md`) and **health-gated updates** (`docs/112-health-gated-updates.md`).

This note tightens that lane with concrete, operationally-proven patterns from other ecosystems:

- **Android/ChromeOS A/B updates**: keep a known-good slot, try the new slot, and *fallback automatically* if boot fails.
- **systemd Automatic Boot Assessment**: boot success is explicitly *blessed* after the system reaches a defined success point.
- **Fedora IoT/CoreOS greenboot**: a small health-check framework that can reboot and rollback after repeated failures.
- **SUSE transactional updates**: snapshot-based atomic updates, often paired with post-boot health checking.

References:
- systemd Automatic Boot Assessment: https://systemd.io/AUTOMATIC_BOOT_ASSESSMENT/
- systemd bless-boot service: https://www.freedesktop.org/software/systemd/man/systemd-bless-boot.service.html
- Fedora IoT greenboot (framework + rollback semantics): https://github.com/fedora-iot/greenboot
- Red Hat MicroShift docs (current greenboot health-check behavior): https://docs.redhat.com/en/documentation/red_hat_build_of_microshift/4.21/html/getting_ready_to_install_microshift/microshift-greenboot
- Red Hat article (greenboot rollback narrative): https://developers.redhat.com/articles/2024/08/12/greenboot-automate-rollbacks-atomically-updated-systems
- Android A/B updates: https://source.android.com/docs/core/ota/ab
- update_engine README (A/B lifecycle and rollback note): https://chromium.googlesource.com/aosp/platform/system/update_engine/+/HEAD/README.md
- SUSE transactional-update man page: https://kubic.opensuse.org/documentation/man-pages/transactional-update.8.html

## The core lesson: "booted" is not "good"

Atomic switching avoids partial upgrades, but it does not answer the operational question:

> **Should this generation become the new default?**

Other ecosystems solve this by separating the state machine:

1) The update/activation system selects a *candidate* slot (next boot).
2) The bootloader enforces bounded retries (try-counters).
3) Userspace runs health checks.
4) Userspace emits an explicit "good" (commit) or "bad" (revert) decision.

The important discipline is **where the boundary is**:

- Bootloader counters handle cases where userspace cannot run.
- Userspace health checks handle cases where the system boots but is broken.

## DeriveBSD mapping

DeriveBSD's equivalents (typed and evidence-bearing):

- **Candidate generation**: a new ZFS BE + its boot-critical closure.
- **Try counters**: `docs/241-boot-try-counters-and-boot-assessment.md` (bounded boot attempts).
- **Health report**: `spec/boot.health.report.schema.json` (`spec/examples/boot.health.report.json`).
- **Bless decision**: `spec/boot.bless.receipt.schema.json` (`spec/examples/boot.bless.receipt.json`).
- **Gate policy**: `spec/boot.health.gate.policy.schema.json` (`spec/examples/boot.health.gate.policy.json`).

### “Required” vs “Wanted” checks (greenboot ergonomics)

greenboot distinguishes checks that **must not fail** from checks that are informative but non-blocking.
DeriveBSD should encode the same concept so operators do not turn off the entire gate when one non-critical probe is flaky.

Suggested structure:

- **required**: failing any required check marks the boot as `bad` and triggers rollback.
- **wanted**: failures are recorded as `warn`/`degraded` but do not block commit unless policy says otherwise.

This should be declared in the **gate policy** (typed input), and reflected in the **health report** (typed output).

### “Boot success point” (systemd ergonomics)

systemd formalizes a generic synchronization point (`boot-complete.target`) and blesses the boot only after it is reached.
DeriveBSD should similarly define a small set of success points (e.g. "multi-user reached", "core services healthy", "control-plane reachable")
so that "good" is not a vague human judgment.

## The state machine (minimal)

This is the smallest state machine that avoids soft-bricks while staying explainable:

- **pending_boot**: candidate BE selected; try-counters initialized.
- **booted_unconfirmed**: userspace running; health checks in progress.
- **committed**: `boot-bless-receipt.decision=good` emitted; candidate becomes default.
- **rolled_back**: `boot-bless-receipt.decision=bad` emitted OR try-counters exhausted; previous BE becomes default.

Tie this to change sets:
- activation emits `change.receipt` and references the boot assessment receipts.
- confirmable change sets (`docs/242-confirmable-change-sets-and-auto-revert.md`) can reuse the same mechanism.

## Evidence and incident handling

Rollback should be self-explaining:

- `boot-health-report` captures *what* failed (and evidence digests).
- `boot-bless-receipt` captures *the decision* (good/bad, counters, correlation ids).
- official support handoff can now carry `boot_bless_receipt_digests` for that exact decision instead of relying on loader counters or greenboot status text.
- optional `incident.bundle` (policy-bounded) captures minimal context (fault/service snapshots, event segments) for remote triage.

This keeps the recovery story deterministic and auditable, instead of "the updater did something".

## Interactions with staged rollouts

Rollout policy already exists (`spec/rollout.policy.schema.json`). The key coupling is:

- A cohort can require **N consecutive good boots** (or a time window) before promotion.
- A cohort can halt or reduce rollout speed based on aggregate rollback rates.

Concrete prior art:
- Fedora CoreOS uses Zincati for automatic updates with phased rollouts (and OSTree rollback): https://docs.fedoraproject.org/en-US/fedora-coreos/auto-updates/

Last updated: 2026-03-21r363
