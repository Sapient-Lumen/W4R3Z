# Official voter-information platform live-edge / latency surface checklist

Use this checklist when official voter-information live media can remain publicly reachable while a viewer may be materially behind the true live edge.

## Scope

- [ ] Reviewed the exact public live-event route, not just an admin preview or producer console.
- [ ] Distinguished behind-live / latency state from pre-start waiting-room state and from post-event replay state.
- [ ] Recorded which player, embed, and device contexts were materially relied on.

## Live-edge / delay review

- [ ] Verified whether ordinary latency, buffering, pause, or DVR behavior could leave a voter materially behind the live edge.
- [ ] Verified whether the route made behind-live state visible enough for an ordinary viewer to notice.
- [ ] Verified whether a practical `Watch Live` / `Jump to live` / equivalent recovery control was present when the viewer was behind.

## Mixed-currentness review

- [ ] Checked whether chat, Q&A, reactions, or transcript-jump surfaces could reflect a different moment than the delayed video pane.
- [ ] Verified the office did not treat “the event is live” as equivalent to “this viewer is currently seeing the controlling live moment.”
- [ ] Verified action-changing instructions did not rely solely on the viewer correctly inferring live-edge status from ambiguous player cues.

## Fallback and recovery posture

- [ ] Verified the current written/help lane remained recoverable while the event was still underway.
- [ ] Verified the canonical office page or named office contact stayed practical for volatile operational questions during the event.
- [ ] Logged whether live-edge recovery or mixed-currentness cues differed across platform, embed, or device contexts.

## Public proof posture

- [ ] Logged that live-edge / behind-live states were reviewed and when.
- [ ] Avoided publishing individualized lag telemetry, named interaction traces, or private player diagnostics.
