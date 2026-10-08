# Risk register rev0094

Risks exercised:

- native shadow result accidentally selected as authoritative;
- Python fallback memory dropped after a successful shadow call;
- native mismatch treated as a test failure rather than sticky fault pressure;
- restart rediscovery of a bad native artifact;
- current fold path drifting away from the native branch spine.

Remaining risk: this is still a no-production protocol lab; there is no sandbox, no production native ABI, and no native parser/crypto.
