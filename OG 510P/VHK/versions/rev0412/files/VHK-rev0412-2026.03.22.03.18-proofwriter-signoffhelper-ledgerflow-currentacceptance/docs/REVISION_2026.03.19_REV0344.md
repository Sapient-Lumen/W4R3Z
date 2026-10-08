# Revision 0344

- promoted cleanup/retime into the generated i3/X11 warm-runtime control plane
- added `optimize_macro.sh`, `apply_optimize_macro.sh`, and `retime_macro.sh` to the generated stack and LLM-facing contracts
- hardened `stack_state_json.sh` so it records per-helper failures instead of collapsing the fused control plane
- updated docs/tests to match the recorder -> cleanup -> retime -> replay loop
