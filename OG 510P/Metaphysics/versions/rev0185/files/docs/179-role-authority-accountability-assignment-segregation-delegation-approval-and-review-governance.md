# 179. Role Authority, Accountability Assignment, Segregation of Duties, Delegation, Approval, and Accountability Review Governance

## Function of this file

Rev0172 made remediation and closure harder to launder.  This file adds the next layer: **accountability cannot be inferred from the existence of a task, gate, report, or remediation row**.  A package may contain a corrective action, a release decision, and a closure verification, while still leaving unclear who is allowed to decide, who is accountable, who merely performs, who reviews, who is separated from whom, what approval means, what consent does not mean, and what must be reopened when the wrong authority is silently assumed.

The operative warning is:

> Assigned work is not accountable authority.  Local authority is not external approval.  Consent language is not public permission.  Delegation is not disappearance of responsibility.  Review is not independent oversight unless the independence relation is actually present.

## Why this layer is needed

The archive now contains validators, gates, cube observations, reports, incident and remediation ledgers, release decisions, risk acceptance rows, and closure evidence.  These controls can still fail by **role laundering**:

1. a tool executes a check and is treated as an approver;
2. a local maintainer writes a release note and is treated as an external reviewer;
3. a remediation owner closes a case and is treated as the independent verifier of that same case;
4. a package recipient relies on a warning and is treated as having consented to downstream use;
5. a delegated task is treated as if accountability moved with it;
6. a role name such as steward, custodian, reviewer, or maintainer is allowed to carry more authority than the row grants.

Rev0173 therefore adds explicit role, authority, assignment, segregation, delegation, approval, consent, and accountability-review surfaces.

## New artifacts

Rev0173 introduces six root artifacts:

- `ROLE_AUTHORITY_MATRIX.yml`
- `ACCOUNTABILITY_ASSIGNMENT_LEDGER.yml`
- `SEGREGATION_OF_DUTIES_POLICY.yml`
- `DELEGATION_HANDOFF_LEDGER.yml`
- `APPROVAL_CONSENT_LEDGER.yml`
- `ACCOUNTABILITY_REVIEW_LEDGER.yml`

and one executable checker:

- `tools/check_accountability_authority.py`

The checker produces these current reports:

- `REGISTERS/role-authority-report-rev0173.yml`
- `REGISTERS/accountability-assignment-report-rev0173.yml`
- `REGISTERS/segregation-duties-report-rev0173.yml`
- `REGISTERS/delegation-handoff-report-rev0173.yml`
- `REGISTERS/approval-consent-report-rev0173.yml`
- `REGISTERS/accountability-review-report-rev0173.yml`

## Control rule

A release, remediation, claim, gate, or public-use statement may not be upgraded from "locally checked" to "properly authorized" unless the relevant authority row grants that authority.  In rev0173 the authority grant is intentionally narrow:

- local package maintenance may be performed;
- local release language may be recorded after gate checks;
- local evidence custody may be recorded;
- local remediation rows may be triaged and closed;
- local warnings may be preserved;
- external approval, public support, public monitoring, legal notice, regulatory authority, public-consent collection, and operational deployment remain ungranted.

## Role authority matrix

`ROLE_AUTHORITY_MATRIX.yml` separates role names from authority scopes.  Each role has:

- a role identifier;
- authority scope;
- accountability scope;
- explicit forbidden authorities;
- separation constraints;
- evidence artifacts;
- whether public authority is granted.

The matrix is deliberately conservative.  It does not create a board, legal function, regulator, customer-support function, public monitoring function, or external audit body.  It only records what the local archive governance process is allowed to claim.

## Accountability assignment ledger

`ACCOUNTABILITY_ASSIGNMENT_LEDGER.yml` maps governance surfaces to accountable and responsible roles.  It prevents a common failure: a record has an owner field, but the owner is not connected to a real role, authority boundary, decision, evidence, or review trigger.

The ledger distinguishes:

- **accountable role**: answerable for the local governance surface;
- **responsible role**: performs or maintains the work;
- **consulted role**: supplies relevant evidence or review input;
- **informed role**: receives the result or relies on warning propagation;
- **non-roles**: validators, scripts, packages, and generated reports, which cannot hold accountability.

## Segregation of duties

`SEGREGATION_OF_DUTIES_POLICY.yml` blocks self-certifying patterns.  In a small local archive, strict institutional independence is not available, but the absence of independence must be explicit.  Rev0173 therefore requires at least local separation claims to be honest:

- the same surface may be locally maintained and locally checked, but this must not be called independent review;
- custody digest generation must not be called legal chain of custody;
- release decision recording must not be called external approval;
- remediation closure must not be called downstream recall;
- public-use warnings must not be called public consent.

The policy records prohibited pairings and observed local combinations.  A prohibited pairing blocks release language if it is asserted as active authority.

## Delegation and handoff

`DELEGATION_HANDOFF_LEDGER.yml` records whether a role may delegate a task and what remains nondelegable.  Its central rule is:

> Delegation transfers execution permission; it does not erase accountability, externalize review, or authorize public reliance.

Delegation rows therefore require:

- source role;
- receiving role;
- task scope;
- retained accountability;
- nondelegable duties;
- handoff evidence;
- expiry or reopen trigger.

## Approval and consent ledger

`APPROVAL_CONSENT_LEDGER.yml` prevents another laundering path: approval words and consent words are often stronger than the artifact warrants.  Rev0173 distinguishes:

- local release decision;
- local gate pass;
- local risk acceptance;
- local warning retention;
- external approval;
- public consent;
- downstream reliance authorization;
- legal or regulatory approval.

Only the first four are locally recorded; the last four remain absent.

## Accountability review ledger

`ACCOUNTABILITY_REVIEW_LEDGER.yml` records review cases that ask whether authority, assignment, segregation, delegation, approval, and consent rows still support the package language.  It does not claim continuous governance or external oversight.  It creates a local review surface that can be queried, fixture-tested, and reopened.

## New statuses

Rev0173 adds six status families:

- `RAR` — role-authority review;
- `AAS` — accountability-assignment status;
- `SOD` — segregation-of-duties status;
- `DLG` — delegation/handoff status;
- `APC` — approval/consent status;
- `ACR` — accountability-review status.

## Forbidden upgrades

The following claims remain forbidden:

- an independent board approved the package;
- a regulator, customer, user, or downstream deployer consented;
- an external reviewer accepted responsibility;
- a script or validator is accountable;
- a role name by itself grants authority;
- local release permission is public deployment permission;
- local remediation closure is downstream recall;
- local warning retention is informed consent;
- local duty separation is organizational independence;
- local custody digesting is legal chain of custody.

## Place in the control sequence

Doc 179 follows doc 178.  The intended late-stage control path is now:

1. release gate checks say whether local release language may be used;
2. attestation and custody ledgers say what evidence may be claimed;
3. observability and remediation ledgers say what happens after release signals or defects;
4. **role and accountability governance says who may make, maintain, review, delegate, approve, or forbid those statements.**

Without doc 179, the archive could still pass a validator while smuggling an authority claim through a role label.  With doc 179, authority must be row-level, local, bounded, reviewable, and explicitly denied where absent.

## Not claimed

Rev0173 does not claim ISO 37000 conformance, ISO/IEC 38500 conformance, a RACI-certified operating model, an internal-audit function, legal authority, public consent collection, customer support, external approval, organizational independence, public governance infrastructure, or operational deployment readiness.  It borrows design pressure from governance and accountability disciplines while preserving the archive's local research-package boundary.
