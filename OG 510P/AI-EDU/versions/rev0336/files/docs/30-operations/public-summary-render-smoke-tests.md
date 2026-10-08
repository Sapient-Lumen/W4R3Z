# Public-summary render smoke tests

Public summaries should be generated from validated service records and redaction profiles, not
rewritten from marketing copy. This surface defines smoke tests for the renderer implied by
[`public-summary-redaction-profiles.md`](public-summary-redaction-profiles.md).

The tests are intentionally modest. They do not prove that a public notice is legally sufficient,
pedagogically wise, or locally approved. They catch preventable leakage and overclaiming before a
human reviewer starts.

## Render checks

| Check | What must pass |
|---|---|
| `RS0` profile exists | Every service-record profile reference resolves to an example profile. |
| `RS1` allowed fields only | The rendered text uses only fields allowed by the selected profile. |
| `RS2` mandatory messages | Profile mandatory messages are appended or already clear. |
| `RS3` no forbidden phrases | Rendered text does not contain profile-specific forbidden phrases. |
| `RS4` human route visible | Profiles requiring contact include a human contact or appeal route. |
| `RS5` weak/stale claim removal | Weak or expired evidence claims do not appear as public promises. |
| `RS6` default profile listed | The default profile appears in the record's profile list. |

`tools/check_public_summary_renders.py` runs these checks against the shipped service-record examples
and redaction-profile examples.

## What the smoke test does not do

The smoke test does not decide whether a summary should publish. It only says the candidate render
is structurally safe enough for human review. Final publication still depends on:

- local owner approval;
- protected-route review;
- evidence freshness;
- sector-adapter obligations;
- current incident/security posture;
- learner, family, staff, or partner notice requirements.

## Manual review prompts

After the tool passes, reviewers should still ask:

1. Would a learner understand what the service does not do?
2. Would a family or teacher know who to contact?
3. Does any claim sound stronger than the evidence grade permits?
4. Does the notice accidentally reveal a protected support fact?
5. Does the notice hide a record effect, queue effect, or official consequence?
6. Is the summary still true after the latest model, workflow, owner, or policy change?

## Current archive bet

Role-appropriate transparency needs tests before prose polish. A plain public summary that exposes
nothing protected and overclaims nothing is more valuable than a polished announcement that blurs
limits.

See [`public-summary-redaction-profiles.md`](public-summary-redaction-profiles.md),
[`public-pilot-summary-examples.md`](public-pilot-summary-examples.md),
[`import-readiness-manifest-and-no-real-data-gate.md`](import-readiness-manifest-and-no-real-data-gate.md),
and `AS-0227`.
