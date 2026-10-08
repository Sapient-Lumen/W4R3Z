# Service-contact exposure review page: bootstrap, tracker, relay, and link-landing disclosure interface spec

This page exists because `private`, `peer-to-peer`, and `encrypted` are not enough.
A system can keep payload content private while still contacting several outside services for bootstrap, metadata introduction, or relayed carriage.

## Operator question

> which external service contacts occurred or remain allowed here, what did each service learn, and which stronger privacy sentence is still blocked?

## When this page must appear

Render whenever the operator is about to:

- tighten or relax network privacy posture
- disable tracker or relay and expect a privacy win
- use link-based onboarding
- explain why a supposedly direct system still contacted Resilio-operated infrastructure
- claim `no third-party involvement` or reject that claim

## Fixed page order

1. **Exposure summary**
2. **Service rows**
3. **Content-exposure boundary**
4. **Disablement consequences**
5. **Claim ceiling**

## 1) Exposure summary

Show, at minimum:

- exposure verdict (`none witnessed`, `metadata only`, `encrypted byte carriage`, `mixed`, `unknown`)
- strongest safe sentence
- blocked stronger sentence
- whether the exposure is current, historical, or merely allowed

## 2) Service rows

Required service rows:

- bootstrap config service
- tracker service
- relay service
- link-landing service
- update / auxiliary service if relevant
- `none / disabled / unknown`

Each row must show:

- service class
- contacted / allowed / disabled / not witnessed status
- data classes exposed
- whether payload content was exposed
- whether peer addresses were exposed
- whether share identifier was exposed
- whether the contact is user-initiated, automatic, or inherited from onboarding

## 3) Content-exposure boundary

The page must explicitly separate:

- payload plaintext exposure
- payload encrypted carriage
- metadata exposure only
- aggregate click / landing exposure only
- no current witness

The operator must be able to answer:

> did any external service ever carry my bytes, or only metadata, or neither?

## 4) Disablement consequences

For each disablement option, show the reachable consequence:

- disabling tracker may reduce WAN peer introduction
- disabling relay may reduce last-resort transfer success
- avoiding link landing may change onboarding convenience
- disabling bootstrap / external service contact may require private replacement infrastructure or manual addressing
- none of these alone prove that all historical exposure is undone

## 5) Claim ceiling

Allowed examples:

- `Tracker learned peer-introduction metadata; payload remained peer-encrypted.`
- `Relay carried encrypted payload; plaintext remained unavailable to the service.`
- `Link landing counted access without seeing the anchor-contained share specifics.`

Blocked examples:

- `No third party learned anything at all.`
- `Encrypted relay use equals no external carriage.`
- `Disabling tracker after the fact erases prior metadata exposure.`
- `Private onboarding guarantees zero service contact everywhere.`

## Main actions

Examples:

- `Disable tracker for this subject`
- `Disable relay fallback`
- `Require manual addressing`
- `Export exposure receipt`
- `Open discovery branch review`
