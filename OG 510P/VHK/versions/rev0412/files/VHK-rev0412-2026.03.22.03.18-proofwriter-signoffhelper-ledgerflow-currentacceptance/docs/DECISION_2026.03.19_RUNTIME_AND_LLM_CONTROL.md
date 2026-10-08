# Decision — runtime ownership and LLM control posture

## Status
Accepted in revision 0325.

## Runtime model

VHK should primarily run as a **long-lived user service bound to the graphical session**.
That service owns warm-path invocation, watchers, bus behavior, and session-local
control while the user is logged into the desktop.

## Still supported

Ad hoc CLI launches remain part of the product:

- `vhk run ...` for one-shot execution
- development/debug flows
- direct invocation from scripts
- explicit human or LLM-driven runs when a resident path is not required

## Why this model

- The user wants VHK available essentially all the time while logged in.
- The resident model supports faster hot paths and more reliable event/watch flows.
- It matches the repo's emerging `graphical-session.target` direction.
- It preserves CLI simplicity without making cold launch the only posture.

## LLM-facing implications

A private LLM should be able to:

- inspect VHK project artifacts
- write or revise macros in a readable format
- trigger reviewable runs through CLI or a thin dispatch surface
- rely on recorder output plus cleanup passes instead of synthesizing every macro from scratch

## Non-goals for now

- pre-login automation
- system-wide daemon claims as the default product story
- pretending every desktop stack has the same runtime/lifecycle rules

## Explicit authoring contract

The private-LLM story is not only run/dispatch. The repo now treats the source/review loop as first-class:

- source path discovery is explicit
- render review is explicit
- lint review is explicit
- project validation is explicit

That contract should be surfaced through generated wrappers and machine-readable JSON so a caller can edit, review, and execute without scraping docs or reverse-engineering YAML layout.
