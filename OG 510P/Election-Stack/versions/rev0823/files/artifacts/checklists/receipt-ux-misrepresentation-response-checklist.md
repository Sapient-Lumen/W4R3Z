# Receipt UX misrepresentation ("don't lie") — response checklist

**Track:** Shared (cross-cutting)


This checklist exists because **receipts are security-critical UX**.
If a client UI implies a ballot is **RECORDED/FINAL/TALLIED** without the corresponding evidence,
the system creates **irrecoverable legitimacy ambiguity**.

Normative reference: `docs/14-receipts-and-state-machine.md`.

## 1) Detect (prove the mismatch)

- ☐ Collect the complaining receipt bundle(s) (screenshots are last resort; prefer the raw receipt objects).
- ☐ Verify whether the bundle contains a valid **inclusion proof** against a known STH.
- ☐ If the bundle contains only an `IntakeReceipt`, treat the ballot as **NOT RECORDED** for messaging and remediation.
- ☐ Determine whether the mismatch is:
  - **local** (one client/app build), or
  - **systemic** (receipt service/log outages, stale endpoints, split views).

## 2) Contain (stop further harm)

- ☐ Freeze the misleading UI string/flow (feature-flag off; force conservative state display).
- ☐ Force all clients into the invariant: **no "RECORDED" unless inclusion proof present**.
- ☐ If the issue is systemic, activate fallback paths (paper/in-person/supervised kiosk) per ops policy.

## 3) Publish (make the failure loud)

- ☐ Publish a `PublicNotice` describing:
  - what the UI incorrectly claimed,
  - which time window / versions are affected,
  - how voters can verify and what fallback to use.
- ☐ If the mismatch affected eligibility to re-cast / cure, publish the remediation policy and deadlines.

## 4) Remediate (repair + evidence)

- ☐ Ship a client hotfix (or configuration patch) that aligns UI states to the state machine.
- ☐ Add/expand an automated test that asserts the mapping:
  - `PENDING` ≠ recorded
  - `RECORDED` requires inclusion proof
  - `FINAL` requires quorum checkpoint
- ☐ Add a drill scenario (or update an existing one) to rehearse this failure mode.

## 5) Postmortem (prevent recurrence)

- ☐ File a `KnownIssue` entry with status and mitigation.
- ☐ If the misleading UI was caused by an ambiguity in `docs/14`, open an ADR and tighten the spec.
