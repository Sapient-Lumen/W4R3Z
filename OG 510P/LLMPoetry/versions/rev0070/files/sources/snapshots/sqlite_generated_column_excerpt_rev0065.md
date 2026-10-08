# SQLite generated columns — bounded documentation note (rev0065)

Source: official SQLite documentation, *Generated Columns*.
Accessed: 2026-06-18T04:34:00-04:00.
Evidence reference: turn515699view3 lines 38–80.

Bounded observations used in P0003-D004:

- A generated column derives its value from other columns in the same row and is not directly writable.
- A VIRTUAL generated column is computed when read.
- D004 changes an ordinary usual-residence field; `vacancy_status` changes only because its expression is recomputed.

This note verifies a mechanism boundary only; it is not literary evidence.
