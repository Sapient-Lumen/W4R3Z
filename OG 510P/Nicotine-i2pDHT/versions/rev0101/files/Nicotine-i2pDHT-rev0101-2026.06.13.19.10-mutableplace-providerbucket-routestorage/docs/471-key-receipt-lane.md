# Key receipt lane

`keyreceiptlane.py` keeps key authority separate from public bridge epochs.

A public bridge epoch can be syntactically valid while operator-key rotation, key compartment evidence, successor repair, or hard-negative scans are stale or under-diverse. The lane models signed receipts for:

- key compartment acceptance;
- operator rotation;
- succession repair;
- bridge epoch authorization;
- hard-negative scan.

Receipts can accept, watch, refuse, or quarantine. Watch does not silently become accept. Refusal is a local hard stop. Family and path diversity are required before receipt memory can be used.

Receipts are evidence, not reputation and not global governance.
