# Delivery settlement after send fence

`deliverysettlement.py` turns a delivered-looking public-edge write into a separate local settlement observation.

It joins:

```text
send fence report
delivery witness report
settlement markers
ack digest
sequence / previous digest
family and path-family diversity
hard-negative pressure
```

It rejects component drift, replay, sequence rollback, same-sequence forks, previous-link mismatch, ack conflict, non-delivered terminal claims, and hard negatives.

Design rule:

```text
A delivery witness is evidence.  Settlement is another exact-boundary permission.
```

Needle: delivery settlement.
