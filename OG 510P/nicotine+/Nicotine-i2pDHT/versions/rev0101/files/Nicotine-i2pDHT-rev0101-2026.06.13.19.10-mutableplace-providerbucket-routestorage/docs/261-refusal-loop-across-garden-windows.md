# Refusal loop across garden windows

`src/i2p_dht_lab/refusalloop.py` extends `workmeter.py` across repeated windows. Useful refusal remains good: gardens should be able to say no with a signed retry hint. The risk is laundering, where repeated refusal-only windows masquerade as contribution.

The current model detects:

- replayed refusal/work receipts across windows;
- refusal-only or refusal-heavy streaks;
- single-family repeated windows;
- invalid underlying work-meter windows;
- balanced service that includes bounded useful refusal.

The rule stays local:

```text
Useful refusal is capacity evidence, not completed work and not currency.
```
