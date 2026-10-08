# Official voter-information virtual-keyboard surface checklist

Use this checklist when an election office expects people to **type into an official voter-information route while a mobile or tablet on-screen keyboard is open**.

## Scope and boundary review

- [ ] Record which public routes are realistically used while the on-screen keyboard is open.
- [ ] Distinguish this surface from general reflow review, field-entry hints, sticky-header overlap, text-assistance mutation, and browser-native validation posture.
- [ ] Keep keyboard-open entry state explicit instead of letting it blur into committed result, accepted submission, or server-reviewed rejection.

## Keyboard-open usability review

- [ ] Review whether the current answer/help lane stays materially usable when focus opens the keyboard and the visible viewport shrinks.
- [ ] Check whether critical controls such as search, continue, submit, reveal, or help actions remain reachable while typing or through a truthful dismiss-and-resume path.
- [ ] Do not assume the browser will resize layout in one universal way when the keyboard appears.

## Error/help visibility review

- [ ] Make sure field-adjacent help or correction text can still be found while the keyboard is open.
- [ ] Do not hide the only practical next-step or correction cue beneath the keyboard.
- [ ] Keep focused-entry state and committed-review state visibly distinct so typing does not masquerade as a final official outcome.

## Support-variance and recovery review

- [ ] Treat keyboard-geometry or layout-adaptation APIs as optional helpers, not as the route’s only safe path.
- [ ] Review a plain recovery story for browsers that do not expose the same keyboard behavior.
- [ ] Preserve the voter’s place/context when the keyboard is dismissed or focus changes.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed routes, critical controls, keyboard-open recovery posture, and last review time.
- [ ] Do not preserve keystroke logs, individualized viewport traces, session replays, or invasive keyboard telemetry merely to prove the posture was reviewed.
