# Scenario family — wiremock recipe exists, but the official fake transport is different

This fixture family exists for SDKs and HTTP clients where maintainers show a community mock-server recipe but also ship an in-process fake transport or transcript-replay adapter.

It is meant to catch support drift such as:

- README guidance implying `wiremock` is the official route when the crate really supports a different fake,
- an in-process fake transport losing parity while community recipes keep passing,
- or scenario corpora that are only witnessed against one backend while the docs imply both.

A good test-surface pack should make three things explicit:

1. which fake backend is **officially_supported**,
2. which recipes are only `best_effort_example`,
3. and which scenarios are witnessed by which backend class.

This family keeps “the ecosystem has a good HTTP mock crate” separate from “this crate publishes a stable fake-backend contract for its downstream users”.
