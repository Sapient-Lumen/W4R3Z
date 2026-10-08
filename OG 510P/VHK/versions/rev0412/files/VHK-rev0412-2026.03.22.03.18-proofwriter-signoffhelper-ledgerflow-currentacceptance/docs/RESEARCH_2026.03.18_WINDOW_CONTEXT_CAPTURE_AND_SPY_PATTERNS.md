# Research — 2026-03-18 — window-context capture and Window Spy patterns

Why this matters
----------------

VHK wants to feel more like a Linux-native counterpart to AutoHotkey plus
Pulover's Macro Creator, not just a raw event recorder. The practical lesson
from mature automation tools is that *window identity* needs to be easy to
observe and cheap to reuse while authoring macros.

What stood out from current prior art
-------------------------------------

1. AutoHotkey still treats Window Spy as a first-class authoring companion.
   The practical lesson is not merely “show the current title”; it is that
   title, class, and process identity should be gathered at author time so the
   user can scope the automation honestly.

2. Pulover's Macro Creator explicitly added window class/title recording as a
   recorder feature, not merely as a separate inspector. That suggests VHK
   should not keep recorder output and app-scope capture as two distant,
   unrelated workflows.

3. `xdotool search` continues to reinforce the Linux/X11 selector reality:
   name/class/classname/role are the common selector lanes, and they are regex-
   oriented. VHK should keep exporting stable selectors conservatively rather
   than pretending titles are durable.

4. AutoKey issue/docs history keeps reinforcing that Linux window filters are
   often coarser than the product author wants. That is another reason VHK
   should preserve a richer internal selector model and emit explicit review
   payloads instead of flattening everything to one lossy title regex.

Product conclusions
-------------------

- Recorder flows should be able to collect active-window evidence while the user
  is already recording input.
- The recorder should distinguish a conservative `stable` selector from a more
  title-sensitive `exact` selector.
- Only the conservative selector should be auto-applied to a macro by default.
- Richer exact/title-regex suggestions should remain sidecar evidence for human
  review.
- This improves the AHK/Pulover feel without pretending window selectors solve
  the harder semantic-UI problem.

Repo follow-through in this revision
------------------------------------

- `vhk record-x11` can now optionally capture active-window context while
  recording.
- The recorder can emit a JSON/YAML sidecar containing captured samples plus
  `stable` / `exact` selector suggestions.
- When recording directly into a project, the recorder can apply the conservative
  stable selector to the macro's top-level `when:` field.
- Macro-file writing now preserves that `when:` selector explicitly.
