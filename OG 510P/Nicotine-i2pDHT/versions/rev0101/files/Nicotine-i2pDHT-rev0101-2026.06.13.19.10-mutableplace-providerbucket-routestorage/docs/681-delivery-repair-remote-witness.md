# Delivery repair remote witness

`deliveryrepairmesh.py` adds remote witness pressure after duplicate delivery becomes possible. A duplicate can be benign only when diverse witnesses say the remote state still matches the intended payload. If remote witnesses report a conflict, the lane accepts repair-required state rather than pretending the retry succeeded cleanly.

Remote witness reports are evidence, not consensus and not global truth.
