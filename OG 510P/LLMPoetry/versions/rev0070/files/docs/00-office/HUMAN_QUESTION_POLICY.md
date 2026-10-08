# Human question policy

The human owner can always steer the project. Future LLM instances may ask questions, but the cube should not become helpless while waiting for an answer.

## Non-blocking default

Questions are recorded in `registries/human_questions.json` and summarized in `HUMAN_QUESTIONS.md`. A future operator should proceed under the recorded default unless the human has answered.

## Blocking only when necessary

A question may block action only when it affects:

1. safety;
2. consent or privacy;
3. legality or rights;
4. whether the human wants a particular creative act at all;
5. a user-provided constraint that cannot be responsibly guessed.

Aesthetic preferences are important, but they should normally become logged defaults, not stoppages.

## Current questions

The current live questions concern P0001 risk profile and human-intervention logging granularity. Defaults are recorded so work can continue.
