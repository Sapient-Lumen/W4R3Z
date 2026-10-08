# ADR 0150 — Continuity journal restart memory

Service-continuity replay memory must survive restart.  rev0039 adds a continuity-specific journal that detects rollback, same-sequence forks, previous-link mismatch, gaps, replay, scope drift, and hard-negative drops.
