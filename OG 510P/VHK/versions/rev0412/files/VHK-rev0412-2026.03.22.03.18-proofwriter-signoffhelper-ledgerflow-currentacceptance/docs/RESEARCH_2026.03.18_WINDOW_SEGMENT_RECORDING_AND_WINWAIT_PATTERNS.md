# Research note — window-segment recording and WinWait-style patterns

Date: 2026-03-18

## Why this note exists

Revision 0315 taught the recorder to capture one window context. Revision 0316
made pointer coordinates relative to that captured window. The missing product
lesson was that many real desktop flows cross *multiple* windows during one
recording. A single selector or a single pointer anchor was still too flat.

## Product lesson

The lesson from AutoHotkey / Window Spy / Pulover / xdotool is not just
"capture the current window". It is:

1. preserve when the active window changed
2. make that transition reviewable as a window guard instead of hiding it in a
   long sleep
3. keep selectors honest enough that two same-app windows do not silently
   collapse into one broad class-only match
4. let relative pointer capture follow those window segments instead of assuming
   one anchor for the whole recording

## What changed in VHK

Revision 0317 threads that lesson into `vhk record-x11` itself:

- active-window capture now keeps elapsed sample timing, not only selector-ish
  identity fields
- recorder output can be segmented when the active window identity changes
- long `Delay` spans are split so inserted `WaitForWindow` guards land near the
  recorded transition
- per-segment selector choice stays conservative: unique stable selectors stay
  stable, ambiguous same-app segments fall back to exact selectors
- recorder-side relative mouse authoring now composes with those same segments,
  so different windows can each keep their own relative anchor

## Why this is the Linux-native move

Linux automation often alternates between lexical replay, WM-aware selectors,
app-aware adapters, and accessibility lanes. A recorder should not pretend those
are all the same thing. Segment guards are valuable because they preserve one
important truth — which window the author was actually using — without claiming
full semantic understanding of the UI.

## Remaining gaps

- no Studio/editor surface yet for reviewing and editing recorded window
  segments visually
- no automatic promotion from segment guards to richer app-native routes yet
- no Wayland-native lexical recorder equivalent yet
- no mixed segment policy yet for flows that should become app-native in one
  region and accessibility-native in another
