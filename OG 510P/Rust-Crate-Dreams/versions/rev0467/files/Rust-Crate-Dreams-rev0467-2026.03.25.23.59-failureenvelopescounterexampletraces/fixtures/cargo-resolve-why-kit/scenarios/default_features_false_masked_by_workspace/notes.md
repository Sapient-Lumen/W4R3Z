# Scenario: default-features = false is masked by workspace pressure

The subject package requests `default-features = false`, but another selected package still keeps default features active.

Why this matters: a serious resolver explanation bundle should preserve negative feature intent instead of silently rewriting the story as “defaults were just on”.
