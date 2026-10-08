# Cooperation benchmark programs should publish direct role-annotated primary verify and refresh targets in handoff packs

## Claim
A compact handoff pack should publish one direct role-annotated `primary_verify_target` and one direct role-annotated `primary_refresh_target` witness.

## Why
The first verify and refresh commands are already present in the pack, but script names alone still force inheritors to reconstruct what those commands act on. Direct role-annotated targets keep the pack locally legible without adding another report family or widening the retained basis.

## Minimal contract
- `primary_verify_target.path` should name the canonical retained machine target for the first verify command.
- `primary_refresh_target.path` should name the canonical retained machine target for the first refresh command.
- `role_codes` should explain both that the target is primary and what retained report it is.
- The targets should stay stable aliases of existing retained paths rather than introducing a second command-selection semantics.
