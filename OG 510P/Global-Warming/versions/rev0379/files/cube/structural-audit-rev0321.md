# Structural Audit rev0321 — Message-Lint and Exercise-Day Capture

## Finding
Rev0320 had official AAR carryforward and packet gates, but it still depended on humans to notice public-message contradictions. Rev0321 adds an executable lint layer.

## Waste removed or contained
- Avoided adding another doctrine-only public-information register.
- Routed public-message proof through `message_lint_fixture -> validator -> result -> SQLite rejection/hold views`.
- Kept reactor-status and future-exercise schedule as context-only clocks, not evidence closure.

## Remaining structural debt
- The scoped SQLite mirror remains emergency-focused rather than a full package mirror.
- Actual June 2026 message packets and AAR/IP artifacts are not yet loaded.
- Legacy 114,494-row nuclear universal crossproduct tables remain retained for compatibility only.
