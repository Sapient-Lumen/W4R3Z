## Peer-row granularity review

### Question this page answers
When the product shows one row or one count, is it talking about **a user**, **a linked-device family**, **one concrete device**, or only **a presentational grouping**?

### Review branches

#### 1) Advanced-folder grouped user row
Use this branch when the folder family supports identity-aware grouping.
Render:
- one **grouped user row**
- expandable **device-seat children** beneath it
- permission scope that applies to the grouped authority unit
- explicit note that visible child-device count can exceed grouped-user count

#### 2) Standard-folder device rows
Use this branch when the folder family does not preserve user identity in the peer list.
Render:
- one row per **device seat**
- no overclaim that several rows are one authority unit unless a stronger proof exists outside the row itself
- explicit warning that a human may appear multiple times through linked devices

#### 3) Renamed-device same-identity case
When device label changes but certificate continuity survives:
- keep the authority unit stable
- show label drift as presentation drift, not participant replacement

#### 4) Identity-regenerated same-human case
When the human-facing name looks familiar but certificate continuity changed:
- treat it as a **new authority unit**
- show prior approval memory as non-transferable unless re-proven

### Count-truth ladder
- **row count** is weaker than **device-seat count**
- **device-seat count** is weaker than **grouped authority count**
- **grouped authority count** is weaker than **permission-bearing participant count**
- **permission-bearing participant count** is weaker than **future-arrival coverage count**

### Forbidden overclaims
Do not let the UI say:
- `2 peers` when it really means two rows of unknown unit class
- `1 user` when the surface only proves one grouped row
- `approved participant` when approval memory scope is only inferred from a row label
