# rev0314 mission kernel

`FT-0181` remains the live mission kernel: move from a real owner contact clock to a real returned owner packet without letting local metadata become evidence.

The rev0314 risk was practical and close to completion. A contact-status JSON could say `SENT_AWAITING_REPLY` or `REASK_AWAITING_REPLY` and carry plausible dates, but downstream intake did not re-read the send-log or reask-log that allegedly created the clock. That left a path for stale or copied clock metadata to become a believable source gate for returned-owner CSV intake.

The working rule is now:

> returned-owner intake may trust an active contact clock only after the clock is re-anchored to its field-lane send/reask source artifact.

The next real action remains router/report-first:

```bash
make owner-field-report
make owner-field-work
make owner-field-next CSV=/path/to/real-owner-return.csv
```

No owner was contacted by this revision. No real CSV or `SRC2+` packet was accepted. No active window, readout, public claim upgrade, service-record change, or closure was authorized.
