# Cycle run sheet refactor — rev0329

## Problem

The cube had become good at saying what not to claim. It was less good at telling the next operator how
to perform the one allowed substantive action after discovery. The gap between `OWNER-PLAN.md` and a
real local cycle invited either inaction or uncontrolled improvisation.

## Refactor

`prepare_teacher_tutor_micro_pilot_pack.py` now emits `CYCLE-RUN-SHEET.md`. The generated field handoff
opens it immediately after the discovery card and owner plan. The readiness scorer requires the sheet
as an entry file, and the next-action text points entry-ready packets to one cycle using that sheet.

## Why this is not bureaucracy

The run sheet is scratch-local and excluded from release packaging unless a future explicit route
accepts a minimized owner-attested readout. It adds no schema, registry, public-claim rule, or new
recorder. It is an execution bridge.

## Correct state machine

1. `NOT_READY`: discovery and owner-plan fields are incomplete or unsafe.
2. `READY_FOR_LOCAL_CYCLE_NOT_EVIDENCE`: the owner plan and run sheet can support exactly one local
   feasibility/usability cycle.
3. `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`: after a real cycle, aggregate rows and a bounded
   decision are coherent enough for local owner review.
4. Result receipt, evidence import, service authority, and public claims remain blocked unless a
   separate accepted route exists.
