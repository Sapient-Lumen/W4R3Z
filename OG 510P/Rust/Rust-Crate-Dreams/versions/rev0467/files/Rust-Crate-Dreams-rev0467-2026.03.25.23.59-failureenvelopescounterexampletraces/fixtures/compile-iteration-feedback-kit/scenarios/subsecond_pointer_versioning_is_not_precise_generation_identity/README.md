# Subsecond pointer versioning is not precise generation identity

This scenario freezes the fact that Subsecond can detour a call to the latest function body while still lacking precise function-generation metadata.
`ptr_address` can change in a way that treats every function as “new,” which is useful for safety but too coarse to serve as a stable route-level generation witness.
