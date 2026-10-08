# Official voter-information fragment-miss surface checklist

Use this checklist for official voter-information routes that **expect voters, helpers, or later reviewers to follow same-page links, copied `#fragment` references, "On this page" jumps, or other section-level destinations that might occasionally miss the intended target**.

## Target inventory and criticality

- [ ] Record which routes rely on section-level links, copied fragment references, or same-page navigation for action-changing content.
- [ ] Identify the critical section targets whose failure could change a voter’s understanding of deadline, location, eligibility, status, or next step.
- [ ] Re-check long pages where old section-level references are likely to keep circulating after ordinary revisions.

## Miss-truthfulness review

- [ ] Review what the route does when a fragment-bearing or same-page destination does not resolve to a real visible target.
- [ ] Review whether a miss is distinguishable from an ordinary successful page load instead of silently dropping the reader into a generic shell.
- [ ] Review whether the failed destination remains identifiable enough that the reader can tell which section or destination class was being attempted.
- [ ] Review whether compact/mobile layouts preserve the same miss cues and do not hide recovery behind collapsed navigation.

## Refinding and fallback review

- [ ] Review whether unresolved targets are paired with a trustworthy current summary, section list, replacement section, or official fallback notice/help path.
- [ ] Review whether collapsed, injected, or deferred sections have an explicit miss posture rather than requiring trial-and-error expansion.
- [ ] Review whether current-location cues remain truthful after a miss and do not falsely imply that the missing target was reached.
- [ ] Review whether the page avoids forcing the reader to infer recovery solely from browser hash changes or page position.

## Evidence posture

- [ ] Preserve a small public digest of reviewed target classes, miss-feedback posture, refinding/fallback policy, and last review time.
- [ ] Do not retain named-user clickstream logs, raw browser histories, or giant session-replay archives merely to prove that a section target once failed to resolve.
