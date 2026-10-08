# Roadmap — X11-first narrowing pass

## Mainline priorities

### 1. Recorder -> cleanup -> replay loop

This is the highest-value authoring loop in the repo.
Focus on:

- cleaner recording segmentation
- better default guards and waits
- more aggressive noise reduction
- clearer rewritten output for human/LLM editing

### 2. Warm runtime ownership

Strengthen the session-bound service path:

- keep `graphical-session.target` ownership explicit
- make thin emit/dispatch paths easy to use from i3 and helper scripts
- preserve ad hoc CLI runs without making them the only supported posture

### 3. X11 performance discipline

Treat performance as a system design problem:

- reduce cold-start pressure
- keep X11 replay warm-path friendly
- prefer better text lanes for bulk payloads
- remove avoidable sleeps/polling where event truth exists

### 4. LLM control surface clarity

Make the repo obviously usable by a private LLM:

- keep macro/project formats readable
- document the edit/review/run loop
- make the source/review contract explicit in JSON and generated wrappers
- make recorder cleanup outputs easier to patch programmatically
- keep command surfaces honest and composable

## Explicitly not on the critical path

- broad Wayland parity
- portal-first activation as a default story
- app-native packs as a roadmap centerpiece
- turning VHK into a speech recognizer instead of an automation engine
