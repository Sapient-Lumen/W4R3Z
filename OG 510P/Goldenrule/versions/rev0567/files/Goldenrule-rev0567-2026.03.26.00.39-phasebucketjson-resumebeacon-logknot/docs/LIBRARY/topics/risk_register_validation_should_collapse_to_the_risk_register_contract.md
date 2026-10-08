# Risk-register validation should collapse to the risk register contract

The retained validation summary for the risk register is only a compact machine-checkable view of the standing risk-register contract.
The durable object should stay the risk register itself plus the rule that validation tracks `domain_counts`, `status_counts`, `overdue_open_or_mitigated`, and `total`.

## Archive consequence

Cite this topic and `docs/RISK_REGISTER.md` instead of preserving another validation-summary family when the only durable question is whether the risk register remains populated, classed, and not silently overdue.
