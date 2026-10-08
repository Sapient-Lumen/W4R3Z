# 444 — Privileged-access tiers, role-restricted logs, and admin-session review

## One-line thesis

Public AI should restrict sensitive administration and log access by role, record privileged actions in detail, and subject elevated sessions to routine review so governance evidence is not left inside an unexamined operator back room.

## Why this matters

Public AI systems often produce a second, less visible system behind the user-facing interface: admin consoles, moderation controls, retrieval settings, prompt editors, vendor support channels, and internal logs full of sensitive interaction data. These backstage controls are where a service can be quietly altered, investigated, or misused. If privileged access is broad and poorly reviewed, the public accountability story collapses exactly where the most consequential technical actions occur.

Current official materials point toward a tighter model. Canada’s 2026 privacy and security guidance for AI help applications says audit logs should maintain detailed records of all access and activity and use role-based access controls so only those with a need to know can access them. The UK’s 2026 AI-ready datasets guidance says organisations should implement role-based access controls and log access and changes. The NCSC’s machine-learning deployment guidance says teams should be able to audit system use, its inputs and outputs, keep appropriate log data for later investigation, and define procedures for managing incidents. The GAO Green Book says logical and physical access controls should restrict information technology to authorised users and that management should limit access to physical and digital resources and records to authorised individuals while maintaining accountability for custody and use.

The archive should therefore add a backstage-governance rule: **the most sensitive AI controls should be both harder to reach and easier to review**. Privilege without routine scrutiny is an accountability blind spot.

## Pattern pack

### 1. Define privileged-access tiers explicitly

Separate at least:

- ordinary service operators,
- reviewers with packet and log access,
- system administrators who can change configuration,
- security or incident responders,
- and vendor or contractor support roles.

Each tier should have a stated purpose and a bounded permission set.

### 2. Keep live interaction logs behind need-to-know controls

Access to prompts, outputs, retrieved sources, and sensitive operational logs should be limited by role and review purpose. Being technically capable of viewing the data should not be enough.

### 3. Log privileged actions at a finer grain than ordinary use

For elevated sessions, record details such as:

- which role accessed the system,
- what settings or content were viewed or changed,
- whether exports were generated,
- whether user-facing safeguards were modified,
- and how long the elevated session lasted.

### 4. Use time-bounded elevation for exceptional actions

When a person needs broader access for incident response, urgent diagnosis, or controlled maintenance, elevate access for a limited window and record the justification, scope, and end of the session.

### 5. Review admin sessions and privileged changes routinely

Do not wait for a scandal to inspect privileged use. Sample and review:

- configuration edits,
- prompt or policy changes,
- bulk exports,
- vendor support sessions,
- and repeated access to sensitive case data.

### 6. Apply the same discipline to vendors and contractors

Third-party support access should use the same or stronger controls as internal staff. Vendor access that bypasses local logging or review should be treated as a governance defect.

### 7. Tie privileged-access review to incident and appeal work

When something goes wrong, investigators should be able to reconstruct whether a privileged action changed the operating conditions, widened access, or altered evidence capture.

## Guardrails

- Privileged roles should be explicitly tiered and justified.
- Sensitive logs and interactions should be role-restricted.
- Elevated actions should be logged in detail.
- Exceptional elevation should be time-bounded and attributed.
- Vendor support access should not bypass local review.

## Failure modes

- **backstage sprawl**: too many staff can reach admin controls or sensitive logs.
- **privilege opacity**: elevated sessions occur but the resulting evidence is too thin to review.
- **support-channel bypass**: vendor staff change settings or inspect data outside the main accountability path.
- **export shadowing**: bulk downloads or packet exports happen without routine scrutiny.
- **incident confusion**: investigators cannot tell whether a privileged action changed the state of the system before or during the failure.

## Practical tests

A privileged-access model passes when it can answer yes to all of the following:

1. Are privileged roles and permission tiers explicitly defined?
2. Is access to sensitive logs and interactions restricted to need-to-know roles?
3. Are privileged actions recorded with enough detail to reconstruct what happened?
4. Are exceptional elevated sessions time-bounded and justified?
5. Are admin changes and support sessions routinely reviewed rather than only after an incident?

## Compression rule for the archive

If the backstage controls of a public AI system are **easy to reach but hard to review**, the governance model is still too vulnerable where the real power sits.
