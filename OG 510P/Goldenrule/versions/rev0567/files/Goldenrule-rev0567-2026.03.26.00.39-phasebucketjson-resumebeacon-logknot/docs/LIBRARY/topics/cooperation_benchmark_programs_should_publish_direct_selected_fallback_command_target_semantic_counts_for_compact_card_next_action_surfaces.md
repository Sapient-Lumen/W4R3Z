# Cooperation benchmark programs should publish direct selected fallback command target semantic counts for compact-card next-action surfaces

A compact-card next-action surface should publish the first fallback target's direct typed semantic counts alongside its direct bytes, sha256, and scale summary.

Why:
- inheritors should not have to reopen retained report JSON or parse English scale summaries just to recover the locally relevant counts behind the first recovery step;
- tools should be able to branch on the fallback target's live logical scale without re-deriving hidden report semantics from builder code;
- recovery surfaces should stay as locally auditable as primary-action surfaces instead of degrading once the preferred command fails.

Minimum rule:
- `selected_fallback_command_target_*count` witnesses should agree with the resolved fallback target report when it is a known typed report.
- `primary_action.fallback_target_*count` should be honest aliases of the matching witness fields rather than an independent second computation.
