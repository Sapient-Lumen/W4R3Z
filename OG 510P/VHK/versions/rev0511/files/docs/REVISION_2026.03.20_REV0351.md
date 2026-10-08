# Revision 0351

This revision tightens the flagship i3/X11 + private-LLM lane instead of widening Linux scope.

## 1. Canonical per-macro author-loop contract

VHK now ships `macro-author-loop-json` and the generated stack now includes `bin/macro_author_loop_json.sh <macro>`.

That helper fuses:

- editable source metadata
- recorder evidence and freshness
- per-macro review debt
- invocation/dispatch contract
- latest-run scope and health
- the recommended next step

This makes the private-LLM authoring loop less fragmented without changing the authority model: checked-in source remains canonical.

## 2. Generated i3/X11 stack exposes the new lane

The generated warm-runtime stack now advertises the helper in:

- `README.md`
- `control-plane.json`
- the script bundle under `bin/`
- recommended control-plane entrypoints

## 3. Docs say the same thing the stack now does

The repo docs now explicitly describe `macro_author_loop_json.sh` as the canonical per-macro handoff for a private LLM on the flagship X11/i3 lane.
