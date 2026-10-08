# 909 — Applied representative-access case packet for Marketplace and Medicare appeal representation: scope, health information, notices, and no appeal right by form friction

## One-line thesis

Marketplace and Medicare appeal representation should be classified as a health-coverage representative-access waist: a person may appoint someone to act in an appeal, claim, grievance, or request, but representation must preserve scope, health-information authorization, notice routing, expiry, revocation, legal-representative alternatives, expedited health-risk access, and the underlying appeal right despite form friction.

## Why this matters

Health-coverage appeals are high-stakes because delay can affect care, medication, premiums, enrollment, cost sharing, claims, and provider access. HealthCare.gov tells Marketplace appellants they can appoint an authorized representative for an appeal, that this person may become the main contact and receive communications, and that an application representative still must be separately appointed for the appeal. Medicare's public forms page identifies CMS-1696 as the appointment-of-representative form used to give another person legal permission to help file an appeal.

HHS Medicare appeal guidance makes the mandate spine visible. It says an appointment should be written, signed and dated by the party and representative, state the appointment, authorize release of personal health information, explain purpose and scope, name the parties, include Medicare or provider identifiers, state relationship or professional status, and be filed with the appeal-processing entity. It also says an appointment is generally valid for one year and can cover more than one appeal filed during that period, and notes that guardians, durable powers of attorney, health care proxies, and state-law representatives may have authority.

The honest form is therefore not “download a form.” It is a health-representation access waist where communication, PHI disclosure, appeal action, fast-track health risk, expiry, and legal-authority alternatives all need a record.

## Pattern pack

### 1. Trigger and dispatcher table

| Field | Finding |
| --- | --- |
| trigger | person wants help filing or conducting a health-coverage appeal, claim, grievance, or request |
| boundary mismatch | application assistance, appeal representation, PHI disclosure, legal representative status, provider appeal role, expedited appeal, and notice routing diverge |
| first-form question | helper, appeal representative, legal representative, provider-initiated route, or transfer of appeal rights |
| lower-form test | ordinary form completion is too thin because the representative may receive health information and control appeal communications |
| heavier-form test | full health-care proxy is too thick where only one coverage appeal or request is at issue |
| form verdict | health-coverage appeal representative-access waist |

### 2. Boundary map

| Component | Boundary rule |
| --- | --- |
| Marketplace application representative | does not automatically cover a Marketplace appeal representative route |
| appeal representative | may receive communications and act on appeal only within the appointment scope |
| PHI authorization | must be explicit because appeal records may include personal medical information |
| expedited appeal | health-risk urgency should not be lost because representative paperwork is incomplete if the person can otherwise ask for speed |
| Medicare appointment | valid for the appointment period and appeal/request scope unless revoked |
| legal representative | court, durable POA, health proxy, or state-law authority may be another valid route |
| provider route | some provider or prescriber actions may proceed without full appointment at lower levels, but higher appeal levels may require appointment |
| revocation | representative authority must be removable without losing the appeal right |

### 3. Evidence-grade table

| Evidence | Governance meaning |
| --- | --- |
| HealthCare.gov appeal-help guidance | authorized representative role, main-contact rule, separate appeal appointment, and appeal-stage actions |
| Medicare appeals forms page | CMS-1696 as the public form for legal permission to help file an appeal and CMS-20031 for transfer of appeal rights |
| HHS right-to-representation guidance | written appointment contents, PHI authorization, professional / relationship disclosure, filing rule, one-year validity, and legal-representative alternatives |
| CMS appointment-of-representative form page | form status and current appointment-of-representative artifact management |

### 4. Live chain notes

Use `848`, `860`, `861`, `894`, `897`, `901`, and `905` first. For this packet, live fields are:

- `406` for identity, mandate, PHI, account, and representative separation;
- `813` for Marketplace, CMS, plan, appeal entity, provider, and representative owner boundaries;
- `815` for appeal continuity, expedited access, coverage continuity, and notice routing;
- `816` for appeal process, PHI, plan, CMS, OMHA, and Marketplace oversight;
- `817` for patients, household members, providers, legal representatives, advocates, and low-digital-access users;
- `818` for appointment, PHI release, notice, hearing, conference, evidence, and decision records;
- `819` for plans, providers, representatives, appeals centers, ombuds, and assisters;
- `820` for form revision, appeal-process changes, or digital appeal portals;
- `821` for appeal, expedited request, representative dispute, dismissal, and revocation routes;
- `824` for plan denial, coverage decision, grievance, and enforcement boundaries.

Reserve `822` and `823` unless payment or supplier portal failures become the center.

### 5. Representative-access docket

This case activates the representative-access tests:

1. **Appeal versus application scope** — distinguish help applying from authority to handle an appeal.
2. **PHI and personal-data release** — record disclosure authority and limits.
3. **Main-contact notice routing** — show whether notices go to the person, representative, or both.
4. **Expedited-health route** — preserve fast-track appeal access despite representative friction.
5. **Legal-representative alternative** — validate guardian, durable POA, health proxy, or state-law route without unnecessary duplicate paperwork.
6. **Provider / prescriber route** — distinguish provider-initiated requests from appointed representation.
7. **Expiry and multi-appeal use** — record validity period and which appeals or requests are covered.
8. **Revocation and replacement** — allow authority to end or shift without appeal-right loss.
9. **Digital and paper parity** — ensure online, mail, fax, phone, language, disability, and assister routes work.
10. **Dismissal protection** — do not let form defects erase appeal rights when cure, good cause, or direct action is possible.

### 6. Opposition and rival readings

**Rival 1: Health-information disclosure needs strict authorization.** The archive accepts this. It asks for cure routes and alternatives, not casual disclosure.

**Rival 2: Appeal entities need a clear person to contact.** True. Main-contact clarity should not hide the person represented from notices, decisions, or revocation.

**Rival 3: Different forms are needed for application and appeal stages.** Sometimes true because the authority differs. The repair is clear transition instructions and no silent loss of appeal help.

**Rival 4: Provider and prescriber exceptions reduce friction.** Useful, but exceptions need boundaries so patients know who is acting and what appeal level is covered.

### 7. Capture and theater channels

- **form-friction theater**: incomplete representative paperwork is treated as loss of appeal-right substance.
- **application-to-appeal gap**: an authorized helper for an application cannot act in the appeal and the person misses the distinction.
- **main-contact erasure**: all communications go to the representative and the patient loses visibility.
- **PHI-overclosure theater**: privacy protection becomes a reason to block advocacy even when proper authorization can be cured.
- **expiry ambiguity**: old appointments are accepted or rejected without visible validity rules.

### 8. Repair surfaces

The packet remains open until the record shows:

- appointment basis and scope;
- PHI authorization;
- party and representative signatures or lawful alternative;
- professional / relationship status;
- filing location and receipt;
- notice route;
- expiry and revocation;
- expedited appeal path;
- provider / prescriber exception boundary;
- cure route for defective representative paperwork.

## Anti-theater tests

This packet fails if the archive treats “authorized representative,” “CMS-1696,” “main contact,” “appeal form,” “doctor can appeal,” or “privacy” as enough. It passes only when scope, PHI, notices, timing, expiry, revocation, expedited access, and direct appeal rights are preserved.

## Holding

Marketplace and Medicare appeal representation is a health-coverage representative-access waist. The rule is: **no appeal right by form friction**. Representation should make appeal rights usable, not convert a health-coverage dispute into a paperwork trap.
