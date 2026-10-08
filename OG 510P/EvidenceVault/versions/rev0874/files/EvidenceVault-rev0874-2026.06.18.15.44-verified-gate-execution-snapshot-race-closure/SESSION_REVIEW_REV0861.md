# Session review — rev0861

Focus: loose streamfold payload recovery.

The riskiest unfinished edge was that rev0860 required recovered payload bytes to
already exist at exact canonical paths. rev0861 adds an executable hash-first
locator that can scan loose candidate roots and stage a complete unique match set
back to canonical paths.

Substantive changes:

- Added `locate_streamfold_payloads_rev0861.py` for exact byte-count/SHA-256
  candidate-root scans.
- Added no-candidate absence reports for the 17-file full set and 4-file minimum
  first recovery set.
- Added synthetic controls for loose-path acceptance, duplicate hash ambiguity,
  symlink skipping, path escape rejection, unsafe stage rejection, and partial
  recovery rejection.
- Added parent-linked rev0861 PCD-style claim/public-input/commitment/certificate
  surfaces and a targeted validator.

Next best step: mount or extract a likely canonical/cache/export source and run
`locate_streamfold_payloads_rev0861.py --mode minimum --stage-dir ...`. Build the
next lane over real staged payload bytes only if hashes match.

Publication remains blocked and no streamfold payload bytes were invented.
