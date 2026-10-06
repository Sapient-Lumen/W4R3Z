# Open questions

Revision: rev0028.

## Runtime

1. What is the smallest useful task registry shape after the worker-agent proof?
2. Should actor/process identity appear before or after cancellation/deadline
   semantics?
3. What object-ref states are needed before transfer pools and shared slabs?
4. How early should the browser Worker/CDP harness arrive?
5. How much of the future scheduler should be proven in Node before browser
   lanes begin?

## Testing facility

1. Should future browser tests lease one browser per shard or one browser per
   test class?
2. What input-hash scheme is enough for local skip-safe cached test results?
3. What is the correct flake classification format for retries?
4. When should timing baselines graduate from seeded estimates to measured
   medians?
5. How should the runner merge multiple shard artifacts across conversation
   turns?
6. Should fixture generation be a manifest test, a prep phase, or a separate
   cacheable action surface?
7. Which browser probes are cheap enough to enter `fast`, and which must remain
   opt-in?

## Cloudtainer process posture

1. Is it ever safe to rely on a background process across multiple tool calls?
2. Should package-release kill any stale local servers/browsers before running?
3. Should the runner record process tree cleanup evidence for browser tests?
4. Should future long browser suites require a max wall budget per shard?


## Rev0005 addition

Rev0005 adds `test/surface-inventory.json`, `test/impact-map.json`, `test/quarantine.json`, affected-file planning via `--changed`, `tools/plan_tests.mjs`, `tools/validate_test_surface.mjs`, and `tools/run_tests.mjs timing summaries`. Future expensive browser/storage/GPU tests should enter as small manifest slices with timing evidence and non-claims.
