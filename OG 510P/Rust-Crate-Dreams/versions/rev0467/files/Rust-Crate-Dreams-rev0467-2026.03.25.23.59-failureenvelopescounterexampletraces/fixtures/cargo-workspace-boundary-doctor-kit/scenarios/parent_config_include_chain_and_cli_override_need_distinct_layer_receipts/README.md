# Scenario — parent config include chain and CLI override need distinct layer receipts

This scenario exists because a single “effective config files” list is not enough.
A parent config can include another file, and a later CLI override can still win.
The receiver needs both **ancestor discovery** and **config layering** to review the incident honestly.
