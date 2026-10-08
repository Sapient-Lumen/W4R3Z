# Installer trust review page, code-sign reputation, UAC consent, and host-mutation scope interface spec

## Purpose

The host-integration contract sheet publishes posture.
This page decides whether installation or host-authorized upgrade is coherent enough to proceed.

The practical review question is:

> are we merely launching a package, or are we asking the operator to cross code-sign reputation warnings and OS-elevation prompts that authorize specific host mutations?

Current official Resilio docs still expose all the raw ingredients:

- SmartScreen may warn because the signer certificate is new or lacks reputation
- the operator may have to choose `Run anyway` or explicitly `Unblock` the file
- silent installation on Windows still triggers UAC confirmation
- accepted consent creates concrete host artifacts such as Program Files contents, menu items, Explorer integration, and registry entries

AnonSync should make the review first-class rather than scattering the answer.

## When this page appears

Render this review when any of the following is true:

- a package install is requested on a host that has not trusted this signer/package combination before
- an installer warning is raised by the OS or browser/download quarantine
- elevation is required to mutate host-wide surfaces
- a silent install still depends on operator-side trust or consent
- an upgrade changes helper, shell, service, or host-wide integration scope

## Review sections

### 1) Provenance fit

Show:

- package origin
- transport path (`downloaded`, `portable copy`, `managed channel`, `unknown`)
- signer identity
- reputation/trust class
- mismatch between expected and observed origin

Verdicts:

- `trusted-known-origin`
- `trusted-but-new-reputation`
- `origin-unclear`
- `signature-mismatch`
- `block`

### 2) Consent fit

Show:

- whether UAC/elevation is required
- whether the current seat can satisfy it
- whether the install flow still claims to be `silent`
- whether refusal falls back to a less-controlled path

Verdicts:

- `consent-ready`
- `consent-required`
- `consent-refused`
- `silent-only-in-name`
- `block`

### 3) Mutation-scope fit

Show:

- filesystem/program-location mutations
- menu/startup/helper mutations
- registry / preference-store mutations
- shell-extension mutations
- whether the requested scope is broader than the operator intended

Verdicts:

- `scope-matches-intent`
- `scope-broader-than-intent`
- `scope-narrower-than-needed`
- `scope-unknown`
- `block`

### 4) Trust-language fit

Show:

- what the product can now safely say (`package trusted enough to install`, `host mutation authorized`, etc.)
- what it still cannot say (`globally trusted`, `safe everywhere`, `silent no-touch install`)

Verdicts:

- `language-safe`
- `language-too-strong`
- `proof-incomplete`

### 5) Review decision

Return one of:

- `proceed`
- `proceed-with-warning`
- `hold-for-operator-attention`
- `block`

## Main surface

A compact result should read like one of these:

- `new signer reputation warning acknowledged; elevated mutation scope matches requested install`
- `installer launch allowed, but host-wide mutation scope is broader than the operator asked for`
- `silent-install claim withheld because OS consent is still interactive`
- `blocked because package origin or signer proof is weaker than requested trust sentence`

## Required copy blocks

### Strong approval

`The package is trusted enough for the reviewed host mutation scope. This does not automatically prove shell activation or future clean removal.`

### Hold for attention

`Installation is still possible, but the package trust story and the host-mutation story are not the same thing. Review the prompts and the affected host surfaces before proceeding.`

### Block

`The requested install claim is stronger than current provenance or consent evidence. Do not treat this package as host-authorized until those gaps are resolved.`

## Event language

Use phrases such as:

- `package trust reviewed`
- `OS consent requested`
- `host mutation scope accepted`
- `silent-install claim withheld`

Avoid phrases such as:

- `safe installer`
- `fully trusted app`
- `no-touch install complete`

## Design tests

The page fails if any of these remain true:

- SmartScreen-style trust warning is reduced to a generic nuisance instead of a trust-class fact
- UAC consent is not modeled as a boundary between package presence and host mutation
- the interface cannot distinguish a package that can launch from one that can install with its full intended surfaces
- the product still says `silent install` when operator attention is required by the OS
