# rev0313 mission kernel

`FT-0181` is still the live mission kernel: route exactly one bounded owner-field
action at a time until real owner-reviewed `SRC2+` evidence exists. The archive
must not substitute local validation success, generated scratch, release
metadata, or public-language controls for actual owner evidence.

The rev0313 risk is practical rather than doctrinal. Rev0308 moved positive
validator source chains into `scratch/field/ft0181/validation/...` to keep them
out of checker scratch. That made them field-shaped. Rev0313 prevents those
fixtures from contaminating later router/report scans.

The working rule is now:

> field-lane validation fixtures may test controls, but they cannot become live
> field state.

The next real action remains router/report-first:

```bash
make owner-field-report
make owner-field-work
make owner-field-next CSV=/path/to/real-owner-return.csv
```

No owner was contacted by this revision. No real CSV or `SRC2+` packet was
accepted. No active window, readout, public claim upgrade, service-record change,
or closure was authorized.
