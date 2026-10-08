# Claim-register validation should collapse to the claim register contract

The retained validation summary for the claim register is only a compact machine-checkable view of the standing register contract.
The durable object should stay the claim register itself plus the rule that validation tracks `class_counts`, `status_counts`, `strict_active_claims`, and `total`.

## Archive consequence

Cite this topic and `docs/CLAIM_REGISTER.md` instead of preserving another validation-summary family when the only durable question is whether the register contract stayed populated and classed.
