# 905 — Representative access, proxy authority, and fiduciary dockets: scope, consent, revocation, payment control, and no public action by password sharing

## One-line thesis

When someone acts for another person before the state, the archive must not treat a login, family relationship, professional role, payment account, appointeeship, power of attorney, guardian order, representative payee appointment, tax authorization, or appeal form as interchangeable authority; every representative route needs a scoped mandate, capacity or consent basis, revocation path, notice and record trail, payment / information boundary, and direct-rights fallback for the person represented.

## Why this matters

The credential-access pass made login a public-law gate. But many high-stakes services are not handled by the principal alone. Children, disabled adults, older people, people in crisis, incarcerated people, people without digital access, businesses, estates, tax clients, patients, and households often depend on another person or organization to apply, appeal, receive information, manage payments, answer notices, or correct records.

This is a governance chokepoint. A service that cannot model representation pushes people into password sharing, informal family control, call-center improvisation, paper forms that never connect to portals, or professional workarounds. A service that over-models representation may erase the person represented, trap them behind a fiduciary, or let a delegate receive notices and money without review. The honest form is not generic delegation. It is a representative-access docket.

The core rule is: **representation is an authority state, not an identity state.** The representative may prove who they are, but the harder question is what they may do, for whom, under what source of authority, for how long, with what records, and how the principal can see, contest, revoke, or escape it.

## Pattern pack

### 1. Honest forms

| Form | What it can authorize | What it must not silently authorize |
| --- | --- | --- |
| helper / assister | help completing a task while the person remains decision-maker | independent action, payment receipt, notice substitution, or consent beyond the session |
| third-party representative | communication, status questions, document help, appeal support | full benefit management, permanent authority, or payment control |
| authorized representative | scoped action for claim, appeal, grievance, tax period, health matter, or programme | all public services, all periods, or unrelated personal data access |
| appointee | benefit claim maintenance and payment management for a person unable to act | medical, housing, banking, tax, or personal-life authority unless separately granted |
| representative payee | receipt and use of specific public payments for the beneficiary | ownership of funds, non-programme financial power, or extinguishment of beneficiary voice |
| power of attorney / guardian / deputy | state-law or court-based legal power | automatic acceptance in every programme where the programme requires its own appointment |
| professional authorization | practice, representation, disclosure, or record access for specific matters | unrestricted account access or password sharing |
| estate / family route | post-death claim, compensation, refund, or redress tail | substitution without proof of entitlement class and conflict controls |

The archive should ask whether the body has selected the correct representative form before it scores access as successful.

### 2. Separate identity, capacity, consent, mandate, action, and benefit

A representative-access system must keep these states apart:

| State | Required record |
| --- | --- |
| identity | the delegate is the named person or entity |
| relationship | family, professional, guardian, attorney, organization, provider, executor, or other role |
| capacity basis | why the principal cannot act, can act with help, or has chosen to delegate |
| consent or legal authority | signature, oral consent, court order, statutory appointment, programme appointment, or representative form |
| scope | matter, programme, period, action class, data class, payment authority, notice authority, appeal authority |
| expiry and revocation | natural expiry, renewal, withdrawal, death, capacity restoration, programme move, conflict, misuse, or replacement |
| action log | what the representative saw, submitted, approved, received, changed, appealed, or withdrew |
| principal receipt | what the person represented can see, contest, or ask to change |

The failure pattern is account fusion: the delegate becomes the practical principal because the system cannot record mandate separately.

### 3. Capacity is not consent, and consent is not capacity

Some arrangements are chosen by a person with capacity. Others are imposed or appointed because the person cannot manage a payment, communicate a decision, or maintain a claim. The docket must not blur those routes.

A chosen representative route should show consent, scope, withdrawal, and no coercion. A capacity-based route should show evidence, least-restrictive design, wishes and feelings where possible, review, restoration route, and misuse protection. A court or legal-authority route should show document validation and whether the programme still requires its own appointment.

When a person can make decisions with support, the system should prefer support over substitution. When a person cannot manage a specific public payment, the system should not infer that they cannot speak, complain, appeal, or control unrelated rights.

### 4. Payment control is the thickest representative lane

A representative who receives money is not merely a communications helper. Payment control needs a fiduciary docket:

