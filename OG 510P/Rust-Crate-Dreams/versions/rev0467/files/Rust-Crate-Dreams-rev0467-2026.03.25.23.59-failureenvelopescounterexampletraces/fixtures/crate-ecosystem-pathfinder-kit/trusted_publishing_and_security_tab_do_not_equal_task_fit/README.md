# Scenario — `trusted_publishing_and_security_tab_do_not_equal_task_fit`

This fixture exists to prove that **P-0509** should not flatten improved supply-chain posture into task fit.

The review question is not “does this crate look more trustworthy to publish and inspect?”
It is “does that trust signal actually answer the role-coverage and interop question for this task?”

## What the scenario should force

- `candidate-import.report.json` may import security/trusted-publishing signals.
- `evidence-origin.report.json` should classify them as **official registry/platform signals** or imported receipts, not crate-fit proof.
- `decision-axis.report.json` should let trust imports help without erasing task fit, role coverage, or migration friction.
- `starter-set-scope.report.json` should be able to say that a stronger org-policy baseline does not automatically become the best teaching or production baseline.

## Why it matters

crates.io now has a Security tab and stronger Trusted Publishing controls.
Those are valuable signals, but they are not the same thing as “this is the right crate stack for the job.”
