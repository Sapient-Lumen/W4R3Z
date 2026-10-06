# Related-work research pass 031 — admission model oracles

Current revision: rev0054

This pass treats `StorageLaneAdmissionHistoryRunner` as earned but not yet trusted enough for OPFS/browser spending. The next pressure is not a larger provider; it is a better oracle.

Ideas stolen into the cube:

- **Model-based testing:** generated commands should be checked against a smaller model, not just against happy-path assertions.
- **Deterministic simulation:** every generated history should be seed-addressable and replayable.
- **History checking:** a proof artifact should say what claim it checked and what it did not check.
- **Finite-state resilience thinking:** admission, provider health, watermarks, retry, and no-mutation behavior should be represented as state transitions with trace evidence.

This revision adds no external code and imports no dependencies. The sources remain research pressure only; the implementation is a small fake-provider model oracle.

Non-claims preserved: No OPFS storage-lane admission-history model proof. No browser Worker storage-lane admission-history model proof. No production overload-governance claim. No exhaustive model checking or formal verification claim. No cross-browser conformance claim. No WebGPU proof.
