# Public trace bootstrap runtime audit — REV0146

Status: `pass`  
Promotion allowed: `false`

Checks that one-command public-trace runtime bootstrap uses a project-local virtualenv whose PATH persists into snapshot and capture phases, that the actual venv Python runs an import/surface smoke before snapshot materialization, and that the active requirements include hf_xet plus slow-link Hugging Face timeout defaults for modern large-file downloads.

## What this prevents

- One-command runner bootstrap disappearing in a child shell before snapshot/capture phases.
- Pip writing into a system/externally-managed Python instead of a project-local environment.
- Large Hugging Face/Xet-backed model download taking the slow/broken path because `hf_xet` is absent or the default Hub download timeout is too short for a 2.2GB file.
- Wasting a snapshot-download/materialization attempt before proving the project-local venv can import the capture stack and Llama eager-attention hook surface.
- Silently writing or reading large Hugging Face/Xet cache material from user-global home state instead of the trace-bound cache root.

## Errors

- none

## Warnings

- none
