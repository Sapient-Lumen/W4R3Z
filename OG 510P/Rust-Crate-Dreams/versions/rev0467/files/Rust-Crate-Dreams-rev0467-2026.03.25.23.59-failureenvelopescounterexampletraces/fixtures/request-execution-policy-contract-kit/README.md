# Request Execution Policy Contract Kit fixtures

These fixtures support **P-0530 Request Execution Policy Contract Kit**.

They exist to keep four receiver-facing truths separate:

1. **idempotency basis** — why replay is safe;
2. **attempt budget** — how many attempts and under what time/backoff rules;
3. **admission path** — where queueing, limiting, rate control, and shedding happen;
4. **attempt topology** — whether execution is single, serially retried, or hedged in parallel.

The scenarios are deliberately small and comparative.
They are designed to stop future passes from flattening “supports retries / timeout / rate limiting” into one fake execution-policy story.
