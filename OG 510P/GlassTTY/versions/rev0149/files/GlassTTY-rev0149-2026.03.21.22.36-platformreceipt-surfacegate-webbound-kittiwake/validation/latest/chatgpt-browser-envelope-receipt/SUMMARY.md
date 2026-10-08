# ChatGPT browser envelope receipt

- generated_at: `2026-03-21T22:05:01Z`
- target support tier: `provisional`

## Browser envelope axes

- browser-engine: Chromium, Firefox, and WebKit proof should remain distinct support envelopes
- browser-brand: one explicit Chromium lane should not silently imply Chrome, Edge, or other branded-browser coverage
- device-class: desktop-web and mobile-web runs should remain separate until both have explicit proof
- execution-profile: headless and live/headed runs should stay visible in the evidence story

## Browser envelope readiness states

- provisional-browser-envelope: repeated proof windows justify only a provisional browser/project-bound support envelope
- experimental-browser-envelope: current evidence can justify only an experimental browser/project-bound support envelope
- hold-for-browser-clarification: proof exists, but the browser engine, brand, device class, or execution mode is still too fuzzy to phrase honestly
- investigated-only: planning or thin proof artifacts exist, but they do not yet justify a live browser envelope
- planning-only: the receipt still describes browser-boundary discipline rather than current live evidence
- stop: the supplied proof windows mix incompatible browser/project profiles and should be split into separate evidence lanes
