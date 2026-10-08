# ACK repair join boundary

`ackrepairjoin.py` joins the delivered ACK lane and the missing-ACK repair lane.

It accepts exactly one of these local states:

```text
terminal ACK/archive/prune path
retry repair path
withdraw repair path
```

It quarantines the dangerous mixed state:

```text
terminal ACK accepted + retry/withdraw repair accepted for the same object
```

It also checks boundary drift, digest drift, hard-negative pressure, remote-commit evidence, low diversity, and retry-idempotency collision.

The practical guess is that late ACKs and missing ACKs will happen in any real network. The cube should therefore make contradiction explicit before live transport exists.

ackrepairjoin audit needle: ACK settlement and repair prune guard.
