# Deployment Boundary Review Runbook v1

Purpose: provide a local procedure for deciding whether archive-derived material may be used as action guidance, workflow support, decision support, policy-like instruction, automated trigger, or operational advice.

Scope: archive summaries, generated outputs, teaching artifacts, public notes, release notes, registers, validators, dashboards, derivative files, fork imports, source-domain adaptations, and any archive-derived artifact proposed for action use. This runbook does not create legal, medical, engineering, financial, safety, institutional, public-administration, employment, educational-assessment, or domain authority.

## Ordered procedure

1. **Identify the artifact and source**
   - Name the version, source files, semantic-fidelity record, output type, and proposed operational context.
   - Stop if the source version or source file cannot be identified.

2. **State the proposed action**
   - Describe whether the artifact will orient, classify, recommend, route, decide, notify, approve, deny, prioritize, escalate, teach, automate, monitor, or govern.

3. **Identify affected parties or systems**
   - State whether only the archive is affected, or whether students, readers, users, contributors, source subjects, public audiences, institutions, or high-stakes parties may be affected.

4. **Check prior governance**
   - Confirm public-use status under `158`, stewardship obligations under `159`, continuity records under `160` when ongoing duties exist, automation boundaries under `163` if tools act, and semantic fidelity under `164` if the material is transformed.

5. **Assign deployment status**
   - Use OP0–OP9. Downgrade if domain authority, source currency, notice, appeal, rollback, or monitoring are missing.

6. **Assign action-reliance class**
   - Use AR0–AR8. Treat institutional, high-stakes, source-dependent, or automated uses as requiring stronger review than local maintenance.

7. **Check domain and source-current requirements**
   - If legal, clinical, engineering, financial, safety, institutional, employment, educational-assessment, or public-administration consequences are possible, require current source review and domain authority before operational use.

8. **Define human review and override**
   - State who reviews, who can override, what evidence is considered, and what cannot be automated or used as sole-basis decision.

9. **Define notice, appeal, correction, and rollback**
   - State how errors, disputes, affected-party challenges, version drift, source changes, or incidents are handled.

10. **Record allowed and forbidden use**
   - Use explicit wording. Do not let orientation, teaching, validation, semantic fidelity, or public citation become deployment permission.

11. **Create or update the deployment-boundary record**
   - Use `REGISTERS/schemas/deployment-boundary-record-v1.yml` for release-level or high-risk records.

12. **Block or quarantine unsafe use**
   - Classify as OP9 or AR8 when operational use outruns authority, safeguards, source currency, or review.

## Minimum evidence

- artifact version and source files,
- proposed action and affected parties,
- semantic-fidelity and public-use status,
- deployment status and action-reliance class,
- domain/source-current review status,
- human-review gate and override path,
- notice, dispute, correction, and rollback path,
- allowed and forbidden use,
- monitoring or next review trigger,
- open operational debt.
