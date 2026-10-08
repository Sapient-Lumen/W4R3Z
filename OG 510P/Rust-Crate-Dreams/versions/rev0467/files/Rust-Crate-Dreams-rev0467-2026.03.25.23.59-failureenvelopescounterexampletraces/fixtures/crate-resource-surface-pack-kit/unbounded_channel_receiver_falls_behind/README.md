# Unbounded channel receiver-falls-behind scenario

Focus: Tokio `unbounded_channel` says sends always succeed while the receiver remains open, and messages are arbitrarily buffered if the receiver falls behind.

Resource-surface reading: `effectively_unbounded` + `unbounded_growth_risk`. The honest support story is not “there is no problem because send is cheap”; it is “this path has no crate-level backpressure cap by default.”
