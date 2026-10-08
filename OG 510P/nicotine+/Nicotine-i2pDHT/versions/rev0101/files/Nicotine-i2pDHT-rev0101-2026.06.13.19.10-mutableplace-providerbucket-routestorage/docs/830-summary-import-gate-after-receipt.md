# Summary import gate after receipt

A receipt does not mutate import state. The import gate requires the export receipt and export fence to agree at the same exact boundary before a redacted summary can be considered import-ready.

The import gate catches:

- export receipt pending
- export fence pending
- import not permitted
- boundary drift
- receipt/export digest drift
- raw leaks
- redaction or contradiction drops
- low family/path diversity

This remains no-network protocol pressure.
