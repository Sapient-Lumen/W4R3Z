## Transfer-cost lineage receipt page

Each serious movement claim stores one durable receipt with these fields:

- requested sentence
- byte-cost class
- reuse basis
- splittability class
- queue order class
- strongest proof level
- active fallback trigger
- blocked stronger sentence

### Example blocked stronger sentences
- `this was higher priority` did **not** prove `this moved fewer bytes`
- `this was renamed` did **not** prove `this avoided retransmission`
- `this normally sends only changed pieces` did **not** prove `this specific edit avoided a whole-file resend`
