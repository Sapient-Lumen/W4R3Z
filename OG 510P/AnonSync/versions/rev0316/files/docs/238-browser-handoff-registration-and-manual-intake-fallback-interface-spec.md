# Browser handoff, protocol registration, and manual-intake fallback interface spec

## Purpose

The archive already had portable-offer inspection, local claim continuity, and typed headless artifact intake language.
What it still lacked was one stricter contract for a common but under-modeled path into the product:

> when an offer link is opened from a browser, what exactly happens if the browser, the OS, or the chosen control surface cannot hand that artifact off to the local runtime?

Current Resilio docs make this seam concrete.
Their current troubleshooting page still says browser opening can fail because the browser cannot pass the link to Sync, because OS protocol associations are missing, or because browser state blocks the scheme.
Their current WebUI docs also still say that clicking a share link or pasting it into the browser address bar does not work when using WebUI, and that the operator must instead manually paste the artifact into `+` → `Enter a key or link`.

That means browser handoff is still not one stable intake contract.
It is an optimistic shortcut with a manual workaround.

## Core decision

AnonSync must treat browser/OS handoff as an **accelerator**, never as the only valid intake path.
Every portable artifact must have:

- one typed manual-intake lane
- one handoff-health explanation surface
- one receipt showing whether the artifact was handed off automatically or imported manually

The operator must never have to guess whether the link failed because the artifact was invalid, because the browser blocked the handoff, or because the seat only supports browser-mediated control.

## Why this matters

Current Resilio behavior still spreads the answer across several places:

- desktop browser handoff can depend on protocol registration or browser settings
- browser state can cache prior deny/allow decisions
- WebUI cannot consume the clicked browser link directly
- manual paste into a generic `key or link` box becomes the fallback path

AnonSync should therefore keep one stronger rule:

> every handoff failure must degrade to typed manual intake with the artifact still inspectable before action.

## Fixed review order

Every browser-opened artifact must render the same sections in the same order:

1. **Artifact detected**
2. **Handoff health**
3. **Fallback intake**
4. **Claim / adopt consequence**
5. **Intake receipt**

### 1) Artifact detected

Show:

- artifact class (`offer`, `seat invite`, `capability envelope`, `snapshot`, `license`, `unknown`)
- source browser or referring surface
- whether the artifact was opened by deep link, pasted text, file import, or QR scan
- whether the local runtime accepted ownership of the handoff

### 2) Handoff health

Show one explicit state:

- `browser handoff succeeded`
- `protocol registration missing`
- `browser blocked scheme`
- `web control surface cannot consume direct link`
- `artifact malformed or unsupported`

### 3) Fallback intake

The fallback lane must always allow:

- paste artifact text
- inspect the parsed artifact type
- compare intended action before apply
- choose which local seat or runtime receives it

A generic input box is not enough.
The fallback must preserve artifact typing.

### 4) Claim / adopt consequence

Show:

- what subject will be created or affected
- whether this is only inspection, inbox entry, or live local adoption
- whether remembered trust or future-arrival policy could widen as a result
- whether the chosen seat/runtime is the same one the browser originally tried to target

### 5) Intake receipt

Record:

- original handoff source
- handoff state
- artifact classification
- chosen fallback path if any
- final local action taken

## Main surface

Every seat should expose one **Import artifact** entry point that is always present even if protocol handlers are broken.
The product should say things like:

- `browser handoff failed; inspect and import manually`
- `this seat accepts typed paste only`
- `web control cannot consume protocol link directly; use import lane`

## Acceptance criteria

This spec is satisfied when:

- no artifact becomes unusable merely because deep-link registration failed
- browser-open, typed paste, QR, and file import all converge on one typed intake surface
- the operator can tell whether the failure was browser/OS handoff or artifact validity
- the fallback path preserves inspection before local adoption
