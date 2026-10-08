# Proof obligation — rev0030

rev0030's local proof obligations are:

1. Absence cannot be accepted as durable unless tombstone evidence joins diverse empty observations.
2. Key compromise recovery cannot rely on the compromised old key alone.
3. Peerbook entrance selection must check contact-family and introducer-family pressure.
4. SAM live-probe work must skip cleanly without a router and bind shadows to contact lease destinations when present.
5. Delta summaries must request repair rather than becoming truth.
6. Branchrecoverfold must keep recovered branchlets visible and preserve rev0029 foldseal regression.

Evidence:

```text
tests/test_rev0030_negspace_peer_delta_keycrisis.py
scripts/ci/run_python_cloudtainer_lane.sh
```
