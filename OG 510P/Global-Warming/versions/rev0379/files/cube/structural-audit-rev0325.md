# Structural audit rev0325

The material change in rev0325 is not another broad registry. It is a local-evidence capture mechanism that can be run against arbitrary folders of exercise artifacts. The evidence-bag builder computes original SHA-256 hashes, writes a manifest and packet JSON, separates sensitive-annex review from public surrogates, and records that no imported bag can auto-close readiness.

The important refactor is the new route:

`minute-zero field capture → evidence bag builder → manifest/hash/custody/sensitive-annex split → validator state → adjudication queue → CAP/retest/verifier → public claim gate`

Public IPAWS/OpenFEMA archive records, FEMA Message Viewer context, public schedules, and public meeting transcripts are explicitly downstream corroboration or contradiction sources. They are not local closure evidence.

The legacy universal crossproduct matrices remain compatibility surfaces only. The scoped emergency SQLite mirror contains rev0325 evidence-bag and alert-archive views; it is not a full archive mirror.
