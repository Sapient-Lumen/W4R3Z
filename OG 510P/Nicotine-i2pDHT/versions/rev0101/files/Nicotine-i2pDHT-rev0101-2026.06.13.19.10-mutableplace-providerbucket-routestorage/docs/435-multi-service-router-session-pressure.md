# Multi-service router/session pressure

A garden profile can run several giving services: seed gate, head watcher, witness cache, bridge relay, provider repair, or catalog mirror. rev0041 proved that one service can model stop/resume. rev0042 adds the missing shared-router pressure: one drained service cannot stop the bundled router while sibling services still need it.

`ServiceRuntimeObservation` is signed local evidence with service name, profile id, session digest, router report digest, state, public-bridge bit, family/path hints, sequence, freshness window, and signer. `assess_multi_service_action` then evaluates isolated session stops versus shared-router actions.

Current risky cases tested:

- isolated target session stop can pass while sibling services remain active;
- bundled-router stop is held when active siblings exist;
- bundled-router stop is held while public bridge exposure remains active;
- shared-router actions need service/path family diversity;
- service observation replay, signature failure, profile drift, router drift, session drift, and same-sequence forks quarantine.

Design guess: a multi-service garden should prefer keeping the router running unless all visible service observations agree that shared-router change is safe.
