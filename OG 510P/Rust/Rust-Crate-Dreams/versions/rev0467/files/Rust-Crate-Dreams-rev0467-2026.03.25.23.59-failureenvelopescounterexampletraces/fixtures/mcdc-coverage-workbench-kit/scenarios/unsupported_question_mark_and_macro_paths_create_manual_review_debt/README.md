# Scenario — unsupported `?` and macro-generated paths create manual-review debt

This scenario protects against concluding that a green automated run means the review queue is empty.

Rust's current branch-coverage limitations issue still leaves `?` and macro-introduced branch spans unsupported or caveat-heavy, so the bundle should emit a `manual-review-debt.report.json` rather than pretending the campaign is fully discharged.
