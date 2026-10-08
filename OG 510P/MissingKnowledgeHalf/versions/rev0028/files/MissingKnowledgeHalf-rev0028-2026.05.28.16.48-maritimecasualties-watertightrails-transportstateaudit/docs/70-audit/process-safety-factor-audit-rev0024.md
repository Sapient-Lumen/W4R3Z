# Process-safety factor audit — rev0024

This audit adds a factor overlay rather than a new hard schema. It uses axes: inventory/energy, barrier health, leading/lagging metrics, MOC/mechanical integrity, offsite consequence, regulatory/guidance rail, and correction infusion.

Findings:

1. The cube needed a process-safety overlay because prior engineering records were too incident-type driven.
2. BP Texas City should be refactored in a later pass using these axes.
3. CSB, OSHA PSM, EPA RMP, and CCPS/OSHA metrics must remain rails, not proof of effectiveness.
4. Pattern maturity is explicitly blocked until controls and recommendation-closure records exist.
5. New sources use explicit locators; legacy locator debt is not paid down in this pass.
