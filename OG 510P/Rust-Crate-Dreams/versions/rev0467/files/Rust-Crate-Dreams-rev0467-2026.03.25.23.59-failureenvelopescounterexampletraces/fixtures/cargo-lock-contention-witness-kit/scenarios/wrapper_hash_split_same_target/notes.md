# wrapper_hash_split_same_target

This scenario exists to keep two different stories separate:

1. **a live wait on a shared root**, and
2. **cache-mode drift caused by wrapper differences**.

The same workspace can experience both at once.
A good witness bundle should be able to report the wait conservatively while still exporting the wrapper context that makes reuse and mitigation expectations different.
