# ChatGPT proof bundle receipt

- generated_at: `2026-03-21T22:05:01Z`
- target bundle state: `hold`

## Bundle quality tiers

- coherent: all three upstream receipts clear honestly, the live proof window is explicit, and the core bundle artifacts are preserved
- reviewable: the bundle is usable for held review, but caution flags or missing secondaries still need to travel with it
- partial: some evidence exists, but the proof window or artifact set is too thin to promote beyond a candidate bundle
- planning-only: the object still describes a plan or receipt stack rather than a named live proof window

## Bundle readiness states

- ready-for-held: route, composer, and submit receipts are honest and the same live proof window preserves the core route/composer/submit/latest-turn artifacts
- ready-with-caution: the bundle can move to held review, but caution flags or thin secondary evidence must remain attached
- hold-for-recapture: some part of the proof window or its artifact set is still too thin for durable held review
- blocked: the current proof window preserves a blocked action path rather than a safe completed baseline
- blocked-by-composer: bundle promotion cannot proceed because composer writability did not clear its own gate
- blocked-by-route: bundle promotion cannot proceed because route proof did not clear its own gate
- planning-only: the bundle is still planning or receipt scaffolding and has not yet become a live captured proof window
- stop: the shell drifted out of the plain route-first baseline and the proof should stop instead of reinterpreting the branch
