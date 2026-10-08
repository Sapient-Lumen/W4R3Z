# Automation Delegation Runbook v1

Purpose: provide a local procedure for deciding which archive tasks may be performed by tools, scripts, scheduled checks, or delegated agents without laundering tool execution into philosophical, source, public, or domain authority.

Scope: local archive editing, packaging, validation, register updates, generated drafts, summaries, scheduled reminders, and future automation proposals. This runbook does not establish public CI, public monitoring, independent review, source currency, domain authority, safety-critical assurance, or operational warranty.

## Ordered procedure

1. **Name the requested automated action**
   - Is the tool inspecting, drafting, editing, validating, packaging, scheduling, notifying, publishing, deleting, retracting, or migrating?
   - Stop if the action is ambiguous.

2. **Assign tool-permission class**
   - Use TP0–TP8 from `docs/163-automation-boundaries-agent-delegation-scheduled-execution-and-tool-permission-governance.md`.
   - Downgrade to TP1 if the scope is unclear.

3. **Declare authorized and prohibited scope**
   - List files, registers, schemas, runbooks, and outputs the tool may touch.
   - List actions it may not take.

4. **Check human-review gate**
   - Require human or domain review for doctrinal changes, source-dependent updates, public-use claims, destructive actions, high-stakes domains, or disputed automation boundaries.

5. **Record inputs and outputs**
   - Preserve enough evidence for a successor to know what the tool saw, produced, changed, skipped, and failed.

6. **Run post-action validation when relevant**
   - If files, manifests, schemas, registers, workflow records, or packages changed, run local validation after the tool acted.

7. **Classify automation status**
   - Use AUTO0–AUTO9 and scheduled-execution class SCH0–SCH8.
   - Do not claim public automation, source monitoring, independent reexecution, or external audit without evidence.

8. **Write or update automation record**
   - Use `REGISTERS/schemas/automation-boundary-record-v1.yml` and current-version automation record when a release relies on automation claims.

9. **State allowed and forbidden claims**
   - Include narrow allowed claim language and explicit forbidden claim language in the handoff.

10. **Escalate or stop**
    - Stop for validation failure, unauthorized scope expansion, hidden source dependency, public-action request without public-use/stewardship authority, or destructive-action request without TP8 authority.

## Minimum automation evidence

- action named,
- permission class assigned,
- authorized scope declared,
- prohibited scope declared,
- tool or agent class named,
- inputs and outputs recorded,
- touched files listed,
- human-review boundary stated,
- post-action validation recorded when relevant,
- allowed and forbidden claims stated,
- open automation debt listed.
