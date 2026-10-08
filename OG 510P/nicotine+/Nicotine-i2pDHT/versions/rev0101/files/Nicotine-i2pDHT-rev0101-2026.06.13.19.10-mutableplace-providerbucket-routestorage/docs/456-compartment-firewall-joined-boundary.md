# Compartment firewall joined boundary

`compartmentfirewall.py` joins four earlier local reports:

1. key-compartment role reports,
2. authority-split assessment,
3. control-intent join report,
4. bridge-firewall report.

The reducer rejects role reuse, missing roles, authority quarantine, control/firewall rejection, profile/service/scope/request drift, public-mode mismatch, close-mode mismatch, low diversity, and live hard-negative pressure.  It deliberately does no network work.  Its output digest is the exact precondition a later side-effect lane may reference.

This is the seam where public bridge exposure becomes especially dangerous: a bridge can look operationally valid while its operator, router, and service keys silently collapse into one compromise domain.
