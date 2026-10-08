# Official voter-information leave warning surface checklist

Use this checklist when an election office relies on **leave-page warnings, unsaved-changes confirmations, or preserve-on-leave posture** to prevent accidental loss on a public voter-information route.

## Scope and route review

- [ ] Record which voter-information routes can still lose meaningful progress if the voter reloads, closes, navigates away, or switches applications before completion.
- [ ] Distinguish leave-page warning posture from broader multi-step preservation, inactivity timeout, hidden-return freshness, local-draft truthfulness, and general overlay behavior.
- [ ] Decide whether each reviewed route needs a browser-generated warning, a route-defined confirmation, preserve-on-hide behavior, or no warning because meaningful state is already preserved.

## Mechanism-truthfulness review

- [ ] Review whether public copy tells the truth about what is actually saved, what is merely local or resumable, and what has not yet reached the office.
- [ ] Do not imply that a browser-generated leave dialog is guaranteed to appear, richly descriptive, or proof that work was preserved.
- [ ] If a custom confirmation is used, name the loss plainly and keep the action choices explicit (for example, Continue without saving vs Go back).
- [ ] Avoid stacking a custom unsaved-changes confirmation on top of a browser-generated leave dialog in a way that tells two different stories about the same state.

## Loss / save boundary review

- [ ] Review whether the route distinguishes unsaved state, local draft state, queued-for-send state, and office-acknowledged state at the moment the voter tries to leave.
- [ ] Do not let leave-warning copy masquerade as submission confirmation, official receipt, or durable portable proof.
- [ ] Review whether the route adds warning behavior only when material unsaved state exists, and removes it again when nothing meaningful would be lost.
- [ ] Re-check any route whose save/resume or submission posture changes materially.

## Reload / mobile / recovery review

- [ ] Review reload, Back/Forward, external-link, sign-in-handoff, and close-tab behavior separately instead of assuming they are all the same leave event.
- [ ] Review mobile app-switch and background-close posture with the assumption that a last-second leave warning may never appear.
- [ ] Keep a bounded restart/help/reopen path so the voter does not have to guess what the safest next step is after leaving or canceling.
- [ ] Verify that any preserved draft or resumable state remains visibly subordinate to the current official page/help lane until the office has actually acknowledged receipt.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed leave-risk routes, mechanism classes, saved-state boundaries, recovery posture, and last review time.
- [ ] Do not preserve raw session recordings, individualized draft contents, or abandonment telemetry merely to prove that leave-risk posture was reviewed.
