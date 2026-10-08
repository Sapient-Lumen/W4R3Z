# Remedy-hardening-attestation successor action authorization review page — may this controller or controller set perform this high-risk successor-world action now?

## Purpose

This page is the operator-facing review for deciding whether a named action inside the successor world is currently legitimate.
It exists so the product can separate `controller roster reviewed` from `this risky action is actually allowed right now`.

## Required review questions

The review must force explicit answers to at least these questions:

1. **What exact action is being requested, and how much harm could a mistake cause?**
2. **Which actors are asking to perform it, and are they all presently eligible for this action family?**
3. **Does this action require a second controller, fresh step-up proof, or manual adjudication?**
4. **May any remembered approval, link setting, or convenience default substitute for fresh authorization here?**
5. **Is the authorization only for this one slice and this one execution window, or broader than that?**
6. **What stronger action-legitimacy sentence must remain blocked even if this single action is allowed?**

## Mandatory review sections

### 1. Requested-action review

Show:

- named action and action family
- purpose basis
- affected or beneficiary slice
- blast radius estimate
- reversibility class

### 2. Actor eligibility review

Show:

- every actor attempting to authorize or execute
- each actor's current controller basis
- whether the actor is direct, delegated, remembered, or shadow
- which actors are ineligible for this action even if they remain controllers generally

### 3. Quorum and step-up review

Show:

- whether one actor is enough
- whether a second controller is mandatory
- whether fresh step-up proof is mandatory
- whether emergency exception rules apply
- whether remembered approval is forbidden for this action class

### 4. Window-and-scope review

Show:

- when the authorization starts and expires
- whether it is one-shot or reusable
- whether it applies only to the named object or a broader family
- which stronger future-action sentence remains blocked

### 5. Sentence chooser

The review must output one and only one primary sentence class such as:

- action gate unreviewed
- routine action allowed for named controller only
- high-risk action blocked pending second controller
- step-up proof missing, action blocked
- emergency containment allowed, broader change blocked
- named action authorized once for named slice only
- reusable standing authorization blocked
- broader family authorization blocked

## Hard rules

The review must never let an operator hide:

- high-risk action inside `same controller who handled the last one`
- remembered approval inside `already trusted`
- emergency authority inside `general permission`
- one-shot authorization inside `this role may do this now`
- slice-limited approval inside a broader reusable standing sentence
