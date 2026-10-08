# Official voter-information constraint-validation surface checklist

Use this checklist when an election office relies on **browser-native HTML constraint validation (`required`, type/range/length/pattern checks, native validation messages, or `reportValidity()` flows)** before a voter can complete a public answer/help step.

## Scope and boundary review

- [ ] Record which public routes rely on browser-native constraint validation before authoritative acceptance.
- [ ] Distinguish this surface from general field-entry guidance, disabled-state posture, text-assistance mutation, and post-submit confirmation/retry controls.
- [ ] Keep the pre-submit browser-blocked state explicit instead of letting it blur into server-reviewed rejection or accepted submission.

## Constraint-validation path review

- [ ] Review whether submit paths use normal interactive validation, `reportValidity()`, custom submit code, `novalidate`, direct `form.submit()`, or some combination.
- [ ] Do not assume browser-native validation is active on every path if some paths bypass it.
- [ ] Keep one coherent explanation of what happens before the route is accepted, rejected by the server, or confirmed.

## Durable explanation review

- [ ] Make the field in error identifiable in durable authored text, not only through a transient browser-native message or red outline.
- [ ] Keep a practical correction cue visible near the field or in a compact page-level summary when the form is longer or multiple fields can fail at once.
- [ ] Treat localized browser-native validation messages as supplementary hints rather than as the sole public explanation of the office’s correction policy.

## Alignment and recovery review

- [ ] Align validation messages with inputs so people using magnification or narrow viewports can tell what failed.
- [ ] Preserve entered values where appropriate so the voter can correct the problem instead of starting from scratch.
- [ ] Do not let browser-blocked pre-submit states masquerade as server-reviewed rejection or accepted submission.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed routes, field classes, submit paths, and last review time.
- [ ] Do not preserve raw failed-entry logs, private screenshots, or invasive per-user invalid-event telemetry merely to prove the posture was reviewed.
