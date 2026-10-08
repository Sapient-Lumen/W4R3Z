# BVPS rev0379 response/receipt inbox

Place each request's receipt or response files in a request-specific subdirectory, for example:

`evidence-intake/bvps-rev0379/inbox/RRT-0378-013/`

Then run:

`python tools/bvps_response_intake_rev0379.py --root . --request-id RRT-0378-013 --input-dir evidence-intake/bvps-rev0379/inbox/RRT-0378-013`

The importer copies files into `evidence-intake/bvps-rev0379/imported/<request-id>/`, writes SHA-256 hashes, and appends an import manifest to the matching sidecar. It does not perform DLP review or adjudicate proofcuts.
