# Control receipt restart memory

`controlreceipt.py` records a joined compartment-firewall report as a signed local receipt.  A receipt is scoped by profile, service, scope digest, request digest, report digest, sequence, previous receipt digest, time window, signer, and family.

The tests cover bad signatures, expiry, replay, rollback, same-sequence forks, previous-link mismatch, kind mismatch, report-digest drift, unaccepted joined reports, and receipt-family monoculture.  A receipt is not a global truth object.  It is local memory that prevents restart and later side-effect code from forgetting which exact joined report it relied on.
