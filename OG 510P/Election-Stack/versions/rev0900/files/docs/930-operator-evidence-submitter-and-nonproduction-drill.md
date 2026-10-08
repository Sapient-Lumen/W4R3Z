# 930 — Operator evidence submitter and non-production drill

**Track:** A — mission-kernel closeout and evidence intake.

v891 created the live-evidence intake validator, but it still left the next operator step implicit: how does a local team turn records sitting outside the governed synthetic archive into a digest-bound submission without copying private records into the release tree?

v892 adds that seam.

## Added surface

- `tools/mission_kernel_evidence_submitter.py`
- `scripts/check_mission_kernel_evidence_submitter.py`
- `schemas/MissionKernelEvidenceSubmission.json`
- `tools/mission_kernel_common.py` source-mode vocabulary for `AUTHORIZED_NONPRODUCTION_DRILL_RECORD`
- extended `tools/mission_kernel_live_evidence_intake.py` drill counters and statuses

The submitter reads an operator plan, hashes files that live outside the governed archive, strips local file paths from the canonical submission, and emits a JSON object that can be passed to:

```bash
python3 tools/mission_kernel_live_evidence_intake.py \
  --submission /path/to/local-mission-kernel-evidence-submission.json \
  --json
```

## Why this is not another registry

The riskiest unfinished task is not describing the seven blockers again. It is safely crossing the boundary from an empty template to actual bytes supplied by an operator.

The submitter therefore enforces three concrete controls:

1. the record bytes are hashed before intake;
2. the source file must be outside the governed synthetic archive; and
3. the emitted submission carries approving-role, redaction, public/private boundary, and retention context.

The source records themselves are not bundled into the archive.

## Non-production drill mode

`AUTHORIZED_NONPRODUCTION_DRILL_RECORD` lets maintainers exercise the same hashing and intake path with external temporary bytes while preserving the live no-go boundary.

A drill-valid row can prove that:

- the plan shape is usable;
- the submitter computes digest-bound evidence objects;
- local file paths are not leaked into the submission;
- the intake validator can count completed evidence classes; and
- governed synthetic-tree paths fail closed.

A drill-valid row does **not** prove that a jurisdiction authorized the record, that the evidence is live, that an election outcome is correct, that publication is approved, or that a live pilot may proceed.

## Release-gate negative controls

`check_mission_kernel_evidence_submitter.py` creates temporary files outside the repository, generates a LWC-001 drill submission, and verifies that the intake status is:

`DRILL_PARTIAL_NOT_LIVE_EVIDENCE`

It then verifies two fail-closed cases:

- the submitter rejects `file_path` values under the governed synthetic archive; and
- the intake validator rejects a drill object whose `record_locator` points back into `artifacts/`.

## Boundary

This is an operator-side intake tool and non-production drill harness. It is not live election evidence, not authorization, not certification, not outcome proof, not current voter instruction, not source-byte completeness, and not legal advice.
