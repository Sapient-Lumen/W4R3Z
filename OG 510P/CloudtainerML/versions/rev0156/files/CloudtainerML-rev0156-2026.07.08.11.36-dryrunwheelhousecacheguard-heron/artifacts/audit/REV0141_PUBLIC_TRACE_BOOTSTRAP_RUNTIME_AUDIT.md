# Public trace bootstrap runtime audit — REV0141

Status: `pass`  
Promotion allowed: `false`

Checks that one-command public-trace runtime bootstrap uses a project-local virtualenv whose PATH persists into snapshot and capture phases, and that the active requirements include hf_xet for modern Hugging Face large-file downloads.

## What this prevents

- One-command runner bootstrap disappearing in a child shell before snapshot/capture phases.
- Pip writing into a system/externally-managed Python instead of a project-local environment.
- Large Hugging Face/Xet-backed model download taking the slow or broken path because `hf_xet` is absent.

## Errors

- none

## Warnings

- none
