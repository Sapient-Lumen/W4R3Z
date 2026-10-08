# Revision 0345

- promoted recorder sidecars into the flagship i3/X11 warm-runtime control plane
- added `macro-recording-json` plus generated `bin/macro_recording_json.sh` so private-LLM/operator flows can review recorded selector/segment evidence directly
- made generated `record_macro.sh` write a predictable `<macro>.window-context.yaml` sidecar next to the resolved macro source
- changed the generated record wrapper to default pointer replay toward `--coord-mode-mouse window` while preserving an env override
- updated docs/tests so the preferred recorder -> recording review -> cleanup -> retime -> replay loop is explicit
