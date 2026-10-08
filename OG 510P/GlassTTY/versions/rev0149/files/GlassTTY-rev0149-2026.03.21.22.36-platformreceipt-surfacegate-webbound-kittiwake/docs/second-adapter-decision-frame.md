# Second adapter decision frame

The second adapter choice should be made explicitly, not by vague preference.

## Why this choice matters
The second adapter is how GlassTTY proves it is genuinely multi-surface rather than Claude-specific with ambitions.

## Decision criteria
Score or narrate each candidate on:
- workflow similarity to existing Claude lane
- expected editor/receiver complexity
- frame/route complexity
- likely support value to operators
- ease of collecting baseline evidence
- likelihood of giving reusable adapter lessons for the remaining surfaces
- risk of fast-moving drift before the first proof lands

## Candidate template

### Candidate: <surface>
- likely first lane:
- likely first workflows to prove:
- reasons it may be easier:
- reasons it may be harder:
- reusable lessons it could provide:
- minimum proof needed to justify selection:

## Decision output
When this choice is made, record in `DECISIONS.md`:
- chosen surface
- why it won
- the first lane
- the first workflow proof target
- what would count as an early success

## Machine-readable companion

Use `SECOND-ADAPTER-MATRIX.json` plus `python scripts/second-adapter-report.py --pretty` when the repo needs a repeatable ranking instead of a fresh prose-only argument.
