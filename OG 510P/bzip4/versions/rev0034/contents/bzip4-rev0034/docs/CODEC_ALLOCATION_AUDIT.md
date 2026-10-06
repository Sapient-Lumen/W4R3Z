# Codec allocation audit

The imported `bz3_new` allocated the suffix-array workspace and immediately
called `memset` on it. The combined allocation-failure check occurred only
after that write. If the suffix-array allocation returned null, the error path
therefore dereferenced null instead of cleaning up and returning initialization
failure.

The active C++20 translation now follows this order:

1. allocate all state components;
2. test every pointer;
3. free any successful partial allocations on failure;
4. initialize the suffix-array bytes only after all allocations are valid.

This does not alter successful encoded bytes. The immutable upstream C oracle is
left untouched so differential tests remain an honest upstream comparison.
