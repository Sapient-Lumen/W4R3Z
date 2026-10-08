# Risk register rev0037

Still risky:

- exact-scope tickets are toy dataclasses, not a production token format;
- receipt sequences are local pressure, not consensus;
- refusal-loop thresholds are guessed;
- ticket issuance is not yet joined to a full scheduler side-effect lane;
- service receipt evidence is not yet persisted through journal/checkpoint;
- no live I2P/SAM transport validates timing, churn, or router behavior.
