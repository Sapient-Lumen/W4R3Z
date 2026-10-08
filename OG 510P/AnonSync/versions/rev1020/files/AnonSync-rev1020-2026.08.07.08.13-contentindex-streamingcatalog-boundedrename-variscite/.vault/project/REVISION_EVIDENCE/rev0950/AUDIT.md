# Rev0950 audit summary

The audit found a remote convergence liveness defect in the shipping C++ folder
path. General post-scan remote apply summed every eligible missing file and
rejected the pass before any effect when the aggregate exceeded one pass budget.
The same sorted projection then failed at the same boundary forever. Zero-byte
files and tombstones created the opposite scale failure: they spent no byte
budget and could drive work and candidate retention toward the full 100,000-path
admission ceiling in one service turn.

Rev0950 retains complete-projection hard admission, but schedules a deterministic
prefix under independent byte and 4,096-operation frontiers. Applied prefix
values become exact no-ops, allowing a stable suffix to advance. Candidate
reservation is bounded by remaining effect allowance. A hard-invalid suffix
still prevents every selected post-scan effect.

The audit also corrected process truthfulness. Deferred remote work or an
unfinished authenticated local scan now fences `settled=true`; durable scan
epoch/cursor/journal state joins the sync process cutpoint, so scan-only
crash-surviving progress is not misreported as a no-op. See
`REMOTE_APPLY_PREFIX_AND_SETTLEMENT_CUTPOINT_AUDIT_rev0950.md`.

The principal remaining scale costs are complete remote projection work, no
persisted remote work cursor, stable-prefix sensitivity to early churn,
root-prefix replay, full immediate-directory buffering, restart-cold payload
namespace scans, and unbounded retained history.
