# Native fault seal

`faultseal.py` makes native shadow-call and result-diff outcomes restart-sticky.

A matching native result can be sealed as non-authority evidence. A mismatch can be sealed to Python fallback and native quarantine. Either way, the seal binds dispatch-fence, shadow-call, result-diff, artifact/source/fallback/oracle/vector/result digests, sequence memory, and diversity pressure.

Fault seal is not cleanup. It is local memory that prevents a bad native artifact from being rediscovered as fresh after restart.
