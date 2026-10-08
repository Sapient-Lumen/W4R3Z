# Miri passes but the FFI boundary stays out of scope

This scenario keeps one operational truth visible:
a passing Miri run can still leave foreign behavior, callbacks, or external symbol assumptions outside the witness boundary.

The receipts should distinguish a useful local witness from a whole-system proof.
