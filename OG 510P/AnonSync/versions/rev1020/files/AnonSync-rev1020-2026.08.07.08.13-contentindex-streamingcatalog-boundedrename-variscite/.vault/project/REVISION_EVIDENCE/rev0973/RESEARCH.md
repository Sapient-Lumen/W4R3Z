# Rev0973 design context

This revision deliberately implements only an explicit durable retention root.
It does not infer deletion authority from reachability, age, quota, or an old
status observation. The next storage-lifecycle slice remains a dry-run planner
that explains every keep/propose reason while accounting for current evidence,
explicit pins, in-flight work, active snapshots, grace, and capacity. Only a
later writer-fenced journal may mutate the payload namespace.

No new claim about third-party product behavior or current external protocol
state is required for this release cutpoint.
