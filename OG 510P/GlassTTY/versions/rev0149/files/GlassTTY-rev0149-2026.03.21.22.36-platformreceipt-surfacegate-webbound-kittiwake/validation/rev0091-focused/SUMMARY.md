GlassTTY rev0091 focused validation

- focused pytest: PASS (49 passed)
- py_compile: PASS
- extension typecheck: PASS
- extension build: PASS
- direct deferred broker-intent proof: PASS (secondary-only one-shot helpers do not create daemon.sock; owner-candidate health ping claims broker lazily)
- archive audit: PASS
- package verification: PASS
- honest gap: no fresh live Chromium/native-host/browser round-trip proven here
- honest gap: the full smoke/full-suite lane still exceeds this container's practical runtime budget, so this handoff relies on focused proofs rather than a green all-tests wrapper
