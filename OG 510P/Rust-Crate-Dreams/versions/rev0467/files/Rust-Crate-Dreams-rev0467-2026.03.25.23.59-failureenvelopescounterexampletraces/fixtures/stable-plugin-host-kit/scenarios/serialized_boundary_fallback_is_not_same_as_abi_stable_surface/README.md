# serialized boundary fallback is a different surface class

This scenario captures a host that keeps dynamic loading but crosses the boundary with serialized messages or opaque handles.
The important truth is that this can be a useful fallback, but it is not the same claim as a typed stable-ABI module.

What the receipt should prove:

- the boundary class is `serialized_boundary`,
- the check basis is weaker and may rely on out-of-band contracts,
- and compatibility witnesses must reflect that narrower basis.
