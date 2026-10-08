# serializable secret opt-in must not masquerade as default export safety

This scenario captures an application that uses `secrecy` but explicitly opts certain secret payloads back into `serde` serialization.

That may be intentional, but it widens the export surface and should not inherit the default “serialization disabled” posture.
