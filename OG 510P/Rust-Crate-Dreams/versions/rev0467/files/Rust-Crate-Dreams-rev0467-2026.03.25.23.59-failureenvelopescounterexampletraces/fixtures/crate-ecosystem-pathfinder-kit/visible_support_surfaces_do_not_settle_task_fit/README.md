# Scenario — `visible_support_surfaces_do_not_settle_task_fit`

This fixture exists to prove that **P-0509** should keep visible public support surfaces separate from task fit.

The review question is not “does this crate present a persuasive public story on crates.io and docs.rs?”
It is “does that visible story actually settle the architectural choice for this task?”

## What the scenario should force

- `support-visibility.report.json` should capture registry/docs surfaces explicitly.
- `candidate-basis.receipt.json` should keep visibility facts separate from inferred task-fit claims.
- `decision-pack.report.json` should be allowed to keep uncertainty open even when the public surface looks polished.

## Why it matters

Security tabs, Trusted Publishing posture, docs.rs target landing pages, SLOC, and browse-source links are valuable inputs.
They still do not erase role coverage gaps, interop mismatches, or lock-in cost.
