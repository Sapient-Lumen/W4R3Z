# Health-gated updates (A/B-style) + automatic rollback

Atomic switching is table-stakes; DeriveBSD should also know whether the new generation is **healthy** before committing.

Useful references:
- Android A/B updates (slot lifecycle; bootloader fallback): https://source.android.com/docs/core/ota/ab
- update_engine README (A/B lifecycle and rollback note): https://chromium.googlesource.com/aosp/platform/system/update_engine/+/HEAD/README.md
- systemd Automatic Boot Assessment (explicit bless/fallback discipline): https://systemd.io/AUTOMATIC_BOOT_ASSESSMENT/
- Fedora IoT greenboot (health checks + reboot/rollback loop): https://github.com/fedora-iot/greenboot
- SUSE transactional updates (snapshot → update → reboot → rollback): https://kubic.opensuse.org/documentation/man-pages/transactional-update.8.html
- FreeBSD boot environments (`bectl(8)`): https://man.freebsd.org/cgi/man.cgi?query=bectl&sektion=8

See also: `docs/335-boot-assessment-greenboot-and-health-gated-rollback.md`, `docs/472-update-delivery-and-release-posture-by-profile.md`.

Product-shape note: `health-gated` is the default delivery/finalization posture for A and B; C may opt into this lane explicitly, while D usually reaches it through offline bundles or mirror-kit promotion rather than always-on live channels.

## DeriveBSD direction

Treat boot into a new ZFS boot environment (BE) like A/B slot switching:

(For the BE ↔ generation contract, see `docs/404-zfs-boot-environments-as-system-generations.md`.)


1) Switch to new BE **tentatively** (next-boot only).
   - set bounded **boot try-counters** for automatic fallback (`docs/241-boot-try-counters-and-boot-assessment.md`)
2) Boot runs a **health probe** (policy-governed, minimal TCB):
   - can `derive verify-host` validate base sets + signatures?
   - are *required* services healthy?
   - did required state/config migrations complete (receipted)?
   - optional “wanted” checks can degrade posture without blocking commit (greenboot ergonomics)
3) If probe passes → **bless** the boot (commit the generation; clear rollback counters).
4) If probe fails → **mark bad** and rollback to previous BE.

This mirrors a common pattern in A/B systems: **boot-success is a separately recorded fact**, not implied by “we rebooted once”.

## Artifacts (typed, evidence-bearing)

DeriveBSD already models this lane with concrete schemas:

- **Gate policy input**: `spec/boot.health.gate.policy.schema.json`
  - defines required vs wanted checks, success point, and retry bounds
- **Health report output**: `spec/boot.health.report.schema.json`
  - lists check outcomes and evidence digests
- **Bless decision receipt**: `spec/boot.bless.receipt.schema.json`
  - records good/bad, try-counter state, and correlation pointers

Optional operational bundle (typically on rollback):

- `incident.bundle` (policy-bounded) referencing the health report and minimal event/svc/fault context

## Interaction with policy

Policy decides:

- which checks are required vs wanted
- how many reboots to tolerate (try-counters)
- whether to require witness attestations for base sets
- whether state/config migrations are allowed automatically, and what receipts are required

See RFC-0080 and `docs/231-ab-updates-and-recovery-semantics.md`.

Last updated: 2026-03-06r201
