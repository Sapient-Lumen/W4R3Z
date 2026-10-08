# Capture batch plan — rev0013

The capture sequence is part of the evidence model.

1. Capture the DOJ SLS source-page backbone.
2. Capture volatile official news releases.
3. Capture and hash P0 legal PDFs privately.
4. Capture and hash P1 legal PDFs privately.
5. Capture the SLS news index for delta comparison.
6. Retry the Cleveland attachment anomaly with failure-mode logging.

This ordering prevents the cube from comparing source states that were captured in incompatible contexts. It also makes failures explicit: a failed fetch does not mean a document never existed, and a changed redirect does not mean the underlying legal effect changed.

