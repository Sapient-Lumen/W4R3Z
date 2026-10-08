# Wake from amnesia — rev0100

Start here after opening the cube cold:

1. Read `docs/1038-rev0100-recordingress-providersemantics-routingspine.md`.
2. Run `pytest tests/test_rev0099_substratereturn_recordoracle_spineaudit.py tests/test_rev0100_recordingress_providersemantics_routingspine.py`.
3. Run `python scripts/evidence/run_micro_simulation.py`.
4. Run `python scripts/evidence/run_cube_audit.py`.

Memory sentence: rev0099 returned to the Python-owned substrate; rev0100 starts admitting records only through Python-owned ingress, provider semantics, and routing-anchor gates.
