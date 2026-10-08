# Risk register rev0083

Open risks:

```text
The native source audit is textual, not formal verification.
The parity vectors are deterministic coverage, not proof.
ctypes calls are still a future packaging and platform risk.
The current native leaf is XOR compare only.
No native parser or crypto is allowed by this revision.
No live I2P/SAM side effect exists.
```

Mitigation guess:

```text
Keep Python as oracle.
Keep fallback always available.
Treat native drift as quarantine, not optimization loss.
Make each native call exact-boundary evidence before future live transport.
```
