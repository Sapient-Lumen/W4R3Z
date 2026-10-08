# rev0061 — deliveryrepair-liveegress-rollbackprobe

This revision follows rev0060's live-send / delivery-witness / send-fence seam into the next bad local state:

```text
live-send gate accepted
+ delivery witness is pending
+ send fence is pending
    != safe retry
    != safe withdraw
    != safe to forget missing acknowledgement
```

rev0061 adds three no-network surfaces:

- `deliveryrepair.py`: missing ACK repair probes, withdraw repair, replay/fork/previous-link checks.
- `rollbackprobe.py`: exact-boundary observations that no remote commit was seen before retry.
- `liveegress.py`: final no-network retry/withdraw gate that refuses duplicate public effects.

Strong sentence:

```text
A missing acknowledgement is not failure, success, or retry permission; it is sticky repair state until repair probes, rollback observations, and egress budgets agree at one exact boundary.
```

The audit/refactor lane is `egressfold.py`, which preserves rev0060 `fenceaudit` predecessor history while pinning the new current surfaces.
