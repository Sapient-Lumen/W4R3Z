# Official voter-information speculative-loading surface checklist

Use this checklist when an election office enables **prefetch, prerender, speculation rules, or similar browser-side future-navigation acceleration on official voter-information routes**.

## Scope and target selection review

- [ ] Record which public route classes are allowed to be prefetched, prerendered, or excluded entirely.
- [ ] Distinguish this surface from generic performance tuning, ordinary cache headers, resumed-state honesty, and post-submit confirmation semantics.
- [ ] Keep side-effectful or rapidly varying route classes explicit instead of treating every likely next click as a safe speculation target.

## Fetch-side-effect review

- [ ] Review whether a plain GET to any speculation target can send codes, consume one-time tokens, change language/session state, start timers, or otherwise advance the workflow.
- [ ] Keep server-side guards explicit for speculative requests whose URL class would otherwise create side effects too early.
- [ ] Do not rely on “the user probably meant to click next” as justification for speculative GET side effects.

## Prerender activation-boundary review

- [ ] Review whether prerendered routes run JavaScript that changes storage, analytics, impressions, timers, or other state as though the voter has already arrived.
- [ ] Defer authoritative side effects until actual activation rather than hidden background rendering.
- [ ] Keep route correctness intact when the browser supports prefetch only, supports neither feature, or creates a speculation that never activates.

## Freshness and stale-speculation review

- [ ] Review whether highly variable pages can go stale between speculation time and activation time.
- [ ] Keep an explicit stale-speculation eviction or invalidation path when governing public answers change.
- [ ] Do not let “instant on activation” masquerade as proof that the activated answer is still current.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed target classes, activation-boundary posture, stale-eviction posture, and last review time.
- [ ] Do not preserve individualized speculative-navigation logs, hover traces, or bulky browser debug dumps merely to prove speculation posture was reviewed.
