# Package hygiene and validator audit — rev0026

Rev0026 removed 5 accidental Python cache files from the working tree before packaging and records that exclusion in `PYCACHE-EXCLUSION-RECEIPT-REV0026.json`.

The refactor remains non-destructive: root surfaces are shadow-mapped, not moved. The validator gained `tools/validators/rev0026_litigation_office_checks.py`, while `make lint` remains the stable entrypoint. New litigation arrays have schema pointers and facet checks, but universal JSON Schema enforcement remains deferred.
