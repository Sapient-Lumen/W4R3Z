# 433 — Approved use-case registers, no-go zones, and tool access tiers

## One-line thesis

Public bodies should not approve AI tools in the abstract; they should approve named use cases, publish or record no-go zones, and tie access tiers to data sensitivity, workflow role, and public impact.

## Why this matters

A great deal of institutional drift begins with an apparently simple sentence: “this tool is approved.” Once that sentence escapes its original context, staff and suppliers start to treat the approval as blanket permission rather than a bounded authorization for a specific job under specific conditions.

That is not enough for public governance. A drafting assistant, summarisation tool, risk flagger, or search copilots may be tolerable for one narrow task and unacceptable for another. The same model that is acceptable for internal note-taking may be inappropriate for handling sensitive personal data, producing reasons given to the public, or materially shaping a frontline decision without a trained reviewer. Governance therefore needs **approved use-case registers**, not generic tool whitelists.

Current official materials support this operational stance. Ofsted says it scrutinises examples of permitted and prohibited use before approval, keeps a register of approved and unapproved uses of AI, assigns a senior owner to each tool or process, and expects staff to use AI according to the approved use case. DWP’s AI security policy similarly distinguishes approved AI tools, requires further approval for sensitive information and for significant use-case change, and obliges users to report misuse or incidents. HMRC’s 2026 generative-AI guidance for software developers adds a useful service-design boundary: AI should support, not replace, human judgment, and tools should clearly flag nuanced cases that require further investigation or qualified advice.

The archive should therefore treat **permission** as a structured object with scope, limits, owners, and renewal triggers. What matters is not whether an institution likes a tool in general, but whether a particular use of that tool is authorized, legible, and survivable.

## Pattern pack

### 1. Register approved uses, not just approved tools

Each consequential AI deployment should have a record that states:

- the named use case,
- the team and senior owner,
- the service context,
- the permitted input classes,
- the permitted output role,
- the required human checks,
- and the reasons this use was approved.

A single tool may have multiple approved uses with different conditions, or one approved use and several prohibited ones.

### 2. Maintain explicit no-go zones

Institutions should maintain written no-go zones such as:

- no use with classified, secret, or otherwise specially protected material without explicit approval,
- no use for final eligibility, enforcement, sanction, or refusal decisions without the governance route required for consequential systems,
- no use for generating reasons given to the public unless the output is reviewed and evidenced,
- no use for sensitive personal-data processing outside approved pathways,
- no use of blocked or unapproved public tools for official work,
- no silent substitution of AI output where policy requires human discretion.

The point is to stop staff learning limits only by rumor or after an incident.

### 3. Tie access tiers to role and data conditions

Access should be tiered. Different people should have different permissions depending on:

- whether they are experimenting, operating, administering, or approving,
- whether the workflow uses public, internal, personal, or sensitive data,
- whether the system affects the public directly,
- and whether the person has completed the role-specific training and runbook acknowledgement required for that tier.

A public tool that everyone can open is not thereby a public tool everyone may use for every official purpose.

### 4. Reapprove when the use case changes materially

A use case should return to governance when:

- new categories of data are introduced,
- the system begins affecting people where it did not before,
- automation depth increases,
- the tool moves from internal assistance to public interaction,
- the provider or model changes,
- or a formerly internal output becomes part of an external decision or communication.

Tool approval without use-case-change control is just a slow path to scope creep.

### 5. Keep permitted and prohibited examples concrete

Every approved-use record should include concrete examples:

- what staff may do,
- what staff may not do,
- what requires escalation,
- and what requires a different system or a human-only route.

These examples are often more governable than abstract rules because they map to actual work.

### 6. Connect public-affecting use cases to public records

When an approved use influences a decision-making process that affects the public, or directly interacts with the public, the institution should connect the internal use-case record to:

- the public registry entry,
- the point-of-interaction notice,
- the system card,
- the impact dossier where one exists,
- and the complaint or appeal route.

Public transparency should describe the actual approved use, not a vague category label.

### 7. Review blocked tools and exceptions as part of governance, not shadow IT

Blocked tools, special exceptions, and temporary approvals should be logged and periodically reviewed. Exception pathways should record:

- who approved the exception,
- why existing tools were insufficient,
- what extra safeguards apply,
- when the exception expires,
- and what would trigger immediate withdrawal.

A permissive shadow exception can quietly become the real operating model unless it is governed as deliberately as the standard path.

## Guardrails

- Do not treat consumer popularity as evidence that a tool is suitable for official work.
- Do not let “internal use only” become a backdoor to consequential use without new approval.
- Keep data sensitivity, public impact, and workflow role visible in every approval.
- Review blocked and approved lists together so that restrictions do not drift into folklore.
- Make it easy for staff to find the current approved-use examples before they act.

## Failure modes

- **blanket approval myth**: staff interpret “approved tool” as permission for any purpose.
- **scope creep by convenience**: a low-stakes assistant quietly becomes part of a consequential workflow.
- **frozen whitelist**: an approved tools list exists, but no one can tell which uses were actually approved.
- **exception sprawl**: temporary carve-outs accumulate until they effectively replace standard governance.
- **shadow prohibition**: frontline staff learn the real no-go zones only through informal warnings after mistakes.

## Practical tests

A use-case approval regime passes when it can answer yes to all of the following:

1. Can the institution show which specific uses of a tool are approved, not just that the tool exists on an approved list?
2. Are no-go zones written down for sensitive data, consequential decisions, and blocked tools?
3. Are access permissions tiered by role, data conditions, and impact?
4. Does a material use-case change trigger reapproval?
5. Can public-facing records describe the actual approved use that affects the public?

## Compression rule for the archive

A tool that is “approved in general” is usually still **ungoverned in practice**.
