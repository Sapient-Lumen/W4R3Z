# Counterfactual shadow contract

This surface defines the minimum contract for the `counterfactual_shadow` field inside `REVISION-RECEIPT.json`.

## Required fields

- `status`
- `nearby_rejected_move`
- `pivot_surface`
- `rejection_reason`
- `still_live`

## Contract discipline

The counterfactual shadow is not a second changelog and not a branch diary.
It is the smallest object that says:
- what nearby alternative was live,
- where the decision concentrated,
- why the alternative was not admitted,
- and whether it remains live somewhere else.

## Failure modes

A counterfactual shadow fails if it:
- disappears on a substantial status-changing revision,
- records a fake alternative that was never genuinely near admission,
- becomes a branch bureaucracy,
- or omits whether the rejected move remains live in quarantine or open questions.

## Current governing move

- `MV-0012` — `shadow-compare`
