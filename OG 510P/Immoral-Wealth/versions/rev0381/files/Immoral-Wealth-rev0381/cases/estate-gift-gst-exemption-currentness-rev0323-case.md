---
status: active_case
claim_kind: case_memo
route_role: temporal_currentness_core
canonical_anchor: false
route_refs:
- temporal_currentness_core
- tax_rail_core
- intergenerational_transfer_core
- case_calibration_core
supersedes: null
depends_on:
- estate-gift-gst-exemption-currentness-rev0323-scoreboard.json
source_refresh_due: 2026-12-31
case_pressure: rev0325_substance_hardening
---

# Estate, gift, GST exemption currentness and law-date risk — active case memo

## Current holding

This case now stands for a narrow but important proposition: transfer-tax conclusions are invalid unless they carry a dated current-law snapshot. For the current snapshot, the archive treats the 2026 federal estate/gift/GST exclusion environment as a live law-date surface, not as stable background doctrine. The controlling evidence package is IRS current-law and inflation-adjustment material showing the 2026 basic exclusion amount and annual exclusion surfaces, alongside IRS statistical releases for estate and gift tax filing patterns. [S427] [S428] [S429] [S430]

The case therefore blocks any certification that relies on an older exemption, sunset, portability, gift-tax, or GST assumption without naming the law date and recertification trigger.

## Unit of analysis

- **Jurisdiction:** United States federal transfer-tax system, with intergenerational-transfer comparison only after law-date alignment.
- **Subsystem:** `temporal_currentness_transfer_tax_case`.
- **Dominant breach:** a wealth-transfer case can appear empirically precise while using a stale legal perimeter.
- **Fastest washout:** planning windows, lifetime gifts, GST allocations, portability claims, sunset/reversion claims, and statutory inflation updates can all change the meaning of the same estate or gift fact pattern.
- **Verdict:** `correction_required` with `medium` confidence.

## Minimum evidence package

A transfer-tax case may use this lane only if it provides: current-law date, effective date, exemption amount, annual exclusion, GST treatment, portability treatment, statistical release date, source refresh due date, and the trigger that reopens the conclusion. A conclusion that says only “the estate-tax exemption is high” or “the exemption will sunset” fails this case.

## Correction path

The correction is not another doctrine memo. It is a small operating invariant: every transfer-tax assertion must bind `law_snapshot_date`, `source_refresh_due`, `exemption_surface`, `vehicle_perimeter`, and `incidence_claim`. That invariant should be enforced in scoreboards, case memos, and source rows.

## What would change the verdict

A softer verdict would require a stable machine-readable IRS/statutory current-law feed that makes stale exemption claims difficult to emit. A harder verdict would be justified if the archive finds case memos that continue to use pre-2026 exemption or sunset assumptions without recertification.

## Limits

This case does not estimate hidden dynastic wealth by itself. It is a validity gate for transfer-tax claims. The dynasty-trust and charitable-vehicle cases carry the separate questions of control duration, opacity, public subsidy, and payout timing.

## Rev0362 claim-edge migration note

Rev0362 moves this case from mechanical current-law associations to **7 locator-bound verified claim edges**. The current 2026 BEA/GST amount, estate filing threshold, portability warning, annual gift exclusion, and Form 709 trigger are now separated. The case remains `not_certified_current` because final §2010 guidance, current Form 706/Form 709 instructions, SOI incidence, and dynasty/GST allocation behavior still need migration. [S542] [S543] [S544] [S545]