- programme owner and payment owner;
- beneficiary owner of the funds;
- representative receipt account;
- spending rule;
- unmet-needs check;
- conserved-funds record;
- accounting and review;
- misuse allegation path;
- restitution and repayment rule;
- change, removal, or direct-payment restoration route.

No public authority should treat payment to a representative as proof that the beneficiary received support.

### 5. Notice routing is authority

When notices go to a representative, the public authority has altered the evidence chain. The docket should record whether notices go to the principal, representative, both, or only one; whether electronic notifications exist; whether the representative must forward notices; whether missed notice can be cured; and whether deadlines run while a mandate is disputed, expired, or not yet recorded.

A representative can help a person avoid missing notices. A bad representative route can create a new notice failure.

### 6. Revocation, replacement, and restoration are live controls

The docket must show how authority ends. A person may recover capacity, revoke a designee, change tax professionals, remove an appointee, die, become unreachable, enter custody, move jurisdictions, or shift from one benefit system to another. Representatives may withdraw, become disqualified, misuse funds, lose professional standing, or stop acting.

Every representative route needs:

1. revocation by principal where possible;
2. withdrawal by representative;
3. public-body removal for misuse or unsuitability;
4. replacement path;
5. restoration to direct action where possible;
6. emergency continuity where payment, medication, housing, travel, or appeal deadlines are live.

### 7. No password-sharing representation

A service that lacks representation will often create a shadow system: a carer logs in as the claimant, a tax professional asks for account credentials, a family member receives a one-time code, a provider uses a staff workaround, or a call-center agent pretends the person is present. That is not user-centered design. It is missing public authority.

The repair is not merely stronger identity proofing. The repair is scoped, recorded, revocable delegation.

### 8. Representative access and the other archive layers

Use this docket with:

- `901` when a representative route depends on a login, identity proofing, or shared sign-on;
- `894` when procedural churn, renewal, or managed migration depends on a representative receiving and acting on notice;
- `897` when compensation, refund, redress, family, estate, or support-scheme payments require representative proof;
- `887` when a migration risks dropping proxy, appointee, POA, guardian, or professional-authorisation records;
- `884` when a service is closed, replaced, or relaunched and mandate records need transition receipts;
- `874` when automated or model-mediated decisions use representative-provided information or send representative notices;
- `856` when the representative portal, professional file, or mandate database becomes the real authority.

### 9. Minimum representative-access docket

A representative-access docket passes only when it names:

1. principal and represented interest;
2. representative identity and relationship;
3. legal, consent, capacity, or programme basis;
4. scope by action, data, payment, period, and service;
5. notice route and principal copy rule;
6. account, credential, and non-digital routes;
7. fiduciary or conflict controls where money or professional power is live;
8. action log and public record trail;
9. revocation, withdrawal, replacement, review, and restoration path;
10. fallback when the representative route fails before a deadline or payment harm.

## Failure modes

- **password-sharing governance**: the public route works only if the principal gives credentials to someone else.
- **relationship overreach**: family, professional, or provider status is treated as authority without scope.
- **capacity overreach**: inability to manage one payment becomes loss of voice across all rights.
- **consent theater**: a checkbox or oral consent is stretched beyond the matter, period, or data class actually authorized.
- **notice substitution harm**: notices go to the representative and the principal loses the chance to act or complain.
- **payment receipt laundering**: the state counts payment to the fiduciary as support delivered to the person.
- **revocation cliff**: removal or withdrawal creates service interruption, missed deadlines, or unpaid benefits.
- **migration erasure**: a new platform loses appointee, POA, guardian, representative-payee, or professional-authorisation records.
- **portal-only representation**: a digital mandate exists, but paper, phone, language, disability, or urgent routes do not.
- **professional capture**: a representative portal privileges professionals over family, legal-aid, disability, or community assistance.

## Anti-theater tests

This note fails if the archive treats “authorized,” “helper,” “appointee,” “payee,” “power of attorney,” “guardian,” “tax professional,” “representative,” “designee,” or “trusted person” as self-executing. It passes only when authority source, scope, records, payment boundary, notice route, revocation, and restoration are visible.

## Holding

Representative access is a public-service authority waist. The rule is: **no public action by password sharing**. A representative route is legitimate only when it preserves the represented person's rights, voice, records, remedies, and exit from the representative relationship.
