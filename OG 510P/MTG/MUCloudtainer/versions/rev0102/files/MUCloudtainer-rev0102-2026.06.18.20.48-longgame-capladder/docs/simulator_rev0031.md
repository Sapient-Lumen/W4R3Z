# rev0031 simulator note

rev0031 does not change card semantics. It changes how we test and prepare the simulator for acceleration.

The simulator remains Python-authoritative. C++ now checks whole forced-action segments, not merely isolated one-action transitions. This matters because a future C++ speedup must carry state across multiple engine steps without re-entering Python after each pass.

No-choice segments are not a new strategic abstraction. They are a transport/acceleration seam:

```text
public legal frame has exactly one legal action
  ↓
no agent choice is needed
  ↓
C++ can eventually advance until the next real choice
```

The current checker proves parity on archived smoke traffic. It does not yet replace the Python rollout loop.
