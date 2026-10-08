# Remedy-hardening-attestation successor action-envelope contract sheet page — target slice, predicted effects, and runtime guardrails

## Purpose

This page is the compact contract for deciding whether a successor-world action that is already authorized and plan-reviewed is also safe to arm for execution.
It exists so the product can distinguish `good plan on paper`, `reviewed runtime envelope`, `guardrails armed`, `fail-closed available`, `trip detected`, `abort in progress`, and `stronger within-envelope sentence blocked`.

## Core fields

- successor-action-envelope identifier
- source successor-action-plan receipt identifier
- source successor-action-authorization receipt identifier
- successor-world identifier
- governed slice identifier
- named action identifier
- chosen actuator family
- reviewed purpose summary
- beneficiary slice identifier
- reviewed spread budget
- reviewed persistence budget
- predicted touched-set snapshot
- predicted object count class
- predicted peer or device count class
- predicted folder or path set
- predicted permission mutation set
- predicted new-admission set
- inherited auto-expansion exposure
- inherited remembered-approval exposure
- inherited rescan or restart exposure
- inherited reconnect exposure
- inherited placeholder-to-full-hydration exposure
- runtime guardrail set
- primary trip condition set
- hard-stop availability class
- fail-closed versus fail-open class
- emergency brake family
- residual side-effects after abort class
- post-abort cleanup obligation class
- runtime observation source set
- strongest currently safe public sentence
- strongest blocked stronger sentence
- next fact that upgrades execution-envelope standing now
- next fact that collapses execution-envelope standing now

## Envelope classes

The page must support at least these classes:

- envelope unreviewed
- review drafted but not armed
- reviewed envelope with soft warning only
- reviewed envelope with hard trip guardrails
- reviewed envelope with fail-closed brake
- reviewed envelope with fail-open risk
- live execution inside envelope so far
- trip detected aborting now
- abort completed with no known overspill
- abort completed with residual overspill
- envelope result unresolved

## Touched-set dimensions

The page must model at least these dimensions:

- objects touched
- folders touched
- peers touched
- linked devices touched
- future arrivals exposed
- permissions changed
- approvals remembered or reused
- bytes hydrated from placeholders
- deletes propagated
- rescans still active
- reconnect paths still armed
- unknown touched-set remainder

## Guardrail families

The page must support at least these families:

- preflight diff required before arming
- count ceiling
- path-pattern ceiling
- peer or device ceiling
- permission-escalation ban
- remembered-approval ban
- full-hydration ban
- forwardable-link ban
- restart-required hold
- rescan-required hold
- manual second-actor confirm
- automatic abort on trip
- manual abort only
- no effective brake available

## Required page panels

### 1. Reviewed target slice board

Show:

- the exact beneficiary slice
- the exact touched-set the operator believes is necessary
- what is explicitly outside the reviewed envelope
- what remains unknown before arming

### 2. Automatic-side-effects board

Show:

- remembered approvals
- linked-device auto-availability exposure
- placeholder hydration exposure
- rescans on clock or start
- reconnect or future-arrival exposure

### 3. Guardrail board

Show:

- every armed trip condition
- whether the trip causes a hard stop, soft warning, or no stop
- whether abort is automatic or manual
- what side-effects may still land after abort starts

### 4. Emergency-brake board

Show:

- available brake types
- what each brake actually stops
- what it does **not** stop
- whether pause is acceptable or insufficient for this action class

### 5. Sentence chooser

The contract must be able to emit one and only one primary sentence class such as:

- plan reviewed, runtime envelope unreviewed
- touched-set preview generated, guardrails not armed
- reviewed envelope armed, fail-closed brake available
- full-hydration path blocked, placeholder-only preview safe
- remembered-approval lane blocked for this action
- trip detected, aborting now
- abort completed, residual overspill still under review
- stronger within-envelope sentence blocked

## Hard rules

The contract must never let an operator hide:

- future auto-admission inside `already approved once`
- full nested-folder hydration inside `just connected the folder`
- rescan-triggered work inside `nothing else should happen now`
- deletion propagation inside `we paused it in time`
- unknown touched-set remainder inside `should only affect the intended slice`
- fail-open behavior inside `we can always stop it later`
