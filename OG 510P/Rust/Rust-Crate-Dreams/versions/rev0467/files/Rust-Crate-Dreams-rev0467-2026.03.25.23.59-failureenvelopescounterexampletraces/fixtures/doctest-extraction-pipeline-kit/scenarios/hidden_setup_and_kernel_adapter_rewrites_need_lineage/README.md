# Hidden setup and kernel adapter rewrites need lineage

This scenario keeps three facts separate:
- rustdoc extracted a doctest from a public item,
- hidden setup lines already existed in the source example,
- and a kernel/embedded-specific adapter injected additional harness material after extraction.

The support contract must not flatten those into “the example ran”.
