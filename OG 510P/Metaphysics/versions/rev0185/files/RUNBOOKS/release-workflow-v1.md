# Release Workflow Runbook v1

Purpose: provide a repeatable local procedure for producing a controlled Metaphysics Archive release.

Scope: local archive releases, governance-layer additions, package repairs, and validation-integrated releases. This runbook does not provide public CI, independent review, source-domain authority, public issue tracking, or automated philosophical validation.

## Ordered stages

1. **Identify predecessor**
   - Record predecessor package, root folder, `VERSION`, manifest status, and known open debts.
   - Stop if predecessor identity is ambiguous.

2. **Classify revision intent**
   - Use `154` to classify the release class.
   - State whether the change is a first-order operator, control-layer addition, infrastructure addition, patch, hotfix, source refresh, deprecation, rollback, or release with declared debt.

3. **Declare scope and non-scope**
   - List expected new files, materially edited files, control files, register artifacts, and tools.
   - State what is not being independently reviewed.

4. **Design the change**
   - Route additions through `144`.
   - Stress-test with `145` when a verdict or new doctrine is involved.
   - Decide whether ledger, terminology, status, dossier, precedent, transmission, reception, release, lineage, provenance, review, public-use, stewardship, continuity, validation, workflow, automation, semantic-fidelity, deployment-boundary, incident-response, post-incident-learning, effectiveness-monitoring, risk-portfolio, or capacity-allocation records are required.

5. **Edit files**
   - Add or modify the numbered document.
   - Update README, `ARCHIVE_INDEX.md`, `VERSION`, `docs/00`, `docs/01`, `docs/03`, `docs/04`, `docs/05`, and relevant control files.

6. **Update registers and schemas**
   - Add or update release-validation transcripts, workflow traces, automation records, semantic-fidelity records, deployment-boundary records, incident-response records, post-incident-learning records, effectiveness-monitoring records, risk-portfolio records, capacity-allocation records, schemas, or runbook references.
   - Preserve old register records unless intentionally deprecated.

7. **Run local validation before packaging**
   - Run `python3 tools/validate_archive.py <root>`.
   - Record failures, skipped checks, remediation, and open validation debt.

8. **Regenerate manifest**
   - Regenerate `MANIFEST.sha256` only after all edits.
   - Exclude `MANIFEST.sha256` itself from its own contents.

9. **Package the archive**
   - Zip the root folder with the versioned root directory intact.
   - Use a filename that matches version and codename.

10. **Fresh-extraction validation**
    - Extract the ZIP to a clean directory.
    - Run `python3 tools/validate_archive.py <extracted-root>`.
    - Stop if validation fails.

11. **Write handoff summary**
    - State new files, edited files, validation result, allowed claims, forbidden claims, and open debts.
    - Do not claim public CI, independent review, public issue tracking, public derivative monitoring, source-watch automation, effectiveness monitoring, derivative monitoring, or domain authority unless evidence exists.

## Minimum release evidence

- predecessor package named,
- release class named,
- touched files listed,
- current `VERSION` set,
- final numbered doc included in README, `ARCHIVE_INDEX.md`, and `docs/00`,
- register artifacts updated when claimed, including post-incident learning artifacts for `167+` releases and effectiveness-monitoring artifacts for `168+` releases, risk-portfolio artifacts for `169+` releases, and capacity-allocation artifacts for `170+` releases,
- validation script run after edits,
- manifest regenerated,
- ZIP created,
- fresh extraction validated,
- handoff limits stated.


## Rev0161 runbook note

For releases at `167+`, this runbook treats post-incident learning as part of release hygiene when a revision claims to learn from an incident, near miss, warning failure, deployment-boundary failure, recovery dispute, or package drift. The release may still be local and non-public, but it should not claim prevention, verified CAPA, independent root-cause review, or safety-case closure unless those are evidenced separately.


## Rev0162 runbook note

For releases at `168+`, this runbook treats longitudinal monitoring, effectiveness review, residual-risk trend assessment, and sunset/renewal discipline as part of release hygiene when a revision claims durable prevention, ongoing control, active monitoring, stable warning retention, source-dependent safety, or retirement of a control. The release may still be local and non-public, but it should not claim active public monitoring, repeated-cycle effectiveness, independent audit, source-watch automation, derivative telemetry, or safe sunset unless those are evidenced separately.


## Rev0163 runbook note

For releases at `169+`, this runbook treats cross-case risk-portfolio review as part of release hygiene when a revision claims collectively manageable residual risk, low cumulative exposure, source-refresh acceptability, derivative safety, deployment readiness, or safe deferral of multiple open debts. The release may still be local and non-public, but it should not claim public risk management, independent portfolio audit, domain risk certification, derivative ecosystem monitoring, source-watch coverage, or low cumulative risk unless those are evidenced separately.


## Rev0164 runbook note

For releases at `170+`, this runbook treats capacity planning, backlog admission, work-in-progress limits, and deferral/resource-debt classification as part of release hygiene when a revision claims that priority work is assigned, scheduled, monitored, manageable, safe to defer, or handled. The release may still be local and non-public, but it should not claim public issue tracking, staffing, service-level commitments, source-watch operations, public monitoring, domain capacity, or operational maintenance unless those are evidenced separately.
