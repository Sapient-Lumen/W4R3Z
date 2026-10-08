# Native result diff

`resultdiff.py` compares a shadow native result against the Python-oracle result.

Matching results become shadow evidence only. Mismatches become native-fault pressure and preserve fallback/quarantine memory. Missing native results can be watched without treating absence as success.

This keeps the native branch useful for optimization research while preventing C output from becoming protocol truth.
