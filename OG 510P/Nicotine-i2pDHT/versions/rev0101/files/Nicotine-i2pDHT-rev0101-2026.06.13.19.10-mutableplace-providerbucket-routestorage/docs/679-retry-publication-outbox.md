# Retry publication outbox

Retry publication is not a resend button. `retrypublish.py` treats retry/withdraw settlement as an input claim and stages publication only with previous-linked markers, component digest binding, family/path diversity, and hard-negative checks.

Late ACK aborts suppress retry publication. Retry-terminal settlement can stage retry publication. Withdraw-terminal settlement can stage withdraw publication. Pending or watchful settlement remains held.
