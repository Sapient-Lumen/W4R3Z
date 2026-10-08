# Wake from amnesia — rev0088

Start here after opening the cube:

1. Read `docs/918-rev0088-nativeunload-sandboxstub-crashgc.md`.
2. Run `pytest tests/test_rev0088_nativeunload_sandboxstub_crashgc.py`.
3. Inspect `src/i2p_dht_lab/nativeunload.py`, `nativesandboxstub.py`, and `nativecrashgc.py`.
4. Remember the nonclaim: the sandbox is a no-network stub, not production isolation.

The revision continues the native/GCC line from rev0081 through rev0087 without granting native authority.
