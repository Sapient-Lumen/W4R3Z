# Control-surface grade page — audience, auth, transport, and fallback interface spec

## Purpose

Give the operator one reviewed answer to:

- who can reach this control surface right now
- what authentication floor currently guards it
- what transport and certificate truth currently protect it
- what control modality is actually in charge
- what fallback path exists if this grade is weaker than expected
- what stronger sentence the product must not claim

This page is the control-plane companion to runtime profile, listener reach, browser trust, and access-recovery pages.
It should appear whenever a seat exposes any control endpoint or whenever a control-grade-changing action is being reviewed.

## Inputs

- seat / host identifier
- current control modality (`desktop-app`, `local-webui`, `lan-webui`, `config-owned`, `cli-only`, `unknown`)
- audience scope (`device-only`, `specific-interface`, `lan`, `proxied`, `unknown`)
- auth posture (`no-password`, `password`, `password-hash`, `external`, `unknown`)
- session posture (session-cookie, remembered-session, no-browser-session, unknown)
- transport posture (`http`, `https-self-signed`, `https-trusted-cert`, `mixed`, `unknown`)
- browser trust posture (`clear`, `warning-expected`, `residue-present`, `blocked`, `not-applicable`)
- control fallback routes
- intake parity exceptions if known
- recent mutations affecting control grade

## Primary questions this page must answer

1. What grade of control surface is active right now?
2. Who can reach it?
3. What auth floor protects it?
4. What transport/certificate truth protects it?
5. What fallback exists if the current surface fails or proves too weak?
6. What stronger claim is not earned yet?

## Layout

### A. Grade verdict strip

Fields:

- control grade label
- strongest safe sentence
- stronger forbidden sentence
- next safest action

Example labels:

- `local-only http control`
- `lan passworded http control`
- `lan https self-signed control`
- `trusted-cert control`
- `config-owned control without live WebUI`
- `browser-blocked but endpoint known`

### B. Audience and reach card

Fields:

- current audience
- listen handle / bind class
- exposure origin (`default`, `reviewed-change`, `config-owned`, `unknown`)
- widening risk verdict

### C. Auth and session card

Fields:

- auth floor
- credential origin (`ui-set`, `config-set`, `none`, `unknown`)
- session persistence class
- reset collateral class (`low`, `review-required`, `unknown`)

### D. Transport and trust card

Fields:

- transport posture
- certificate class
- browser trust posture
- durable hardening gap

### E. Modality and fallback card

Fields:

- active control modality
- secondary control route
- whether live WebUI is present, degraded, or disabled
- intake parity warning if browser-open differs from manual intake

### F. Grade sentence block

Three stacked lines:

- **What this surface is**
- **What it is protected by**
- **What it is not yet entitled to claim**

Example:

- `This seat currently exposes LAN-reachable WebUI.`
- `It requires a password but still uses HTTP transport.`
- `It must not be described as trusted remote administration until transport and certificate posture are strengthened.`

## Required interactions

- `Review exposure/auth mutation`
- `Inspect certificate posture`
- `Open control access recovery`
- `Compare fallback routes`
- `Export control-surface receipt`

## Guardrails

- Never flatten audience, auth, and transport into one generic `WebUI enabled` sentence.
- Never imply trusted remote administration when only HTTP or self-signed-bypass posture exists.
- Never imply `password protected` is a sufficient grade sentence by itself.
- Never hide the absence of live WebUI when config-owned control disables it.
- Never hide a known manual-intake-only caveat behind a generic `open link` affordance.

## Output

A reviewed control-grade verdict that downstream mutation, trust-recovery, and runtime pages inherit without reinterpretation.
