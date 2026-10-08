# Authority State Vocabulary

This file normalizes state terms for the authority/delegation/proxy family.

Use these terms when a dossier concerns who may act, disclose, receive, file, waive, bind, appeal, purchase, sell, settle, consent, or decide for another subject.

## Core states

| State | Definition | Use when |
|---|---|---|
| `no-authority` | The actor has no recognized power for the requested action. | denial, fraud resistance, unsupported proxy claims |
| `grant-pending` | A grant has been requested or initiated but is not yet effective. | onboarding, acceptance, verification, approval queues |
| `delegate-unverified` | A claimed representative has not been bound to an identity or credential. | proofing, onboarding, anti-fraud checks |
| `authority-active` | A current recognized grant exists for at least one action. | ordinary reliance, portals, wallets, registries |
| `scope-limited` | Authority exists but only for specified acts, records, values, channels, or time windows. | transaction gating, minimized delegation |
| `joint-approval-required` | The action requires multiple representatives, co-signers, guardians, officials, or controls. | fiduciary decisions, corporate authority, dual control |
| `step-up-required` | The grant is insufficient without additional authentication, consent, confirmation, or review. | high-risk actions, payments, settlements, medical decisions |
| `nondelegable-action` | The action cannot be delegated under the relevant policy or law. | voting, certain signatures, personal testimony, sensitive waivers |
| `verifier-unregistered` | The relying party is not authorized to request or rely on the authority proof. | wallet ecosystems, disclosure-policy enforcement |
| `authority-stale` | A proof of authority is older than the allowed reliance window. | cached credentials, offline artifacts, status-list lag |
| `revocation-pending` | A termination, narrowing, objection, death, capacity change, or role change has been lodged but not fully propagated. | transition periods, recipient-graph updates |
| `revoked` | Authority has ended and should no longer be accepted prospectively. | revocation lists, blocked representatives |
| `expired` | Authority ended by time, review date, matter closure, or period limit. | scheduled reviews, power expiry, temporary representatives |
| `suspended` | Authority is paused pending investigation, dispute, legal hold, outage, or abuse review. | safeguarding, misconduct, account compromise |
| `offline-verifiable` | Authority can be checked without a live query, subject to policy limits. | outage fallback, field work, disaster response |
| `fallback-accepted` | A non-normal evidence route is accepted under documented conditions. | paper proof, caseworker override, emergency continuity |
| `disputed-authority` | The authority relation or its use is contested. | remedy intake, abuse allegations, scope disputes |
| `abuse-watch` | Authority remains possible but is monitored or rate-limited due to risk signals. | safeguarding, fraud, mass representative systems |

## Stage terms

Use these as `authority_stage` values:

- `define`
- `grant`
- `bind`
- `scope`
- `publish`
- `present`
- `verify`
- `act`
- `log`
- `revoke`
- `propagate`
- `fallback`
- `dispute`
- `audit`

## Role terms

Use these as `authority_role` values:

- `principal-subject`
- `delegate-representative`
- `guardian-fiduciary`
- `organizational-admin`
- `legal-person-controller`
- `service-account`
- `ai-agent`
- `issuer-authentic-source`
- `authority-broker`
- `verifier-relying-party`
- `scope-translator`
- `revocation-publisher`
- `fallback-operator`
- `reviewer-auditor`
- `abuse-monitor`

## Distinctions from nearby vocabularies

### Authority versus identity

Identity state says whether the actor is who they claim to be. Authority state says whether that actor may exercise a power in relation to another subject.

### Authority versus access

Access can be read-only, local, reversible, or nonbinding. Delegated authority can bind a principal, waive rights, disclose private data, initiate transactions, or create liability. Do not collapse the two.

### Authority versus standing

Standing is a remedy-door authority state: the filer may contest or request review. The same actor might have standing to complain but no authority to settle or withdraw.

### Authority versus freshness

A credential can be current but wrongly scoped. A credential can be stale but valid for a low-risk offline check. Authority vocabulary should be combined with freshness vocabulary when the reliance window matters.

### Authority versus consent

Consent is one form of grant. Authority can also arise from law, office, guardianship, corporate role, court order, account policy, emergency rule, or public-interest standing.

## Red flags

Avoid using “authorized” without specifying:

- authorized by whom;
- for which subject;
- for which action;
- for which record or matter;
- for which channel;
- for how long;
- with what revocation path;
- with what evidence;
- with what dispute route;
- with what liability consequence.

That checklist is the minimum bar for future authority-family dossiers.
