# keyring mock backend must not masquerade as persistent store support

This scenario captures a production app that uses a native keyring backend on supported targets but swaps to the `keyring` mock store in tests.

The mock store is extremely useful, but it provides **no persistence** and must not inherit the persistence contract of the native store.
