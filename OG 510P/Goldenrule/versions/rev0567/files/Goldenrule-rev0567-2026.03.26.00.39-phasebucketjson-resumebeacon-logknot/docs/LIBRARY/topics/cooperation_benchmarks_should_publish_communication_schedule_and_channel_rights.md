# Cooperation benchmarks should publish communication schedule and channel rights

Communication is not a harmless wrapper around the same cooperation benchmark.
A benchmark can change behavior by changing **whether communication is allowed**, **when it is allowed**, and **what kind of messages are permitted**.
Two recent sources now make the compact archive rule clear:

- `RS-GR-055` shows that in indefinitely repeated human–AI Prisoner's Dilemma, changing communication timing from pre-play-only to every-round chat changes the treatment interpretation itself: repeated communication boosts human–human cooperation but has almost no detectable extra effect against the AI partner.
- `RS-GR-056` shows that allowing communication can materially raise cooperation with both humans and LLMs, even when it does not eliminate the human–machine gap.

## Minimum contract

Whenever a cooperation benchmark includes any message channel, publish:

1. whether communication is **disallowed**, **pre-play only**, **every round**, or otherwise scheduled;
2. whether messages are **free-form**, **templated**, or **tool-mediated**;
3. any **turn limits**, **token limits**, or moderation / filtering applied to messages;
4. whether both sides have **symmetric message rights**;
5. and whether headline results are compared **within one communication regime** or **pooled across regimes**.

## Implementor consequence

Do not compare or pool cooperation scores across studies or lanes if the communication schedule or channel rights differ.
A policy can look more or less cooperative partly because the benchmark changed the communication contract rather than the strategic situation.

## Archive consequence

Keep the retained object tiny.
One benchmark-card row is enough: communication schedule, channel type, symmetry, and any binding message limits.
That prevents future sessions from laundering a communication-interface effect into a policy-generalization claim.
