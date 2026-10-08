
# Release changes only the CLI promise, not the library baseline

This scenario exists to show that MSRV drift should be reported at member granularity and packed into one review bundle.

What should happen:
- the diff reports only the changed member promise,
- it keeps authoring-floor drift separate from public library support,
- and the bundle joins policy, activation, command-floor, and lockfile receipts without flattening them.

The point is not to produce a giant matrix dump.
The point is to give reviewers one compact, honest support bundle.
