# Scenario — newer revalidated pack supersedes an older public summary

A public frozen pack for one release pair was once accurate, but a later revalidation produced a newer current pack for the same lane after source-head and recipe changes.

This scenario demonstrates that the older pack should not keep presenting itself as the active public contract. It should become `superseded`, keep its history, and point at the newer pack instead of competing with it.
