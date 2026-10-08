# Research — app-native protocol lanes and semantic adapters

## Thesis

A Linux-native AHK-class tool should not assume that all automation starts from
keyboard/pointer replay. Some apps already ship deliberate control interfaces
that are stronger, more semantic, and often more desktop-agnostic than replay.

## Product lesson

Treat these app-native control surfaces as explicit adapter lanes:

- terminal-native control (kitty remote control, WezTerm CLI)
- media-player IPC (mpv JSON IPC)
- browser-native extension/userscript hooks (qutebrowser userscripts)

## VHK implication

When project selectors clearly point at these apps, planner output should:

- surface an app-native control lane explicitly
- keep the adapter reviewable instead of hiding it behind generic replay prose
- preserve fallback text/pointer/vision routes for hosts where the app-specific
  protocol is absent

## Near-term implementation note

This revision intentionally stops at planning/output truth. The next concrete
step is to add one or two real adapter generators or manifests so app-native
lanes become deployable artifacts rather than only design guidance.
