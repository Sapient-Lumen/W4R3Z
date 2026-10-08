# 929 — Live evidence intake validator and mission-kernel common refactor

**Track:** A

v890 made the seven live mission blockers actionable, but the archive still lacked the next executable seam: a way to distinguish a real jurisdictional evidence submission from an empty template, generated synthetic packet, or narrative assertion.

v891 adds that seam.

## 929.1 What changed

Added:

- `tools/mission_kernel_live_evidence_intake.py`
- `scripts/check_mission_kernel_live_evidence_intake.py`
- `schemas/MissionKernelLiveEvidenceIntake.json`
- `artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-submission-empty.json`
- `artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-intake-status.json`
- `artifacts/examples/example_county_2026_municipal_pilot/live-closeout-evidence-intake-status.csv`
- `artifacts/examples/example_county_2026_municipal_pilot/public-live-closeout-intake-status.md`
- `artifacts/reports/mission-kernel-live-evidence-intake-rev0891.json`

Refactored:

- `tools/mission_kernel_common.py` now owns the mission-kernel element labels, evidence-class map, source-mode vocabulary, redaction/public-boundary value set, and governed-synthetic-path guard.
- `tools/mission_kernel_live_workqueue.py` now consumes that common model instead of owning a private evidence-class taxonomy.
- `tools/mission_kernel_live_evidence_intake.py` consumes the same common model, so the workqueue and intake validator cannot silently drift into different definitions of the required records.

## 929.2 Current result

The shipped Example County submission is deliberately empty:

- decision: `UNFILLED_TEMPLATE_NOT_EVIDENCE`
- live evidence objects: `0`
- valid live evidence objects: `0`
- missing live-evidence work items: `7`

The generated intake status therefore remains:

`NO_GO_NO_LIVE_EVIDENCE_SUBMITTED`

This is a useful no-go. It proves the archive has an executable intake contract and that the governed synthetic tree has not fabricated live evidence.

## 929.3 Validation rules

A future filled submission may not close a work item merely by adding prose. For each required evidence class, the validator expects a live object to provide at least:

- `source_mode` equal to `LIVE_AUTHORIZED_LOCAL_RECORD`;
- a `record_locator` that does not point back into the governed synthetic archive;
- a `sha256:<64 hex>` digest;
- an `approving_role`;
- a completed `redaction_status`;
- a `public_private_boundary`; and
- work-item coverage for the minimum evidence classes inherited from the live workqueue.

The validator rejects governed synthetic paths such as `artifacts/`, `docs/`, `schemas/`, `scripts/`, `tools/`, `observer-kit/`, and `evidence/lock/` as live source records. A generated artifact can be a derivative or public summary later, but it cannot be the field evidence that closes the live closeout gap.

## 929.4 Why this is higher priority than more doctrine

The riskiest unfinished work is the transition from synthetic assurance to a real closeout chain. Before any jurisdiction can attempt that transition safely, the cube must have a concrete intake gate that fails closed on:

- empty submissions;
- partial evidence;
- missing digests;
- missing approving roles;
- generated synthetic archive paths misused as source evidence;
- missing redaction/public-boundary review; and
- evidence classes that do not match the blocker being closed.

v891 provides that gate without claiming field readiness.

## 929.5 Maintainer commands

Regenerate the intake status after a workqueue or submission change:

```bash
python3 tools/mission_kernel_live_evidence_intake.py --write
```

Check the shipped no-go intake pack:

```bash
python3 scripts/check_mission_kernel_live_evidence_intake.py
```

Evaluate an external filled submission without writing governed outputs:

```bash
python3 tools/mission_kernel_live_evidence_intake.py \
  --submission /path/to/local-live-closeout-evidence-submission.json \
  --json
```

## 929.6 Boundary

This revision is not live election evidence, not certification, not outcome proof, not current voter instruction, not public-release authorization, and not legal advice. It adds the validator a real submission must pass before humans can review whether live closeout reliance is even plausible.
