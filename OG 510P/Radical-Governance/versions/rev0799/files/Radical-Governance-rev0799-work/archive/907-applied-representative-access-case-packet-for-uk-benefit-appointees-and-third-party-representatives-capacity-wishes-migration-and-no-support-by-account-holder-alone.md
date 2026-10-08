# 907 — Applied representative-access case packet for UK benefit appointees and third-party representatives: capacity, wishes, migration, and no support by account holder alone

## One-line thesis

UK benefit appointeeship and third-party representative routes should be classified as a benefit-claim and payment-management representative-access waist: an appointee may make and maintain claims and manage payments for someone who cannot do so, while a third-party representative may support a person who can decide; neither route should become mere account-holder control, password sharing, or transfer of all welfare authority by administrative convenience.

## Why this matters

The UK benefit system exposes several representative forms at once. GOV.UK says an appointee for someone claiming benefits is responsible for making and maintaining claims, signing claim forms, reporting changes, spending benefits paid directly to the appointee in the claimant's best interests, and telling the benefit office if the appointeeship should end. GOV.UK also has a broader “help someone with a benefit claim” route for written authority, including power of attorney, deputyship, and appointeeship.

Social Security Scotland makes the distinction even sharper. Its public guidance distinguishes third-party representatives from appointees: if a person can make their own decisions, they cannot have an appointee, but they may authorize someone to support applications, ask about progress, receive notifications, seek explanations, and help with redetermination or appeal. For appointeeship, Social Security Scotland says it considers whether the person cannot make or communicate decisions, arranges a visit, asks how the person feels where possible, and treats DWP appointeeship as not normally enough for Scottish applications because the legal systems differ.

The honest form is therefore not “the person who has the login.” It is a layered representative-access system: support where possible, substitution where necessary, and migration review where benefits or legal systems move.

## Pattern pack

### 1. Trigger and dispatcher table

| Field | Finding |
| --- | --- |
| trigger | person needs help with benefit claim, cannot manage claim / payments, or authorizes someone to support action |
| boundary mismatch | supported decision-making, appointee substitution, written authority, payment receipt, online account control, and jurisdictional migration diverge |
| first-form question | helper, third-party representative, written-authority representative, appointee, deputy, guardian, or direct claimant route |
| lower-form test | ordinary account access is too thin because representative authority affects claims, notices, payments, appeals, and overpayments |
| heavier-form test | appointeeship is too thick when a person can decide with support |
| form verdict | benefit representative-access and payment-management waist |

### 2. Boundary map

| Component | Boundary rule |
| --- | --- |
| claimant legal entitlement | remains with claimant, not the appointee or helper |
| third-party support | can help while the person remains decision-maker |
| appointeeship | applies where the person cannot manage or communicate the relevant decision / claim route |
| payment receipt | benefit paid to appointee must be spent for claimant's best interests or wants and needs under the programme rule |
| overpayment | appointee may carry reporting and repayment duties where they knowingly or wrongly manage information |
| jurisdictional migration | DWP appointeeship may need review when Scottish benefits move systems |
| online journal / account | cannot be the sole representation record |
| revocation / ending | must be available when the claimant can manage affairs or the representative should stop acting |

### 3. Evidence-grade table

| Evidence | Governance meaning |
| --- | --- |
| GOV.UK appointee guidance | DWP appointee responsibilities for claims, changes, payments, best interests, and ending appointeeship |
| GOV.UK help-someone-benefit-claim guidance | written authority, LPA / EPA, deputyship, appointeeship, and claimant-present call routes |
| Social Security Scotland acting-on-behalf guidance | distinction between third-party representative and appointee, capacity boundary, visits, wishes / feelings, Scottish-law review, and DWP-to-Scotland migration |

### 4. Live chain notes

Use `848`, `860`, `861`, `894`, `897`, `901`, and `905` first. For this packet, live fields are:

- `406` for account, mandate, appointee, and delegated authority separation;
- `813` for DWP, Social Security Scotland, local authority, and claimant-owner boundaries;
- `815` for claim, renewal, payment, migration, and appointee-review continuity;
- `816` for review, complaints, redeterminations, appeals, and overpayment controls;
- `817` for disabled adults, carers, family appointees, corporate appointees, third-party representatives, and claimant voice;
- `818` for appointment, written-authority, notification, online journal, payment, and overpayment records;
- `819` for benefit offices, carers, advice organizations, devolved agencies, and legal representatives;
- `820` for cross-system migration from DWP to Social Security Scotland;
- `821` for appeal, redetermination, appointee dispute, and overpayment challenge;
- `822` for benefit payments and appointee-held money.

Reserve `823` and `824` unless outsourced casework or enforcement sanction becomes live.

### 5. Representative-access docket

This case activates the representative-access tests:

1. **Support-before-substitution** — if the person can decide, use third-party representation or written authority rather than appointeeship.
2. **Capacity and communication record** — show why appointeeship is needed and what wishes / feelings were considered.
3. **Claim-maintenance scope** — name which benefits, changes, reviews, journals, and appeals the appointee controls.
4. **Payment-management boundary** — record who receives payment and how it is spent for the claimant.
5. **Notice routing** — show whether letters, journals, electronic updates, and redetermination notices reach the claimant, appointee, or both.
6. **Overpayment responsibility** — distinguish claimant entitlement, appointee reporting duties, and repayment liability.
7. **Cross-jurisdiction migration** — preserve appointee review when benefits move from DWP to Social Security Scotland.
8. **Ending and restoration** — record how an appointee stops acting when the person can manage affairs or the appointee is unsuitable.
9. **Assisted non-digital routes** — ensure phone, paper, visit, disability, language, and advice routes are real.
10. **Anti-password-sharing record** — do not let online account control substitute for mandate evidence.

### 6. Opposition and rival readings

**Rival 1: Appointeeship prevents missed claims and protects vulnerable people.** The archive accepts this. The case asks for support-before-substitution and continuing review.

**Rival 2: Digital accounts need a single responsible user.** That may be operationally convenient, but legal responsibility must not be hidden inside login control.

**Rival 3: Devolved systems make uniform mandate records difficult.** True. That increases the need for transition receipts when benefits move.

**Rival 4: Families and carers often know best.** Often true, but the claimant's wishes, appeal rights, payment interests, and direct voice still need records.

### 7. Capture and theater channels

- **account-holder theater**: whoever controls the portal is treated as the claimant.
- **substitution-over-support theater**: appointeeship is used where help with decision-making would suffice.
- **notice-disappearance theater**: appointee-only communication hides claim loss or appeal deadlines from the claimant.
- **migration-erasure theater**: appointeeship status moves or fails to move across systems without review.
- **best-interests slogan theater**: payment to an appointee is counted as claimant support without spending and needs records.

### 8. Repair surfaces

The packet remains open until the record shows:

- representative type and legal basis;
- capacity / communication finding;
- claimant wishes and feelings where possible;
- benefit and action scope;
- notice and journal routing;
- payment receipt and spending boundary;
- redetermination / appeal authority;
- overpayment rule;
- appointee review and ending path;
- migration receipt when benefit administration shifts.

## Anti-theater tests

This packet fails if the archive treats “carer,” “appointee,” “written authority,” “online journal,” “best interests,” or “DWP appointee” as enough. It passes only when support, substitution, scope, payment, notice, appeal, overpayment, review, and migration boundaries are explicit.

## Holding

UK benefit appointees and third-party representatives are a benefit representative-access waist. The rule is: **no support by account holder alone**. The right belongs to the claimant even when another person maintains the claim or receives the payment.
