# Native shadow call

`nativeshadowcall.py` models a future native leaf observation after `dispatchfence` has accepted a Python-held path.

Rules:

- shadow mode must be explicit;
- native result selection is forbidden;
- native authority claims quarantine;
- Python fallback must remain active;
- dispatch-fence, oracle, fallback, tombstone, quarantine, and crash memory must be preserved;
- a native result digest is only evidence.

The point is to let the lab collect native-result observations without letting them become dispatch permission.
