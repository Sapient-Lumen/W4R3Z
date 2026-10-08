# Session deep audit — rev0309

Focus: tax-administration access memo compactness and cube anti-pattern specificity.

## What was risky

After rev0308, tax-administration access remained the largest high-stakes memo-bloat family with legacy `Anti-patterns` and `What would change the recommendation` sections. It also had a cube-quality issue: 16 tax-administration records still used broad `anti_pattern=rent_extraction`, which blurred refund capture, contest-window lock-in, official-error overcollection, third-party record mismatch, filing-channel paywalls, and bankless fallback failures.

## What changed

Rev0309 converts tax-administration local failure and change-trigger taxonomies into compact capsules backed by the route's controlled cube axes. It also ensures every tax-administration route memo points to its actor-accountability profile. The cube refactor replaces tax-admin `rent_extraction` with route-specific anti-pattern values.

## Audit/refactor performed

`tools/audit_prose_bloat.py` now has tax-administration family gates. `tools/audit_axis_hygiene.py` now rejects tax-administration route records that collapse back into generic `rent_extraction` anti-patterns.

## Remaining risk

The next bloat targets are legal-enforcement, labor/care, environment/climate, and social-floor route memos. The next cube hygiene issue is likely not placeholder removal but deciding which family-specific anti-pattern values can be safely shared across families without losing coercion, care, or ecological-harm distinctions.
