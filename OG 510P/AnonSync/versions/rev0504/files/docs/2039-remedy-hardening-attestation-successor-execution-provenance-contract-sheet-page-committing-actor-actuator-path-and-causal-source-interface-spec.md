# Remedy-hardening-attestation successor execution provenance contract sheet page — committing actor, actuator path, and causal source

## Purpose

This page is the operator-facing contract sheet for one attempted execution run.
It exists to answer a narrow but decisive question:

**if this run fires, what exact actor, subsystem, and actuator path is allowed to cause it, and what adjacent automatic behaviors must never be mistaken for that reviewed cause?**

## Core decision this page must support

The page must let the product distinguish at least these states:

- bound preview exists, no execution source selected
- execution source selected, manual launch pending
- execution source selected, background auto-behavior could still widen or substitute
- run started by reviewed actor through reviewed actuator
- run started by system process under reviewed authority
- run outcome appeared, but causal source is ambiguous
- reviewed actuator diverged from actual actuator
- execution attribution contradicted after the fact

## Minimum fields

### Identity and binding

- action identifier
- successor world identifier
- bound-preview receipt identifier
- execution-run identifier
- reviewed actuator identifier
- reviewed commit token identifier
- reviewed beneficiary slice
- reviewed touched-set summary

### Authorized execution source

- allowed initiating actor set
- allowed subsystem or process set
- required step-up state at fire time
- allowed execution window
- allowed runtime world
- required reviewed actuator path
- forbidden substitute actuator paths
- replay prohibition state

### Attribution hazards

- linked-device auto-arrival hazard
- remembered-approval hazard
- pending-folder auto-connect hazard
- start-time rescan hazard
- scheduled rescan hazard
- pause-residue hazard
- permission-lane substitution hazard
- service-world or sibling-process ambiguity hazard

### Causal source section

- actual initiator if known
- actual subsystem or process if known
- actual actuator path if known
- actual world of execution if known
- first observed effect time
- substitution or widening detected
- strongest safe sentence now
- strongest blocked stronger attributable-execution sentence now

## Required layout

### Header

Show:

- action name
- execution-run identifier
- attribution state
- reviewed actuator versus actual actuator
- current strongest safe sentence

### Left column — what was allowed to fire

Show:

- bound preview summary
- allowed actor and subsystem set
- allowed actuator path
- allowed world and window
- forbidden substitutes

### Right column — what could blur attribution

Show:

- active hazards
- automatic behaviors still live
- adjacent lanes that can produce similar visible outcomes
- why `same result` can still hide a different cause

### Footer decision rail

The footer must expose:

- may fire now / may not fire now
- attribution watcher armed / missing
- strongest honest sentence now
- strongest blocked stronger attributable-execution sentence now

## Hard rules

This page must never collapse:

- `commit authorized` into `execution source identified`
- `same operator` into `same reviewed actuator path`
- `same visible result` into `same causal chain`
- `background automation consistent with intent` into `reviewed run fired`
- `no contradiction noticed yet` into `execution provenance proved`
