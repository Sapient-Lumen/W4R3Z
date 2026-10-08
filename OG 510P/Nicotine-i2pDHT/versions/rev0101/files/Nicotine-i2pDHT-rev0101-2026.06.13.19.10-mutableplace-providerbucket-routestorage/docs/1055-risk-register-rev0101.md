# Risk register rev0101

High-risk seams now modeled:

- mutable rollback/fork/tombstone/gap pressure after ingress
- provider-index bucket overflow and content-storage temptation
- route-table monoculture and garden/introducer authority drift
- hard-negative memory dropped during local placement
- accepted records quietly becoming state without exact-boundary checks

Open risks:

- no live churn model for bucket aging
- no production mutable-record storage backend
- no production provider proof protocol
- no live I2P routing transport
